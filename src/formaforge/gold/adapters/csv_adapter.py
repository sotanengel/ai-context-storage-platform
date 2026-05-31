"""CSV Gold adapter."""

import csv
import io

from formaforge.gold.adapters.base import BaseAdapter
from formaforge.models.silver import CdmDocument, CdmTableBlock


class CsvAdapter(BaseAdapter):
    adapter_name = "csv"

    def render(self, doc: CdmDocument, **opts: str) -> str:
        table_blocks = [b for b in doc.blocks if isinstance(b, CdmTableBlock)]
        if not table_blocks:
            raise ValueError("CSV adapter requires at least one table block in the CDM document.")
        block = table_blocks[0]
        col_names = [c.split(":")[0] for c in block.columns]
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(col_names)
        writer.writerows(block.rows)
        return buf.getvalue()
