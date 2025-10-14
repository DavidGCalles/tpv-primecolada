<template>
  <nav>
    <h1 class="title">Prime Colada</h1>
    <router-link to="/admin" v-if="userState.isAdmin">Admin</router-link>
    <button @click="logout">Logout</button>
  </nav>
</template>

<script setup>
import { userState } from '../stateHelper';
import { useRouter } from 'vue-router';

const router = useRouter();

const logout = () => {
  userState.logout();
  router.push('/login');
};
</script>
