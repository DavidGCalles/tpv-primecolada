<template>
  <div class="login-container">
    <h2>Login</h2>
    <form @submit.prevent="login">
      <div class="form-group">
        <label for="phone">Phone Number:</label>
        <input type="text" id="phone" v-model="phone" required />
      </div>
      <button type="submit">Login</button>
    </form>
    <p v-if="error" class="error-message">{{ error }}</p>
  </div>
</template>

<script>
import { clientsApi } from '../api';
import { userState } from '../stateHelper';

export default {
  data() {
    return {
      phone: '',
      error: null,
    };
  },
  methods: {
    async login() {
      this.error = null;
      try {
        const response = await clientsApi.login(this.phone);
        const { access_token, user } = response.data;
        localStorage.setItem('token', access_token);
        localStorage.setItem('user', JSON.stringify(user));
        userState.login(user);
        if (userState.isAdmin) {
          this.$router.push({ name: 'Ventas' }); // Redirect admin to Ventas view
        } else {
          this.$router.push({ name: 'UserView' }); // Redirect user to UserView
        }
      } catch (error) {
        this.error = 'Login failed. Please check your phone number.';
        console.error(error);
      }
    },
  },
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
.form-group {
  margin-bottom: 15px;
}
label {
  display: block;
  margin-bottom: 5px;
}
input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
button {
  width: 100%;
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.error-message {
  color: red;
  margin-top: 10px;
}
</style>
