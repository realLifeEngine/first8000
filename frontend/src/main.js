import { createApp } from 'vue'
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
const app = createApp(App)
app.use(router)
app.use(PrimeVue)
app.use(ToastService)
app.use(ConfirmationService)
app.component('Toast', Toast)
app.component('ConfirmDialog', ConfirmDialog)
app.mount('#app')
