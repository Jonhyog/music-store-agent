import { Fragment, useMemo } from "react"
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
  Reasoning,
  ReasoningContent,
  ReasoningTrigger,
} from "@/components/ai-elements/reasoning"
import { Button } from "@/components/ui/button"
import { Shimmer } from "@/components/ai-elements/shimmer"
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
  const { t } = useTranslation()
  if (part.type === "reasoning") {
    return (
      <Reasoning isStreaming={part.state === "streaming"}>
        <ReasoningTrigger
          getThinkingMessage={(isStreaming, duration) =>
            isStreaming || duration === 0 ? (
              <Shimmer duration={1}>{t("chat.reasoning.thinking")}</Shimmer>
            ) : (
              <p>
                {duration === undefined
                  ? t("chat.reasoning.thoughtBriefly")
                  : t("chat.reasoning.thoughtFor", { count: duration })}
              </p>
            )
          }
        />
        <ReasoningContent>{part.text}</ReasoningContent>
      </Reasoning>
    )
  }
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
  interruptedIds,
  hasError,
  onRetry,
  empty,
}: {
  messages: UIMessage[]
  modelChanges: ModelChange[]
  interruptedIds: ReadonlySet<string>
  hasError: boolean
  onRetry: () => void
  empty: React.ReactNode
}) {
  const { t } = useTranslation()
  const body = useMemo(
    () =>
      messages.length === 0 ? (
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
                  {interruptedIds.has(message.id) && (
                    <p className="text-xs text-muted-foreground italic">
                      {t("chat.interrupted")}
                    </p>
                  )}
                </MessageContent>
              </Message>
            </Fragment>
          ))}
          <ModelDividers changes={modelChanges} atIndex={messages.length} />
        </>
      ),
    [messages, modelChanges, interruptedIds, empty, t]
  )
  return (
    <Conversation>
      <ConversationContent>
        {body}
        {hasError && (
          <div
            role="alert"
            className="flex items-center gap-3 text-sm text-destructive"
          >
            {t("chat.error")}
            <Button type="button" variant="outline" size="sm" onClick={onRetry}>
              {t("chat.retry")}
            </Button>
          </div>
        )}
      </ConversationContent>
      <ConversationScrollButton aria-label={t("chat.scrollToBottom")} />
    </Conversation>
  )
}
