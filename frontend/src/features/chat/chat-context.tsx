import { createContext, useContext, useEffect, useMemo, useState } from "react"
import { useChat } from "@ai-sdk/react"
import type { ChatStatus, UIMessage } from "ai"

import type { Customer } from "@/features/customers/api"
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
  /** Switches Customer; with messages present, asks for confirmation first. */
  changeCustomer: (next: Customer | null) => void
  /** The Customer awaiting confirmation (`null` inside means Visitor), if any. */
  pendingCustomer: { customer: Customer | null } | null
  confirmCustomerChange: () => void
  cancelCustomerChange: () => void
}

const ChatContext = createContext<ChatContextValue | null>(null)

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const { customer, setCustomer, identityHeaders } = useIdentity()
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

  const [pendingCustomer, setPendingCustomer] =
    useState<ChatContextValue["pendingCustomer"]>(null)

  const value = useMemo<ChatContextValue>(() => {
    const clear = () => {
      void stop()
      void deleteConversation(conversationId)
      setConversationId(crypto.randomUUID())
    }
    // A Conversation is bound to one identity, so a new Customer means a new Conversation.
    const switchCustomer = (next: Customer | null) => {
      clear()
      setCustomer(next)
    }
    return {
      messages,
      status,
      isStreaming: status === "submitted" || status === "streaming",
      send: (text) => void sendMessage({ text }),
      clear,
      changeCustomer: (next) => {
        if (next?.customer_id === customer?.customer_id) return
        if (messages.length === 0) switchCustomer(next)
        else setPendingCustomer({ customer: next })
      },
      pendingCustomer,
      confirmCustomerChange: () => {
        if (pendingCustomer) switchCustomer(pendingCustomer.customer)
        setPendingCustomer(null)
      },
      cancelCustomerChange: () => setPendingCustomer(null),
    }
  }, [
    messages,
    status,
    sendMessage,
    stop,
    conversationId,
    customer,
    setCustomer,
    pendingCustomer,
  ])

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>
}

export function useChatSession() {
  const ctx = useContext(ChatContext)
  if (!ctx) throw new Error("useChatSession must be used within ChatProvider")
  return ctx
}
