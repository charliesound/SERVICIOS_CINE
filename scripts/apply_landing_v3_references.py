#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEDIA_DIR = ROOT / "src_frontend" / "public" / "landing-media"
COMPONENTS_DIR = ROOT / "src_frontend" / "src" / "components" / "landing"


def has_video(file_name: str) -> bool:
    return (MEDIA_DIR / file_name).exists()


def optional_video_prop(file_name: str, indent: str = "        ") -> str:
    if not has_video(file_name):
        return ""
    return f"\n{indent}videoSrc=\"/landing-media/{file_name}\""


def write_helper_component() -> Path:
    helper_path = COMPONENTS_DIR / "LandingMediaBackground.tsx"
    helper_source = """interface LandingMediaBackgroundProps {
  imageSrc: string
  videoSrc?: string
  alt?: string
  className?: string
  mediaClassName?: string
  overlayClassName?: string
  imageLoading?: 'eager' | 'lazy'
}

function getVideoType(videoSrc: string): string {
  return videoSrc.endsWith('.webm') ? 'video/webm' : 'video/mp4'
}

export default function LandingMediaBackground({
  imageSrc,
  videoSrc,
  alt = '',
  className = '',
  mediaClassName = 'h-full w-full object-cover',
  overlayClassName,
  imageLoading = 'lazy',
}: LandingMediaBackgroundProps) {
  return (
    <div className={className}>
      {videoSrc ? (
        <video
          className={mediaClassName}
          autoPlay
          muted
          loop
          playsInline
          preload="metadata"
          poster={imageSrc}
          aria-hidden={alt ? undefined : true}
        >
          <source src={videoSrc} type={getVideoType(videoSrc)} />
        </video>
      ) : (
        <img
          src={imageSrc}
          alt={alt}
          className={mediaClassName}
          loading={imageLoading}
        />
      )}
      <div className={overlayClassName} />
    </div>
  )
}
"""
    helper_path.write_text(helper_source, encoding="utf-8")
    return helper_path


def update_file(path: Path, replacements: list[tuple[str, str]]) -> None:
    source = path.read_text(encoding="utf-8")
    updated = source
    for before, after in replacements:
        if before in updated:
            updated = updated.replace(before, after)
    if updated != source:
        path.write_text(updated, encoding="utf-8")


def ensure_import(path: Path, import_line: str, anchor: str | None = None) -> None:
    source = path.read_text(encoding="utf-8")
    if import_line in source:
        return
    if anchor and anchor in source:
        updated = source.replace(anchor, anchor + import_line, 1)
    else:
        updated = import_line + "\n" + source
    path.write_text(updated, encoding="utf-8")


def hero_replacements() -> list[tuple[str, str]]:
    hero_media = f"""          <LandingMediaBackground
            className=\"landing-cinematic-hero-image\"
            imageSrc=\"/landing-media/landing-hero-main-v3.webp\"{optional_video_prop('landing-hero-main-v3.mp4', '            ')}
            alt=\"Cineframe cinematografico generado por IA\"
            mediaClassName=\"h-full w-full object-cover\"
            overlayClassName=\"absolute inset-0 bg-gradient-to-r from-[#080808] via-transparent to-transparent\"
            imageLoading=\"eager\"
          />"""
    old_block = """          <div className="landing-cinematic-hero-image">
            <img
              src="/landing-media/landing-hero-main-v2.webp"
              alt="Cineframe cinematográfico generado por IA"
              className="h-full w-full object-cover"
              loading="eager"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-[#080808] via-transparent to-transparent" />
          </div>"""
    return [(old_block, hero_media)]


def section_background_replacement(
    image_name: str,
    video_name: str | None,
    overlay_class: str,
) -> str:
    return (
        "      <LandingMediaBackground\n"
        '        className="landing-section-bg-img"\n'
        f'        imageSrc="/landing-media/{image_name}"'
        f"{optional_video_prop(video_name, '        ') if video_name else ''}\n"
        '        alt=""\n'
        '        mediaClassName="h-full w-full object-cover opacity-[0.13]"\n'
        f'        overlayClassName="{overlay_class}"\n'
        '        imageLoading="lazy"\n'
        '      />'
    )


