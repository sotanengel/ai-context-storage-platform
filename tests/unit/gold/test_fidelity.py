"""Tests for Gold adapter fidelity scoring."""

from formaforge.gold.fidelity import fidelity_score
from formaforge.models.silver import CdmDocument, CdmFrontmatter, CdmTableBlock


def _make_doc(**kwargs: object) -> CdmDocument:
    fm = CdmFrontmatter(source_format="json", source_uri="", structure_class="structured")
    return CdmDocument(frontmatter=fm, **kwargs)  # type: ignore[arg-type]


def test_fidelity_score_with_title_and_body() -> None:
    doc = _make_doc(title="Products", body="Overview of items")
    rendered = "# Products\n\nOverview of items"
    assert fidelity_score(doc, rendered) == 1.0


def test_fidelity_score_with_table_block() -> None:
    block = CdmTableBlock(columns=["id:int", "name:str"], rows=[[1, "Widget"]])
    doc = _make_doc(title="Products", blocks=[block])
    rendered = "# Products\nid:int\nWidget"
    assert fidelity_score(doc, rendered) > 0.0


def test_fidelity_score_empty_doc_returns_one() -> None:
    doc = _make_doc()
    assert fidelity_score(doc, "anything") == 1.0
