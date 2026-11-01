import { useTranslation } from "react-i18next"

export function ChatPage() {
  const { t } = useTranslation()
  return <p className="text-muted-foreground">{t("chat.placeholder")}</p>
}
