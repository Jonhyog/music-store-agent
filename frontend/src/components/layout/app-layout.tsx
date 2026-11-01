import { Outlet } from "react-router"

import { Header } from "./header"

export function AppLayout() {
  return (
    <div className="flex min-h-svh flex-col">
      <Header />
      <main className="flex-1 p-4">
        <Outlet />
      </main>
    </div>
  )
}
