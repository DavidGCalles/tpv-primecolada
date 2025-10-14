<template>
  <div class="user-view-container">
    <h2>Welcome, {{ userState.user.nombre }}</h2>
    <p>Phone: {{ userState.user.telefono }}</p>
    <h3>Your Ventas:</h3>
    <!-- Ventas list will be implemented here -->
  </div>
</template>

<script>
import { userState } from '../stateHelper';

export default {
  data() {
    return {
      userState,
    };
  },
};
</script>

<style scoped>
.user-view-container {
  padding: 20px;
}
</style>
