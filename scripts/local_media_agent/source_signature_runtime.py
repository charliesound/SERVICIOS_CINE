"""CID Local Media Agent — B2B in-memory SourceSignature runtime cache.

Owns the project-scoped load/save orchestration of the B2A signature cache and
exposes a thin in-memory runtime context consumed by
:func:`audio_source_intelligence.group_related_media`.

Boundaries
----------
This module does NOT own grouping algorithms, the source registry, or the
derivation of ``media_ref``. Those remain owned by ``audio_source_intelligence``
and ``media_catalog`` respectively. The runtime only bridges:

- the caller-owned project scope (``project_id``, ``local_appdata``),
- the B2A persistence APIs (pure load/save/lookup/upsert),

via a small ``SignatureCacheRuntime`` dataclass carrying no project identity of
its own. Persistence happens only through the explicit
:func:`save_signature_cache_runtime` helper; nothing here writes per-signature.

Fingerprints are keyed by the canonical ``media_ref`` and contain only
``{"size": int, "mtime_ns": int}``. No absolute path, current location, drive
letter, source alias, display label or SHA participates in cache identity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from scripts.local_media_agent.audio_source_intelligence import (
    ENVELOPE_BLOCKS_PER_SECOND,
    SIGNATURE_SAMPLE_RATE,
    SOURCE_SIGNATURE_ALGORITHM_VERSION,
    WINDOW_SECONDS_DEFAULT,
    SourceSignature,
)
from scripts.local_media_agent.source_signature_cache import (
    SourceSignatureCacheError,
    empty_signature_cache,
    load_signature_cache,
    lookup_cached_signature,
    normalize_signature_config,
    save_signature_cache,
    upsert_cached_signature,
)


def _canonical_signature_config() -> dict[str, Any]:
    """Canonical extraction config matching default ``extract_source_signature``."""
    return normalize_signature_config(
        {
            "window_seconds": WINDOW_SECONDS_DEFAULT,
            "blocks_per_second": ENVELOPE_BLOCKS_PER_SECOND,
            "sample_rate": SIGNATURE_SAMPLE_RATE,
            "include_sha256": True,
            "decoder": None,
        }
    )


@dataclass
class SignatureCacheRuntime:
    """Mutable in-memory runtime context for the signature-content cache.

    Designed to be self-contained and dependency-free of project persistence:
    the grouping layer only calls :meth:`lookup`, :meth:`note_signature_build`
    and :meth:`upsert`. Persistence is performed by the caller through
    :func:`save_signature_cache_runtime`.

    Thread safety: this context is not promised to be concurrently safe; the
    current analysis worker is a single thread.
    """

    cache: dict[str, Any] = field(default_factory=dict)
    fingerprints: Mapping[str, Mapping[str, int]] = field(default_factory=dict)
    signature_algorithm_version: str = SOURCE_SIGNATURE_ALGORITHM_VERSION
    signature_config: Mapping[str, Any] = field(
        default_factory=_canonical_signature_config
    )
    cache_hits: int = 0
    cache_misses: int = 0
    signature_builds: int = 0
    cache_upserts: int = 0
    dirty: bool = False
    cache_load_error_code: str | None = None

    def lookup(self, media_ref: str) -> SourceSignature | None:
        """Return a cached signature on a valid hit, else ``None``.

        Increments ``cache_hits`` on a hit and ``cache_misses`` on an eligible
        miss. No persistence, filesystem or media access occur.
        """
        fingerprint = self._fingerprint_for(media_ref)
        if fingerprint is None:
            return None
        hit = lookup_cached_signature(
            self.cache,
            media_ref,
            size=fingerprint["size"],
            mtime_ns=fingerprint["mtime_ns"],
            signature_algorithm_version=self.signature_algorithm_version,
            signature_config=self.signature_config,
        )
        if hit is not None:
            self.cache_hits += 1
            return hit
        self.cache_misses += 1
        return None

    def note_signature_build(self) -> None:
        """Record that the canonical/default signature builder is about to run."""
        self.signature_builds += 1

    def upsert(self, media_ref: str, signature: SourceSignature) -> bool:
        """Insert or replace one canonical in-memory cache entry.

        Uses the already-supplied fingerprint. If no usable fingerprint exists
        for ``media_ref`` the entry is not stored and ``False`` is returned.
        Persistence is NOT performed here.
        """
        fingerprint = self._fingerprint_for(media_ref)
        if fingerprint is None:
            return False
        upsert_cached_signature(
            self.cache,
            media_ref,
            size=fingerprint["size"],
            mtime_ns=fingerprint["mtime_ns"],
            signature_algorithm_version=self.signature_algorithm_version,
            signature_config=self.signature_config,
            signature=signature,
        )
        self.cache_upserts += 1
        self.dirty = True
        return True

    def _fingerprint_for(self, media_ref: str) -> dict[str, int] | None:
        fp = self.fingerprints.get(media_ref)
        if not isinstance(fp, Mapping):
            return None
        size = fp.get("size")
        mtime_ns = fp.get("mtime_ns")
        if isinstance(size, bool) or not isinstance(size, int):
            return None
        if isinstance(mtime_ns, bool) or not isinstance(mtime_ns, int):
            return None
        return {"size": size, "mtime_ns": mtime_ns}


def load_signature_cache_runtime(
    project_id: str,
    *,
    fingerprints: Mapping[str, Mapping[str, int]],
    local_appdata: str | Path | None = None,
    signature_algorithm_version: str = SOURCE_SIGNATURE_ALGORITHM_VERSION,
    signature_config: Mapping[str, Any] | None = None,
) -> SignatureCacheRuntime:
    """Load a project cache into a runtime, tolerating a corrupt/missing cache.

    A missing file yields an empty valid cache. A corrupt cache does not abort
    the caller: ``cache_load_error_code`` captures the controlled error and an
    empty valid cache is returned (``dirty`` stays ``False``) so the corrupt
    file is not immediately overwritten.
    """
    load_error_code: str | None = None
    try:
        cache = load_signature_cache(project_id, local_appdata=local_appdata)
    except SourceSignatureCacheError as exc:
        cache = empty_signature_cache(project_id)
        load_error_code = exc.code
    return SignatureCacheRuntime(
        cache=cache,
        fingerprints=fingerprints,
        signature_algorithm_version=signature_algorithm_version,
        signature_config=normalize_signature_config(signature_config),
        cache_load_error_code=load_error_code,
    )


def save_signature_cache_runtime(
    runtime: SignatureCacheRuntime,
    project_id: str,
    *,
    local_appdata: str | Path | None = None,
) -> bool:
    """Persist the runtime cache exactly once if dirty.

    Returns ``True`` when a save occurred. A clean runtime is never written.
    """
    if not runtime.dirty:
        return False
    save_signature_cache(runtime.cache, project_id, local_appdata=local_appdata)
    runtime.dirty = False
    return True


__all__ = [
    "SignatureCacheRuntime",
    "load_signature_cache_runtime",
    "save_signature_cache_runtime",
]
