# Guion Analysis Directive

## Purpose
Analyze script/screenplay content to determine the appropriate processing pipeline.

## Content Types

### scene_for_storyboard
- Script contains visual descriptions, scene directions, camera cues
- Keywords: INT, EXT, visual description, action lines, camera movement
- Pipeline: storyboard_pipeline
- Goal: Generate visual storyboard frames from scene text

### scene_for_voice
- Script contains dialogue-heavy content, voice-over cues, narration
- Keywords: dialogue, narrator, voice-over, monologue, conversation
- Pipeline: voice_dubbing_pipeline
- Goal: Generate voice/dubbing assets from dialogue

### script_general
- Script does not fit clearly into storyboard or voice categories
- Generic screenplay content
- Pipeline: script_analysis_pipeline
- Goal: General analysis and metadata extraction

## Priority Assessment
- HIGH: Demo goal specified, production-ready content, explicit deadline
- MEDIUM: Clear content type, well-formatted script
- LOW: Fragmented content, unclear goal, minimal text

## Output Format
Return JSON with:
- content_type: one of the three categories
- recommended_pipeline: corresponding pipeline name
- priority: "high", "medium", or "low"
- confidence: "llm" or "rule_based"
