"""Silver normalization: route Bronze records to the correct converter."""

from formaforge.ai.ai_converter import AiConverter
from formaforge.models.bronze import BronzeRecord, StructureClass
from formaforge.models.silver import CdmDocument, ConversionMethod
from formaforge.privacy.pii_detector import PiiDetector
from formaforge.silver.converters import ConverterRegistry


class UnknownFormatError(ValueError):
    pass


class SilverNormalizer:
    def __init__(
        self,
        *,
        converter_registry: ConverterRegistry | None = None,
        ai_converter: AiConverter | None = None,
        pii_detector: PiiDetector | None = None,
    ) -> None:
        self._converter_registry = converter_registry or ConverterRegistry.default()
        self._ai_converter = ai_converter
        self._pii_detector = pii_detector or PiiDetector()

    def normalize(
        self,
        record: BronzeRecord,
        conversion_method: ConversionMethod = ConversionMethod.AUTO,
    ) -> CdmDocument:
        raw_bytes = self._read_raw(record)
        effective_method = self._resolve_method(record, conversion_method)

        if effective_method == ConversionMethod.DETERMINISTIC:
            doc = self._convert_deterministic(raw_bytes, record)
        else:
            raw_text = raw_bytes.decode("utf-8", errors="replace")
            doc = self._get_ai_converter().convert(
                raw_text, record.source_uri, record.source_format
            )

        pii_flags = self._pii_detector.detect(doc.body)
        if pii_flags:
            doc.frontmatter.pii_flags = pii_flags
        return doc

    def _resolve_method(
        self, record: BronzeRecord, requested: ConversionMethod
    ) -> ConversionMethod:
        if requested != ConversionMethod.AUTO:
            return requested
        if record.structure_class == StructureClass.STRUCTURED:
            return ConversionMethod.DETERMINISTIC
        fmt = record.source_format
        if fmt in ("pdf", "docx", "xlsx"):
            return ConversionMethod.DETERMINISTIC
        return ConversionMethod.AI

    def _convert_deterministic(self, raw_bytes: bytes, record: BronzeRecord) -> CdmDocument:
        fmt = record.source_format
        converter = self._converter_registry.get(fmt)
        if not converter:
            raise UnknownFormatError(f"No deterministic converter for format: {fmt!r}")
        return converter.convert_bytes(raw_bytes, record.source_uri)

    def _read_raw(self, record: BronzeRecord) -> bytes:
        from pathlib import Path

        return Path(record.raw_content_path).read_bytes()

    def _get_ai_converter(self) -> AiConverter:
        if self._ai_converter is None:
            self._ai_converter = AiConverter()
        return self._ai_converter
