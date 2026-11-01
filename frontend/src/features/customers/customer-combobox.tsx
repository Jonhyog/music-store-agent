import { useCallback, useMemo, useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { CheckIcon, ChevronsUpDownIcon } from "lucide-react"
import { useTranslation } from "react-i18next"

import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { cn } from "@/lib/utils"

import { fetchCustomers, type Customer } from "./api"
import { useIdentity } from "./identity"

// cmdk always marks one item as selected and moves the mark on pointer move.
// Only paint it while the pointer is over the list or the keyboard is in use.
const ITEM_CLASS =
  "data-selected:bg-transparent group-data-[active=true]/cmd:data-[selected=true]:bg-muted"

export function CustomerCombobox() {
  const { t } = useTranslation()
  const { customer, setCustomer } = useIdentity()
  const [open, setOpen] = useState(false)
  // Whether the pointer is over the list or the keyboard is in use.
  const [active, setActive] = useState(false)
  const { data, isPending, isError } = useQuery({
    queryKey: ["customers"],
    queryFn: fetchCustomers,
    staleTime: Infinity,
  })

  const label = useCallback(
    (c: Customer) =>
      t("customer.option", {
        name: c.name,
        city: c.city,
        count: c.order_count,
      }),
    [t]
  )

  const select = useCallback(
    (next: Customer | null) => {
      setCustomer(next)
      setOpen(false)
    },
    [setCustomer]
  )

  const customerItems = useMemo(
    () =>
      data?.customers.map((c) => (
        <CommandItem
          className={ITEM_CLASS}
          key={c.customer_id}
          value={label(c)}
          onSelect={() => select(c)}
        >
          {label(c)}
          <CheckIcon
            className={cn(
              "ml-auto",
              customer?.customer_id !== c.customer_id && "opacity-0"
            )}
          />
        </CommandItem>
      )),
    [data, customer, label, select]
  )

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          aria-label={t("customer.label")}
          className="w-64 justify-between"
        >
          <span className="truncate">
            {customer ? customer.name : t("customer.visitor")}
          </span>
          <ChevronsUpDownIcon className="opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-96 p-0" align="end">
        <Command
          className="group/cmd"
          data-active={active}
          onKeyDown={() => setActive(true)}
          onPointerMove={() => setActive(true)}
          onPointerLeave={() => setActive(false)}
        >
          <CommandInput placeholder={t("customer.search")} />
          <CommandList>
            <CommandEmpty>{t("customer.empty")}</CommandEmpty>
            <CommandGroup>
              <CommandItem
                className={ITEM_CLASS}
                value={t("customer.visitor")}
                onSelect={() => select(null)}
              >
                {t("customer.visitor")}
                <CheckIcon className={cn("ml-auto", customer && "opacity-0")} />
              </CommandItem>
              {isPending && (
                <div className="px-2 py-1.5 text-sm text-muted-foreground">
                  {t("customer.loading")}
                </div>
              )}
              {isError && (
                <div className="px-2 py-1.5 text-sm text-destructive">
                  {t("customer.error")}
                </div>
              )}
              {customerItems}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
