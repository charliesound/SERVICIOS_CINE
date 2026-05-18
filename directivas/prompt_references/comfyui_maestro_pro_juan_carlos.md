# ComfyUI Maestro Pro - Juan Carlos Edition

## Mission

Official prompt and workflow baseline for CID storyboard generation.

## Core Rules

- Do not invent ComfyUI nodes.
- Use only real workflow JSON structures validated for the current backend.
- Build cinematic prompts first, then map them to FLUX, SDXL, or WAN workflows.
- Keep VRAM usage consistent with the selected workflow family.
- Treat ControlNet as optional and only when the workflow already supports it.
- Use production cinematography language grounded in the script.
- Apply anti-hallucination validation before render submission.
- Prefer MasterPack conventions as the primary source for production consistency.

## Prompt Structure

- Subject identity must stay stable across the sequence.
- Action must come from the script, not from stylistic improvisation.
- Location, time of day, and mood must be explicit.
- Camera, lighting, and lens must reinforce the dramatic objective.
- Negative prompts must prevent identity drift, text artifacts, watermarking, and anatomy failures.

## Anti-Hallucination Validation

- Reject props, wardrobe, creatures, or architecture not present in the script.
- Reject extra characters unless the script explicitly implies them.
- Reject contradictory time-of-day lighting.
- Reject fantasy, sci-fi, or horror drift unless the scene already supports it.

## Workflow Families

- FLUX: premium still frames with rich atmosphere and controlled detail.
- SDXL: reliable cinematic storyboard frames for still render queues.
- WAN: compact subject-action-location-time prompting for consistency.

## Production Principle

- Every generated frame must read like a director-approved storyboard panel, not a generic AI image.
