import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from "react"
import { XIcon } from "lucide-react"

const DISMISS_AFTER_MS = 6000

type Toast = { id: number; message: string }

type ToastContextValue = { toast: (message: string) => void }

const ToastContext = createContext<ToastContextValue | null>(null)

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])
  const nextId = useRef(0)

  const dismiss = useCallback(
    (id: number) => setToasts((all) => all.filter((t) => t.id !== id)),
    []
  )
  const toast = useCallback(
    (message: string) => {
      const id = nextId.current++
      setToasts((all) => [...all, { id, message }])
      setTimeout(() => dismiss(id), DISMISS_AFTER_MS)
    },
    [dismiss]
  )
  const value = useMemo(() => ({ toast }), [toast])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div
        role="status"
        aria-live="polite"
        className="fixed right-4 bottom-4 z-50 flex w-80 flex-col gap-2"
      >
        {toasts.map((t) => (
          <div
            key={t.id}
            className="flex items-start gap-2 rounded-md border bg-popover p-3 text-sm text-popover-foreground shadow-md"
          >
            <span className="flex-1">{t.message}</span>
            <button
              type="button"
              aria-label="Close"
              className="text-muted-foreground hover:text-foreground"
              onClick={() => dismiss(t.id)}
            >
              <XIcon className="size-4" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error("useToast must be used within ToastProvider")
  return ctx
}
