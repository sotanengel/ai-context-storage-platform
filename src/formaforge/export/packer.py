"""Pack Bronze storage into a ZIP archive with manifest and AI guide."""

from __future__ import annotations

import zipfile
from pathlib import Path

from formaforge.export.guide import GuideGenerator
from formaforge.export.manifest import ArchiveManifest


class EmptyBronzeStorageError(ValueError):
    """Raised when there are no Bronze records to pack."""


class BronzePacker:
    def pack(
        self,
        manifest: ArchiveManifest,
        storage_dir: Path,
        output_path: Path,
    ) -> Path:
        if manifest.record_count == 0:
            raise EmptyBronzeStorageError("no Bronze records found; ingest data before packing")

        storage_dir = storage_dir.resolve()
        output_path = output_path.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        guide_text = GuideGenerator().render(manifest)
        manifest_json = manifest.model_dump_json(indent=2)

        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", manifest_json)
            zf.writestr("FORMAFORGE_AI_RESTORE_GUIDE.md", guide_text)
            for entry in manifest.records:
                record_dir = storage_dir / entry.bronze_id
                zf.write(record_dir / "meta.json", entry.meta_path)
                zf.write(record_dir / "raw", entry.archive_path)

        return output_path

    @classmethod
    def pack_storage(
        cls,
        storage_dir: Path,
        output_path: Path,
        *,
        manifest: ArchiveManifest | None = None,
    ) -> Path:
        from formaforge.export.scanner import BronzeStorageScanner

        if manifest is None:
            manifest = BronzeStorageScanner().scan(storage_dir)
        return cls().pack(manifest, storage_dir, output_path)
