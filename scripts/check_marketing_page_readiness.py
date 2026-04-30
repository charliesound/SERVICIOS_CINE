#!/usr/bin/env python3

from pathlib import Path
import unicodedata
import sys


ROOT = Path('/opt/SERVICIOS_CINE')


def normalize(text: str) -> str:
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(char for char in text if not unicodedata.combining(char))
    return text.lower()


def main() -> int:
    landing_candidates = [
        ROOT / 'src_frontend/src/pages/AilinkCinemaMarketingPage.tsx',
        ROOT / 'src_frontend/src/pages/LandingPage.tsx',
    ]
    support_candidates = [
        ROOT / 'src_frontend/src/data/landingContent.ts',
        ROOT / 'src_frontend/src/data/marketingContent.ts',
        ROOT / 'docs/commercial/CID_CLIENT_FAQ.md',
    ]

    landing_file = next((path for path in landing_candidates if path.exists()), None)
    if landing_file is None:
        print('FAIL: No marketing landing page found')
        return 1

    existing_files = [landing_file] + [path for path in support_candidates if path.exists()]

    print('=' * 60)
    print('AILinkCinema Marketing Readiness Check')
    print('=' * 60)

    print('\n1. Files checked...')
    for path in existing_files:
        print(f'   OK: {path.relative_to(ROOT)}')

    combined = '\n'.join(path.read_text(encoding='utf-8') for path in existing_files)
    normalized = normalize(combined)

    required_phrases = [
        'AILinkCinema es una agencia',
        'detectar problemas',
        'soluciones de inteligencia artificial',
        'CID',
        'Cine Inteligente Digital',
        'trabajen en armonía',
        '¿AILinkCinema y CID son lo mismo?',
        '¿Qué necesito para probarlo?',
    ]

    print('\n2. Required positioning phrases...')
    missing = []
    for phrase in required_phrases:
        if phrase in combined:
            print(f'   OK: {phrase}')
        else:
            missing.append(phrase)

    if missing:
        print('   FAIL: Missing required phrases:')
        for phrase in missing:
            print(f'     - {phrase}')
        return 1

    forbidden_phrases = [
        'garantiza distribución',
        'garantiza subvención',
        'presupuesto definitivo',
        'sustituye al productor',
    ]

    print('\n3. Forbidden phrases...')
    found_forbidden = []
    for phrase in forbidden_phrases:
        if normalize(phrase) in normalized:
            found_forbidden.append(phrase)

    if found_forbidden:
        print('   FAIL: Forbidden phrases detected:')
        for phrase in found_forbidden:
            print(f'     - {phrase}')
        return 1

    print('   OK: No forbidden phrases detected')

    print('\n' + '=' * 60)
    print('MARKETING PAGE READY')
    print('=' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
