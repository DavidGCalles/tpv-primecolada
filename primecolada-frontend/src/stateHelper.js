// src/stateHelper.js
import { reactive } from 'vue';

export const userState = reactive({
  user: null,
  isAdmin: false,
  dbId: null, // <--- NUEVO: ID interno de base de datos (Shadow ID)

  login(userData, dbId = null) { // <--- Aceptamos dbId
    this.user = userData;
    this.isAdmin = false;
    if (dbId) this.dbId = dbId;
  },
  logout() {
    this.user = null;
    this.isAdmin = false;
    this.dbId = null;
    localStorage.removeItem('dbId'); // Limpieza
  }
});

export const VentaState = {
  ERROR: 0,
  EN_COLA: 1,
  LAVANDO: 2,
  PTE_RECOGIDA: 3,
  RECOGIDO: 4
};

export const getVentaStateName = (stateValue) => {
  const state = Object.keys(VentaState).find(key => VentaState[key] === stateValue);
  return state ? state.replace('_', ' ') : 'Desconocido';
};