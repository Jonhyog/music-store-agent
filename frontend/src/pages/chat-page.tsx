import { Trash2Icon } from "lucide-react"
import { useTranslation } from "react-i18next"

import { Button } from "@/components/ui/button"

import {
  PromptInput,
  PromptInputBody,
  PromptInputFooter,
  PromptInputSubmit,
  PromptInputTextarea,
} from "@/components/ai-elements/prompt-input"
import { useChatSession } from "@/features/chat/chat-context"
import { StarterSuggestions } from "@/features/chat/starter-suggestions"
import { MessageList } from "@/features/chat/message-list"

export function ChatPage() {
  const { t } = useTranslation()
  const { messages, status, isStreaming, send, clear } = useChatSession()

  return (
    <div className="mx-auto flex min-h-0 w-full max-w-3xl flex-1 flex-col gap-4">
      <MessageList
        messages={messages}
        hasError={status === "error"}
        empty={<StarterSuggestions onPick={send} />}
      />
      <PromptInput
        onSubmit={({ text }) => {
          if (!isStreaming && text.trim()) send(text.trim())
        }}
      >
        <PromptInputBody>
          <PromptInputTextarea placeholder={t("chat.inputPlaceholder")} />
        </PromptInputBody>
        <PromptInputFooter className="justify-between">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            disabled={messages.length === 0}
            onClick={clear}
          >
            <Trash2Icon />
            {t("chat.clear")}
          </Button>
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
