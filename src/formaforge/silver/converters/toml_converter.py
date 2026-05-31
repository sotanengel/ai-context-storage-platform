"""TOML → CDM deterministic converter."""

import tomllib

from formaforge.models.silver import CdmDocument
from formaforge.silver.converters.base import BaseConverter


class TomlConverter(BaseConverter):
    source_format = "toml"

    def convert(self, raw: str, source_uri: str = "") -> CdmDocument:
        data = tomllib.loads(raw)
        fm = self._make_frontmatter(source_uri)
        blocks = self._classify_payload(data)
        return CdmDocument(frontmatter=fm, blocks=blocks)
