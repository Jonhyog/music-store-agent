import { useTranslation } from "react-i18next"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

import { useChatSession } from "./chat-context"

export function CustomerSwitchDialog() {
  const { t } = useTranslation()
  const { pendingCustomer, confirmCustomerChange, cancelCustomerChange } =
    useChatSession()
  const name = pendingCustomer?.customer?.name ?? t("customer.visitor")

  return (
    <Dialog
      open={pendingCustomer !== null}
      onOpenChange={(open) => !open && cancelCustomerChange()}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{t("chat.switchCustomer.title")}</DialogTitle>
          <DialogDescription>
            {t("chat.switchCustomer.description", { name })}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={cancelCustomerChange}>
            {t("chat.switchCustomer.cancel")}
          </Button>
          <Button onClick={confirmCustomerChange}>
            {t("chat.switchCustomer.confirm")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
