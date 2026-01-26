// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './main.css'
import { userState } from './stateHelper'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from './firebase'
import { userApi } from './api'

let authReady = false;

onAuthStateChanged(auth, async (user) => {
  if (user) {
    // Recuperar dbId guardado en Login
    const savedDbId = localStorage.getItem('dbId');
    userState.login(user, savedDbId);

    if (!user.isAnonymous) {
      try {
        const profile = await userApi.getProfile();
        userState.isAdmin = profile.data.is_admin;
        console.log("Perfil recargado:", profile.data);
      } catch (err) {
        console.error("Error perfil load:", err);
        userState.isAdmin = false;
      }
    }
    // No guardamos user object entero en localStorage, Firebase lo gestiona
  } else {
    userState.logout();
  }
  
  if (!authReady) {
    authReady = true;
    createApp(App).use(router).mount('#app');
  }
});