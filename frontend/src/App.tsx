import { BrowserRouter, Route, Routes } from "react-router"

import { AppLayout } from "@/components/layout/app-layout"
import { IdentityProvider } from "@/features/customers/identity"
import { ChatPage } from "@/pages/chat-page"
import { ComplaintsPage } from "@/pages/complaints-page"
import { NotFoundPage } from "@/pages/not-found-page"

export function App() {
  return (
    <IdentityProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route index element={<ChatPage />} />
            <Route path="complaints" element={<ComplaintsPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </IdentityProvider>
  )
}

export default App
