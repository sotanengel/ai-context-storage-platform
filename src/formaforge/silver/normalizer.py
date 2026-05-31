"""Silver normalization: route Bronze records to the correct converter."""

from formaforge.ai.ai_converter import AiConverter
from formaforge.models.bronze import BronzeRecord, StructureClass
from formaforge.models.silver import CdmDocument, ConversionMethod
from formaforge.silver.converters.base import BaseConverter
from formaforge.silver.converters.csv_converter import CsvConverter
from formaforge.silver.converters.docx_converter import DocxConverter
from formaforge.silver.converters.json_converter import JsonConverter
from formaforge.silver.converters.markdown_converter import MarkdownConverter
from formaforge.silver.converters.pdf_converter import PdfConverter
from formaforge.silver.converters.toml_converter import TomlConverter
from formaforge.silver.converters.xlsx_converter import XlsxConverter
from formaforge.silver.converters.xml_converter import XmlConverter
from formaforge.silver.converters.yaml_converter import YamlConverter
from formaforge.silver.pii_detector import PiiDetector

_DETERMINISTIC_CONVERTERS: dict[str, BaseConverter] = {
    "json": JsonConverter(),
    "jsonl": JsonConverter(),
    "yaml": YamlConverter(),
    "csv": CsvConverter(),
    "tsv": CsvConverter(),
    "xml": XmlConverter(),
    "toml": TomlConverter(),
    "markdown": MarkdownConverter(),
    "pdf": PdfConverter(),
    "docx": DocxConverter(),
    "xlsx": XlsxConverter(),
}


class UnknownFormatError(ValueError):
    pass


class SilverNormalizer:
    def normalize(
        self,
        record: BronzeRecord,
        conversion_method: ConversionMethod = ConversionMethod.AUTO,
    ) -> CdmDocument:
        raw_bytes = self._read_raw(record)
        effective_method = self._resolve_method(record, conversion_method)

        if effective_method == ConversionMethod.DETERMINISTIC:
            doc = self._convert_deterministic(raw_bytes, record)
        else:
            raw_text = raw_bytes.decode("utf-8", errors="replace")
            doc = AiConverter().convert(raw_text, record.source_uri, record.source_format)

        pii_flags = PiiDetector().detect(doc.body)
        if pii_flags:
            doc.frontmatter.pii_flags = pii_flags
        return doc

    def _resolve_method(
        self, record: BronzeRecord, requested: ConversionMethod
    ) -> ConversionMethod:
        if requested != ConversionMethod.AUTO:
            return requested
        if record.structure_class == StructureClass.STRUCTURED:
            return ConversionMethod.DETERMINISTIC
        fmt = record.source_format
        if fmt in ("pdf", "docx", "xlsx"):
            return ConversionMethod.DETERMINISTIC
        return ConversionMethod.AI

    def _convert_deterministic(self, raw_bytes: bytes, record: BronzeRecord) -> CdmDocument:
        fmt = record.source_format
        converter = _DETERMINISTIC_CONVERTERS.get(fmt)
        if not converter:
            raise UnknownFormatError(f"No deterministic converter for format: {fmt!r}")
        return converter.convert_bytes(raw_bytes, record.source_uri)

    def _read_raw(self, record: BronzeRecord) -> bytes:
        from pathlib import Path

        return Path(record.raw_content_path).read_bytes()
