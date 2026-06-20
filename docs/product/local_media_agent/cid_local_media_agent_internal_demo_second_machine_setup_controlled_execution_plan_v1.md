# CID Local Media Agent - Internal Demo Second Machine Setup Controlled Execution Plan v1

## Phase

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.PLAN.V1

## Objective

Define the exact command plan for one future controlled internal second-machine setup execution.

This phase does not execute setup.

This phase does not install the product.

This phase does not create an installer.

This phase does not create a commercial package.

This phase does not authorize client-facing demo, public demo, sales demo, paid pilot use, production use, or installation on a client computer.

## Source Stable State

Source stable HEAD:

9f665c1823435084f8a9181e2b3ac9420bc47011

Source commit:

test: add CID Local Media Agent controlled execution authorization gate

Source tag:

cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-controlled-execution-authorization-gate-v1-20260620

Source accepted result:

LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_AUTHORIZATION_GATE_PASS_READY_FOR_CONTROLLED_EXECUTION_PLAN

## Plan Decision

Decision:

PLAN_READY_FOR_CONTROLLED_EXECUTION_PLAN_QA_GATE

This means the exact command plan may be validated by a later QA gate.

It does not mean setup execution is authorized inside this phase.

It does not mean setup execution has happened.

It does not mean installation has happened.

It does not mean an installer exists.

## Execution Plan Scope

The future controlled execution plan is limited to:

- one internal second machine
- one project-owner controlled machine
- one disposable internal workspace
- one repository clone or verified existing clone
- one expected HEAD
- one virtual environment
- one dependency installation inside that virtual environment
- one validation sequence
- one controlled fixture input
- one visible report CLI execution
- one generated markdown report
- one evidence record

## Machine Preconditions

Before any future execution, the operator must confirm:

- machine owner is project owner
- machine is internal only
- machine is not client-owned
- machine is not productora-owned
- machine is not school-owned
- machine is not investor-owned
- machine does not contain client media
- machine does not contain production footage
- machine does not contain confidential script material
- machine does not contain copied environment secrets
- machine does not contain copied database files
- workspace is disposable
- workspace is outside client media folders
- workspace is outside production footage folders
- workspace is outside confidential project folders

## Repository Preconditions

Before any future execution, the operator must confirm:

- repository path is controlled
- repository remote is expected
- current branch is main
- local HEAD is expected
- remote main is expected
- required source tag is present remotely
- repository is clean before execution
- no local untracked project files are present except planned fixture/output paths outside the repository when applicable

Expected HEAD for the future execution plan:

9f665c1823435084f8a9181e2b3ac9420bc47011

Required source tag for the future execution plan:

cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-controlled-execution-authorization-gate-v1-20260620

## Controlled Workspace Plan

The future controlled workspace must be created with a neutral internal path.

Allowed example shape:

/tmp/cid_local_media_agent_second_machine_controlled_execution_v1

The workspace must contain only:

- repository clone or verified repository folder
- controlled fixture input
- controlled output root
- generated visible report
- evidence record

The workspace must not contain:

- real media
- production footage
- client media
- confidential scripts
- environment secret files
- database files
- installer artifacts
- license activation files
- public demo assets
- sales demo assets

## Exact Future Command Plan

The later execution phase may use a command plan with this shape, adapted only for the actual internal machine path.

Step 1 - create controlled workspace:

mkdir -p /tmp/cid_local_media_agent_second_machine_controlled_execution_v1

Step 2 - enter controlled workspace:

cd /tmp/cid_local_media_agent_second_machine_controlled_execution_v1

Step 3 - clone repository or verify existing controlled clone:

git clone https://github.com/charliesound/SERVICIOS_CINE.git SERVICIOS_CINE

Step 4 - enter repository:

cd SERVICIOS_CINE

Step 5 - verify branch:

git branch --show-current

Step 6 - verify local HEAD:

git rev-parse HEAD

Step 7 - verify remote main:

git ls-remote --heads origin main

Step 8 - verify required remote tag:

git ls-remote --tags origin | grep cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-controlled-execution-authorization-gate-v1-20260620

Step 9 - create virtual environment:

python3 -m venv .venv

Step 10 - activate virtual environment:

source .venv/bin/activate

Step 11 - install documented dependencies:

python -m pip install -U pip

Step 12 - install project test dependencies using documented project method only:

python -m pip install -e ".[test]"

Step 13 - run approved validation tests:

python -m pytest tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_authorization_gate.py -q
python -m pytest tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness_qa_gate.py -q
python -m pytest tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness.py -q
python -m pytest tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan_qa_gate.py -q
python -m pytest tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan.py -q
python -m pytest tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_readiness.py -q
python -m pytest tests/unit/test_cid_local_media_agent_visible_report_internal_demo_readiness.py -q
python -m pytest tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py -q
python -m pytest tests/unit/test_cid_local_media_agent_visible_report_runtime_cli_implementation_qa_gate.py -q
python -m pytest tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py -q
python -m pytest tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_controlled_runtime_implementation_qa_gate.py -q

