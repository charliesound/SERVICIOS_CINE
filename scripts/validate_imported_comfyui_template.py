#!/usr/bin/env python3
"""Validate imported ComfyUI workflow templates for security and correctness.
Fails if required placeholders are missing or security risks are found."""

import json
import sys
import re
from pathlib import Path

def validate_template(filepath):
    """Validate a ComfyUI workflow template."""
    errors = []
    warnings = []
    
    # 1. Check JSON validity
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: Invalid JSON - {e}")
        return False
    
    text = json.dumps(data)
    text_lower = text.lower()
    
    # 2. Check for security risks (MUST FAIL)
    risk_patterns = {
        'absolute_windows_path': r'[A-Za-z]:\\',
        'absolute_wsl_path': r'/mnt/[a-z]/',
        '.env': r'\.env',
        'api_key': r'api[_-]?key',
        'token': r'\btoken\b',
        'bearer': r'bearer',
        'password': r'password',
        'secret': r'secret',
        'openai_key': r'sk-[a-zA-Z0-9]{32,}'
    }
    
    for risk_name, pattern in risk_patterns.items():
        if re.search(pattern, text, re.I):
            errors.append(f"Security risk: {risk_name} detected")
    
    # 3. Check for raw model files (MUST FAIL)
    model_extensions = r'\.(safetensors|ckpt|pt|pth|bin)[\s"\'`]'
    if re.search(model_extensions, text_lower):
        matches = re.findall(r'[\w/\\]+\.(safetensors|ckpt|pt|pth|bin)', text)
        errors.append(f"Raw model files found: {matches[:5]}")
    
    # 4. Required placeholders for ANY template
    required_placeholders = ['{{POSITIVE_PROMPT}}', '{{NEGATIVE_PROMPT}}', 
                            '{{WIDTH}}', '{{HEIGHT}}', '{{STEPS}}', '{{CFG}}', '{{SEED}}']
    
    for ph in required_placeholders:
        if ph not in text:
            errors.append(f"Missing required placeholder: {ph}")
    
    # 5. Strict Flux detection
    flux_detected = False
    if '{{UNET_NAME}}' in text:
        flux_detected = True
    elif re.search(r'(?:class_type["\']?\s*:\s*["\']?|")\b(UNETLoader|DualCLIPLoader|FluxGuidance|ModelSamplingFlux)\b', text):
        flux_detected = True
    
    if flux_detected:
        flux_placeholders = ['{{UNET_NAME}}', '{{CLIP_L_NAME}}', '{{T5XXL_NAME}}', '{{VAE_NAME}}']
        for ph in flux_placeholders:
            if ph not in text:
                errors.append(f"Missing Flux placeholder: {ph}")
    
    # 6. Strict SDXL detection — no confundir con T5XXL ni "xl" genérico
    sdxl_detected = False
    if 'CheckpointLoaderSimple' in text:
        sdxl_detected = True
    elif '{{CHECKPOINT_NAME}}' in text:
        sdxl_detected = True
    else:
        # Solo detectar SDXL si hay nombres reales de modelos SDXL, NO "xl" genérico
        sdxl_signals = re.findall(r'\b(sdxl|juggernaut|realvisxl|epicrealismxl|sd[\s._-]?xl)\b', text_lower)
        if sdxl_signals:
            sdxl_detected = True
    
    if sdxl_detected:
        if '{{CHECKPOINT_NAME}}' not in text:
            errors.append("Missing {{CHECKPOINT_NAME}} for SDXL workflow")
    
    # 7. Warning for mixed signals
    if flux_detected and sdxl_detected:
        warnings.append("Both Flux and SDXL detected - verify correct placeholders")
    
    # Report
    if errors:
        print(f"VALIDATION FAILED: {len(errors)} error(s)")
        for e in errors:
            print(f"  ERROR: {e}")
        if warnings:
            print("\nWarnings:")
            for w in warnings:
                print(f"  WARNING: {w}")
        return False
    else:
        print("TEMPLATE VALIDATION PASS")
        if warnings:
            print("Warnings:")
            for w in warnings:
                print(f"  WARNING: {w}")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_imported_comfyui_template.py <template.json>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    if not Path(filepath).exists():
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)
    
    success = validate_template(filepath)
    sys.exit(0 if success else 1)
