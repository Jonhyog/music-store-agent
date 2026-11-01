import { API_URL } from "@/lib/config"

export type Customer = {
  customer_id: number
  name: string
  phone: string
  email: string
  city: string
  order_count: number
}

type CustomersResponse = { customers: Customer[]; page: number; total: number }

export async function fetchCustomers(): Promise<Customer[]> {
  const res = await fetch(`${API_URL}/customers?page=1&pageSize=50`)
  if (!res.ok) throw new Error(`Failed to load customers (${res.status})`)
  const body = (await res.json()) as CustomersResponse
  return body.customers
}
