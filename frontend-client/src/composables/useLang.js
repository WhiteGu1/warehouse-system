import { ref, computed } from 'vue'
import { messages, getLang, setLang } from '../i18n'

const lang = ref(getLang())

export function useLang() {
  const t = computed(() => messages[lang.value] || messages.zh)

  const switchLang = () => {
    lang.value = lang.value === 'zh' ? 'es' : 'zh'
    setLang(lang.value)
  }

  return { lang, t, switchLang }
}