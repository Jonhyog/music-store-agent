import { useTranslation } from "react-i18next"

import { Suggestion, Suggestions } from "@/components/ai-elements/suggestion"
import { useIdentity } from "@/features/customers/identity"

/** Starter questions for an empty chat; order questions need a Customer. */
export function StarterSuggestions({
  onPick,
}: {
  onPick: (text: string) => void
}) {
  const { t } = useTranslation()
  const { customer } = useIdentity()
  const list = (key: string) =>
    t(key, { returnObjects: true }) as unknown as string[]
  const catalog = list("chat.suggestions.catalog")
  const orders = customer ? list("chat.suggestions.orders") : []

  return (
    <Suggestions className="flex-wrap justify-center whitespace-normal">
      {[...catalog, ...orders].map((text) => (
        <Suggestion key={text} suggestion={text} onClick={onPick} />
      ))}
    </Suggestions>
  )
}
