import { useTranslation } from "react-i18next"

import { Badge } from "@/components/ui/badge"

import type { Complaint } from "./api"

const UNITS: [Intl.RelativeTimeFormatUnit, number][] = [
  ["day", 86_400],
  ["hour", 3_600],
  ["minute", 60],
]

export function relativeTime(iso: string, locale: string, now = Date.now()) {
  const seconds = Math.round((new Date(iso).getTime() - now) / 1000)
  const formatter = new Intl.RelativeTimeFormat(locale, { numeric: "auto" })
  for (const [unit, size] of UNITS) {
    if (Math.abs(seconds) >= size) {
      return formatter.format(Math.trunc(seconds / size), unit)
    }
  }
  return formatter.format(0, "second")
}

export function ComplaintCard({ complaint }: { complaint: Complaint }) {
  const { t, i18n } = useTranslation()
  const created = new Date(complaint.created_at)
  return (
    <article className="flex flex-col gap-2 rounded-lg border p-4">
      <div className="flex items-center justify-between gap-2">
        <span className="font-semibold">
          {t("complaints.protocol", { id: complaint.complaint_id })}
        </span>
        <Badge variant="secondary">
          {t(`complaints.category.${complaint.category}`)}
        </Badge>
      </div>
      <div className="text-sm">
        {complaint.customer_name}
        {complaint.order_id !== null && (
          <span className="text-muted-foreground">
            {" · "}
            {t("complaints.order", { id: complaint.order_id })}
          </span>
        )}
      </div>
      <time
        dateTime={complaint.created_at}
        title={created.toLocaleString(i18n.language)}
        className="text-xs text-muted-foreground"
      >
        {relativeTime(complaint.created_at, i18n.language)}
      </time>
      <p className="text-sm whitespace-pre-wrap">{complaint.description}</p>
    </article>
  )
}
