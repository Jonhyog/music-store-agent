import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { ChevronLeftIcon, ChevronRightIcon, RefreshCwIcon } from "lucide-react"
import { useTranslation } from "react-i18next"

import { Button } from "@/components/ui/button"
import { Spinner } from "@/components/ui/spinner"
import {
  COMPLAINTS_PAGE_SIZE,
  fetchComplaints,
} from "@/features/complaints/api"
import { ComplaintCard } from "@/features/complaints/complaint-card"
import { ComplaintsCustomerFilter } from "@/features/complaints/customer-filter"

export function ComplaintsPage() {
  const { t } = useTranslation()
  const [customerId, setCustomerId] = useState<number | null>(null)
  const [page, setPage] = useState(1)
  const { data, isPending, isError, isFetching, refetch } = useQuery({
    queryKey: ["complaints", page, customerId],
    queryFn: () => fetchComplaints(page, customerId),
    // Staff expect fresh data when they open the screen or press refresh.
    staleTime: 0,
  })

  const pages = data
    ? Math.max(1, Math.ceil(data.total / COMPLAINTS_PAGE_SIZE))
    : 1

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <h1 className="text-xl font-semibold">{t("complaints.title")}</h1>
        <div className="ml-auto flex items-center gap-2">
          <ComplaintsCustomerFilter
            value={customerId}
            onChange={(id) => {
              setCustomerId(id)
              setPage(1)
            }}
          />
          <Button
            variant="outline"
            onClick={() => void refetch()}
            disabled={isFetching}
          >
            {isFetching ? <Spinner /> : <RefreshCwIcon />}
            {t("complaints.refresh")}
          </Button>
        </div>
      </div>

      {isPending && <Spinner className="mx-auto" />}
      {isError && (
        <div role="alert" className="text-sm text-destructive">
          {t("complaints.error")}{" "}
          <Button variant="link" onClick={() => void refetch()}>
            {t("complaints.retry")}
          </Button>
        </div>
      )}
      {data && data.complaints.length === 0 && (
        <p className="py-8 text-center text-muted-foreground">
          {t("complaints.empty")}
        </p>
      )}
      {data && data.complaints.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.complaints.map((c) => (
            <ComplaintCard key={c.complaint_id} complaint={c} />
          ))}
        </div>
      )}

      {data && data.total > COMPLAINTS_PAGE_SIZE && (
        <div className="flex items-center justify-center gap-3">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
          >
            <ChevronLeftIcon />
            {t("complaints.previous")}
          </Button>
          <span className="text-sm text-muted-foreground">
            {t("complaints.pageOf", { page, pages })}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= pages}
            onClick={() => setPage(page + 1)}
          >
            {t("complaints.next")}
            <ChevronRightIcon />
          </Button>
        </div>
      )}
    </div>
  )
}
