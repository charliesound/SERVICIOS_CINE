from __future__ import annotations

from collections import Counter
from dataclasses import dataclass as _dataclass, field as _field
import os
from pathlib import Path
from typing import Iterable


PREFLIGHT_PASS = "PREFLIGHT_PASS"
PREFLIGHT_FAIL = "PREFLIGHT_FAIL"
PREFLIGHT_BLOCKED = "PREFLIGHT_BLOCKED"

_DEFAULT_MAX_FILE_COUNT = 25
_DEFAULT_MAX_TOTAL_SIZE_BYTES = 10 * 1024 * 1024 * 1024
_DEFAULT_MAX_SCAN_DEPTH = 3
_DEFAULT_ACCEPTED_EXTENSIONS = (".mov", ".mp4", ".mxf", ".wav", ".aif", ".aiff")

_INPUT_LABEL = "selected_input_folder"
_OUTPUT_LABEL = "selected_output_folder"


@_dataclass(frozen=True)
class RealPreflightRequest:
    input_folder_path: str | os.PathLike[str] | None
    output_folder_path: str | os.PathLike[str] | None
    max_file_count: int = _DEFAULT_MAX_FILE_COUNT
    max_total_size_bytes: int = _DEFAULT_MAX_TOTAL_SIZE_BYTES
    max_scan_depth: int = _DEFAULT_MAX_SCAN_DEPTH
    accepted_extensions: tuple[str, ...] = _DEFAULT_ACCEPTED_EXTENSIONS
    follow_symlinks: bool = False


@_dataclass(frozen=True)
class RealPreflightResult:
    status: str
    sanitized_input_folder_label: str = _INPUT_LABEL
    sanitized_output_folder_label: str = _OUTPUT_LABEL
    media_file_count: int = 0
    total_selected_media_size_bucket: str = "0B"
    maximum_detected_scan_depth: int = 0
    accepted_extension_counts: dict[str, int] = _field(default_factory=dict)
    ignored_extension_counts: dict[str, int] = _field(default_factory=dict)
    rejected_extension_counts: dict[str, int] = _field(default_factory=dict)
    failed_check_identifiers: tuple[str, ...] = ()
    remediation_items: tuple[str, ...] = ()


def run_real_preflight_check(request: RealPreflightRequest) -> RealPreflightResult:
    if not isinstance(request, RealPreflightRequest):
        return _blocked(
            failed_check_identifiers=("SANITIZED_PAYLOAD_READY",),
            remediation_items=("Use a valid real preflight request.",),
        )

    accepted_extensions = _normalize_extensions(request.accepted_extensions)
    if not accepted_extensions:
        return _blocked(
            failed_check_identifiers=("ACCEPTED_EXTENSIONS_PRESENT",),
            remediation_items=("Configure at least one accepted extension.",),
        )

    numeric_error = _validate_numeric_limits(request)
    if numeric_error:
        return _blocked(
            failed_check_identifiers=(numeric_error,),
            remediation_items=("Use conservative positive preflight limits.",),
        )

    input_path = _coerce_path(request.input_folder_path)
    output_path = _coerce_path(request.output_folder_path)

    if input_path is None:
        return _blocked(
            failed_check_identifiers=("INPUT_FOLDER_EXISTS",),
            remediation_items=("Select a local input folder.",),
        )

    if output_path is None:
        return _blocked(
            failed_check_identifiers=("OUTPUT_FOLDER_PREPARABLE",),
            remediation_items=("Select a separated local output folder.",),
        )

    if request.follow_symlinks:
        return _blocked(
            failed_check_identifiers=("SYMLINKS_NOT_FOLLOWED",),
            remediation_items=("Disable symlink following for real preflight.",),
        )

    if not _looks_local_path(input_path) or not _looks_local_path(output_path):
        return _blocked(
            failed_check_identifiers=("INPUT_FOLDER_LOCAL_ONLY",),
            remediation_items=("Select local folders only.",),
        )

    input_block = _validate_input_folder(input_path)
    if input_block:
        return input_block

    input_resolved = input_path.resolve(strict=True)
    output_resolved = output_path.resolve(strict=False)

    if _paths_overlap(input_resolved, output_resolved):
        return _blocked(
            failed_check_identifiers=("INPUT_OUTPUT_SEPARATED",),
            remediation_items=("Choose an output folder separated from the input folder.",),
        )

    output_block = _validate_output_folder(output_path)
    if output_block:
        return output_block

    return _scan_input_folder(
        input_resolved=input_resolved,
        accepted_extensions=accepted_extensions,
        max_file_count=request.max_file_count,
        max_total_size_bytes=request.max_total_size_bytes,
        max_scan_depth=request.max_scan_depth,
    )


