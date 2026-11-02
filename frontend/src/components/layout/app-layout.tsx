import { Outlet } from "react-router"
import { useTranslation } from "react-i18next"

import { useBackendStatus } from "@/features/backend/backend-status"

import { Header } from "./header"

export function AppLayout() {
  const { t } = useTranslation()
  const { reachable } = useBackendStatus()
  return (
    <div className="flex h-svh flex-col">
      <Header />
      {!reachable && (
        <div
          role="alert"
          className="bg-destructive px-4 py-2 text-center text-sm text-white"
        >
          {t("backend.unreachable")}
        </div>
      )}
      <main className="flex min-h-0 flex-1 flex-col overflow-y-auto p-4">
        <Outlet />
      </main>
    </div>
  )
}
