#!/usr/bin/env python3

from pathlib import Path
import sys
import unicodedata


ROOT = Path('/opt/SERVICIOS_CINE')
COMMERCIAL_DIR = ROOT / 'docs' / 'commercial'
REQUIRED_DOCS = [
    'CID_ONE_PAGER.md',
    'CID_SALES_DECK.md',
    'CID_DEMO_10_MIN_SCRIPT.md',
    'CID_DEMO_30_MIN_SCRIPT.md',
    'CID_PILOT_PROPOSAL.md',
    'CID_CLIENT_FAQ.md',
    'CID_MEETING_CHECKLIST.md',
    'CID_PILOT_DATA_REQUEST.md',
    'CID_EMAIL_OUTREACH_TEMPLATE.md',
]


def normalize(text: str) -> str:
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(char for char in text if not unicodedata.combining(char))
    return text.lower()


def main() -> int:
    print('=' * 60)
    print('AILinkCinema + CID Sales Kit Readiness Check')
    print('=' * 60)

    print('\n1. Checking docs/commercial directory...')
    if not COMMERCIAL_DIR.exists():
        print('   FAIL: docs/commercial does not exist')
        return 1
    print('   OK: docs/commercial exists')

    print('\n2. Checking required documents...')
    missing = []
    existing_paths = []
    for name in REQUIRED_DOCS:
        path = COMMERCIAL_DIR / name
        if path.exists():
            existing_paths.append(path)
            print(f'   OK: {name}')
        else:
            missing.append(name)

    if missing:
        print(f"   FAIL: Missing documents: {', '.join(missing)}")
        return 1

    combined = '\n'.join(path.read_text(encoding='utf-8') for path in existing_paths)
    combined_normalized = normalize(combined)

    print('\n3. Checking core positioning phrases...')
    required_phrases = [
        'AILinkCinema',
        'CID',
        'detectar problemas',
        'soluciones de inteligencia artificial',
        'Cine Inteligente Digital',
        'storyboard',
        'piloto',
    ]
    missing_phrases = []
    for phrase in required_phrases:
        if normalize(phrase) in combined_normalized:
            print(f'   OK: {phrase}')
        else:
            missing_phrases.append(phrase)

    if missing_phrases:
        print('   FAIL: Missing positioning phrases:')
        for phrase in missing_phrases:
            print(f'     - {phrase}')
        return 1

    print('\n4. Checking FAQ requirements...')
    faq_path = COMMERCIAL_DIR / 'CID_CLIENT_FAQ.md'
    faq_text = faq_path.read_text(encoding='utf-8')
    faq_normalized = normalize(faq_text)
    faq_requirements = [
        '¿AILinkCinema y CID son lo mismo?',
        '¿Y si mi problema no encaja con CID?',
        '¿CID hace storyboard?',
    ]
    missing_faq = []
    for phrase in faq_requirements:
        if normalize(phrase) in faq_normalized:
            print(f'   OK: {phrase}')
        else:
            missing_faq.append(phrase)

    if missing_faq:
        print('   FAIL: Missing FAQ entries:')
        for phrase in missing_faq:
            print(f'     - {phrase}')
        return 1

    print('\n5. Checking pilot proposal structure...')
    proposal_path = COMMERCIAL_DIR / 'CID_PILOT_PROPOSAL.md'
    proposal_text = proposal_path.read_text(encoding='utf-8')
    proposal_normalized = normalize(proposal_text)
    proposal_requirements = [
        'Diagnóstico AILinkCinema',
        'Piloto CID',
        'qué no entra',
    ]
    missing_proposal = []
    for phrase in proposal_requirements:
        if normalize(phrase) in proposal_normalized:
            print(f'   OK: {phrase}')
        else:
            missing_proposal.append(phrase)

    if missing_proposal:
        print('   FAIL: Missing proposal sections:')
        for phrase in missing_proposal:
            print(f'     - {phrase}')
        return 1

    print('\n6. Checking forbidden phrases...')
    forbidden_phrases = [
        'garantiza distribución',
        'garantiza subvención',
        'presupuesto definitivo',
        'sustituye al productor',
    ]
    found_forbidden = []
    for phrase in forbidden_phrases:
        if normalize(phrase) in combined_normalized:
            found_forbidden.append(phrase)

    if found_forbidden:
        print('   FAIL: Forbidden phrases detected:')
        for phrase in found_forbidden:
            print(f'     - {phrase}')
        return 1

    print('   OK: No forbidden phrases detected')

    print('\n' + '=' * 60)
    print('SALES KIT READY')
    print('=' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
