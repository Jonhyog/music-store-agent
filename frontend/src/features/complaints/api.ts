import { API_URL } from "@/lib/config"

export type ComplaintCategory =
  "product_defect" | "delivery" | "service" | "payment" | "other"

export type Complaint = {
  complaint_id: number
  customer_id: number
  customer_name: string
  order_id: number | null
  category: ComplaintCategory
  description: string
  conversation_id: string
  created_at: string
}

export type ComplaintsResponse = {
  complaints: Complaint[]
  page: number
  total: number
}

export const COMPLAINTS_PAGE_SIZE = 12

export async function fetchComplaints(
  page: number,
  customerId: number | null
): Promise<ComplaintsResponse> {
  const params = new URLSearchParams({
    page: String(page),
    pageSize: String(COMPLAINTS_PAGE_SIZE),
  })
  if (customerId !== null) params.set("customerId", String(customerId))
  const res = await fetch(`${API_URL}/complaints?${params}`)
  if (!res.ok) throw new Error(`Failed to load complaints (${res.status})`)
  return (await res.json()) as ComplaintsResponse
}
