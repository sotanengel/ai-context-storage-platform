"""Tests for binary document converters (PDF, DOCX, XLSX)."""

from unittest.mock import MagicMock, patch

import pytest

from formaforge.models.silver import CdmDocument, CdmTableBlock

# ── PDF ──────────────────────────────────────────────────────────────────────


def test_pdf_converter_returns_cdm_document() -> None:
    from formaforge.silver.converters.pdf_converter import PdfConverter

    mock_page = MagicMock()
    mock_page.get_text.return_value = "Hello from PDF"

    with patch("formaforge.silver.converters.pdf_converter._open_pdf") as mock_open:
        mock_open.return_value = [mock_page]
        doc = PdfConverter().convert_bytes(b"%PDF-1.4 fake", "test.pdf")

    assert isinstance(doc, CdmDocument)
    assert "Hello from PDF" in doc.body


def test_pdf_converter_sets_source_format() -> None:
    from formaforge.silver.converters.pdf_converter import PdfConverter

    mock_page = MagicMock()
    mock_page.get_text.return_value = "text"

    with patch("formaforge.silver.converters.pdf_converter._open_pdf") as mock_open:
        mock_open.return_value = [mock_page]
        doc = PdfConverter().convert_bytes(b"fake", "")

    assert doc.frontmatter.source_format == "pdf"
    assert doc.frontmatter.structure_class == "unstructured"


def test_pdf_converter_raises_when_library_missing() -> None:
    from formaforge.silver.converters.pdf_converter import PdfConverter

    with (
        patch(
            "formaforge.silver.converters.pdf_converter._open_pdf",
            side_effect=ImportError("pymupdf not installed"),
        ),
        pytest.raises(ImportError),
    ):
        PdfConverter().convert_bytes(b"fake", "")


# ── DOCX ─────────────────────────────────────────────────────────────────────


def test_docx_converter_extracts_paragraphs() -> None:
    from formaforge.silver.converters.docx_converter import DocxConverter

    mock_doc = MagicMock()
    mock_para = MagicMock()
    mock_para.style.name = "Normal"
    mock_para.text = "Some paragraph text"
    mock_doc.paragraphs = [mock_para]
    mock_doc.tables = []

    with patch("formaforge.silver.converters.docx_converter._open_docx", return_value=mock_doc):
        doc = DocxConverter().convert_bytes(b"fake docx", "report.docx")

    assert "Some paragraph text" in doc.body


def test_docx_converter_extracts_heading_as_title() -> None:
    from formaforge.silver.converters.docx_converter import DocxConverter

    mock_doc = MagicMock()
    h1 = MagicMock()
    h1.style.name = "Heading 1"
    h1.text = "My Document Title"
    body_para = MagicMock()
    body_para.style.name = "Normal"
    body_para.text = "Body text"
    mock_doc.paragraphs = [h1, body_para]
    mock_doc.tables = []

    with patch("formaforge.silver.converters.docx_converter._open_docx", return_value=mock_doc):
        doc = DocxConverter().convert_bytes(b"fake", "")

    assert doc.title == "My Document Title"


def test_docx_converter_extracts_tables() -> None:
    from formaforge.silver.converters.docx_converter import DocxConverter

    mock_doc = MagicMock()
    mock_doc.paragraphs = []

    cell_a = MagicMock()
    cell_a.text = "name"
    cell_b = MagicMock()
    cell_b.text = "age"
    header_row = MagicMock()
    header_row.cells = [cell_a, cell_b]

    cell_c = MagicMock()
    cell_c.text = "Alice"
    cell_d = MagicMock()
    cell_d.text = "30"
    data_row = MagicMock()
    data_row.cells = [cell_c, cell_d]

    mock_table = MagicMock()
    mock_table.rows = [header_row, data_row]
    mock_doc.tables = [mock_table]

    with patch("formaforge.silver.converters.docx_converter._open_docx", return_value=mock_doc):
        doc = DocxConverter().convert_bytes(b"fake", "")

    assert len(doc.blocks) == 1
    assert isinstance(doc.blocks[0], CdmTableBlock)
    assert "Alice" in doc.blocks[0].rows[0]


def test_docx_converter_raises_when_library_missing() -> None:
    from formaforge.silver.converters.docx_converter import DocxConverter

    with (
        patch(
            "formaforge.silver.converters.docx_converter._open_docx",
            side_effect=ImportError("python-docx not installed"),
        ),
        pytest.raises(ImportError),
    ):
        DocxConverter().convert_bytes(b"fake", "")


# ── XLSX ─────────────────────────────────────────────────────────────────────


def test_xlsx_converter_extracts_sheet_as_table() -> None:
    from formaforge.silver.converters.xlsx_converter import XlsxConverter

    mock_ws = MagicMock()
    mock_ws.title = "Sheet1"
    mock_ws.iter_rows.return_value = [
        [MagicMock(value="id"), MagicMock(value="name")],
        [MagicMock(value=1), MagicMock(value="Alice")],
        [MagicMock(value=2), MagicMock(value="Bob")],
    ]

    mock_wb = MagicMock()
    mock_wb.worksheets = [mock_ws]

    with patch("formaforge.silver.converters.xlsx_converter._open_xlsx", return_value=mock_wb):
        doc = XlsxConverter().convert_bytes(b"fake xlsx", "data.xlsx")

    assert len(doc.blocks) == 1
    assert isinstance(doc.blocks[0], CdmTableBlock)
    assert doc.blocks[0].rows[0][1] == "Alice"


def test_xlsx_converter_title_from_first_sheet() -> None:
    from formaforge.silver.converters.xlsx_converter import XlsxConverter

    mock_ws = MagicMock()
    mock_ws.title = "Sales"
    mock_ws.iter_rows.return_value = [
        [MagicMock(value="col")],
        [MagicMock(value="val")],
    ]
    mock_wb = MagicMock()
    mock_wb.worksheets = [mock_ws]

    with patch("formaforge.silver.converters.xlsx_converter._open_xlsx", return_value=mock_wb):
        doc = XlsxConverter().convert_bytes(b"fake", "")

    assert doc.title == "Sales"


def test_xlsx_converter_raises_when_library_missing() -> None:
    from formaforge.silver.converters.xlsx_converter import XlsxConverter

    with (
        patch(
            "formaforge.silver.converters.xlsx_converter._open_xlsx",
            side_effect=ImportError("openpyxl not installed"),
        ),
        pytest.raises(ImportError),
    ):
        XlsxConverter().convert_bytes(b"fake", "")