Step 14 - create controlled fixture and output folders outside real media:

mkdir -p /tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_fixture_input
mkdir -p /tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_output

Step 15 - create controlled scanner-result fixture only:

python - <<'FIXTURE'
from pathlib import Path
import json
from tests.unit.test_cid_local_media_agent_visible_report_runtime_generator import _valid_scanner_result

fixture = Path("/tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_fixture_input/controlled_scanner_result.json")
fixture.parent.mkdir(parents=True, exist_ok=True)
fixture.write_text(json.dumps(_valid_scanner_result(), indent=2, sort_keys=True), encoding="utf-8")
print(f"CONTROLLED_FIXTURE={fixture}")
FIXTURE

Step 16 - run visible report CLI with controlled fixture input only:

python scripts/local_media_agent/visible_report_runtime_cli.py \
  --scanner-result-json /tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_fixture_input/controlled_scanner_result.json \
  --output-root /tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_output \
  --print-output-path

Step 17 - inspect generated report path:

ls -l /tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_output/05_reports/cid_local_media_agent_visible_report_v1.md

Step 18 - write evidence record:

python - <<'EVIDENCE'
from pathlib import Path
import json
from datetime import datetime, timezone

root = Path("/tmp/cid_local_media_agent_second_machine_controlled_execution_v1")
evidence = {
    "phase": "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.EVIDENCE.V1",
    "authorization_source": "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.AUTHORIZATION.GATE.V1",
    "expected_head": "9f665c1823435084f8a9181e2b3ac9420bc47011",
    "source_tag": "cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-controlled-execution-authorization-gate-v1-20260620",
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "internal_only": True,
    "controlled_fixture_only": True,
    "real_media_used": False,
    "client_material_used": False,
    "installer_created": False,
    "client_installation": False,
    "public_demo": False,
    "sales_demo": False,
    "database_write": False,
    "saas_upload": False,
}
path = root / "controlled_execution_evidence_v1.json"
path.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
print(f"EVIDENCE={path}")
EVIDENCE

## Required Stop Conditions

The future execution phase must stop before any visible report CLI execution if:

- machine owner is not project owner
- machine is client-owned
- machine is productora-owned
- machine is school-owned
- machine is investor-owned
- workspace is not controlled
- workspace is inside client media folder
- workspace is inside production footage folder
- workspace is inside confidential project folder
- repository remote is unexpected
- branch is not main
- local HEAD does not match expected HEAD
- remote main does not match expected HEAD
- required remote tag is missing
- repository is dirty before execution
- virtual environment cannot be created
- dependency installation fails
- approved validation tests fail
- controlled fixture cannot be created
- output root is not controlled
- any real media is requested
- any production footage is requested
- any client media is requested
- any confidential script material is requested
- any environment secret file is requested
- any database file is requested
- any installer action is requested
- any license activation action is requested
- any public demo action is requested
- any sales demo action is requested
- any SaaS upload is requested
- any database write is requested

## Explicitly Blocked Commands

The future execution phase must not include commands that:

- run scanner on real media
- run media probing on real files
- run ffprobe on real files
- run ffmpeg on real files
- synchronize audio
- transcribe audio
- generate subtitles
- translate subtitles
- export DaVinci Resolve timelines
- export Avid timelines
- upload to SaaS
- write to database
- copy secrets
- copy environment files
- copy database files
- create installer package
- sign installer
- activate license
- connect license server
- install on client computer
- present public demo
- present sales demo

## Presenter Language

The future execution phase must state:

This is one controlled internal second-machine setup execution.

This is not a commercial installation.

This is not a client installation.

This is not an installer.

This is not a public demo.

This is not a sales demo.

This uses controlled fixture input only.

This does not scan real media.

This does not probe real media.

This does not sync audio.

This does not transcribe.

This does not generate subtitles.

This does not export timelines.

This does not upload to SaaS.

This does not write to a database.

## Next Safe Phase

The next safe phase may be:

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.PLAN.QA.GATE.V1

That phase may validate the exact command plan.

It must not execute setup.

It must not install the product.

It must not create an installer.

It must not authorize client installation.

It must not authorize public demo use.

It must not authorize sales demo use.

## Validation Evidence Required

This controlled execution plan is accepted only with:

- controlled execution plan test passing
- controlled execution authorization gate test passing
- second machine setup execution readiness QA gate test passing
- second machine setup execution readiness test passing
- second machine setup plan QA gate test passing
- second machine setup plan test passing
- second machine setup readiness test passing
- internal demo readiness test passing
- CLI test passing
- CLI implementation QA gate passing
- runtime generator test passing
- controlled runtime implementation QA gate passing
- supporting implemented runtime chain tests passing
- diff check passing
- WSL/repo guard passing
- database backend regression guard passing

## Acceptance Result

LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_PLAN_PASS_READY_FOR_PLAN_QA_GATE
