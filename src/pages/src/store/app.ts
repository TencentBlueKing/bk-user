import { defineStore } from 'pinia';
import { computed, ref } from 'vue';


export default defineStore('app', () => {
  const currentOrg = ref({});

  return {
    currentOrg,
  };
});
