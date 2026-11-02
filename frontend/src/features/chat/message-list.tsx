import { Fragment } from "react"
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

import type { ModelChange } from "./chat-context"

function ModelDividers({
  changes,
  atIndex,
}: {
  changes: ModelChange[]
  atIndex: number
}) {
  const { t } = useTranslation()
  return changes
    .filter((c) => c.atIndex === atIndex)
    .map((c, i) => (
      <div
        key={i}
        role="separator"
        className="flex items-center gap-3 text-xs text-muted-foreground"
      >
        <span className="h-px flex-1 bg-border" />
        {t("chat.modelChanged", { model: c.modelLabel })}
        <span className="h-px flex-1 bg-border" />
      </div>
    ))
}

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
  modelChanges,
  hasError,
  empty,
}: {
  messages: UIMessage[]
  modelChanges: ModelChange[]
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
          <>
            {messages.map((message, index) => (
              <Fragment key={message.id}>
                <ModelDividers changes={modelChanges} atIndex={index} />
                <Message from={message.role}>
                  <MessageContent>
                    {message.parts.map((part, i) => (
                      <MessagePart key={i} part={part} />
                    ))}
                  </MessageContent>
                </Message>
              </Fragment>
            ))}
            <ModelDividers changes={modelChanges} atIndex={messages.length} />
          </>
        )}
        {hasError && (
          <p role="alert" className="text-sm text-destructive">
            {t("chat.error")}
          </p>
        )}
      </ConversationContent>
      <ConversationScrollButton aria-label={t("chat.scrollToBottom")} />
    </Conversation>
  )
}
