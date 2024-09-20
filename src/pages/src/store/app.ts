import { defineStore } from 'pinia';
import { ref } from 'vue';


export default defineStore('app', () => {
  const currentTenant = ref({});

  const currentOrg = ref({});

  const isSearchTree = ref(false);

  const reloadIndex = ref(1);

  return {
    currentTenant,
    currentOrg,
    isSearchTree,
    reloadIndex,
  };
});
