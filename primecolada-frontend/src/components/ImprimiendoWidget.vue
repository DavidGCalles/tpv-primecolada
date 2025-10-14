<template>
  <div class="imprimiendo-widget card">
    <h4 class="card-header">En Impresión</h4>
    <div class="card-body">
      <ul v-if="imprimiendoVentas.length" class="list-group list-group-flush">
        <li v-for="venta in imprimiendoVentas" :key="venta.id" class="list-group-item d-flex justify-content-between align-items-center">
          <span>{{ venta.nombre }} - Tel: {{ venta.telefono }}</span>
          <button @click="generateQrCode(venta.id)" class="btn btn-sm btn-primary">QR</button>
        </li>
      </ul>
      <p v-else class="text-muted">No hay ventas imprimiéndose.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { socket } from '../api';

const imprimiendoVentas = ref([]);

const emit = defineEmits(['generate-qr']);

const generateQrCode = (ventaId) => {
  emit('generate-qr', ventaId);
};

onMounted(() => {
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    imprimiendoVentas.value = data;
  };
});

onBeforeUnmount(() => {
  socket.onmessage = null;
});
</script>

<style scoped>
.imprimiendo-widget {
  max-height: 300px;
  overflow-y: auto;
}
.card-header {
  font-weight: bold;
}
</style>
