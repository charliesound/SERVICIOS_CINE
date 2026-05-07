#!/usr/bin/env python3
"""Select and optimize landing page images from ComfyUI output."""
import os
import sys
from PIL import Image

SRC = "/mnt/g/COMFYUI_HUB/output"
DST = os.path.abspath("src_frontend/public/landing-media")
EXT = (".png", ".jpg", ".jpeg", ".webp")


def get_images(src):
    """Get all candidate images sorted by size descending."""
    images = []
    for f in os.listdir(src):
        fp = os.path.join(src, f)
        if not os.path.isfile(fp):
            continue
        if not f.lower().endswith(EXT):
            continue
        sz = os.path.getsize(fp)
        images.append((sz, f, fp))
    images.sort(key=lambda x: x[0], reverse=True)
    return images


def convert_to_webp(src_path, dst_name, quality=85):
    """Convert image to WebP and save to destination."""
    try:
        img = Image.open(src_path).convert("RGB")
        dst_path = os.path.join(DST, dst_name)
        img.save(dst_path, "WEBP", quality=quality, method=6)
        dst_size = os.path.getsize(dst_path)
        return dst_path, dst_size
    except Exception as e:
        print(f"  ERROR converting {src_path}: {e}")
        return None, 0


def main():
    os.makedirs(DST, exist_ok=True)
    images = get_images(SRC)
    print(f"Found {len(images)} images in {SRC}")

    # Selection strategy: pick diverse, high-res images by name patterns
    # We need 8 images for different landing sections
    selection_map = [
        # (name_pattern, output_name, min_size_kb)
        # Hero cinematic
        ("ComfyUI-close_up_00010_", "hero-cinematic", 800),
        ("ComfyUI-close_up_00009_", "hero-cinematic-alt", 800),
        # Studio interface / AI canvas
        ("Qwen-Image-2512_00061_", "studio-interface", 800),
        ("Qwen-Image-2512_00066_", "studio-interface-alt", 800),
        # Storyboard panel
        ("storyboard_sdxl_ipadapter_shot_reverse_shot_contraplano_00135_", "storyboard-panel", 800),
        ("storyboard_sdxl_ipadapter_shot_reverse_shot_contraplano_00136_", "storyboard-panel-alt", 800),
        # Pipeline frame
        ("ComfyUI_00153_", "pipeline-frame", 800),
        ("ComfyUI_00147_", "pipeline-frame-alt", 800),
        # Moodboard / look development
        ("Qwen-Image_00005_", "moodboard-frame", 800),
        ("Qwen-Image_00003_", "moodboard-frame-alt", 800),
        # Delivery / final production
        ("REAL-ESGAN-upscale-4x/Timeline 1_00086446", "delivery-frame", 800),
        # Character / scene
        ("face_swap_00001_", "character-scene", 800),
        # Background abstract
        ("ComfyUI_00126_", "bg-abstract", 800),
    ]

    copied = []
    errors = []
    used_files = set()

    for pattern, output_name, min_kb in selection_map:
        # Search by pattern
        candidates = [
            (sz, f, fp)
            for sz, f, fp in images
            if pattern in f and fp not in used_files
        ]
        if not candidates:
            # Try searching subdirectories
            for root, dirs, files in os.walk(SRC):
                for fn in files:
                    if fn.lower().endswith(EXT) and pattern in fn:
                        fp = os.path.join(root, fn)
                        sz = os.path.getsize(fp)
                        candidates.append((sz, fn, fp))
            candidates.sort(key=lambda x: x[0], reverse=True)

        if candidates:
            sz, fn, fp = candidates[0]
            dst_name = f"{output_name}.webp"
            print(f"Converting {fn} ({sz//1024}K) -> {dst_name} ...")
            dst_path, dst_sz = convert_to_webp(fp, dst_name)
            if dst_path:
                copied.append((fn, dst_name, sz // 1024, dst_sz // 1024))
                used_files.add(fp)
            else:
                errors.append(fn)
        else:
            print(f"  WARNING: No image found for pattern '{pattern}'")

    # Fallback: if some failed, pick best available from remaining
    remaining = [(sz, f, fp) for sz, f, fp in images if fp not in used_files]
    remaining.sort(key=lambda x: x[0], reverse=True)

    # Check which output files are missing
    desired = [output_name for _, output_name, _ in selection_map]
    existing = {os.path.splitext(f)[0] for f in os.listdir(DST)}
    missing = [d for d in desired if d not in existing]

    if missing and remaining:
        for name in missing:
            if not remaining:
                break
            sz, fn, fp = remaining.pop(0)
            dst_name = f"{name}.webp"
            print(f"  FALLBACK: using {fn} ({sz//1024}K) -> {dst_name}")
            dst_path, dst_sz = convert_to_webp(fp, dst_name)
            if dst_path:
                copied.append((fn, dst_name, sz // 1024, dst_sz // 1024))
                used_files.add(fp)

    print(f"\n{'='*60}")
    print(f"COPIED {len(copied)} images to {DST}")
    print(f"{'='*60}")
    for src_name, dst_name, src_kb, dst_kb in copied:
        pct = int((1 - dst_kb / src_kb) * 100) if src_kb else 0
        print(f"  {dst_name:30s}  {src_name:50s}  {src_kb:>6}K -> {dst_kb:>6}K ({pct}% saved)")
    if errors:
        print(f"\nERRORS: {errors}")


if __name__ == "__main__":
    main()
