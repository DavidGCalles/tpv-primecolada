<template>
  <div class="login-container">
    <div class="card">
      <h1 class="login-header">TPV PrimeColada</h1>
      
      <div v-if="error" class="alert error">{{ error }}</div>

      <button @click="loginGoogle" class="btn btn-google">
        <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="G" width="18">
        Entrar con Google
      </button>

      <div class="divider"><span>O usa tu correo</span></div>

      <form @submit.prevent="handleEmailAuth">
        <div class="form-group">
          <input v-model="email" type="email" placeholder="Correo electrónico" required />
        </div>
        <div class="form-group">
          <input v-model="password" type="password" placeholder="Contraseña" required />
        </div>
        
        <div class="btn-group">
          <button type="submit" class="btn btn-primary">
            {{ isRegistering ? 'Registrarse' : 'Iniciar Sesión' }}
          </button>
        </div>
        
        <p class="toggle-text" @click="isRegistering = !isRegistering">
          {{ isRegistering ? '¿Ya tienes cuenta? Inicia sesión' : '¿No tienes cuenta? Regístrate' }}
        </p>
      </form>

      <div class="divider"><span>Invitados</span></div>

      <button @click="loginAnonymous" class="btn btn-secondary">
        Ver Horarios (Sin cuenta)
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { 
  signInWithPopup, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signInAnonymously
} from 'firebase/auth';
import { auth, googleProvider } from '../firebase';
import { userState } from '../stateHelper';
import { userApi, clientsApi } from '../api';

const router = useRouter();
const email = ref('');
const password = ref('');
const error = ref('');
const isRegistering = ref(false);

const handleSuccess = async (user, destination = null) => {
  console.log("✅ Auth Firebase OK:", user.uid);
  
  try {
    let dbId = null;
    let isAdmin = false;

    if (!user.isAnonymous) {
      // Intentamos login en backend.
      // Solo enviamos teléfono si Firebase nos lo da garantizado (user.phoneNumber)
      // Si no, el backend buscará solo por UID.
      try {
        const loginPayload = {
            telefono: user.phoneNumber || null, 
            nombre: user.displayName || user.email
        };
        
        const backendResponse = await clientsApi.login(loginPayload);
        
        dbId = backendResponse.data.id;
        isAdmin = backendResponse.data.user?.admin || false;
        
        localStorage.setItem('dbId', dbId);
        console.log("🔗 Vinculación Backend OK. DB_ID:", dbId);

      } catch (err) {
        // Si el usuario es nuevo Y no tiene teléfono en Google, el backend dará 404.
        // En ese caso, hacemos fallback a un perfil básico (sin historial shadow).
        console.warn("⚠️ Backend login falló (Usuario nuevo sin teléfono vinculado):", err);
        try {
            // Intentamos obtener perfil si existiera, o continuamos sin dbId
             const profile = await userApi.getProfile();
             if (profile.data) isAdmin = profile.data.is_admin;
        } catch (e) { 
            console.log("Nuevo usuario detectado sin historial previo.");
        }
      }
    }

    userState.login(user, dbId);
    userState.isAdmin = isAdmin;

    if (destination) {
      router.push(destination);
    } else if (userState.isAdmin) {
      router.push('/admin');
    } else {
      router.push(user.isAnonymous ? '/horarios' : '/user');
    }

  } catch (err) {
    handleError(err);
  }
};

const handleError = (err) => {
  console.error("❌ Error Auth:", err);
  error.value = err.message || "Error desconocido";
};

const loginGoogle = async () => {
  error.value = '';
  try {
    const result = await signInWithPopup(auth, googleProvider);
    handleSuccess(result.user);
  } catch (err) { handleError(err); }
};

const handleEmailAuth = async () => {
  error.value = '';
  try {
    let result;
    if (isRegistering.value) {
      result = await createUserWithEmailAndPassword(auth, email.value, password.value);
    } else {
      result = await signInWithEmailAndPassword(auth, email.value, password.value);
    }
    handleSuccess(result.user);
  } catch (err) { handleError(err); }
};

const loginAnonymous = async () => {
  error.value = '';
  try {
    const result = await signInAnonymously(auth);
    handleSuccess(result.user, '/horarios'); 
  } catch (err) { handleError(err); }
};
</script>

<style scoped>
.login-container { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #f0f2f5; }
.card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; }
.login-header {color: #4897f7; }
.form-group { margin-bottom: 1rem; }
input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
.btn { width: 100%; padding: 10px; border: none; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-bottom: 0.5rem; transition: background 0.2s; }
.btn-primary { background: #007bff; color: white; }
.btn-primary:hover { background: #0056b3; }
.btn-secondary { background: #6c757d; color: white; }
.btn-secondary:hover { background: #545b62; }
.btn-google { background: white; color: #757575; border: 1px solid #ddd; display: flex; align-items: center; justify-content: center; gap: 10px; }
.btn-google:hover { background: #f8f9fa; }
.divider { display: flex; align-items: center; margin: 1.5rem 0; color: #777; font-size: 0.8rem; }
.divider::before, .divider::after { content: ""; flex: 1; border-bottom: 1px solid #ddd; }
.divider span { padding: 0 10px; }
.toggle-text { color: #007bff; cursor: pointer; font-size: 0.9rem; margin-top: 1rem; }
.toggle-text:hover { text-decoration: underline; }
.error { background: #ffebee; color: #c62828; padding: 10px; border-radius: 4px; margin-bottom: 1rem; font-size: 0.9rem; }
</style>