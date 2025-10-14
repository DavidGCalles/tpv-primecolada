<template>
  <div class="summary-card">
    <div class="summary-header" @click="toggleExpand">
      <span>Resumen de Ventas</span>
      <span class="toggle-icon">{{ isExpanded ? '▲' : '▼' }}</span>
    </div>
    <div v-show="isExpanded" class="summary-body">
      <div
        v-for="(count, state) in statusCounts"
        :key="state"
        class="status-item"
        @click="$emit('filter', state)"
      >
        <span class="status-name">{{ state }}</span>
        <span class="status-count">{{ count }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { getVentaStateName } from '../stateHelper';

defineProps({
  statusCounts: {
    type: Object,
    required: true
  }
});

const isExpanded = ref(true);

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value;
};

</script>

<style scoped>
.summary-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  margin-bottom: 1.5rem;
  overflow: hidden;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.15);
  font-weight: 600;
  color: #fff;
  transition: background-color 0.2s ease-in-out;
}

.summary-header:hover {
  background: rgba(255, 255, 255, 0.25);
}

.toggle-icon {
  font-size: 0.8em;
  color: #fff;
}

.summary-body {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 16px;
}

.status-item {
  background-color: rgba(255, 255, 255, 0.1);
  padding: 8px 12px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.status-item:hover {
  transform: translateY(-2px);
  background-color: rgba(255, 255, 255, 0.2);
}

.status-name {
  font-weight: 500;
  font-size: 0.9rem;
  color: #fff;
}

.status-count {
  background-color: #3b82f6;
  color: white;
  border-radius: 9999px; /* Use a large radius for a pill shape */
  padding: 4px 10px;     /* Adjust padding for better proportions */
  font-size: 0.85rem;
  font-weight: bold;
  text-align: center;
  line-height: 1;        /* Improve vertical alignment */
}

@media (max-width: 768px) {
  .summary-body {
    flex-direction: column;
    align-items: stretch;
  }
  .status-item {
    justify-content: space-between;
  }
}
</style>
