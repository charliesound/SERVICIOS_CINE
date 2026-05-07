#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path('/opt/SERVICIOS_CINE')


def require(condition: bool, label: str, errors: list[str]) -> None:
    if condition:
        print(f'PASS: {label}')
    else:
        errors.append(label)
        print(f'FAIL: {label}')


def contains(path: Path, needle: str) -> bool:
    if not path.exists():
        return False
    return needle in path.read_text(encoding='utf-8')


def main() -> int:
    errors: list[str] = []

    base = ROOT / 'src/services/llm/base.py'
    provider = ROOT / 'src/services/llm/ollama_provider.py'
    service = ROOT / 'src/services/llm/llm_service.py'
    prompts = ROOT / 'src/services/llm/prompts.py'
    json_utils = ROOT / 'src/services/llm/json_utils.py'
    config = ROOT / 'src/config.py'
    env_example = ROOT / '.env.example'
    script_intake = ROOT / 'src/services/script_intake_service.py'
    storyboard_service = ROOT / 'src/services/storyboard_service.py'
    cid_pipeline = ROOT / 'src/services/cid_pipeline_preset_service.py'
    workflow_routes = ROOT / 'src/routes/workflow_routes.py'
    ops_routes = ROOT / 'src/routes/ops_routes.py'

    require(base.exists(), 'LLM base layer exists', errors)
    require(provider.exists(), 'OllamaProvider exists', errors)
    require(service.exists(), 'LLM service exists', errors)
    require(prompts.exists(), 'LLM prompts exists', errors)
    require(json_utils.exists(), 'LLM json utils exists', errors)

    require(contains(provider, '/api/chat'), 'OllamaProvider uses /api/chat', errors)
    require(contains(config, 'LLM_PROVIDER'), 'config.py contains LLM_PROVIDER', errors)
    require(contains(config, 'OLLAMA_BASE_URL'), 'config.py contains OLLAMA_BASE_URL', errors)
    require(contains(config, 'get_llm_settings'), 'config.py exposes get_llm_settings', errors)
    require(contains(script_intake, 'llm_service'), 'script_intake_service uses llm_service or fallback', errors)
    require(contains(storyboard_service, 'llm_service'), 'storyboard_service uses llm_service or fallback', errors)
    require(contains(cid_pipeline, 'recommend_preset_with_llm'), 'pipeline preset service supports LLM recommendation', errors)
    require(contains(workflow_routes, 'llm_recommendation'), 'workflow routes expose LLM recommendation', errors)
    require(contains(ops_routes, '/llm/status'), 'ops routes expose LLM status endpoint', errors)
    require(contains(env_example, 'OLLAMA_MODEL=qwen2.5:14b'), '.env.example contains Ollama variables', errors)
    require('AUTH_SECRET_KEY=' in env_example.read_text(encoding='utf-8'), '.env.example still avoids removing auth placeholders', errors)
    require('print(' not in provider.read_text(encoding='utf-8'), 'Ollama provider does not print secrets', errors)

    print('\n--- Result ---')
    if errors:
        print(f'FAIL: {len(errors)} contract check(s) failed')
        for error in errors:
            print(f' - {error}')
        return 1
    print('PASS: LLM Ollama contract checks passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
