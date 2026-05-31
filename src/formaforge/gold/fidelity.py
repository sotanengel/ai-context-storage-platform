"""Structural fidelity scoring for Gold adapter benchmark output."""

from formaforge.models.silver import CdmDocument, CdmTableBlock


def fidelity_score(doc: CdmDocument, rendered: str) -> float:
    """Estimate structural fidelity of rendered output vs source CDM (0.0–1.0).

    Checks for presence of title, body text, and each table/data block.
    """
    checks: list[bool] = []

    if doc.title:
        checks.append(doc.title.lower() in rendered.lower())

    if doc.body.strip():
        first_word = doc.body.strip().split()[0].lower()
        checks.append(first_word in rendered.lower())

    for block in doc.blocks:
        if isinstance(block, CdmTableBlock) and block.columns:
            checks.append(block.columns[0].lower() in rendered.lower())
        else:
            checks.append(len(rendered) > 0)

    if not checks:
        return 1.0
    return sum(checks) / len(checks)
