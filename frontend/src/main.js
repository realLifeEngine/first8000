import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import 'primevue/resources/themes/lara-light-teal/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'
import './styles/tokens.css'
import './styles/base.css'
import './styles/primevue-overrides.css'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(PrimeVue)
app.use(ToastService)
app.use(ConfirmationService)
app.component('Toast', Toast)
app.component('ConfirmDialog', ConfirmDialog)

// Resolve auth state (validate stored token, load profile) before the
// router's first navigation guard runs.
useAuthStore(pinia).bootstrap().finally(() => {
  app.mount('#app')
})
