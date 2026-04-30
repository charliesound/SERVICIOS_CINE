# Campaign Routing Directive

## Purpose
Determine which campaign and target system should receive a classified lead.

## Routing Matrix

| Classification    | Primary Target    | Secondary Target     | Campaign                    |
|-------------------|-------------------|----------------------|-----------------------------|
| storyboard_ia     | cine_ai_platform  | web_ailink_cinema    | storyboard_ia_launch        |
| voz_doblaje       | cid               | cine_ai_platform     | voice_dubbing_campaign      |
| guion_ia          | cid               | web_ailink_cinema    | script_ai_campaign          |
| produccion_general| cid               | cine_ai_platform     | general_demo_campaign       |

## Next Actions by Priority

### High Priority
- immediate_outreach: Trigger same-day contact workflow
- Notify sales team via webhook
- Create high-priority task in CRM

### Medium Priority
- schedule_demo: Add to demo queue within 48 hours
- Send automated follow-up email
- Assign to appropriate campaign segment

### Low Priority
- add_to_nurture: Add to email nurture sequence
- Tag for future retargeting
- Include in monthly newsletter

## Integration Points
- CID: Central lead database and CRM
- CINE_AI_PLATFORM: AI-powered content generation
- Web Ailink_Cinema: Marketing site and demo scheduler
