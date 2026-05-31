"""XML Gold adapter."""

import xml.etree.ElementTree as ET
from typing import Any

from formaforge.gold.adapters.base import BaseAdapter
from formaforge.models.silver import CdmDataBlock, CdmDocument, CdmTableBlock


class XmlAdapter(BaseAdapter):
    adapter_name = "xml"

    def render(self, doc: CdmDocument, **opts: str) -> str:
        root = ET.Element("document")
        if doc.title:
            title_el = ET.SubElement(root, "title")
            title_el.text = doc.title
        for block in doc.blocks:
            if isinstance(block, CdmTableBlock):
                self._append_table(root, block)
            elif isinstance(block, CdmDataBlock):
                self._append_data(root, block)
        if doc.body:
            body_el = ET.SubElement(root, "body")
            body_el.text = doc.body
        ET.indent(root, space="  ")
        return ET.tostring(root, encoding="unicode", xml_declaration=False)

    def _append_table(self, parent: ET.Element, block: CdmTableBlock) -> None:
        table_el = ET.SubElement(parent, "table")
        col_names = [c.split(":")[0] for c in block.columns]
        for row in block.rows:
            row_el = ET.SubElement(table_el, "row")
            for name, value in zip(col_names, row, strict=True):
                cell = ET.SubElement(row_el, name)
                cell.text = str(value)

    def _append_data(self, parent: ET.Element, block: CdmDataBlock) -> None:
        data_el = ET.SubElement(parent, "data")
        self._dict_to_xml(data_el, block.content)

    def _dict_to_xml(self, parent: ET.Element, data: Any) -> None:
        if isinstance(data, dict):
            for key, value in data.items():
                child = ET.SubElement(parent, str(key))
                self._dict_to_xml(child, value)
        elif isinstance(data, list):
            for item in data:
                item_el = ET.SubElement(parent, "item")
                self._dict_to_xml(item_el, item)
        else:
            parent.text = str(data) if data is not None else ""
