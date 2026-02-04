import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

import { CurrentTenantData } from '@/http/types/organizationFiles';
import { CurrentOrg } from '@/types/store';

export default defineStore('app', () => {
  const defaultOrg: CurrentOrg = {
    tenantId: '',
    deptId: 0,
    tenantName: '',
    deptName: '',
    organizationPath: '',
  };

  const currentTenant = ref<CurrentTenantData>({
    id: '',
    name: '',
    logo: '',
    data_sources: [],
  });
  /** 更新当前租户logo */
  const curTenantLogo = ref('');

  /**
   * 当前选中的（租户/协同租户/部门信息），其中租户可能为本租户/协同租户
   */
  const currentOrg = ref<CurrentOrg>({ ...defaultOrg });
  const isSearchTree = ref(false);

  const reloadIndex = ref(1);

  /** 更新当前租户logo */
  const updateCurrentTenantLogo = (logo: string) => {
    curTenantLogo.value = logo;
  };

  /** 更新当前租户name */
  const updateCurrentTenantName = (name: string) => {
    currentTenant.value.name = name;
  };

  /** 更新当前组织信息 */
  const updateCurrentOrg = (org: Partial<CurrentOrg>) => {
    // 使用默认值覆盖，若未传入deptId则默认为0，即代表当前选中的实际为顶部租户，deptId为0
    Object.assign(currentOrg.value, { ...defaultOrg, ...org });
  };

  /**
   * 是否配置了本地数据源
   * @description 数据源配置允许有一个本地数据源和一个外部数据源
   */
  const isConfiguredLocalSource = computed(() => currentTenant.value.data_sources?.some(item => item.type === 'local'));

  return {
    curTenantLogo,
    currentTenant,
    currentOrg,
    isSearchTree,
    reloadIndex,
    isConfiguredLocalSource,
    updateCurrentTenantLogo,
    updateCurrentTenantName,
    updateCurrentOrg,
  };
});
