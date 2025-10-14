<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <h2>Detalle de Venta</h2>
      <div v-if="venta">
        <p><strong>Nombre:</strong> {{ venta.nombre }}</p>
        <p><strong>Teléfono:</strong> {{ venta.telefono }}</p>
        <p><strong>Estado:</strong> {{ getVentaStateName(venta.estado_actual) }}</p>
        <p v-if="venta.coste && venta.coste.lavadora > 0"><strong>Lavadora:</strong> {{ venta.coste.lavadora }}€</p>
        <p v-if="venta.coste && venta.coste.secadora > 0"><strong>Secadora:</strong> {{ venta.coste.secadora }}€</p>
        <p v-if="venta.coste && venta.coste.total > 0"><strong>Total:</strong> {{ venta.coste.total }}€</p>
      </div>
      <div v-else>
        <p>Cargando...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { getVentaStateName } from '../stateHelper';

defineProps({
  venta: Object
});
</script>