def main() -> int:
    COMPONENTS_DIR.mkdir(parents=True, exist_ok=True)
    helper_path = write_helper_component()

    background_import = "import LandingMediaBackground from '@/components/landing/LandingMediaBackground'\n"

    ensure_import(
        COMPONENTS_DIR / "LandingHeroCinematic.tsx",
        background_import,
        "import LandingActionButton from '@/components/landing/LandingActionButton'\n",
    )
    ensure_import(
        COMPONENTS_DIR / "LandingProblemSolution.tsx",
        background_import,
        "import { AlertTriangle, Cpu, Orbit, GitBranch, Zap } from 'lucide-react'\n",
    )
    ensure_import(
        COMPONENTS_DIR / "LandingPipelineBuilder.tsx",
        background_import,
        "import { Brain, Cpu, Orbit, GitBranch } from 'lucide-react'\n",
    )
    ensure_import(
        COMPONENTS_DIR / "LandingDiferencial.tsx",
        background_import,
        "import { Sparkles, ShieldCheck, Scale, BadgeCheck, Layers, Eye } from 'lucide-react'\n",
    )
    ensure_import(COMPONENTS_DIR / "LandingAudienceB2B.tsx", background_import)

    update_file(COMPONENTS_DIR / "LandingHeroCinematic.tsx", hero_replacements())

    for file_name, old_block, new_block in [
        (
            "LandingProblemSolution.tsx",
            """      <div className="landing-section-bg-img">
        <img
          src="/landing-media/landing-problem-fragmented-v2.webp"
          alt=""
          className="h-full w-full object-cover opacity-[0.13]"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-[#080808] via-transparent to-[#080808]" />
      </div>""",
            section_background_replacement(
                "landing-problem-fragmented-v3.webp",
                None,
                "absolute inset-0 bg-gradient-to-r from-[#080808] via-transparent to-[#080808]",
            ),
        ),
        (
            "LandingPipelineBuilder.tsx",
            """      <div className="landing-section-bg-img">
        <img
          src="/landing-media/landing-cid-orchestration-v2.webp"
          alt=""
          className="h-full w-full object-cover opacity-[0.13]"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#080808] via-transparent to-[#080808]" />
      </div>""",
            section_background_replacement(
                "landing-cid-orchestration-v3.webp",
                "landing-cid-orchestration-v3.mp4",
                "absolute inset-0 bg-gradient-to-t from-[#080808] via-transparent to-[#080808]",
            ),
        ),
        (
            "LandingDiferencial.tsx",
            """      <div className="landing-section-bg-img">
        <img
          src="/landing-media/landing-professional-differential-v2.webp"
          alt=""
          className="h-full w-full object-cover opacity-[0.13]"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-[#080808] via-transparent to-[#080808]" />
      </div>""",
            section_background_replacement(
                "landing-professional-differential-v3.webp",
                None,
                "absolute inset-0 bg-gradient-to-r from-[#080808] via-transparent to-[#080808]",
            ),
        ),
        (
            "LandingAudienceB2B.tsx",
            """      <div className="landing-section-bg-img">
        <img
          src="/landing-media/landing-producers-studios-v2.webp"
          alt=""
          className="h-full w-full object-cover opacity-[0.13]"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-[#080808] via-transparent to-[#080808]" />
      </div>""",
            section_background_replacement(
                "landing-producers-studios-v3.webp",
                None,
                "absolute inset-0 bg-gradient-to-r from-[#080808] via-transparent to-[#080808]",
            ),
        ),
    ]:
        path = COMPONENTS_DIR / file_name
        update_file(path, [(old_block, new_block)])

    storyboard_path = COMPONENTS_DIR / "LandingStoryboardCanvas.tsx"
    update_file(
        storyboard_path,
        [
            ("/landing-media/landing-storyboard-preview-v2.webp", "/landing-media/landing-storyboard-preview-v3.webp"),
            ("/landing-media/landing-comfyui-generation-v2.webp", "/landing-media/landing-comfyui-generation-v3.webp"),
            ("/landing-media/landing-concept-keyvisual-v2.webp", "/landing-media/landing-concept-keyvisual-v3.webp"),
            ("/landing-media/landing-delivery-final-v2.webp", "/landing-media/landing-delivery-final-v3.webp"),
        ],
    )

    modules_path = COMPONENTS_DIR / "LandingStudioModules.tsx"
    update_file(
        modules_path,
        [
            ("/landing-media/landing-problem-fragmented-v2.webp", "/landing-media/landing-problem-fragmented-v3.webp"),
            ("/landing-media/landing-concept-keyvisual-v2.webp", "/landing-media/landing-concept-keyvisual-v3.webp"),
            ("/landing-media/landing-storyboard-preview-v2.webp", "/landing-media/landing-storyboard-preview-v3.webp"),
            ("/landing-media/landing-ai-reasoning-v2.webp", "/landing-media/landing-ai-reasoning-v3.webp"),
        ],
    )

    print(f"Helper prepared: {helper_path.relative_to(ROOT)}")
    print("Landing V3 reference application complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
