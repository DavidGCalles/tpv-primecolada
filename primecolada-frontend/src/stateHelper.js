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
  EN_COLA: 1,
  LAVANDO: 2,
  PTE_RECOGIDA: 3,
  RECOGIDO: 4
};

export const getVentaStateName = (stateValue) => {
  const state = Object.keys(VentaState).find(key => VentaState[key] === stateValue);
  return state ? state.replace('_', ' ') : 'Desconocido';
};
