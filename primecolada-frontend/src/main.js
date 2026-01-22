import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './main.css'
import { userState } from './stateHelper'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from './firebase'
import { userApi } from './api'

let authReady = false;

onAuthStateChanged(auth, (user) => {
  if (user) {
    userState.login(user);
    if (!user.isAnonymous) {
      userApi.getProfile().then(profile => {
        userState.isAdmin = profile.data.is_admin;
        console.log("Perfil obtenido en app load:", profile.data);
      }).catch(err => {
        console.error("Error obteniendo perfil en app load:", err);
        userState.isAdmin = false;
      });
    }
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
