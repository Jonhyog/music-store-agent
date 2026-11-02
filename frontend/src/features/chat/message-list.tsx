import { getToolName, isToolUIPart, type UIMessage } from "ai"
import { useTranslation } from "react-i18next"

import {
  Conversation,
  ConversationContent,
  ConversationEmptyState,
  ConversationScrollButton,
} from "@/components/ai-elements/conversation"
import {
  Message,
  MessageContent,
  MessageResponse,
} from "@/components/ai-elements/message"
import {
  Tool,
  ToolContent,
  ToolHeader,
  ToolInput,
  ToolOutput,
} from "@/components/ai-elements/tool"

function MessagePart({ part }: { part: UIMessage["parts"][number] }) {
  if (part.type === "text") {
    return <MessageResponse>{part.text}</MessageResponse>
  }
  if (isToolUIPart(part)) {
    return (
      <Tool>
        <ToolHeader
          type="dynamic-tool"
          state={part.state}
          toolName={getToolName(part)}
        />
        <ToolContent>
          <ToolInput input={part.input} />
          <ToolOutput output={part.output} errorText={part.errorText} />
        </ToolContent>
      </Tool>
    )
  }
  return null
}

export function MessageList({
  messages,
  hasError,
  empty,
}: {
  messages: UIMessage[]
  hasError: boolean
  empty: React.ReactNode
}) {
  const { t } = useTranslation()
  return (
    <Conversation>
      <ConversationContent>
        {messages.length === 0 ? (
          <ConversationEmptyState
            title={t("chat.emptyTitle")}
            description={t("chat.emptyDescription")}
          >
            {empty}
          </ConversationEmptyState>
        ) : (
          messages.map((message) => (
            <Message key={message.id} from={message.role}>
              <MessageContent>
                {message.parts.map((part, i) => (
                  <MessagePart key={i} part={part} />
                ))}
              </MessageContent>
            </Message>
          ))
        )}
        {hasError && (
          <p role="alert" className="text-sm text-destructive">
            {t("chat.error")}
          </p>
        )}
      </ConversationContent>
      <ConversationScrollButton />
    </Conversation>
  )
}
