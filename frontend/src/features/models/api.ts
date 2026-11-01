import { API_URL } from "@/lib/config"

export type ModelInfo = {
  id: string
  provider: "ollama" | "openai"
  label: string
  available: boolean
  default: boolean
}

export type ModelsResponse = {
  models: ModelInfo[]
}

export async function fetchModels(): Promise<ModelsResponse> {
  const res = await fetch(`${API_URL}/models`)
  if (!res.ok) throw new Error(`Failed to load models (${res.status})`)
  return (await res.json()) as ModelsResponse
}
