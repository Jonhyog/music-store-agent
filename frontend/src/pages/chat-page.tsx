import { useTranslation } from "react-i18next"

import {
  PromptInput,
  PromptInputBody,
  PromptInputFooter,
  PromptInputSubmit,
  PromptInputTextarea,
} from "@/components/ai-elements/prompt-input"
import { useChatSession } from "@/features/chat/chat-context"
import { MessageList } from "@/features/chat/message-list"

export function ChatPage() {
  const { t } = useTranslation()
  const { messages, status, isStreaming, send } = useChatSession()

  return (
    <div className="mx-auto flex min-h-0 w-full max-w-3xl flex-1 flex-col gap-4">
      <MessageList
        messages={messages}
        hasError={status === "error"}
        empty={null}
      />
      <PromptInput
        onSubmit={({ text }) => {
          if (!isStreaming && text.trim()) send(text.trim())
        }}
      >
        <PromptInputBody>
          <PromptInputTextarea placeholder={t("chat.inputPlaceholder")} />
        </PromptInputBody>
        <PromptInputFooter className="justify-end">
          <PromptInputSubmit
            status={status}
            disabled={isStreaming}
            aria-label={t("chat.send")}
          />
        </PromptInputFooter>
      </PromptInput>
    </div>
  )
}