def _coerce_path(value: str | os.PathLike[str] | None) -> Path | None:
    if value is None:
        return None
    try:
        text = os.fspath(value)
    except TypeError:
        return None
    if not str(text).strip():
        return None
    return Path(text)


def _normalize_extensions(values: Iterable[str]) -> tuple[str, ...]:
    normalized: list[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        extension = value.strip().lower()
        if not extension:
            continue
        if not extension.startswith("."):
            extension = f".{extension}"
        if extension not in normalized:
            normalized.append(extension)
    return tuple(normalized)


def _validate_numeric_limits(request: RealPreflightRequest) -> str | None:
    if not isinstance(request.max_file_count, int) or request.max_file_count <= 0:
        return "MEDIA_FILE_COUNT_WITHIN_LIMIT"
    if not isinstance(request.max_total_size_bytes, int) or request.max_total_size_bytes <= 0:
        return "TOTAL_MEDIA_SIZE_WITHIN_LIMIT"
    if not isinstance(request.max_scan_depth, int) or request.max_scan_depth < 0:
        return "SCAN_DEPTH_WITHIN_LIMIT"
    return None


def _looks_local_path(path: Path) -> bool:
    text = str(path)
    backslash = chr(92)
    if "://" in text:
        return False
    if backslash * 2 in text:
        return False
    lower = text.lower()
    if len(lower) >= 3 and lower[1:3] == ":" + backslash:
        return False
    if lower.startswith("/mnt/"):
        return False
    return True


def _validate_input_folder(input_path: Path) -> RealPreflightResult | None:
    try:
        if input_path.is_symlink():
            return _blocked(("SYMLINKS_NOT_FOLLOWED",), ("Select a non-symlink input folder.",))
        if not input_path.exists():
            return _blocked(("INPUT_FOLDER_EXISTS",), ("Select an existing local input folder.",))
        if not input_path.is_dir():
            return _blocked(("INPUT_FOLDER_IS_DIRECTORY",), ("Select a directory as input.",))
        if not os.access(input_path, os.R_OK | os.X_OK):
            return _blocked(("INPUT_FOLDER_ACCESSIBLE",), ("Select an accessible input folder.",))
    except OSError:
        return _blocked(("INPUT_FOLDER_ACCESSIBLE",), ("Select an accessible input folder.",))
    return None


def _validate_output_folder(output_path: Path) -> RealPreflightResult | None:
    try:
        if output_path.is_symlink():
            return _blocked(("SYMLINKS_NOT_FOLLOWED",), ("Select a non-symlink output folder.",))
        if output_path.exists():
            if not output_path.is_dir():
                return _blocked(("OUTPUT_FOLDER_PREPARABLE",), ("Select a directory as output.",))
            if not os.access(output_path, os.W_OK | os.X_OK):
                return _blocked(("OUTPUT_FOLDER_PREPARABLE",), ("Select a writable output folder.",))
            return None

        parent = output_path.parent
        if not parent.exists() or not parent.is_dir():
            return _blocked(("OUTPUT_FOLDER_PREPARABLE",), ("Select an output folder with an existing parent.",))
        if parent.is_symlink():
            return _blocked(("SYMLINKS_NOT_FOLLOWED",), ("Select a non-symlink output parent folder.",))
        if not os.access(parent, os.W_OK | os.X_OK):
            return _blocked(("OUTPUT_FOLDER_PREPARABLE",), ("Select a writable output parent folder.",))
    except OSError:
        return _blocked(("OUTPUT_FOLDER_PREPARABLE",), ("Select a safely preparable output folder.",))
    return None


def _paths_overlap(first: Path, second: Path) -> bool:
    try:
        first_abs = os.path.abspath(os.fspath(first))
        second_abs = os.path.abspath(os.fspath(second))
        common = os.path.commonpath([first_abs, second_abs])
    except (OSError, ValueError):
        return True
    return common == first_abs or common == second_abs


def _scan_input_folder(
    *,
    input_resolved: Path,
    accepted_extensions: tuple[str, ...],
    max_file_count: int,
    max_total_size_bytes: int,
    max_scan_depth: int,
) -> RealPreflightResult:
    accepted_counts: Counter[str] = Counter()
    ignored_counts: Counter[str] = Counter()
    rejected_counts: Counter[str] = Counter()
    media_file_count = 0
    total_size = 0
    maximum_depth = 0

    stack: list[tuple[Path, int]] = [(input_resolved, 0)]

    while stack:
        directory, depth = stack.pop()

        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    try:
                        if entry.is_symlink():
                            return _blocked(
                                ("SYMLINKS_NOT_FOLLOWED",),
                                ("Remove symlinks from the selected input tree.",),
                                media_file_count=media_file_count,
                                total_size=total_size,
                                maximum_depth=maximum_depth,
                                accepted_counts=accepted_counts,
                                ignored_counts=ignored_counts,
                                rejected_counts=rejected_counts,
                            )

                        entry_path = Path(entry.path)

                        if entry.is_dir(follow_symlinks=False):
                            next_depth = depth + 1
                            maximum_depth = max(maximum_depth, next_depth)

                            if next_depth > max_scan_depth:
                                return _blocked(
                                    ("SCAN_DEPTH_WITHIN_LIMIT",),
                                    ("Reduce folder nesting before running real preflight.",),
                                    media_file_count=media_file_count,
                                    total_size=total_size,
                                    maximum_depth=maximum_depth,
                                    accepted_counts=accepted_counts,
                                    ignored_counts=ignored_counts,
                                    rejected_counts=rejected_counts,
                                )

                            if not _is_inside(input_resolved, entry_path.resolve(strict=False)):
                                return _blocked(
                                    ("TRAVERSAL_DID_NOT_ESCAPE_INPUT",),
                                    ("Keep traversal inside the selected input folder.",),
                                    media_file_count=media_file_count,
                                    total_size=total_size,
                                    maximum_depth=maximum_depth,
                                    accepted_counts=accepted_counts,
                                    ignored_counts=ignored_counts,
                                    rejected_counts=rejected_counts,
                                )

                            stack.append((entry_path, next_depth))
                            continue

                        if not entry.is_file(follow_symlinks=False):
                            ignored_counts["<non_file>"] += 1
                            continue

                        extension = entry_path.suffix.lower()
                        if not extension:
                            ignored_counts["<no_extension>"] += 1
                            continue

                        if extension not in accepted_extensions:
                            rejected_counts[extension] += 1
                            continue

                        media_file_count += 1
                        accepted_counts[extension] += 1

                        if media_file_count > max_file_count:
                            return _blocked(
                                ("MEDIA_FILE_COUNT_WITHIN_LIMIT",),
                                ("Reduce selected media file count.",),
                                media_file_count=media_file_count,
                                total_size=total_size,
                                maximum_depth=maximum_depth,
                                accepted_counts=accepted_counts,
                                ignored_counts=ignored_counts,
                                rejected_counts=rejected_counts,
                            )

                        total_size += max(0, entry.stat(follow_symlinks=False).st_size)

                        if total_size > max_total_size_bytes:
                            return _blocked(
                                ("TOTAL_MEDIA_SIZE_WITHIN_LIMIT",),
                                ("Reduce selected media size.",),
                                media_file_count=media_file_count,
                                total_size=total_size,
                                maximum_depth=maximum_depth,
                                accepted_counts=accepted_counts,
                                ignored_counts=ignored_counts,
                                rejected_counts=rejected_counts,
                            )
                    except OSError:
                        return _blocked(
                            ("INPUT_FOLDER_ACCESSIBLE",),
                            ("Resolve filesystem access errors before running real preflight.",),
                            media_file_count=media_file_count,
                            total_size=total_size,
                            maximum_depth=maximum_depth,
                            accepted_counts=accepted_counts,
                            ignored_counts=ignored_counts,
                            rejected_counts=rejected_counts,
                        )
        except OSError:
            return _blocked(
                ("INPUT_FOLDER_ACCESSIBLE",),
                ("Resolve filesystem access errors before running real preflight.",),
                media_file_count=media_file_count,
                total_size=total_size,
                maximum_depth=maximum_depth,
                accepted_counts=accepted_counts,
                ignored_counts=ignored_counts,
                rejected_counts=rejected_counts,
            )

    if media_file_count == 0:
        return _result(
            status=PREFLIGHT_FAIL,
            failed_check_identifiers=("ACCEPTED_EXTENSIONS_PRESENT",),
            remediation_items=("Select at least one supported media placeholder.",),
            media_file_count=0,
            total_size=total_size,
            maximum_depth=maximum_depth,
            accepted_counts=accepted_counts,
            ignored_counts=ignored_counts,
            rejected_counts=rejected_counts,
        )

    return _result(
        status=PREFLIGHT_PASS,
        failed_check_identifiers=(),
        remediation_items=(),
        media_file_count=media_file_count,
        total_size=total_size,
        maximum_depth=maximum_depth,
        accepted_counts=accepted_counts,
        ignored_counts=ignored_counts,
        rejected_counts=rejected_counts,
    )


def _is_inside(root: Path, candidate: Path) -> bool:
    try:
        root_abs = os.path.abspath(os.fspath(root))
        candidate_abs = os.path.abspath(os.fspath(candidate))
        return os.path.commonpath([root_abs, candidate_abs]) == root_abs
    except (OSError, ValueError):
        return False


def _blocked(
    failed_check_identifiers: tuple[str, ...],
    remediation_items: tuple[str, ...],
    *,
    media_file_count: int = 0,
    total_size: int = 0,
    maximum_depth: int = 0,
    accepted_counts: Counter[str] | None = None,
    ignored_counts: Counter[str] | None = None,
    rejected_counts: Counter[str] | None = None,
) -> RealPreflightResult:
    return _result(
        status=PREFLIGHT_BLOCKED,
        failed_check_identifiers=failed_check_identifiers,
        remediation_items=remediation_items,
        media_file_count=media_file_count,
        total_size=total_size,
        maximum_depth=maximum_depth,
        accepted_counts=accepted_counts or Counter(),
        ignored_counts=ignored_counts or Counter(),
        rejected_counts=rejected_counts or Counter(),
    )


def _result(
    *,
    status: str,
    failed_check_identifiers: tuple[str, ...],
    remediation_items: tuple[str, ...],
    media_file_count: int,
    total_size: int,
    maximum_depth: int,
    accepted_counts: Counter[str],
    ignored_counts: Counter[str],
    rejected_counts: Counter[str],
) -> RealPreflightResult:
    return RealPreflightResult(
        status=status,
        sanitized_input_folder_label=_INPUT_LABEL,
        sanitized_output_folder_label=_OUTPUT_LABEL,
        media_file_count=media_file_count,
        total_selected_media_size_bucket=_size_bucket(total_size),
        maximum_detected_scan_depth=maximum_depth,
        accepted_extension_counts=_counter_to_dict(accepted_counts),
        ignored_extension_counts=_counter_to_dict(ignored_counts),
        rejected_extension_counts=_counter_to_dict(rejected_counts),
        failed_check_identifiers=tuple(dict.fromkeys(failed_check_identifiers)),
        remediation_items=tuple(dict.fromkeys(remediation_items)),
    )


def _counter_to_dict(counter: Counter[str]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def _size_bucket(size_bytes: int) -> str:
    if size_bytes <= 0:
        return "0B"
    if size_bytes <= 100 * 1024 * 1024:
        return "<=100MB"
    if size_bytes <= 1024 * 1024 * 1024:
        return "<=1GB"
    if size_bytes <= _DEFAULT_MAX_TOTAL_SIZE_BYTES:
        return "<=10GB"
    return ">10GB"
