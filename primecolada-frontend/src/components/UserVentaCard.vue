<template>
  <div class="card">
    <div class="card-header">
      <h3>{{ new Date(venta.created_at).toLocaleDateString()}}</h3>
    </div>
    <div class="card-body">
      <p><strong>Estado:</strong> {{ getVentaStateName(venta.estado_actual) }}</p>
      <p><strong>Total:</strong> {{ venta.coste.total }}€</p>
    </div>
  </div>
</template>

<script setup>
import { getVentaStateName } from '../stateHelper';

const props = defineProps({
  venta: {
    type: Object,
    required: true
  }
});
</script>

<style scoped>
.card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 1rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
}

.card-header h3 {
  margin: 0;
  color: #fff;
}

.card-body p {
  margin: 0.5rem 0;
}
</style>
