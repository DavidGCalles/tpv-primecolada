<template>
  <div class="glass-container">
    <Navbar v-if="userState.user" />
    <router-view />
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue';
import { userState } from './stateHelper';
</script>
