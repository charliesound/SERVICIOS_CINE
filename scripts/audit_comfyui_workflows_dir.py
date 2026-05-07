#!/usr/bin/env python3
"""
Reliable audit script for ComfyUI workflows in /mnt/g/COMFYUI_HUB/workflows.
Uses strict node-based detection instead of broad text matching.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any
from datetime import datetime, timezone

# Paths
WORKFLOWS_ROOT = Path("/mnt/g/COMFYUI_HUB/workflows")
INVENTORY_PATH = Path("/opt/SERVICIOS_CINE/docs/validation/comfyui_models_inventory.json")
OUTPUT_JSON = Path("/opt/SERVICIOS_CINE/docs/validation/comfyui_workflows_dir_audit.json")
OUTPUT_MD = Path("/opt/SERVICIOS_CINE/docs/validation/comfyui_workflows_dir_audit.md")

# Strict node types for family detection
STRICT_NODES = {
    'sdxl': {'CheckpointLoaderSimple', 'KSampler', 'CLIPTextEncode', 'EmptyLatentImage', 'VAEDecode', 'SaveImage'},
    'flux': {'UNETLoader', 'DualCLIPLoader', 'FluxGuidance', 'BasicGuider', 'ModelSamplingFlux', 'FluxKontext'},
    'flux2': {'Flux2', 'Flux2Scheduler', 'EmptyFlux2LatentImage'},
    'wan': {'Wan', 'WanVideo', 'WanImageToVideo', 'WanVideoSampler', 'WanVACE', 'WanFun'},
    'ltx': {'LTX', 'LTXV', 'LTXVideo', 'LTXConditioning', 'LTXVScheduler'},
    'audio': {'LoadAudio', 'SaveAudio', 'Whisper', 'TTS', 'VoiceClone', 'RVC', 'MusicGen', 'StableAudio', 'LatentSync', 'Wav2Lip'},
    'video': {'VideoCombine', 'VHS', 'LoadVideo', 'SaveVideo', 'ImageToVideo', 'TextToVideo'}
}

# SDXL model patterns (strict)
SDXL_MODELS = re.compile(r'(sdxl|juggernaut_xl|realvisxl|epicrealismxl|dreamshaperxl|animagine_xl|base_xl)', re.I)

# Flux model patterns
FLUX_MODELS = re.compile(r'flux1?[-._]?(schnell|dev|kontext|krea)', re.I)

# Flux2 model patterns  
FLUX2_MODELS = re.compile(r'flux[-._]?2', re.I)

# Wan model patterns
WAN_MODELS = re.compile(r'wan2?[-._]?(1|2|2\.1|2\.2)', re.I)

# LTX model patterns
LTX_MODELS = re.compile(r'ltx[-._]?(video|v)?[-._]?\d', re.I)

# Audio model patterns
AUDIO_MODELS = re.compile(r'(whisper|tts|elevenlabs|rvc|musicgen|stableaudio)', re.I)

# Security risk patterns
RISK_PATTERNS = {
    'absolute_windows_path': re.compile(r'[A-Z]:\\'),
    'absolute_wsl_path': re.compile(r'/mnt/[a-z]/'),
    'references_env': re.compile(r'\.env'),
    'api_key': re.compile(r'(api[_-]?key|bearer\s+[a-z0-9])', re.I),
    'openai_key': re.compile(r'sk-[a-zA-Z0-9]{32,}'),
    'token': re.compile(r'\btoken\b.*[=:]', re.I),
    'credentials': re.compile(r'(password|secret|credential)', re.I)
}

# Custom node risk assessment
LOW_RISK_NODES = {'CheckpointLoaderSimple', 'KSampler', 'CLIPTextEncode', 'EmptyLatentImage', 
                   'VAEDecode', 'SaveImage', 'LoadImage', 'VAELoader'}
MEDIUM_RISK_NODES = {'UNETLoader', 'DualCLIPLoader', 'FluxGuidance', 'BasicGuider', 
                     'ControlNetApply', 'ControlNetLoader'}
HIGH_RISK_NODES = {'WanVideo', 'LTXV', 'MuseTalk', 'Wav2Lip', 'LatentSync', 
                     'ElevenLabs', 'WanImageToVideo', 'LTXVideoSampler'}


def classify_format(filepath: Path) -> str:
    """Classify workflow format by loading full JSON."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            return 'unknown_json'
        
        # API format: has 'prompt' key with nodes having 'class_type'
        if 'prompt' in data and isinstance(data['prompt'], dict):
            first_node = next(iter(data['prompt'].values()), None)
            if first_node and isinstance(first_node, dict) and 'class_type' in first_node:
                return 'api_format'
        
        # Check if root keys point to nodes with class_type
        if data:
            first_val = next(iter(data.values()), None)
            if isinstance(first_val, dict) and 'class_type' in first_val:
                return 'api_format'
        
        # UI format: has 'nodes' (list) or 'links' (list)
        if 'nodes' in data and isinstance(data['nodes'], list):
            return 'ui_format'
        if 'links' in data and isinstance(data['links'], list):
            return 'ui_format'
        
        return 'unknown_json'
    
    except Exception:
        return 'invalid_json'


