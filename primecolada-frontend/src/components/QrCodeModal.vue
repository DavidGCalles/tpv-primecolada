<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <h3 v-if="userName">QR para: {{ userName }}</h3>
      <canvas ref="canvas"></canvas>
      <p><a :href="url" target="_blank">Ver en el tracker</a></p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import QRCode from 'qrcode';

const props = defineProps({
  url: {
    type: String,
    required: true
  },
  userName: {
    type: String,
    default: ''
  }
});

const canvas = ref(null);

onMounted(() => {
  QRCode.toCanvas(canvas.value, props.url, (error) => {
    if (error) console.error(error);
  });
});
</script>
