import { useTranslation } from "react-i18next"

import { Suggestion } from "@/components/ai-elements/suggestion"
import { useIdentity } from "@/features/customers/identity"

const CATALOG_SUGGESTIONS = [
  "chat.suggestions.guitars",
  "chat.suggestions.address",
  "chat.suggestions.price",
] as const
const ORDER_SUGGESTIONS = ["chat.suggestions.return"] as const

/** Starter questions for an empty chat; order questions need a Customer. */
export function StarterSuggestions({
  onPick,
}: {
  onPick: (text: string) => void
}) {
  const { t } = useTranslation()
  const { customer } = useIdentity()
  const keys = customer
    ? [...CATALOG_SUGGESTIONS, ...ORDER_SUGGESTIONS]
    : CATALOG_SUGGESTIONS

  return (
    <div className="flex flex-wrap justify-center gap-2">
      {keys.map((key) => (
        <Suggestion
          key={key}
          suggestion={t(key)}
          onClick={onPick}
          className="h-auto py-1.5 whitespace-normal"
        />
      ))}
    </div>
  )
}
