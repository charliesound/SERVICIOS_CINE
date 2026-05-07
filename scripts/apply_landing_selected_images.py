from pathlib import Path
from PIL import Image
import re

REPO = Path("/opt/SERVICIOS_CINE")
REVIEW = REPO / ".tmp/landing_image_review"
OUT = REPO / "src_frontend/public/landing-media"

OUT.mkdir(parents=True, exist_ok=True)

# Selección elegida por contexto
SELECTIONS = {
    "landing-hero-main.webp": ("hero_concept", 4),
    "landing-problem-fragmented.webp": ("other", 14),
    "landing-ai-reasoning.webp": ("pipeline", 9),
    "landing-comfyui-generation.webp": ("comfyui_output", 25),
    "landing-cid-orchestration.webp": ("pipeline", 34),
    "landing-storyboard-preview.webp": ("comfyui_output", 67),
    "landing-concept-keyvisual.webp": ("comfyui_output", 118),
    "landing-producers-studios.webp": ("comfyui_input", 199),
    "landing-professional-differential.webp": ("comfyui_input", 217),
    "landing-delivery-final.webp": ("comfyui_output", 120),
}

MANIFEST_CANDIDATES = {
    "hero_concept": [
        REVIEW / "hero_concept.txt",
        REVIEW / "hero_concept_manifest.txt",
    ],
    "other": [
        REVIEW / "other.txt",
        REVIEW / "other_manifest.txt",
    ],
    "pipeline": [
        REVIEW / "pipeline.txt",
        REVIEW / "pipeline_ui.txt",
        REVIEW / "pipeline_manifest.txt",
        REVIEW / "pipeline_ui_manifest.txt",
    ],
    "comfyui_output": [
        REVIEW / "comfyui_output_manifest.txt",
    ],
    "comfyui_input": [
        REVIEW / "comfyui_input_manifest.txt",
    ],
}

TARGET_SIZE = {
    "landing-hero-main.webp": (1920, 1080),
    "landing-problem-fragmented.webp": (1600, 1000),
    "landing-ai-reasoning.webp": (1600, 1000),
    "landing-comfyui-generation.webp": (1600, 1000),
    "landing-cid-orchestration.webp": (1600, 1000),
    "landing-storyboard-preview.webp": (1600, 1000),
    "landing-concept-keyvisual.webp": (1600, 1000),
    "landing-producers-studios.webp": (1600, 1000),
    "landing-professional-differential.webp": (1600, 1000),
    "landing-delivery-final.webp": (1600, 1000),
}

def find_manifest(group: str) -> Path:
    for path in MANIFEST_CANDIDATES[group]:
        if path.exists():
            return path
    raise FileNotFoundError(f"No encuentro manifest para grupo '{group}'. Busqué: {MANIFEST_CANDIDATES[group]}")

def read_manifest(group: str) -> dict[int, Path]:
    manifest = find_manifest(group)
    result: dict[int, Path] = {}

    for line in manifest.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue

        parts = line.split("\t")
        if len(parts) < 2:
            continue

        try:
            idx = int(parts[0].strip())
        except ValueError:
            continue

        path = Path(parts[1].strip())
        result[idx] = path

    return result

def center_crop_resize(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    img = img.convert("RGB")
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        box = (left, 0, left + new_w, src_h)
    else:
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        box = (0, top, src_w, top + new_h)

    img = img.crop(box)
    img = img.resize((target_w, target_h), Image.LANCZOS)
    return img

def export_webp(src: Path, dst: Path, size: tuple[int, int]) -> None:
    if not src.exists():
        raise FileNotFoundError(f"No existe imagen origen: {src}")

    with Image.open(src) as img:
        final = center_crop_resize(img, *size)
        final.save(dst, "WEBP", quality=88, method=6)

def main() -> None:
    print("Aplicando selección de imágenes landing...")
    resolved = {}

    manifests_cache: dict[str, dict[int, Path]] = {}

    for output_name, (group, idx) in SELECTIONS.items():
        if group not in manifests_cache:
            manifests_cache[group] = read_manifest(group)

        manifest = manifests_cache[group]
        if idx not in manifest:
            raise KeyError(f"No existe índice {idx} en manifest '{group}'")

        src = manifest[idx]
        dst = OUT / output_name
        size = TARGET_SIZE[output_name]

        export_webp(src, dst, size)
        resolved[output_name] = src

        print(f"OK {output_name}")
        print(f"   <- {src}")

    summary = OUT / "_landing_selected_images_manifest.txt"
    summary.write_text(
        "\n".join(f"{name}\t{src}" for name, src in resolved.items()),
        encoding="utf-8",
    )

    print("")
    print(f"Manifest final: {summary}")
    print("Selección aplicada correctamente.")

if __name__ == "__main__":
    main()
