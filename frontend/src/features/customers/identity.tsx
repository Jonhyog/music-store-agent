import { createContext, useContext, useMemo, useState } from "react"

import type { Customer } from "./api"

/** The selected identity: a Customer, or null for the Visitor. */
type IdentityContextValue = {
  customer: Customer | null
  setCustomer: (customer: Customer | null) => void
  /** Headers the chat should send; empty for the Visitor. */
  identityHeaders: { "x-customer-id"?: string }
}

const IdentityContext = createContext<IdentityContextValue | null>(null)

export function IdentityProvider({ children }: { children: React.ReactNode }) {
  const [customer, setCustomer] = useState<Customer | null>(null)
  const value = useMemo<IdentityContextValue>(
    () => ({
      customer,
      setCustomer,
      identityHeaders: customer
        ? { "x-customer-id": String(customer.customer_id) }
        : {},
    }),
    [customer]
  )
  return (
    <IdentityContext.Provider value={value}>
      {children}
    </IdentityContext.Provider>
  )
}

export function useIdentity() {
  const ctx = useContext(IdentityContext)
  if (!ctx) throw new Error("useIdentity must be used within IdentityProvider")
  return ctx
}
