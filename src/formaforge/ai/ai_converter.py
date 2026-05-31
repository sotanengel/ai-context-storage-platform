"""AI-assisted converter for unstructured content using Anthropic SDK."""

import os

import anthropic

from formaforge.ai.prompts import UNSTRUCTURED_TO_CDM_PROMPT_V1
from formaforge.models.silver import CdmDocument, CdmFrontmatter, ConversionMethod
from formaforge.silver.cdm_parser import CdmParser


class AiConverter:
    MODEL = "claude-sonnet-4-6"

    def __init__(
        self,
        require_api_key: bool = False,
        parser: CdmParser | None = None,
    ) -> None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if require_api_key and not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
        self._client = anthropic.Anthropic(api_key=api_key)
        self._async_client = anthropic.AsyncAnthropic(api_key=api_key)
        self._parser = parser or CdmParser()

    def convert(self, raw: str, source_uri: str = "", source_format: str = "text") -> CdmDocument:
        prompt = UNSTRUCTURED_TO_CDM_PROMPT_V1.format(
            source_uri=source_uri,
            source_format=source_format,
            raw_content=raw[:8000],
        )
        message = self._client.messages.create(
            model=self.MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        first_block = message.content[0]
        response_text = getattr(first_block, "text", None)
        if not isinstance(response_text, str):
            return self._fallback_doc(raw, source_uri, source_format)

        try:
            doc = self._parser.parse(response_text)
            doc.frontmatter.conversion_method = ConversionMethod.AI
            return doc
        except Exception:
            return self._fallback_doc(raw, source_uri, source_format)

    async def convert_async(
        self, raw: str, source_uri: str = "", source_format: str = "text"
    ) -> CdmDocument:
        """Stream conversion via AsyncAnthropic; accumulates full CDM text before parsing."""
        prompt = UNSTRUCTURED_TO_CDM_PROMPT_V1.format(
            source_uri=source_uri,
            source_format=source_format,
            raw_content=raw[:8000],
        )
        accumulated: list[str] = []
        async with self._async_client.messages.stream(
            model=self.MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        ) as stream:
            async for chunk in stream.text_stream:
                accumulated.append(chunk)

        full_text = "".join(accumulated)
        try:
            doc = self._parser.parse(full_text)
            doc.frontmatter.conversion_method = ConversionMethod.AI
            return doc
        except Exception:
            return self._fallback_doc(raw, source_uri, source_format)

    def _fallback_doc(self, raw: str, source_uri: str, source_format: str) -> CdmDocument:
        fm = CdmFrontmatter(
            source_format=source_format,
            source_uri=source_uri,
            structure_class="unstructured",
            conversion_method=ConversionMethod.AI,
            conversion_confidence=0.1,
        )
        return CdmDocument(
            frontmatter=fm,
            title="",
            body=raw[:2000],
        )
