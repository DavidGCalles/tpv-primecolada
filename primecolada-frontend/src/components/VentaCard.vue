<template>
  <div class="card">
    <button class="icon-button delete-button" @click="$emit('delete', venta.id)" v-if="showActions">🗑️</button>
    <div class="card-header" @click="$emit('view-details', venta)">
      <h3>{{ venta.nombre }}</h3>
    </div>
    <div class="card-body">
      <p><strong>Teléfono:</strong> {{ venta.telefono }}</p>
      <p><strong>Estado:</strong> {{ getVentaStateName(editableVenta.estado_actual) }}</p>
      <p><strong>Lavadora:</strong> <input type="number" v-model.number="editableVenta.coste.lavadora" @change="updateVenta" />€</p>
      <p><strong>Secadora:</strong> <input type="number" v-model.number="editableVenta.coste.secadora" @change="updateVenta" />€</p>
      <p><strong>Total:</strong> {{ totalCoste }}€</p>
    </div>
    <div class="state-buttons">
      <button
        v-for="state in filteredStates"
        :key="state.value"
        @click="changeState(state.value)"
        :class="{ active: editableVenta.estado_actual === state.value }"
      >
        {{ state.name }}
      </button>
    </div>
    <div class="card-actions" v-if="showActions">
      <!-- "Generar QR" button removed -->
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { getVentaStateName, VentaState } from '../stateHelper';

const props = defineProps({
  venta: {
    type: Object,
    required: true
  },
  showActions: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['view-details', 'delete', 'update']);

const editableVenta = ref(JSON.parse(JSON.stringify(props.venta)));

const filteredStates = computed(() => {
  return Object.entries(VentaState)
    .map(([name, value]) => ({ name: getVentaStateName(value), value }))
    .filter(state => state.value !== VentaState.ERROR)
    .slice(-4);
});

watch(() => props.venta, (newVenta) => {
  editableVenta.value = JSON.parse(JSON.stringify(newVenta));
}, { deep: true });

const totalCoste = computed(() => {
  const lavadora = Number(editableVenta.value.coste.lavadora) || 0;
  const secadora = Number(editableVenta.value.coste.secadora) || 0;
  const total = lavadora + secadora;
  editableVenta.value.coste.total = total;
  return total;
});

const updateVenta = () => {
  emit('update', editableVenta.value);
};

const changeState = (newState) => {
  editableVenta.value.estado_actual = newState;
  updateVenta();
};
</script>

<style scoped>
.card {
  position: relative;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 1rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.card-header {
  cursor: pointer;
  margin-bottom: 0.5rem;
}

.card-header h3 {
  margin: 0;
  color: #fff;
}

.card-body p {
  margin: 0.5rem 0;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  align-items: center;
}

.card-title-input {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 1.5rem;
  font-weight: bold;
  width: 100%;
}

.card-body select, .card-body input {
  background: transparent;
  border: 1px solid #ccc;
  border-radius: 4px;
  color: #fff;
  padding: 0.25rem;
}

.icon-button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.5rem;
  padding: 0;
}

.delete-button {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  z-index: 10;
}

.state-buttons {
  display: flex;
  justify-content: space-around;
  margin-top: 1rem;
}

.state-buttons button {
  background-color: #555;
  border: none;
  border-radius: 5px;
  color: white;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  font-size: 0.75rem;
}

.state-buttons button.active {
  background-color: #007bff;
}
</style>
