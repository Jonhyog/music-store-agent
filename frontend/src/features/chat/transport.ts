import { DefaultChatTransport, type UIMessage } from "ai"

import { API_URL } from "@/lib/config"

/** A rejected request: the server answered, but with an error status. */
export class ChatHttpError extends Error {
  readonly status: number
  readonly detail: string

  constructor(status: number, detail: string) {
    super(`Chat request failed (${status}): ${detail}`)
    this.status = status
    this.detail = detail
  }
}

/** Like `fetch`, but turns an error status into a `ChatHttpError` carrying the status. */
async function fetchOrThrowHttpError(
  input: RequestInfo | URL,
  init?: RequestInit
): Promise<Response> {
  const response = await fetch(input, init)
  if (response.ok) return response
  let detail = ""
  try {
    detail = String(((await response.json()) as { detail?: unknown }).detail)
  } catch {
    // Not a JSON body; the status alone is enough.
  }
  throw new ChatHttpError(response.status, detail)
}

/** The text of the newest user message: the only thing the server needs per turn. */
function lastUserText(messages: UIMessage[]): string {
  const last = messages.findLast((m) => m.role === "user")
  return (
    last?.parts.map((p) => (p.type === "text" ? p.text : "")).join("") ?? ""
  )
}

/**
 * Sends `{ conversation_id, message }` to `POST /chat`; history lives on the server.
 * Headers are read at send time, so `setHeaders` keeps the latest Customer and model in effect.
 */
export function createChatTransport() {
  let headers: Record<string, string> = {}
  const transport = new DefaultChatTransport<UIMessage>({
    api: `${API_URL}/chat`,
    fetch: fetchOrThrowHttpError,
    prepareSendMessagesRequest: ({ id, messages }) => ({
      body: { conversation_id: id, message: lastUserText(messages) },
      headers,
    }),
  })
  return {
    transport,
    setHeaders: (next: Record<string, string>) => {
      headers = next
    },
  }
}

/** Forgets the Conversation on the server. Best effort: the client has moved on regardless. */
export async function deleteConversation(id: string): Promise<void> {
  try {
    await fetch(`${API_URL}/chat/${id}`, { method: "DELETE" })
  } catch {
    // The server drops idle conversations with the process; nothing to recover.
  }
}
