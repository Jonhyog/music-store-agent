import { Outlet } from "react-router"

import { Header } from "./header"

export function AppLayout() {
  return (
    <div className="flex h-svh flex-col">
      <Header />
      <main className="flex min-h-0 flex-1 flex-col overflow-y-auto p-4">
        <Outlet />
      </main>
    </div>
  )
}
