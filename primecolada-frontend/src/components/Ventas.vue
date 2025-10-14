<template>
  <div>
    <div class="container mt-4">
      <div class="row mb-4">
        <div class="col-md-8">
          <StatusSummary :status-counts="statusCounts" @filter="filterByStatus" />
        </div>
        <div class="col-md-4">
          <ImprimiendoWidget @generate-qr="generateQrCode" />
        </div>
      </div>
      
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h1>Gestión de Ventas</h1>
        <div>
          <input type="text" v-model="searchQuery" placeholder="Buscar ventas..." class="search-input">
          <button @click="openCreateModal" class="btn btn-primary">➕ Nueva Venta</button>
        </div>
      </div>
      
      <!-- Sales cards -->
      <div class="cards-container">
        <VentaCard
          v-for="venta in filteredVentas"
          :key="venta.id"
          :venta="venta"
          @view-details="openDetailModal"
          @update="updateVenta"
          @delete="deleteVenta"
        />
      </div>
      
      <VentaModal v-if="showVentaModal" :venta="currentVenta" @close="showVentaModal = false" @save="saveVenta" />
      <QrCodeModal v-if="showQrModal" :url="qrCodeUrl" @close="showQrModal = false" />
      <VentaDetailModal v-if="showDetailModal" :venta="currentVenta" @close="showDetailModal = false" />

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { ventasApi } from '../api';
import QrCodeModal from './QrCodeModal.vue';
import VentaModal from './VentaModal.vue';
import VentaDetailModal from './VentaDetailModal.vue';
import StatusSummary from './StatusSummary.vue';
import VentaCard from './VentaCard.vue';
import ImprimiendoWidget from './ImprimiendoWidget.vue';
import { getVentaStateName, VentaState } from '../stateHelper';

const allVentas = ref([]);
const searchQuery = ref('');
const currentVenta = ref(null);
const showVentaModal = ref(false);
const showQrModal = ref(false);
const showDetailModal = ref(false);
const qrCodeUrl = ref('');
const selectedStatus = ref(null);

const statusCounts = computed(() => {
  // Initialize counts for all states to 0, preserving order
  const counts = {};
  for (const stateKey in VentaState) {
    const stateName = getVentaStateName(VentaState[stateKey]);
    counts[stateName] = 0;
  }

  // Calculate counts from actual sales data
  allVentas.value.forEach(venta => {
    const stateName = getVentaStateName(venta.estado_actual);
    if (counts.hasOwnProperty(stateName)) {
      counts[stateName]++;
    }
  });

  return counts;
});

const filteredVentas = computed(() => {
  let ventas = allVentas.value;

  if (selectedStatus.value !== null) {
    ventas = ventas.filter(venta => venta.estado_actual === selectedStatus.value);
  }

  if (!searchQuery.value) {
    return ventas;
  }

  return ventas.filter(venta =>
    venta.nombre.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    venta.telefono.toString().includes(searchQuery.value)
  );
});

const filterByStatus = (statusName) => {
  const stateValue = Object.keys(VentaState).find(key => key.replace('_', ' ') === statusName);
  if (stateValue) {
    selectedStatus.value = VentaState[stateValue];
  } else {
    selectedStatus.value = null; // Or handle as a "clear filter" action
  }
};

const openCreateModal = () => {
  currentVenta.value = null;
  showVentaModal.value = true;
};

const openDetailModal = (venta) => {
  currentVenta.value = venta;
  showDetailModal.value = true;
};

const generateQrCode = (ventaId) => {
  if (typeof window !== 'undefined') {
    const url = `${window.location.origin}/venta/${ventaId}`;
    qrCodeUrl.value = url;
    showQrModal.value = true;
  }
};

const fetchVentas = async () => {
  console.log('Attempting to fetch ventas...');
  try {
    const response = await ventasApi.getAll();
    console.log('Ventas fetched successfully:', response.data);
    allVentas.value = response.data;
  } catch (error) {
    console.error('Error fetching ventas:', error);
  }
};

const saveVenta = async (venta) => {
  try {
    if (venta.id) {
      // Update
      await ventasApi.update(venta.id, venta);
    } else {
      // Create
      await ventasApi.create(venta);
    }
    showVentaModal.value = false;
    await fetchVentas();
  } catch (error) {
    console.error(error);
  }
};

const updateVenta = async (venta) => {
  try {
    await ventasApi.update(venta.id, venta);
    await fetchVentas();
  } catch (error) {
    console.error('Error updating venta:', error);
  }
};

const deleteVenta = async (id) => {
  if (window.confirm('¿Estás seguro de que quieres eliminar esta venta?')) {
    try {
      await ventasApi.delete(id);
      await fetchVentas();
    } catch (error) {
      console.error(error);
    }
  }
};

onMounted(() => {
  console.log('Ventas component mounted. Calling fetchVentas.');
  fetchVentas();
});

</script>

<style scoped>
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.search-input {
  margin: 0 1rem;
  flex-grow: 1;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

@media (max-width: 768px) {
  .header-container {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    margin: 0.5rem 0;
  }
}
</style>
