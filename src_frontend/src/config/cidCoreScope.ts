export const CID_CORE_SCOPE_ENABLED = true

const LAB_SOLUTION_SLUGS = new Set(['dubbing', 'sound-post'])
const HIDDEN_WORKFLOW_CATEGORIES = new Set(['dubbing'])
const HIDDEN_PIPELINE_MODES = new Set(['dubbing', 'sound'])

export const CID_CORE_FUTURE_PRODUCTS = [
  'DubbingTake Studio AI',
  'Sound Post AI',
  'Restoration Lab AI',
] as const

export function isCidCoreCustomerVisibleSolution(slug: string) {
  return !CID_CORE_SCOPE_ENABLED || !LAB_SOLUTION_SLUGS.has(slug)
}

export function isCidCoreLabSolution(slug: string) {
  return CID_CORE_SCOPE_ENABLED && LAB_SOLUTION_SLUGS.has(slug)
}

export function isCidCoreVisibleWorkflowCategory(category: string) {
  return !CID_CORE_SCOPE_ENABLED || !HIDDEN_WORKFLOW_CATEGORIES.has(category)
}

export function isCidCoreVisiblePipelineMode(mode: string) {
  return !CID_CORE_SCOPE_ENABLED || !HIDDEN_PIPELINE_MODES.has(mode)
}
