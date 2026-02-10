import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

import { getCollaboration, getCurrentTenant } from '@/http/organizationFiles';
import { CollaborationItemData, CurrentTenantData } from '@/http/types/organizationFiles';
import { IOrg } from '@/types/organization';
import { SelectedOrg } from '@/types/store';

/**
 * @description 原appStore 改为 organizationStore 因为该store只用于组织架构相关
 */
export default defineStore('organization', () => {
  const defaultOrg: SelectedOrg = {
    tenantId: '',
    deptId: 0,
    tenantName: '',
    deptName: '',
    dataSourceId: undefined,
    tenantLogo: '',
    organizationPath: '',
  };

  /**
   * 本租户信息 - 此账号的租户信息（不与协同租户信息混用）
   */
  const currentTenant = ref<CurrentTenantData>({
    id: '',
    name: '',
    logo: '',
    data_sources: [],
  });

  /**
   * 当前在组织架构 - 侧栏选中的（租户/协同租户/部门信息），其中租户可能为本租户或协同租户
   * @description 原currentOrg 改为 selectedOrg 更有选中的含义
   */
  const selectedOrg = ref<SelectedOrg>({ ...defaultOrg });

  /** 协同租户信息列表 */
  const collaborationList = ref<CollaborationItemData[]>([]);

  const isSearchTree = ref(false);
  const reloadIndex = ref(1);

  /**
   * 是否配置了本地数据源
   * @description 数据源配置允许有一个本地数据源和一个外部数据源
   */
  const isConfiguredLocalSource = computed(() => currentTenant.value.data_sources?.some(item => item.plugin_id === 'local'));

  /**
   * 当前选中的数据源
   */
  const curSelectedDataSource = computed(() => {
    if (selectedOrg.value.dataSourceId) {
      return currentTenant.value.data_sources?.find(item => item.id === selectedOrg.value.dataSourceId);
    }
    return null;
  });
  /**
   * 本地数据源ID
   */
  const localSourceId = computed(() => currentTenant.value.data_sources?.find(item => item.plugin_id === 'local')?.id);

  /**
   * LDAP数据源ID
   */
  const ldapSourceId = computed(() => currentTenant.value.data_sources?.find(item => item.plugin_id === 'ldap')?.id);

  /**
   * 是否选中了协同租户
   * @description 当选中的租户不为本租户，代表选中了协同租户
   */
  const curSelectedTenant = computed(() => {
    if (selectedOrg.value.tenantId !== currentTenant.value.id) {
      return 'collaboration';
    }
    return 'current';
  });

  /**
   * 当前选中的类型
   * @description tenant: 租户，department: 部门
   */
  const curSelectedType = computed(() => {
    if (selectedOrg.value.deptId === 0) {
      return 'tenant';
    }
    return 'department';
  });

  /** 更新当前组织信息 */
  const updateSelectedOrg = (org: SelectedOrg) => {
    // 使用默认值覆盖，若未传入deptId则默认为0，即代表当前选中的实际为顶部租户，deptId为0
    Object.assign(selectedOrg.value, { ...defaultOrg, ...org });
  };

  /** 获取当前租户信息 */
  const handleFetchCurrentTenant = async () => {
    const res = await getCurrentTenant();
    currentTenant.value = res?.data;
  };

  /** 获取协同租户列表 */
  const handleFetchCollaborationList = async () => {
    const res = await getCollaboration();
    collaborationList.value = res?.data;
  };

  /**
   * 获取当前选中的租户logo
   * @param tenantId 租户ID
   * @param deptId 部门ID，默认为当前选中的部门ID
   * @description 通过传参判断是否为协同租户，避免依赖 isSelectedCollaboration 的时序问题
   */
  const getTenantLogo = (tenantId: string) => {
    // 判断是否为协同租户：租户ID不是本租户 且 部门ID为0（即选中的是租户根节点）
    const isCollaboration = tenantId !== currentTenant.value.id;

    if (isCollaboration) {
      return collaborationList.value.find(item => item.id === tenantId)?.logo || '';
    }
    return currentTenant.value.logo;
  };

  /** 本租户是否配置了该插件数据源 */
  // eslint-disable-next-line max-len
  const hasPluginDataSource = (pluginId: string) => currentTenant.value.data_sources?.some(item => item.plugin_id === pluginId);

  /** 与本地数据源ID是否一致 */
  const isEqualLocalSourceId = (dataSourceId: IOrg['data_source_id']) => dataSourceId === localSourceId.value;

  /** 获取数据源信息 */
  const getDataSourceInfo = (dataSourceId: IOrg['data_source_id']) => currentTenant.value.data_sources?.find(item => item.id === dataSourceId);

  return {
    collaborationList,
    currentTenant,
    curSelectedTenant,
    curSelectedType,
    curSelectedDataSource,
    isConfiguredLocalSource,
    isSearchTree,
    localSourceId,
    ldapSourceId,
    reloadIndex,
    selectedOrg,
    getDataSourceInfo,
    getTenantLogo,
    handleFetchCollaborationList,
    handleFetchCurrentTenant,
    hasPluginDataSource,
    isEqualLocalSourceId,
    updateSelectedOrg,
  };
});
