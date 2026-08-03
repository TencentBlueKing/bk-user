import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

import { getDataSourcePlugins } from '@/http/dataSourceFiles';
import { getCollaboration, getCurrentTenant } from '@/http/organizationFiles';
import { DataSourcePluginsItemData } from '@/http/types/dataSourceFiles';
import { CollaborationItemData, CurrentTenantData } from '@/http/types/organizationFiles';
import { IOrg } from '@/types/organization';
import { SelectedOrg } from '@/types/store';

/** 富化后的数据源实例（含前端拼接字段） */
type EnrichedDataSourceItem = CurrentTenantData['data_sources'][number] & {
  name: string;
  logo?: string;
  description?: string;
};

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
  const currentTenant = ref<Omit<CurrentTenantData, 'data_sources'> & { data_sources: EnrichedDataSourceItem[] }>({
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
    if (selectedOrg.value.dataSourceId !== undefined) {
      return currentTenant.value.data_sources?.find(item => item.id === selectedOrg.value.dataSourceId);
    }
    return null;
  });
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
   * @description tenant: 租户，source: 数据源，department: 部门
   */
  const curSelectedType = computed(() => {
    if (selectedOrg.value.nodeType) {
      return selectedOrg.value.nodeType;
    }
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

  const enrichDataSources = (
    sources: (CurrentTenantData['data_sources'][number] & {
      name?: string;
      logo?: string;
      description?: string;
    })[],
    plugins: DataSourcePluginsItemData[],
  ): EnrichedDataSourceItem[] => {
    const pluginMap = new Map(plugins.map(plugin => [plugin.id, plugin]));
    return sources.map((source) => {
      const plugin = pluginMap.get(source.plugin_id);
      return {
        ...source,
        name: source.name,
        logo: plugin?.logo || '',
        description: plugin?.description || '',
      };
    });
  };

  /** 获取当前租户信息 */
  const handleFetchCurrentTenant = async () => {
    try {
      const [tenantResult, pluginResult] = await Promise.allSettled([
        getCurrentTenant(),
        getDataSourcePlugins(),
      ]);

      const tenant = tenantResult.status === 'fulfilled' ? tenantResult.value?.data : undefined;
      if (!tenant) {
        throw tenantResult.status === 'rejected' ? tenantResult.reason : new TypeError('Invalid current tenant response');
      }

      const plugins = pluginResult.status === 'fulfilled' && Array.isArray(pluginResult.value?.data)
        ? pluginResult.value.data
        : [];

      currentTenant.value = {
        ...tenant,
        logo: typeof tenant.logo === 'string' ? tenant.logo : '',
        data_sources: enrichDataSources(tenant.data_sources || [], plugins),
      };
    } catch (e) {
      console.warn('Failed to fetch current tenant', e);
    }
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

  /** 获取数据源信息 */
  const getDataSourceInfo = (dataSourceId: IOrg['data_source_id']) => currentTenant.value.data_sources?.find(item => item.id === dataSourceId);

  /** 数据源实例是否为本地数据源 */
  const isEqualLocalSourceId = (dataSourceId: IOrg['data_source_id']) => (
    getDataSourceInfo(dataSourceId)?.plugin_id === 'local'
  );

  return {
    collaborationList,
    currentTenant,
    curSelectedTenant,
    curSelectedType,
    curSelectedDataSource,
    isConfiguredLocalSource,
    isSearchTree,
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
