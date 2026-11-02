import { createContext, useContext, useEffect, useMemo, useState } from "react"
import { useChat } from "@ai-sdk/react"
import type { ChatStatus, UIMessage } from "ai"

import { useIdentity } from "@/features/customers/identity"
import { useModel } from "@/features/models/model-context"

import { createChatTransport, deleteConversation } from "./transport"

type ChatContextValue = {
  messages: UIMessage[]
  status: ChatStatus
  isStreaming: boolean
  send: (text: string) => void
  /** Ends the current Conversation and starts an empty one. */
  clear: () => void
}

const ChatContext = createContext<ChatContextValue | null>(null)

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const { identityHeaders } = useIdentity()
  const { modelHeaders } = useModel()

  const [{ transport, setHeaders }] = useState(createChatTransport)
  useEffect(() => {
    setHeaders({ ...identityHeaders, ...modelHeaders })
  }, [setHeaders, identityHeaders, modelHeaders])

  // A reload starts a fresh Conversation: the id is never persisted.
  const [conversationId, setConversationId] = useState(() =>
    crypto.randomUUID()
  )
  const { messages, status, sendMessage, stop } = useChat({
    id: conversationId,
    transport,
  })

  const value = useMemo<ChatContextValue>(
    () => ({
      messages,
      status,
      isStreaming: status === "submitted" || status === "streaming",
      send: (text) => void sendMessage({ text }),
      clear: () => {
        void stop()
        void deleteConversation(conversationId)
        setConversationId(crypto.randomUUID())
      },
    }),
    [messages, status, sendMessage, stop, conversationId]
  )

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>
}

export function useChatSession() {
  const ctx = useContext(ChatContext)
  if (!ctx) throw new Error("useChatSession must be used within ChatProvider")
  return ctx
}
