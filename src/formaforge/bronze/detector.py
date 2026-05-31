"""Format and structure class detection for Bronze ingestion."""

import json

from formaforge.models.bronze import StructureClass

_STRUCTURED_EXTENSIONS = {
    "json",
    "jsonl",
    "yaml",
    "yml",
    "csv",
    "tsv",
    "xml",
    "toml",
    "md",
    "markdown",
}
_UNSTRUCTURED_EXTENSIONS = {"pdf", "docx", "doc", "pptx", "txt", "png", "jpg", "jpeg"}

_FORMAT_BY_EXTENSION = {
    "json": "json",
    "jsonl": "jsonl",
    "yaml": "yaml",
    "yml": "yaml",
    "csv": "csv",
    "tsv": "tsv",
    "xml": "xml",
    "toml": "toml",
    "md": "markdown",
    "markdown": "markdown",
    "pdf": "pdf",
    "docx": "docx",
    "txt": "text",
}


class StructureClassifier:
    def classify(self, content: bytes, filename: str | None) -> StructureClass:
        ext = self._extension(filename)
        if ext in _STRUCTURED_EXTENSIONS:
            return StructureClass.STRUCTURED
        if ext in _UNSTRUCTURED_EXTENSIONS:
            return StructureClass.UNSTRUCTURED
        return self._classify_by_content(content)

    def detect_format(self, content: bytes, filename: str | None) -> str:
        ext = self._extension(filename)
        if ext in _FORMAT_BY_EXTENSION:
            return _FORMAT_BY_EXTENSION[ext]
        return self._sniff_format(content)

    def _extension(self, filename: str | None) -> str:
        if not filename:
            return ""
        parts = filename.rsplit(".", 1)
        return parts[-1].lower() if len(parts) > 1 else ""

    def _classify_by_content(self, content: bytes) -> StructureClass:
        text = content[:4096].decode("utf-8", errors="ignore").strip()
        if text.startswith("%PDF"):
            return StructureClass.UNSTRUCTURED
        if self._is_json(text):
            return StructureClass.STRUCTURED
        if self._is_xml(text):
            return StructureClass.STRUCTURED
        if self._looks_like_csv(text):
            return StructureClass.STRUCTURED
        return StructureClass.UNSTRUCTURED

    def _sniff_format(self, content: bytes) -> str:
        text = content[:4096].decode("utf-8", errors="ignore").strip()
        if text.startswith("%PDF"):
            return "pdf"
        if self._is_json(text):
            return "json"
        if self._is_xml(text):
            return "xml"
        if self._looks_like_csv(text):
            return "csv"
        return "text"

    def _is_json(self, text: str) -> bool:
        stripped = text.strip()
        if not (stripped.startswith("{") or stripped.startswith("[")):
            first_line = stripped.split("\n")[0].strip()
            if first_line.startswith("{") or first_line.startswith("["):
                try:
                    json.loads(first_line)
                    return True
                except json.JSONDecodeError:
                    return False
            return False
        try:
            json.loads(stripped)
            return True
        except json.JSONDecodeError:
            return False

    def _is_xml(self, text: str) -> bool:
        stripped = text.strip()
        return stripped.startswith("<?xml") or stripped.startswith("<")

    def _looks_like_csv(self, text: str) -> bool:
        lines = [ln for ln in text.split("\n") if ln.strip()]
        if len(lines) < 2:
            return False
        counts = [ln.count(",") for ln in lines[:5]]
        return all(c == counts[0] for c in counts) and counts[0] >= 1
