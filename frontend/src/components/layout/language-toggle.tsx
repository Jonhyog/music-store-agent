import { useTranslation } from "react-i18next"

import { Button } from "@/components/ui/button"

export function LanguageToggle() {
  const { t, i18n } = useTranslation()
  const next = i18n.language === "en" ? "pt-BR" : "en"
  return (
    <Button
      variant="outline"
      size="sm"
      aria-label={t("language.toggleTo")}
      title={t("language.toggleTo")}
      onClick={() => void i18n.changeLanguage(next)}
    >
      {t("language.short")}
    </Button>
  )
}
