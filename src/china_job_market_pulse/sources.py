from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol

from .io import load_job_dataset
from .models import JobDataset


AccessMode = Literal["synthetic", "user_export", "public_dataset", "authorized_api"]


@dataclass(frozen=True, slots=True)
class SourceMetadata:
    """Provenance required before a source adapter is used."""

    name: str
    license: str
    access_mode: AccessMode


class SourceAdapter(Protocol):
    metadata: SourceMetadata

    def load(self) -> JobDataset:
        ...


@dataclass(frozen=True, slots=True)
class LocalFileAdapter:
    """Load a user-owned CSV/JSON export without making network requests."""

    path: Path | str
    metadata: SourceMetadata
    deduplicate: bool = True

    def load(self) -> JobDataset:
        return load_job_dataset(
            self.path,
            deduplicate=self.deduplicate,
            source_name=self.metadata.name,
            source_license=self.metadata.license,
            access_mode=self.metadata.access_mode,
        )
