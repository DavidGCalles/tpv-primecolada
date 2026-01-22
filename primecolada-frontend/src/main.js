import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './main.css'
import { userState } from './stateHelper'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from './firebase'

let authReady = false;

onAuthStateChanged(auth, (user) => {
  if (user) {
    userState.login(user);
    localStorage.setItem('user', JSON.stringify(user));
  } else {
    userState.logout();
    localStorage.removeItem('user');
  }
  if (!authReady) {
    authReady = true;
    createApp(App).use(router).mount('#app');
  }
});
