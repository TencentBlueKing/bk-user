import { defineStore } from 'pinia';
import { ref } from 'vue';


export default defineStore('app', () => {
  const currentTenant = ref({});

  const currentOrg = ref({});

  const isSearchTree = ref(false);

  const reloadIndex = ref(1);

  /** 更新当前租户logo */
  const updateCurrentTenantLogo = (logo: string) => {
    currentTenant.value = {
      ...currentTenant.value,
      logo,
    };
  };

  /** 更新当前租户name */
  const updateCurrentTenantName = (name: string) => {
    currentTenant.value = {
      ...currentTenant.value,
      name,
    };
  };

  return {
    currentTenant,
    currentOrg,
    isSearchTree,
    reloadIndex,
    updateCurrentTenantLogo,
    updateCurrentTenantName,
  };
});
