# Leads Classification Directive

## Purpose
Classify incoming leads from Web Ailink_Cinema into actionable categories for routing to CID, CINE_AI_PLATFORM, or keeping in the web CRM.

## Classification Categories

### storyboard_ia
- Lead expresses interest in AI-generated storyboards
- Keywords: storyboard, visual, scene visualization, shot planning
- Target pipeline: CINE_AI_PLATFORM storyboard generation
- Secondary: Web Ailink_Cinema for demo scheduling

### voz_doblaje
- Lead expresses interest in AI voice/dubbing services
- Keywords: voice, dubbing, audio, narration, localization
- Target pipeline: CID voice processing
- Secondary: CINE_AI_PLATFORM for integrated workflows

### guion_ia
- Lead expresses interest in AI script/screenplay tools
- Keywords: script, screenplay, writing, narrative, story
- Target pipeline: CID script analysis
- Secondary: Web Ailink_Cinema for content marketing

### produccion_general
- Lead expresses general interest without specific category
- Keywords: production, platform, demo, general inquiry
- Target pipeline: CID as central hub
- Secondary: All platforms for cross-promotion

## Priority Assessment
- HIGH: Mentions urgency, demo request, company name present, budget discussion
- MEDIUM: Either urgency OR company present
- LOW: General inquiry, no specific signals

## Output Format
Return JSON with:
- classification: one of the four categories
- lead_type: "inbound_lead"
- priority: "high", "medium", or "low"
- confidence: "llm" or "rule_based"
