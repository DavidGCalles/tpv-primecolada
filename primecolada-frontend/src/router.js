import { createRouter, createWebHistory } from 'vue-router';
import Ventas from './components/Ventas.vue';
import Login from './components/Login.vue';
import UserView from './components/UserView.vue';
import { userState } from './stateHelper';

const routes = [
  {
    path: '/horarios',
    name: 'Horarios',
    component: UserView
  }
  ,{
    path: '/admin',
    name: 'Ventas',
    component: Ventas,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/user',
    name: 'UserView',
    component: UserView,
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    redirect: '/login',
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  if (to.name === 'Login' && userState.user) {
    if (userState.isAdmin) {
      return next({ name: 'Ventas' });
    } else {
      return next({ name: 'UserView' });
    }
  }

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!userState.user) {
      next({ name: 'Login' });
    } else {
      if (to.matched.some(record => record.meta.requiresAdmin)) {
        if (userState.isAdmin) {
          next();
        } else {
          next({ name: 'UserView' }); // Or a dedicated 'unauthorized' page
        }
      } else {
        next();
      }
    }
  } else {
    next();
  }
});

export default router;
