<template>
  <div class="user-view-container">
    <h2>Bienvenido, {{ userState.user.displayName || userState.user.email || 'Usuario' }}</h2>
    
    <div class="user-info-card">
      <p><strong>Email:</strong> {{ userState.user.email }}</p>
      <p><strong>ID de Usuario (UID):</strong> <small>{{ userState.user.uid }}</small></p>
      <p v-if="userState.user.phoneNumber"><strong>Teléfono:</strong> {{ userState.user.phoneNumber }}</p>
    </div>

    <h3>Tus pedidos:</h3>
    <div v-if="loading">Cargando pedidos...</div>
    <div v-if="error" class="error-msg">{{ error }}</div>
    
    <div v-if="ventas.length" class="ventas-grid">
      <UserVentaCard v-for="venta in ventas" :key="venta.id" :venta="venta" />
    </div>
    <div v-else-if="!loading">
      <p>No tienes pedidos registrados.</p>
    </div>
  </div>
</template>

<script>
import { userState } from '../stateHelper';
import { ventasApi } from '../api';
import UserVentaCard from './UserVentaCard.vue';

export default {
  components: {
    UserVentaCard,
  },
  data() {
    return {
      userState,
      ventas: [],
      loading: false,
      error: null,
    };
  },
  created() {
    this.fetchVentas();
  },
  methods: {
    async fetchVentas() {
      if (!this.userState.user) return;

      this.loading = true;
      try {
        // CAMBIO CRÍTICO: Usamos dbId si existe (usuario reclamado), si no, fallback a UID
        const queryId = this.userState.dbId || this.userState.user.uid;
        
        console.log("Solicitando ventas para Client ID:", queryId);
        const response = await ventasApi.getAll(queryId);
        this.ventas = response.data;
      } catch (err) {
        this.error = 'Error al cargar tus pedidos.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.user-view-container {
  padding: 20px;
  color: #fff;
}
.user-info-card {
  background: rgba(255, 255, 255, 0.1);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
.ventas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}
.error-msg {
  color: #ff6b6b;
  font-weight: bold;
}
</style>