"""YAML → CDM deterministic converter."""

import yaml

from formaforge.models.silver import CdmDocument
from formaforge.silver.converters.base import BaseConverter


class YamlConverter(BaseConverter):
    source_format = "yaml"

    def convert(self, raw: str, source_uri: str = "") -> CdmDocument:
        data = yaml.safe_load(raw)
        fm = self._make_frontmatter(source_uri)
        blocks = self._classify_payload(data)
        return CdmDocument(frontmatter=fm, blocks=blocks)
