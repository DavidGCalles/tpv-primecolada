<template>
  <div class="user-view-container">
    <h2>Bienvenido, {{ userState.user.nombre }}</h2>
    <p>Telefono: {{ userState.user.telefono }}</p>
    <h3>Tus pedidos:</h3>
    <div v-if="loading">Loading...</div>
    <div v-if="error">{{ error }}</div>
    <div v-if="ventas.length" class="ventas-grid">
      <UserVentaCard v-for="venta in ventas" :key="venta.id" :venta="venta" />
    </div>
    <div v-else>
      <p>No ventas found.</p>
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
      this.loading = true;
      try {
        const response = await ventasApi.getAll(this.userState.user.telefono);
        this.ventas = response.data;
      } catch (err) {
        this.error = 'Failed to load ventas.';
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
}
.ventas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}
</style>
