import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './main.css'
import { userState } from './stateHelper'

const user = localStorage.getItem('user');
if (user) {
  userState.login(JSON.parse(user));
}

createApp(App).use(router).mount('#app')
