<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <canvas ref="canvas"></canvas>
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
  }
});

const canvas = ref(null);

onMounted(() => {
  QRCode.toCanvas(canvas.value, props.url, (error) => {
    if (error) console.error(error);
  });
});
</script>
