"""CID CLI command: EDITORIAL_SELECTION collaboration (create/list/transition).

Producer/director decide what should be edited; editor executes. CID keeps the
shared selection and status visible. This slice tracks status and DaVinci
readiness only; it never generates FCPXML and never reads source media.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import TextIO

from scripts.local_media_agent.editorial_selection import (
    STATUSES,
    SelectionError,
    SelectionStore,
    apply_transition,
    create_selection,
    render_view,
)

EXIT_SUCCESS = 0
EXIT_INTERNAL_FAILURE = 1
EXIT_ARGUMENTS_REJECTED = 2

CLI_ARGUMENTS_REJECTED = "CID_EDITORIAL_SELECTION_ARGUMENTS_REJECTED"
CLI_INTERNAL_FAILURE = "CID_EDITORIAL_SELECTION_INTERNAL_FAILURE"

VALID_VIEWS = ("producer", "director", "editor")


class _ControlledArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValueError(message)


def _build_parser() -> argparse.ArgumentParser:
    parser = _ControlledArgumentParser(
        prog="cid selection",
        description="CID EDITORIAL_SELECTION collaboration (local, read-only media).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Create a selection from evidence.")
    create.add_argument("--evidence-path", required=True)
    create.add_argument("--candidate", required=True)
    create.add_argument("--requested-by-role", required=True)
    create.add_argument("--note")
    create.add_argument("--store", required=True)

    listing = sub.add_parser("list", help="List selections (optional status filter).")
    listing.add_argument("--store", required=True)
    listing.add_argument("--status")
    listing.add_argument("--view", choices=VALID_VIEWS, default="producer")

    transition = sub.add_parser("transition", help="Apply a status transition.")
    transition.add_argument("--store", required=True)
    transition.add_argument("--selection", required=True)
    transition.add_argument("--to", required=True)
    transition.add_argument("--actor-role", required=True)
    transition.add_argument("--editor-note")

    return parser


def _run_create(args, out, err) -> int:
    selection = create_selection(
        args.evidence_path,
        args.candidate,
        args.requested_by_role,
        note=args.note,
    )
    store = SelectionStore(args.store)
    if store.exists(selection["selection_id"]):
        err.write(f"CID_EDITORIAL_SELECTION_ALREADY_EXISTS:{selection['selection_id']}\n")
        return EXIT_ARGUMENTS_REJECTED
    store.write(selection)
    out.write(
        json.dumps(
            {
                "selection_id": selection["selection_id"],
                "candidate_id": selection["candidate_id"],
                "status": selection["status"],
                "davinci_reference_status": selection["davinci_reference_status"],
                "stored": True,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n"
    )
    return EXIT_SUCCESS


def _run_list(args, out, err) -> int:
    store = SelectionStore(args.store)
    status_filter = args.status
    if status_filter is not None and status_filter not in STATUSES:
        err.write(CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED
    selections = store.list(status=status_filter)
    if args.view == "json":
        out.write(json.dumps(selections, ensure_ascii=False, sort_keys=True) + "\n")
        return EXIT_SUCCESS
    if not selections:
        out.write("NO_SELECTIONS\n")
        return EXIT_SUCCESS
    blocks = [render_view(args.view, s) for s in selections]
    out.write("\n---\n".join(blocks))
    return EXIT_SUCCESS


def _run_transition(args, out, err) -> int:
    store = SelectionStore(args.store)
    try:
        current = store.read(args.selection)
    except SelectionError:
        err.write(f"SELECTION_NOT_FOUND:{args.selection}\n")
        return EXIT_ARGUMENTS_REJECTED
    updated = apply_transition(
        current,
        args.to,
        args.actor_role,
        editor_note=args.editor_note,
    )
    store.write(updated)
    out.write(
        json.dumps(
            {
                "selection_id": updated["selection_id"],
                "from_status": current["status"],
                "status": updated["status"],
                "actor_role": args.actor_role,
                "updated": True,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n"
    )
    return EXIT_SUCCESS


def run_cli(
    argv: list[str] | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    out = sys.stdout if stdout is None else stdout
    err = sys.stderr if stderr is None else stderr
    try:
        args = _build_parser().parse_args(list(sys.argv[1:] if argv is None else argv))
        if args.command == "create":
            return _run_create(args, out, err)
        if args.command == "list":
            return _run_list(args, out, err)
        if args.command == "transition":
            return _run_transition(args, out, err)
        err.write(CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED
    except (SelectionError, ValueError, TypeError, OSError):
        err.write(CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED
    except Exception:
        err.write(CLI_INTERNAL_FAILURE + "\n")
        return EXIT_INTERNAL_FAILURE


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
