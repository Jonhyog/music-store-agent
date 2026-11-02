import { useState } from "react"
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
import { fetchCustomers } from "@/features/customers/api"
import { cn } from "@/lib/utils"

type Props = {
  value: number | null
  onChange: (customerId: number | null) => void
}

export function ComplaintsCustomerFilter({ value, onChange }: Props) {
  const { t } = useTranslation()
  const [open, setOpen] = useState(false)
  const { data } = useQuery({
    queryKey: ["customers"],
    queryFn: fetchCustomers,
    staleTime: Infinity,
  })
  const selected = data?.customers.find((c) => c.customer_id === value)

  const select = (id: number | null) => {
    onChange(id)
    setOpen(false)
  }

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
        <Command>
          <CommandInput placeholder={t("complaints.search")} />
          <CommandList>
            <CommandEmpty>{t("customer.empty")}</CommandEmpty>
            <CommandGroup>
              <CommandItem
                value={t("complaints.allCustomers")}
                onSelect={() => select(null)}
              >
                {t("complaints.allCustomers")}
                <CheckIcon
                  className={cn("ml-auto", value !== null && "opacity-0")}
                />
              </CommandItem>
              {data?.customers.map((c) => (
                <CommandItem
                  key={c.customer_id}
                  value={c.name}
                  onSelect={() => select(c.customer_id)}
                >
                  {c.name}
                  <CheckIcon
                    className={cn(
                      "ml-auto",
                      value !== c.customer_id && "opacity-0"
                    )}
                  />
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
