import { useMemo } from "react"
import { useTranslation } from "react-i18next"

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { cn } from "@/lib/utils"

import { useModel } from "./model-context"

function AvailabilityDot({ available }: { available: boolean }) {
  return (
    <span
      aria-hidden
      className={cn(
        "size-2 shrink-0 rounded-full",
        available ? "bg-emerald-500" : "bg-muted-foreground/40"
      )}
    />
  )
}

export function ModelSelect() {
  const { t } = useTranslation()
  const { models, isPending, isError, modelId, setModelId } = useModel()

  const modelItems = useMemo(
    () =>
      models.map((m) => (
        <SelectItem key={m.id} value={m.id} disabled={!m.available}>
          <AvailabilityDot available={m.available} />
          {m.label}
          {!m.available && (
            <span className="text-muted-foreground">
              {t("model.unavailable")}
            </span>
          )}
        </SelectItem>
      )),
    [models, t]
  )

  return (
    <Select
      value={modelId ?? ""}
      onValueChange={setModelId}
      disabled={models.length === 0}
    >
      <SelectTrigger className="w-56" aria-label={t("model.label")}>
        <SelectValue
          placeholder={
            isPending
              ? t("model.loading")
              : isError
                ? t("model.error")
                : t("model.placeholder")
          }
        />
      </SelectTrigger>
      <SelectContent position="popper" align="end">
        {modelItems}
      </SelectContent>
    </Select>
  )
}
