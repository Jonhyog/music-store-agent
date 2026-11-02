import { useMemo, useState } from "react"
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
import { COMMAND_ITEM_CLASS } from "@/features/customers/command-item-class"
import { fetchCustomers } from "@/features/customers/api"
import { cn } from "@/lib/utils"

type Props = {
  value: number | null
  onChange: (customerId: number | null) => void
}

export function ComplaintsCustomerFilter({ value, onChange }: Props) {
  const { t } = useTranslation()
  const [open, setOpen] = useState(false)
  // Whether the pointer is over the list or the keyboard is in use.
  const [active, setActive] = useState(false)
  const { data } = useQuery({
    queryKey: ["customers"],
    queryFn: fetchCustomers,
    staleTime: Infinity,
  })
  const selected = data?.customers.find((c) => c.customer_id === value)

  const customerItems = useMemo(
    () =>
      data?.customers.map((c) => (
        <CommandItem
          className={COMMAND_ITEM_CLASS}
          key={c.customer_id}
          value={c.name}
          onSelect={() => {
            onChange(c.customer_id)
            setOpen(false)
          }}
        >
          {c.name}
          <CheckIcon
            className={cn("ml-auto", value !== c.customer_id && "opacity-0")}
          />
        </CommandItem>
      )),
    [data, value, onChange]
  )

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          aria-label={t("complaints.filterLabel")}
          className="w-64 justify-between"
        >
          <span className="truncate">
            {selected ? selected.name : t("complaints.allCustomers")}
          </span>
          <ChevronsUpDownIcon className="opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-72 p-0" align="start">
        <Command
          className="group/cmd"
          data-active={active}
          onKeyDown={() => setActive(true)}
          onPointerMove={() => setActive(true)}
          onPointerLeave={() => setActive(false)}
        >
          <CommandInput placeholder={t("complaints.search")} />
          <CommandList>
            <CommandEmpty>{t("customer.empty")}</CommandEmpty>
            <CommandGroup>
              <CommandItem
                className={COMMAND_ITEM_CLASS}
                value={t("complaints.allCustomers")}
                onSelect={() => {
                  onChange(null)
                  setOpen(false)
                }}
              >
                {t("complaints.allCustomers")}
                <CheckIcon
                  className={cn("ml-auto", value !== null && "opacity-0")}
                />
              </CommandItem>
              {customerItems}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
