import { createContext, useContext, useEffect, useMemo, useState } from "react"
import { useChat } from "@ai-sdk/react"
import type { ChatStatus, UIMessage } from "ai"

import type { Customer } from "@/features/customers/api"
import { useIdentity } from "@/features/customers/identity"
import { useModel } from "@/features/models/model-context"

import { createChatTransport, deleteConversation } from "./transport"

/** A model switch mid-Conversation, shown before the message at `atIndex`. */
export type ModelChange = { atIndex: number; modelLabel: string }

type ChatContextValue = {
  messages: UIMessage[]
  modelChanges: ModelChange[]
  status: ChatStatus
  isStreaming: boolean
  send: (text: string) => void
  /** Ends the current Conversation and starts an empty one. */
  clear: () => void
  /** Switches model, keeping the Conversation and marking the switch in the history. */
  changeModel: (id: string) => void
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
  const { models, modelId, setModelId, modelHeaders } = useModel()

  const { transport, setHeaders } = useMemo(() => createChatTransport(), [])
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

  const [modelChanges, setModelChanges] = useState<ModelChange[]>([])
  const [pendingCustomer, setPendingCustomer] =
    useState<ChatContextValue["pendingCustomer"]>(null)

  const value = useMemo<ChatContextValue>(() => {
    const clear = () => {
      void stop()
      void deleteConversation(conversationId)
      setConversationId(crypto.randomUUID())
      setModelChanges([])
    }
    // A Conversation is bound to one identity, so a new Customer means a new Conversation.
    const switchCustomer = (next: Customer | null) => {
      clear()
      setCustomer(next)
    }
    return {
      messages,
      modelChanges,
      status,
      isStreaming: status === "submitted" || status === "streaming",
      send: (text) => void sendMessage({ text }),
      clear,
      changeModel: (id) => {
        const label = models.find((m) => m.id === id)?.label
        if (id === modelId || !label) return
        setModelId(id)
        if (messages.length > 0) {
          setModelChanges([
            ...modelChanges,
            { atIndex: messages.length, modelLabel: label },
          ])
        }
      },
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
    modelChanges,
    status,
    sendMessage,
    stop,
    conversationId,
    models,
    modelId,
    setModelId,
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
