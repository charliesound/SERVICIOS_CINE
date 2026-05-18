# Prompt Reference Loader

## Source Directory

- `directivas/prompt_references/`

## Loader Contract

- Load markdown references defensively.
- If one file is missing, keep the service operational.
- Expose source paths so generated metadata can trace the prompt references used.
- Use `negative_prompt_library.md` as the single source for negative prompt assembly.
- Use `wan22_prompt_template.md` as the compact subject-action-location-time baseline.
- Use `camera_motion_dictionary.md` as the approved motion vocabulary.
- Use `comfyui_maestro_pro_juan_carlos.md` as the production ruleset.
