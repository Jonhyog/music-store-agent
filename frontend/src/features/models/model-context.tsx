import { createContext, useContext, useMemo, useState } from "react"
import { useQuery } from "@tanstack/react-query"

import { fetchModels, type ModelInfo } from "./api"

type ModelContextValue = {
  models: ModelInfo[]
  isPending: boolean
  isError: boolean
  /** The model the chat should use: the user's choice, else the server default. */
  modelId: string | null
  setModelId: (id: string) => void
  /** Headers the chat should send. */
  modelHeaders: { "x-model"?: string }
}

const ModelContext = createContext<ModelContextValue | null>(null)

export function ModelProvider({ children }: { children: React.ReactNode }) {
  const { data, isPending, isError } = useQuery({
    queryKey: ["models"],
    queryFn: fetchModels,
    staleTime: 30_000,
  })
  const [chosenId, setModelId] = useState<string | null>(null)

  const value = useMemo<ModelContextValue>(() => {
    const models = data?.models ?? []
    // Ignore a choice that has since become unavailable.
    const chosen = models.find((m) => m.id === chosenId && m.available)
    const modelId = (chosen ?? models.find((m) => m.default))?.id ?? null
    return {
      models,
      isPending,
      isError,
      modelId,
      setModelId,
      modelHeaders: modelId ? { "x-model": modelId } : {},
    }
  }, [data, isPending, isError, chosenId])

  return <ModelContext.Provider value={value}>{children}</ModelContext.Provider>
}

export function useModel() {
  const ctx = useContext(ModelContext)
  if (!ctx) throw new Error("useModel must be used within ModelProvider")
  return ctx
}
