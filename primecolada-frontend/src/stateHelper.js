import { reactive } from 'vue';

export const userState = reactive({
  user: null,
  isAdmin: false,
  login(userData) {
    this.user = userData;
    this.isAdmin = false;
  },
  logout() {
    this.user = null;
    this.isAdmin = false;
  }
});

export const VentaState = {
  ERROR: 0,
  IMPRIMIENDO: 1,
  EN_COLA: 2,
  LAVANDO: 3,
  PTE_RECOGIDA: 4,
  RECOGIDO: 5
};

export const getVentaStateName = (stateValue) => {
  const state = Object.keys(VentaState).find(key => VentaState[key] === stateValue);
  return state ? state.replace('_', ' ') : 'Desconocido';
};