def get_nodes_from_workflow(data: dict) -> List[dict]:
    """Extract node list from workflow regardless of format."""
    nodes = []
    
    # API format
    if 'prompt' in data and isinstance(data['prompt'], dict):
        nodes = list(data['prompt'].values())
    # UI format
    elif 'nodes' in data and isinstance(data['nodes'], list):
        nodes = data['nodes']
    # Direct dict where values are nodes
    else:
        nodes = [v for v in data.values() if isinstance(v, dict) and 'class_type' in v]
    
    return [n for n in nodes if isinstance(n, dict)]


def detect_families_strict(nodes: List[dict]) -> List[str]:
    """Detect families based on actual node types and model names."""
    families = set()
    all_text = json.dumps(nodes)
    
    # Check node class_types
    for node in nodes:
        class_type = node.get('class_type', '')
        
        # SDXL: CheckpointLoaderSimple with SDXL model
        if class_type == 'CheckpointLoaderSimple':
            widgets = node.get('widgets_values', [])
            if widgets and isinstance(widgets[0], str):
                model_name = widgets[0]
                if SDXL_MODELS.search(model_name):
                    families.add('sdxl')
        
        # Flux detection
        elif class_type in STRICT_NODES['flux'] or 'Flux' in class_type:
            families.add('flux')
        
        # Flux2 detection
        elif any(x in class_type for x in ['Flux2', 'EmptyFlux2']):
            families.add('flux2')
        
        # Wan detection
        elif any(x in class_type for x in ['Wan', 'WanVideo', 'WanImage']):
            families.add('wan')
        
        # LTX detection
        elif any(x in class_type for x in ['LTX', 'LTXV', 'LTXVideo']):
            families.add('ltx')
        
        # Audio detection
        elif any(x in class_type for x in ['Audio', 'Whisper', 'TTS', 'Voice', 'Wav2Lip', 'LatentSync']):
            families.add('audio')
        
        # Video detection
        elif any(x in class_type for x in ['Video', 'VHS', 'LoadVideo', 'SaveVideo']):
            families.add('video')
    
    # Also check model names in widgets_values
    for node in nodes:
        widgets = node.get('widgets_values', [])
        if not isinstance(widgets, list):
            continue
        for w in widgets:
            if not isinstance(w, str):
                continue
            if FLUX_MODELS.search(w):
                families.add('flux')
            if FLUX2_MODELS.search(w):
                families.add('flux2')
            if WAN_MODELS.search(w):
                families.add('wan')
            if LTX_MODELS.search(w):
                families.add('ltx')
            if SDXL_MODELS.search(w):
                families.add('sdxl')
            if AUDIO_MODELS.search(w):
                families.add('audio')
    
    return list(families)


def detect_nodes_strict(nodes: List[dict]) -> Set[str]:
    """Detect target nodes from workflow nodes."""
    found = set()
    
    for node in nodes:
        class_type = node.get('class_type', '')
        node_type = node.get('type', '')
        title = node.get('title', '')
        
        search_text = f"{class_type} {node_type} {title}"
        
        for category, node_list in STRICT_NODES.items():
            for node_name in node_list:
                if node_name.lower() in search_text.lower():
                    found.add(node_name)
    
    return found


