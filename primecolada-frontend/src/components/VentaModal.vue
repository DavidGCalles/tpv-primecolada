<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <h2>{{ venta ? 'Editar Venta' : 'Crear Venta' }}</h2>
      <form @submit.prevent="save">
        <input type="text" v-model="editableVenta.nombre" placeholder="Nombre" required>
        <input type="number" v-model="editableVenta.telefono" placeholder="Teléfono" required>
        
        <label for="lavadora">Lavadora (€)</label>
        <input type="number" id="lavadora" v-model.number="editableVenta.coste.lavadora" step="0.5" min="0">
        
        <label for="secadora">Secadora (€)</label>
        <input type="number" id="secadora" v-model.number="editableVenta.coste.secadora" step="0.5" min="0">

        <label for="total">Total (€)</label>
        <input type="number" id="total" v-model.number="editableVenta.coste.total" step="0.5" min="0" required>

        <select v-model="editableVenta.estado_actual">
          <option v-for="(stateValue, stateName) in displayedStates" :key="stateValue" :value="stateValue">
            {{ stateName.replace('_', ' ') }}
          </option>
        </select>
        <button type="submit">Guardar</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, watchEffect, computed } from 'vue';
import { VentaState } from '../stateHelper';

const props = defineProps({
  venta: Object
});

const emit = defineEmits(['close', 'save']);

const displayedStates = computed(() => {
  if (props.venta) {
    return VentaState;
  }
  const { ERROR, IMPRIMIENDO, ...filteredStates } = VentaState;
  return filteredStates;
});

const editableVenta = ref({
  nombre: '',
  telefono: '',
  estado_actual: VentaState.EN_COLA,
  coste: {
    lavadora: 0,
    secadora: 0,
    total: 0
  }
});

watchEffect(() => {
  if (props.venta) {
    editableVenta.value = JSON.parse(JSON.stringify(props.venta));
    if (!editableVenta.value.coste) {
      editableVenta.value.coste = { lavadora: 0, secadora: 0, total: 0 };
    }
  } else {
    editableVenta.value = {
      nombre: '',
      telefono: '',
      estado_actual: VentaState.EN_COLA,
      coste: {
        lavadora: 0,
        secadora: 0,
        total: 0
      }
    };
  }
});

watch(() => [editableVenta.value.coste.lavadora, editableVenta.value.coste.secadora], () => {
  editableVenta.value.coste.total = (editableVenta.value.coste.lavadora || 0) + (editableVenta.value.coste.secadora || 0);
});

const save = () => {
  const ventaToSave = {
    ...editableVenta.value,
    estado_actual: parseInt(editableVenta.value.estado_actual, 10)
  };
  emit('save', ventaToSave);
};
</script>
