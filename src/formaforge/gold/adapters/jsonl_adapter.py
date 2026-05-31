"""JSONL Gold adapter (OpenAI / Google / Anthropic fine-tune schemas)."""

import json
from typing import Any

from formaforge.gold.adapters.base import BaseAdapter
from formaforge.models.silver import CdmDocument
from formaforge.silver.cdm_writer import CdmWriter


class JsonlAdapter(BaseAdapter):
    adapter_name = "jsonl"

    def render(self, doc: CdmDocument, **opts: str) -> str:
        schema = opts.get("schema", "openai").lower()
        content = self._doc_to_text(doc)
        if schema == "openai":
            record = self._openai_record(content)
        elif schema == "google":
            record = self._google_record(content)
        else:
            record = self._anthropic_record(content)
        return json.dumps(record, ensure_ascii=False)

    def _doc_to_text(self, doc: CdmDocument) -> str:
        return CdmWriter().write(doc)

    def _openai_record(self, content: str) -> dict[str, Any]:
        return {"messages": [{"role": "user", "content": content}]}

    def _google_record(self, content: str) -> dict[str, Any]:
        return {"contents": [{"role": "user", "parts": [{"text": content}]}]}

    def _anthropic_record(self, content: str) -> dict[str, Any]:
        return {"messages": [{"role": "user", "content": content}]}
