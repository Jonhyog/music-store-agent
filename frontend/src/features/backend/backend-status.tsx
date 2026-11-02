import { createContext, useContext, useMemo } from "react"
import { useQuery } from "@tanstack/react-query"

import { API_URL } from "@/lib/config"

const CHECK_EVERY_MS = 30_000
const RECHECK_WHEN_DOWN_MS = 3_000

/** Reachable means the server answered at all, whatever the status. */
async function pingBackend(): Promise<true> {
  await fetch(`${API_URL}/models`)
  return true
}

type BackendStatusValue = {
  reachable: boolean
  /** Checks again now, e.g. after a chat request failed to connect. */
  recheck: () => void
}

const BackendStatusContext = createContext<BackendStatusValue | null>(null)

export function BackendStatusProvider({
  children,
}: {
  children: React.ReactNode
}) {
  const { isError, refetch } = useQuery({
    queryKey: ["backend-reachable"],
    queryFn: pingBackend,
    retry: false,
    refetchInterval: (query) =>
      query.state.status === "error" ? RECHECK_WHEN_DOWN_MS : CHECK_EVERY_MS,
  })
  const value = useMemo<BackendStatusValue>(
    () => ({ reachable: !isError, recheck: () => void refetch() }),
    [isError, refetch]
  )
  return (
    <BackendStatusContext.Provider value={value}>
      {children}
    </BackendStatusContext.Provider>
  )
}

export function useBackendStatus() {
  const ctx = useContext(BackendStatusContext)
  if (!ctx)
    throw new Error(
      "useBackendStatus must be used within BackendStatusProvider"
    )
  return ctx
}
