import { Link } from "react-router"
import { useTranslation } from "react-i18next"

export function NotFoundPage() {
  const { t } = useTranslation()
  return (
    <div className="flex flex-col items-center gap-2 py-16 text-center">
      <h1 className="text-2xl font-semibold">{t("notFound.title")}</h1>
      <p className="text-muted-foreground">{t("notFound.description")}</p>
      <Link to="/" className="underline">
        {t("notFound.back")}
      </Link>
    </div>
  )
}
