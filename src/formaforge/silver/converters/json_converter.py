"""JSON → CDM deterministic converter."""

import json

from formaforge.models.silver import CdmDocument
from formaforge.silver.converters.base import BaseConverter


class JsonConverter(BaseConverter):
    source_format = "json"

    def convert(self, raw: str, source_uri: str = "") -> CdmDocument:
        data = json.loads(raw)
        fm = self._make_frontmatter(source_uri)
        blocks = self._classify_payload(data)
        return CdmDocument(frontmatter=fm, blocks=blocks)
