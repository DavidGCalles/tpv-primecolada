<template>
  <div class="user-view-container">
    <h2>Bienvenido, {{ userState.user.displayName || userState.user.email || 'Usuario' }}</h2>
    
    <div class="user-info-card">
      <p><strong>Email:</strong> {{ userState.user.email }}</p>
      <p v-if="userState.user.phoneNumber"><strong>Teléfono:</strong> {{ userState.user.phoneNumber }}</p>
      <p v-else-if="userData?.telefono"><strong>Teléfono (Vinculado):</strong> {{ userData.telefono }}</p>
    </div>

    <h3>Tus pedidos:</h3>
    
    <div v-if="loading">Cargando pedidos...</div>
    
    <div v-if="error" class="error-msg">{{ error }}</div>
    
    <div v-if="ventas.length" class="ventas-grid">
      <UserVentaCard v-for="venta in ventas" :key="venta.id" :venta="venta" />
    </div>

    <div v-else-if="!loading" class="empty-state">
      <p>No tienes pedidos registrados.</p>
      
      <button 
        v-if="!showClaimForm" 
        class="btn-text-link" 
        @click="showClaimForm = true"
      >
        📥 ¿Hiciste un pedido en tienda física? Recupéralo aquí
      </button>
    </div>

    <div v-if="showClaimForm && ventas.length === 0" class="claim-section">
      <div class="claim-header">
        <h3>Vincular Historial</h3>
        <button class="close-btn" @click="showClaimForm = false">✕</button>
      </div>
      <p>Introduce el teléfono que usaste en la tienda:</p>
      
      <div class="claim-form">
        <input 
          v-model="phoneToClaim" 
          type="tel" 
          placeholder="Ej: 666111222" 
          :disabled="claiming" 
          @keyup.enter="claimHistory"
        />
        <button @click="claimHistory" :disabled="claiming || !phoneToClaim">
          {{ claiming ? '⌛' : 'Recuperar' }}
        </button>
      </div>
      <p v-if="claimError" class="error-msg small">{{ claimError }}</p>
    </div>

  </div>
</template>

<script>
import { ref } from 'vue';
import { userState } from '../stateHelper';
import { ventasApi, clientsApi, userApi } from '../api';
import UserVentaCard from './UserVentaCard.vue';

export default {
  components: {
    UserVentaCard,
  },
  data() {
    return {
      userState,
      userData: {}, 
      ventas: [],
      loading: false,
      error: null,
      
      // Claiming Logic
      showClaimForm: false, // <--- NUEVO ESTADO DE VISIBILIDAD
      phoneToClaim: '',
      claiming: false,
      claimError: ''
    };
  },
  async created() {
    await this.fetchProfile();
    await this.fetchVentas();
  },
  methods: {
    async fetchProfile() {
      try {
        // Aquí podrías cargar datos extra si el endpoint lo soportara
      } catch (e) { console.error(e); }
    },
    async fetchVentas() {
      if (!this.userState.user) return;
      this.loading = true;
      try {
        const queryId = this.userState.dbId || this.userState.user.uid;
        const response = await ventasApi.getAll(queryId);
        this.ventas = response.data;
        
        // Si encontramos ventas, ocultamos el formulario automáticamente
        if (this.ventas.length > 0) {
            this.showClaimForm = false;
        }
      } catch (err) {
        this.error = 'Error al cargar tus pedidos.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    async claimHistory() {
      if (!this.phoneToClaim) return;
      this.claiming = true;
      this.claimError = '';
      
      try {
        const payload = {
          telefono: this.phoneToClaim,
          nombre: this.userState.user.displayName || this.userState.user.email
        };
        
        const response = await clientsApi.login(payload);
        
        const newDbId = response.data.id;
        userState.login(this.userState.user, newDbId);
        localStorage.setItem('dbId', newDbId);
        
        this.phoneToClaim = '';
        this.ventas = [];
        await this.fetchVentas(); 
        // fetchVentas cerrará el formulario si encuentra algo
        
      } catch (err) {
        console.error("Error claiming history:", err);
        this.claimError = "No se pudo encontrar historial para este número.";
      } finally {
        this.claiming = false;
      }
    }
  },
};
</script>

<style scoped>
.user-view-container { padding: 20px; color: #fff; max-width: 800px; margin: 0 auto; }
.user-info-card { background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid rgba(255, 255, 255, 0.2); }
.ventas-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.error-msg { color: #ff6b6b; font-weight: bold; }
.small { font-size: 0.8rem; margin-top: 5px; }

/* Empty State & Toggle */
.empty-state {
    text-align: center;
    margin-top: 40px;
    color: rgba(255, 255, 255, 0.7);
}
.btn-text-link {
    background: none;
    border: none;
    color: #00d2ff;
    text-decoration: underline;
    cursor: pointer;
    font-size: 0.9rem;
    margin-top: 10px;
    padding: 5px;
}
.btn-text-link:hover { color: #fff; }

/* Claim Section Styles */
.claim-section {
  background: rgba(0, 210, 255, 0.1);
  border: 1px solid rgba(0, 210, 255, 0.3);
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
  animation: fadeIn 0.3s ease-out;
}
.claim-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}
.claim-header h3 { margin: 0; font-size: 1.1rem; color: #00d2ff; }
.close-btn {
    background: none; border: none; color: #fff; font-size: 1.2rem; cursor: pointer; opacity: 0.7;
}
.close-btn:hover { opacity: 1; }

.claim-form { display: flex; gap: 10px; margin-top: 10px; }
.claim-form input { flex: 1; padding: 10px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.3); background: rgba(0,0,0,0.2); color: white; }
.claim-form button { background: #00d2ff; border: none; padding: 0 20px; border-radius: 4px; color: #004e66; font-weight: bold; cursor: pointer; }
.claim-form button:disabled { opacity: 0.6; cursor: not-allowed; }

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>