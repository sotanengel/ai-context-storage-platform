"""Version-pinned prompt templates for AI-assisted CDM conversion."""

UNSTRUCTURED_TO_CDM_PROMPT_V1 = """\
You are a precise document normalizer. Convert the provided raw text into a
Canonical Document Model (CDM) Markdown document.

Rules:
1. Output MUST start with a YAML frontmatter block (---).
2. Required frontmatter fields:
   - source_format: (detected format, e.g. "pdf", "text", "docx")
   - source_uri: (pass through the value provided)
   - structure_class: "unstructured"
   - conversion_method: "ai"
   - conversion_confidence: (float 0.0-1.0 reflecting your confidence)
   - cdm_schema_version: "2.0"
   - pii_flags: (list of field names containing PII, or [])
3. After frontmatter: one H1 title (# Title).
4. For any tabular data you find: use ```table blocks with columns/rows YAML.
5. For prose: write clean CommonMark in the body.
6. Do NOT invent information not present in the source.

Source URI: {source_uri}
Source format: {source_format}

Raw content:
{raw_content}

Output the CDM document now:
"""

PROMPT_VERSION = "v1"
