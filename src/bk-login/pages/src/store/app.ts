import { defineStore } from 'pinia';
import { ref } from 'vue';

export default defineStore('app', () => {
  const tenantId = ref('');
  const manageIdpId = ref('');

  return {
    tenantId,
    manageIdpId,
  };
});
