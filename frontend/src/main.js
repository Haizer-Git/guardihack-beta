import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import './style.css'


axios.defaults.baseURL = 'http://127.0.0.1:9414'
axios.defaults.withCredentials = true
const app = createApp(App)
app.use(router)
app.mount('#app')
