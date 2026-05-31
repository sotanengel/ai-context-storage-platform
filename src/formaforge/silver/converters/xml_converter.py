"""XML → CDM deterministic converter."""

from typing import Any

import defusedxml.ElementTree as ET

from formaforge.models.silver import CdmDataBlock, CdmDocument
from formaforge.silver.converters.base import BaseConverter


class XmlConverter(BaseConverter):
    source_format = "xml"

    def convert(self, raw: str, source_uri: str = "") -> CdmDocument:
        root = ET.fromstring(raw)
        fm = self._make_frontmatter(source_uri)
        data = self._element_to_dict(root)

        if isinstance(data, dict) and len(data) == 1:
            inner = next(iter(data.values()))
            if (
                isinstance(inner, list)
                and inner
                and all(isinstance(i, dict) for i in inner)
                and self._is_uniform_object_array(inner)
            ):
                block = self._build_table_block(inner)
                return CdmDocument(frontmatter=fm, blocks=[block])

        data_block = CdmDataBlock(content=data)
        return CdmDocument(frontmatter=fm, blocks=[data_block])

    def _element_to_dict(self, element: Any) -> Any:
        children = list(element)
        if not children:
            text = (element.text or "").strip()
            return text if text else None

        child_dicts: dict[str, Any] = {}
        for child in children:
            key = child.tag
            value = self._element_to_dict(child)
            if key in child_dicts:
                existing = child_dicts[key]
                if not isinstance(existing, list):
                    child_dicts[key] = [existing]
                assert isinstance(child_dicts[key], list)
                child_dicts[key].append(value)
            else:
                child_dicts[key] = value

        if element.attrib:
            child_dicts["@attributes"] = dict(element.attrib)

        if len(set(c.tag for c in children)) == 1 and len(children) > 1:
            tag = children[0].tag
            return {element.tag: child_dicts.get(tag, [])}

        return child_dicts
