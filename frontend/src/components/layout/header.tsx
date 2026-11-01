import { NavLink, useLocation } from "react-router"
import { useTranslation } from "react-i18next"

import { CustomerCombobox } from "@/features/customers/customer-combobox"
import { cn } from "@/lib/utils"

import { LanguageToggle } from "./language-toggle"

const linkClass = ({ isActive }: { isActive: boolean }) =>
  cn(
    "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
    isActive
      ? "bg-accent text-accent-foreground"
      : "text-muted-foreground hover:text-foreground"
  )

export function Header() {
  const { t } = useTranslation()
  const { pathname } = useLocation()
  return (
    <header className="flex items-center gap-4 border-b px-4 py-3">
      <span className="text-lg font-semibold">{t("app.storeName")}</span>
      <nav className="flex gap-1">
        <NavLink to="/" end className={linkClass}>
          {t("nav.chat")}
        </NavLink>
        <NavLink to="/complaints" className={linkClass}>
          {t("nav.complaints")}
        </NavLink>
      </nav>
      <div className="ml-auto flex items-center gap-2">
        {pathname === "/" && <CustomerCombobox />}
        <LanguageToggle />
      </div>
    </header>
  )
}
