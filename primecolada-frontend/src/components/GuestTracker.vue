<template>
  <div class="tracking-container" :class="statusColorClass">
    
    <div v-if="loading" class="center-content">
      <div class="pulse-loader">⌛</div>
      <p>Buscando tu colada...</p>
    </div>

    <div v-else-if="error" class="center-content error-mode">
      <div class="status-icon">😕</div>
      <p class="error-text">{{ error }}</p>
      <button @click="fetchStatus" class="action-btn retry-btn">Intentar de nuevo</button>
      <router-link to="/login" class="sub-link">¿Eres cliente registrado?</router-link>
    </div>

    <div v-else class="center-content">
      <div class="status-icon">{{ statusIcon }}</div>
      
      <h1 class="status-text">{{ statusText }}</h1>
      
      <div class="info-card">
        <p class="alias">Hola, <strong>{{ venta.alias }}</strong></p>
        <div class="divider"></div>
        <p class="cost">Total: <span class="price">{{ venta.coste.total }}€</span></p>
        <p class="updated">Actualizado: {{ lastUpdated }}</p>
      </div>

      <button @click="fetchStatus" class="action-btn refresh-btn">🔄 Actualizar Estado</button>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { ventasApi } from '../api';
import { VentaState } from '../stateHelper';

const route = useRoute();
const venta = ref(null);
const loading = ref(true);
const error = ref(null);

const fetchStatus = async () => {
  loading.value = true;
  error.value = null;
  const id = route.params.id;
  
  // Pequeño delay artificial (300ms) para que el usuario sienta que "pasa algo" al refrescar
  await new Promise(r => setTimeout(r, 300));

  try {
    const response = await ventasApi.getPublicStatus(id);
    venta.value = response.data;
  } catch (err) {
    console.error(err);
    if (err.response && err.response.status === 404) {
      error.value = "No encontramos este ticket. Comprueba el enlace o pregunta al personal.";
    } else {
      error.value = "Error de conexión. Comprueba tu internet.";
    }
  } finally {
    loading.value = false;
  }
};

const statusColorClass = computed(() => {
  if (!venta.value) return 'bg-gray';
  const s = venta.value.estado_actual;
  
  if (s === VentaState.EN_COLA) return 'bg-red';
  if (s === VentaState.LAVANDO) return 'bg-yellow';
  if (s === VentaState.PTE_RECOGIDA) return 'bg-green';
  if (s === VentaState.RECOGIDO) return 'bg-blue';
  return 'bg-gray';
});

const statusText = computed(() => {
  if (!venta.value) return '';
  const s = venta.value.estado_actual;
  
  if (s === VentaState.EN_COLA) return 'EN COLA';
  if (s === VentaState.LAVANDO) return 'LAVANDO';
  if (s === VentaState.PTE_RECOGIDA) return 'LISTO';
  if (s === VentaState.RECOGIDO) return 'ENTREGADO';
  return 'DESCONOCIDO';
});

const statusIcon = computed(() => {
  if (!venta.value) return '';
  const s = venta.value.estado_actual;
  
  if (s === VentaState.EN_COLA) return '🛑';     // Stop
  if (s === VentaState.LAVANDO) return '🧼';     // Jabón/Lavado
  if (s === VentaState.PTE_RECOGIDA) return '✅'; // Check verde
  if (s === VentaState.RECOGIDO) return '👋';     // Adiós
  return '❓';
});

const lastUpdated = computed(() => {
  if (!venta.value || !venta.value.updated_at) return 'Ahora mismo';
  const d = new Date(venta.value.updated_at);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
});

onMounted(() => {
  fetchStatus();
});
</script>

<style scoped>
.tracking-container {
  border-radius: 15px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  text-align: center;
  transition: background 0.5s ease;
  padding: 20px;
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
}

/* Semáforo Visual */
.bg-red { background: linear-gradient(135deg, #ff5f6d 0%, #ffc371 100%); } /* Naranja rojizo */
.bg-yellow { background: linear-gradient(135deg, #fce38a 0%, #f38181 100%); color: #4a4a4a !important; }
.bg-green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
.bg-blue { background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%); }
.bg-gray { background: #2c3e50; }

/* Ajustes específicos para fondo claro (Amarillo) */
.bg-yellow .status-text, .bg-yellow p, .bg-yellow .status-icon { color: #333; text-shadow: none; }
.bg-yellow .info-card { background: rgba(255,255,255,0.6); border-color: rgba(0,0,0,0.1); color: #333; }
.bg-yellow .divider { background: rgba(0,0,0,0.1); }

.center-content {
  width: 100%;
  max-width: 380px;
  animation: popIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.status-icon { font-size: 6rem; margin-bottom: 0.5rem; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.2)); }
.status-text { font-size: 3.5rem; font-weight: 900; margin: 0 0 1.5rem 0; line-height: 1; letter-spacing: -1px; text-transform: uppercase; }

.info-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 1.5rem;
  border-radius: 20px;
  margin-bottom: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
}

.alias { font-size: 1.2rem; margin: 0; }
.cost { font-size: 1.1rem; margin: 10px 0; }
.price { font-weight: 900; font-size: 1.4rem; }
.updated { font-size: 0.8rem; opacity: 0.8; margin-top: 10px; font-style: italic; }

.divider { height: 1px; background: rgba(255,255,255,0.3); margin: 10px 0; }

.action-btn {
  background: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 50px;
  font-size: 1.1rem;
  font-weight: 700;
  color: #333;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  transition: transform 0.1s;
  width: 100%;
}
.action-btn:active { transform: scale(0.96); }

.error-text { font-size: 1.2rem; margin-bottom: 2rem; line-height: 1.4; }
.sub-link { display: block; margin-top: 20px; color: rgba(255,255,255,0.8); text-decoration: underline; }

@keyframes popIn {
  from { opacity: 0; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1); }
}
</style>