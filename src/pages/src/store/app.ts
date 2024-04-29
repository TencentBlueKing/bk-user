import { defineStore } from 'pinia';
import { ref } from 'vue';


export default defineStore('app', () => {
  const currentOrg = ref({});

  const isSearchTree = ref(false);

  return {
    currentOrg,
    isSearchTree,
  };
});