def extract_models_from_nodes(nodes: List[dict]) -> Dict[str, List[str]]:
    """Extract model names from node inputs and widgets."""
    models = {
        'checkpoints': [],
        'loras': [],
        'vae': [],
        'unet': [],
        'clip': [],
        'controlnet': [],
        'audio': [],
        'video': []
    }
    
    for node in nodes:
        class_type = node.get('class_type', '')
        widgets = node.get('widgets_values', [])
        inputs = node.get('inputs', {})
        
        # CheckpointLoaderSimple
        if class_type == 'CheckpointLoaderSimple' and widgets:
            models['checkpoints'].append(widgets[0])
        
        # LoRALoader
        elif 'LoRA' in class_type and widgets:
            models['loras'].append(widgets[0])
        
        # VAELoader
        elif 'VAELoader' in class_type and widgets:
            models['vae'].append(widgets[0])
        
        # UNETLoader
        elif 'UNETLoader' in class_type and widgets:
            models['unet'].append(widgets[0])
        
        # Check inputs for model names
        if isinstance(inputs, dict):
            for key, val in inputs.items():
                if isinstance(val, str) and val.endswith(('.safetensors', '.ckpt', '.pt', '.pth', '.bin')):
                    if 'clip' in key.lower():
                        models['clip'].append(val)
                    elif 'control' in key.lower():
                        models['controlnet'].append(val)
    
    return models


def detect_security_risks(data: dict) -> List[str]:
    """Detect security risks in workflow data."""
    risks = []
    text = json.dumps(data)
    
    for risk_name, pattern in RISK_PATTERNS.items():
        if pattern.search(text):
            risks.append(risk_name)
    
    return risks


def assess_custom_node_risk(nodes: List[dict]) -> str:
    """Assess custom node risk level."""
    all_class_types = [n.get('class_type', '') for n in nodes]
    all_text = ' '.join(all_class_types)
    
    # Check for high risk nodes
    for node_name in HIGH_RISK_NODES:
        if node_name in all_text:
            return 'high'
    
    # Check for medium risk nodes
    for node_name in MEDIUM_RISK_NODES:
        if node_name in all_text:
            return 'medium'
    
    return 'low'


def calculate_score_strict(fmt: str, families: List[str], nodes_found: Set[str], 
                          risks: List[str], missing_models: List[str], task: str,
                          nodes: List[dict] = None) -> int:
    """Calculate workflow score with strict rules."""
    score = 0
    
    # Format bonus
    if fmt == 'api_format':
        score += 30
    elif fmt == 'ui_format':
        score += 10
    
    # Node bonuses (only if relevant to task)
    if task == 'storyboard_sdxl' or task == 'storyboard_fast_sdxl':
        if 'CheckpointLoaderSimple' in nodes_found:
            score += 20
        if 'KSampler' in nodes_found:
            score += 20
        if 'CLIPTextEncode' in nodes_found:
            score += 15
        if 'SaveImage' in nodes_found or 'SaveVideo' in nodes_found:
            score += 10
    
    elif task == 'flux_concept_art' or task == 'flux2_concept_art':
        if 'UNETLoader' in nodes_found or 'CheckpointLoaderSimple' in nodes_found:
            score += 20
        if 'DualCLIPLoader' in nodes_found or 'CLIPTextEncode' in nodes_found:
            score += 15
        if 'KSampler' in nodes_found or 'BasicGuider' in nodes_found:
            score += 15
    
    elif task == 'wan_video':
        if any(n in nodes_found for n in ['WanVideo', 'WanImageToVideo']):
            score += 30
        if 'VideoCombine' in nodes_found or 'SaveVideo' in nodes_found:
            score += 20
    
    elif task == 'ltx_video':
        if any(n in nodes_found for n in ['LTX', 'LTXVideo']):
            score += 30
        if 'VideoCombine' in nodes_found or 'SaveVideo' in nodes_found:
            score += 20
    
    elif task in ['audio', 'lipsync']:
        if any(n in nodes_found for n in ['LoadAudio', 'Whisper', 'TTS', 'Wav2Lip']):
            score += 30
    
    # Family bonuses
    if 'sdxl' in families and 'storyboard' in task:
        score += 20
    if 'flux' in families and 'flux' in task:
        score += 30
    if 'wan' in families and 'video' in task:
        score += 30
    if 'ltx' in families and 'video' in task:
        score += 30
    
    # Penalties
    if any('LoRA' in n for n in nodes_found):
        score -= 30
    if risks:
        score -= 50 * len(risks)
    if missing_models:
        score -= 50 * len(missing_models)
    
    # Custom node risk penalty
    if nodes:
        risk_level = assess_custom_node_risk(nodes)
        if risk_level == 'high':
            score -= 40
        elif risk_level == 'medium':
            score -= 20
    
    return max(score, 0)


