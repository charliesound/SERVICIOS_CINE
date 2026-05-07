/**
 * API client for Ollama-based storyboard analysis and prompt generation.
 */

import api from './client'

export interface OllamaModelStatus {
  name: string
  available: boolean
}

export interface OllamaStatusResponse {
  ollama_available: boolean
  base_url: string
  models: string[]
  analysis_model: OllamaModelStatus
  visual_model: OllamaModelStatus
  fallback_model: OllamaModelStatus
}

export interface StoryboardPromptRequest {
  generation_mode: 'FULL_SCRIPT' | 'SEQUENCE' | 'SCENE_RANGE' | 'SINGLE_SCENE' | 'SELECTED_SCENES'
  sequence_id?: string | null
  scene_number?: number | null
  selected_scenes?: number[]
  scene_range?: {
    start: number | null
    end: number | null
  }
  refine_with_visual_model?: boolean
}

export interface ScenePrompt {
  scene_number: number
  sequence_id: string
  refined_storyboard_prompt?: string
  comfyui_positive_prompt?: string
  comfyui_negative_prompt?: string
  shot_design?: {
    shot_type: string
    camera_angle: string
    lens: string
    camera_movement: string
    composition: string
    lighting: string
    color_palette: string
    texture: string
    cinematic_reference: string
  }
  continuity?: {
    character_continuity_prompt: string
    environment_continuity_prompt: string
    wardrobe_continuity_prompt: string
    seed_strategy: string
  }
  base_storyboard_prompt?: string
  negative_prompt?: string
}

export interface StoryboardPromptsResponse {
  project_id: string
  analysis_model: string
  visual_model: string
  generation_mode: string
  total_scenes: number
  selected_scenes: number[]
  storyboard_prompts: ScenePrompt[]
}

export const ollamaStoryboardApi = {
  getOllamaStatus: async (): Promise<OllamaStatusResponse> => {
    const { data } = await api.get<OllamaStatusResponse>('/ops/ollama/status')
    return data
  },

  analyzeProjectWithLocalOllama: async (projectId: string): Promise<Record<string, unknown>> => {
    const { data } = await api.post<Record<string, unknown>>(
      `/projects/${projectId}/analyze/local-ollama`
    )
    return data
  },

  generateStoryboardPromptsFromAnalysis: async (
    projectId: string,
    payload: StoryboardPromptRequest
  ): Promise<StoryboardPromptsResponse> => {
    const { data } = await api.post<StoryboardPromptsResponse>(
      `/projects/${projectId}/storyboard/prompts/from-analysis`,
      payload
    )
    return data
  },
}
