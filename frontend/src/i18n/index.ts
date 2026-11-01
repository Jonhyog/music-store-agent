import i18n from "i18next"
import { initReactI18next } from "react-i18next"

import en from "./en.json"
import ptBR from "./pt-BR.json"

export const LANGUAGES = ["pt-BR", "en"] as const
export type Language = (typeof LANGUAGES)[number]

const STORAGE_KEY = "language"

function initialLanguage(): Language {
  const stored = localStorage.getItem(STORAGE_KEY)
  return LANGUAGES.find((l) => l === stored) ?? "pt-BR"
}

void i18n.use(initReactI18next).init({
  resources: { "pt-BR": { translation: ptBR }, en: { translation: en } },
  lng: initialLanguage(),
  fallbackLng: "pt-BR",
  interpolation: { escapeValue: false },
})

i18n.on("languageChanged", (lng) => {
  localStorage.setItem(STORAGE_KEY, lng)
  document.documentElement.lang = lng
})
document.documentElement.lang = i18n.language

export default i18n