def get_task_fit(families: List[str]) -> List[str]:
    """Determine task fit based on families."""
    tasks = []
    if 'sdxl' in families:
        tasks.append('storyboard')
    if 'flux' in families:
        tasks.append('concept_art')
    if 'flux2' in families:
        tasks.append('flux2_gen')
    if 'wan' in families or 'ltx' in families:
        tasks.append('video')
    if 'audio' in families:
        tasks.append('audio')
    if 'video' in families:
        tasks.append('video_editing')
    return tasks


def load_inventory() -> tuple[set, dict]:
    """Load model inventory."""
    inventory_models = set()
    inventory_data = {}
    
    if INVENTORY_PATH.exists():
        try:
            with open(INVENTORY_PATH, 'r', encoding='utf-8') as f:
                inventory_data = json.load(f)
                categories = inventory_data.get('categories', {})
                for cat, model_list in categories.items():
                    for m in model_list:
                        if isinstance(m, dict) and 'name' in m:
                            inventory_models.add(m['name'])
        except Exception:
            pass
    
    return inventory_models, inventory_data


def main():
    """Main audit function."""
    if not WORKFLOWS_ROOT.exists():
        print(f"Error: {WORKFLOWS_ROOT} does not exist.")
        return
    
    print(f"Starting reliable audit of {WORKFLOWS_ROOT}...")
    
    # Load inventory
    inventory_models, inventory_data = load_inventory()
    print(f"Loaded {len(inventory_models)} models from inventory")
    
    # Collect workflow files
    workflow_files = []
    for ext in ('*.json', '*.workflow'):
        for f in WORKFLOWS_ROOT.rglob(ext):
            f_str = str(f).lower()
            # Exclude patterns
            if any(x in f_str for x in ['.venv', 'node_modules', '__pycache__', '.git', 
                                         '_trash', 'donutmochi', 'zzz-']):
                continue
            # Skip large files (>10MB)
            try:
                if f.stat().st_size > 10 * 1024 * 1024:
                    continue
            except OSError:
                continue
            workflow_files.append(f)
    
    workflow_files = list(set(workflow_files))
    total = len(workflow_files)
    print(f"Found {total} workflow files to audit...")
    
    # Process workflows
    api_count = 0
    ui_count = 0
    invalid_count = 0
    unknown_count = 0
    candidates = []
    
    for i, wf_path in enumerate(workflow_files):
        if i % 50 == 0:
            print(f"Processing {i}/{total}...")
        
        fmt = classify_format(wf_path)
        
        if fmt == 'invalid_json':
            invalid_count += 1
            continue
        elif fmt == 'api_format':
            api_count += 1
        elif fmt == 'ui_format':
            ui_count += 1
        else:
            unknown_count += 1
            continue
        
        # Load full data
        try:
            with open(wf_path, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
        except Exception:
            invalid_count += 1
            continue
        
        # Get nodes
        nodes = get_nodes_from_workflow(data)
        
        # Detect families (strict)
        families = detect_families_strict(nodes)
        
        # Detect nodes
        nodes_found = detect_nodes_strict(nodes)
        
        # Extract models
        models_used = extract_models_from_nodes(nodes)
        
        # Security risks
        risks = detect_security_risks(data)
        
        # Task fit
        task_fit = get_task_fit(families)
        
        # Check models in inventory
        missing_models = []
        for cat, model_list in models_used.items():
            for m in model_list:
                if m and m not in inventory_models:
                    missing_models.append(m)
        
        # Custom node risk
        custom_risk = assess_custom_node_risk(nodes)
        
        # Calculate scores for different tasks
        scores = {}
        for task in ['storyboard_sdxl', 'storyboard_fast_sdxl', 'flux_concept_art', 
                     'flux2_concept_art', 'wan_video', 'ltx_video', 'audio', 'lipsync']:
            scores[task] = calculate_score_strict(fmt, families, nodes_found, risks, missing_models, task, nodes)
        
        # Recommendation
        max_score = max(scores.values())
        if risks or missing_models:
            recommendation = 'needs_manual_review'
        elif max_score >= 50:
            recommendation = 'candidate_for_template'
        elif max_score >= 30:
            recommendation = 'use_as_reference'
        else:
            recommendation = 'do_not_use'
        
        candidates.append({
            'path': str(wf_path.relative_to(WORKFLOWS_ROOT)),
            'name': wf_path.name,
            'format': fmt,
            'families': families,
            'task_fit': task_fit,
            'node_count': len(nodes_found),
            'detected_nodes': list(nodes_found),
            'models_used': models_used,
            'models_found_in_inventory': [],
            'missing_models': missing_models[:5],
            'security_risks': risks,
            'custom_node_risk': custom_risk,
            'score': max_score,
            'scores_by_task': scores,
            'recommendation': recommendation
        })
    
    # Build recommendations
    recommended = {
        'storyboard_sdxl': [],
        'storyboard_fast_sdxl': [],
        'flux_concept_art': [],
        'flux2_concept_art': [],
        'qwen_image': [],
        'wan_video': [],
        'ltx_video': [],
        'hunyuan_video': [],
        'upscale_delivery': [],
        'audio': [],
        'lipsync': [],
        'voice_dubbing': []
    }
    
    for c in candidates:
        name = c['name']
        path = c['path']
        families = c['families']
        scores = c['scores_by_task']
        
        if scores.get('storyboard_sdxl', 0) >= 30:
            recommended['storyboard_sdxl'].append({'name': name, 'path': path, 'score': scores['storyboard_sdxl']})
        if 'flux' in families and scores.get('flux_concept_art', 0) >= 30:
            recommended['flux_concept_art'].append({'name': name, 'path': path, 'score': scores['flux_concept_art']})
        if 'flux2' in families:
            recommended['flux2_concept_art'].append({'name': name, 'path': path, 'score': scores.get('flux2_concept_art', 0)})
        if 'wan' in families:
            recommended['wan_video'].append({'name': name, 'path': path, 'score': scores.get('wan_video', 0)})
        if 'ltx' in families:
            recommended['ltx_video'].append({'name': name, 'path': path, 'score': scores.get('ltx_video', 0)})
        if 'audio' in families:
            recommended['audio'].append({'name': name, 'path': path})
        if 'lipsync' in families or 'audio' in families:
            recommended['lipsync'].append({'name': name, 'path': path})
    
    # Sort recommendations by score
    for key in recommended:
        if recommended[key] and isinstance(recommended[key][0], dict) and 'score' in recommended[key][0]:
            recommended[key].sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # Build output
    output = {
        'workflow_root': str(WORKFLOWS_ROOT),
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'total_files': total,
        'api_format': api_count,
        'ui_format': ui_count,
        'unknown_json': unknown_count,
        'invalid_json': invalid_count,
        'candidates': candidates,
        'recommended_for_ailinkcinema': {k: [c['name'] for c in v[:10]] for k, v in recommended.items()}
    }
    
    # Write JSON
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Write MD summary
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write("# ComfyUI Workflows Directory Audit Report (Reliable)\n\n")
        f.write(f"**Workflow Root**: `{WORKFLOWS_ROOT}`\n")
        f.write(f"**Generated At**: {output['generated_at']}\n\n")
        f.write("## Summary\n")
        f.write(f"- **Total Files**: {total}\n")
        f.write(f"- **API Format**: {api_count}\n")
        f.write(f"- **UI Format**: {ui_count}\n")
        f.write(f"- **Unknown JSON**: {unknown_count}\n")
        f.write(f"- **Invalid JSON**: {invalid_count}\n\n")
        
        f.write("## Recommendations (Strict Filtering)\n")
        for cat, wfs in recommended.items():
            if wfs:
                f.write(f"### {cat.replace('_', ' ').title()}\n")
                for wf in wfs[:5]:
                    score_str = f" (Score: {wf['score']})" if 'score' in wf else ""
                    f.write(f"- **{wf['name']}**{score_str}\n")
                f.write("\n")
    
    print(f"\nAudit complete!")
    print(f"Total: {total}, API: {api_count}, UI: {ui_count}, Invalid: {invalid_count}")
    print(f"Reports saved to:\n- {OUTPUT_JSON}\n- {OUTPUT_MD}")


if __name__ == "__main__":
    main()
