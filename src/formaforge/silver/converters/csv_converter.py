"""CSV/TSV → CDM deterministic converter."""

import csv
import io
from typing import Any

from formaforge.models.silver import CdmDocument, CdmTableBlock
from formaforge.silver.converters.base import BaseConverter


class CsvConverter(BaseConverter):
    source_format = "csv"

    def convert(self, raw: str, source_uri: str = "") -> CdmDocument:
        delimiter = "\t" if "\t" in raw.split("\n")[0] else ","
        reader = csv.DictReader(io.StringIO(raw), delimiter=delimiter)
        rows_raw = list(reader)
        fm = self._make_frontmatter(source_uri)
        if not rows_raw:
            return CdmDocument(frontmatter=fm)
        keys = list(rows_raw[0].keys())
        sample = rows_raw[0]
        columns = [f"{k}:{self._infer_type(self._coerce(sample[k]))}" for k in keys]
        rows: list[list[Any]] = [[self._coerce(row[k]) for k in keys] for row in rows_raw]
        block = CdmTableBlock(columns=columns, rows=rows)
        return CdmDocument(frontmatter=fm, blocks=[block])

    def _coerce(self, value: str) -> Any:
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value
