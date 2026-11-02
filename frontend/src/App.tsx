import { BrowserRouter, Route, Routes } from "react-router"

import { AppLayout } from "@/components/layout/app-layout"
import { Toaster } from "@/components/ui/sonner"
import { BackendStatusProvider } from "@/features/backend/backend-status"
import { ChatProvider } from "@/features/chat/chat-context"
import { IdentityProvider } from "@/features/customers/identity"
import { ModelProvider } from "@/features/models/model-context"
import { ChatPage } from "@/pages/chat-page"
import { ComplaintsPage } from "@/pages/complaints-page"
import { NotFoundPage } from "@/pages/not-found-page"

export function App() {
  return (
    <>
      <Toaster />
      <BackendStatusProvider>
        <IdentityProvider>
          <ModelProvider>
            <ChatProvider>
              <BrowserRouter>
                <Routes>
                  <Route element={<AppLayout />}>
                    <Route index element={<ChatPage />} />
                    <Route path="complaints" element={<ComplaintsPage />} />
                    <Route path="*" element={<NotFoundPage />} />
                  </Route>
                </Routes>
              </BrowserRouter>
            </ChatProvider>
          </ModelProvider>
        </IdentityProvider>
      </BackendStatusProvider>
    </>
  )
}

export default App
