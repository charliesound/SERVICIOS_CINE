export interface Shot {
  id: string;
  scene_id: string;
  type: string;
  prompt: string;
  negative_prompt?: string | null;
  seed: number;
  cfg: number;
  steps: number;
  workflow_key: string;
  refs: string[];
}
