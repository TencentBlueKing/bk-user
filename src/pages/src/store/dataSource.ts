import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

import { getDataSourceList, getDataSourcePlugins, getSyncRecords } from '@/http/dataSourceFiles';
import { DataSourceItemData, DataSourcePluginsItemData, SyncRecords, SyncRecordsParams } from '@/http/types/dataSourceFiles';

export const useDataSourceStore = defineStore('dataSource', () => {
  const dataSource = ref<DataSourceItemData[]>([]);
  const dataSourcePlugins = ref<DataSourcePluginsItemData[]>([]);
  const dataSourceSyncStatusMap = ref<Map<number, SyncRecords['results'][number]>>(new Map());

  /** 是否已配置本地数据源插件 */
  const isConfiguredLocalPlugin = computed(() => dataSource.value.some(item => item.plugin_id === 'local'));

  /** 是否已配置通用数据源插件 */
  const isConfiguredGeneralPlugin = computed(() => dataSource.value.some(item => item.plugin_id === 'general'));

  /** 是否已配置其他数据源插件 */
  const isConfiguredOtherPlugin = computed(() => dataSource.value.length > 0 && !isConfiguredLocalPlugin.value);

  /** 本地数据源ID */
  const localDataSourceId = computed(() => getDataSourceInfo('local')?.id);

  /** 获取当前配置的数据源插件 */
  const handleFetchCurrentDataSource = async () => {
    const res = await getDataSourceList({ type: 'real' });
    dataSource.value = res.data;
  };

  /** 获取所有数据源插件 */
  const handleFetchAllDataSourcePlugins = async () => {
    const res = await getDataSourcePlugins();
    dataSourcePlugins.value = res.data;
  };

  /**
   * 获取指定数据源的同步状态
   * @param dataSources 要获取同步状态的数据源列表，包含 id 和 pluginId
   */
  const handleFetchSyncStatus = async (dataSources: { id: number; pluginId: string }[]) => {
    if (!dataSources || dataSources.length === 0) return;
    // 并发获取所有目标数据源的同步记录
    const results = await Promise.all(dataSources.map(({ pluginId }) => {
      const params: SyncRecordsParams = {
        plugin_id: pluginId,
        page: 1,
        page_size: 10,
      };
      return getSyncRecords(params);
    }));
    // 将每个数据源的最新状态存入 Map
    results.forEach((res, index) => {
      const dataSourceId = dataSources[index].id;
      const data = res?.data?.results?.[0];
      if (data) {
        dataSourceSyncStatusMap.value.set(dataSourceId, data);
      }
    });
  };

  /** 获取指定数据源信息 */
  const getDataSourceInfo = (pluginId: string) => dataSource.value.find(item => item.plugin_id === pluginId);

  /** 获取指定数据源实例 */
  const getDataSourceById = (id?: number | string) => dataSource.value.find(item => item.id === Number(id));

  /** 获取指定插件类型下的所有数据源实例 */
  const getDataSourcesByPlugin = (pluginId: string) => dataSource.value.filter(item => item.plugin_id === pluginId);

  /**
   * 初始化所有已配置数据源的同步状态
   */
  const handleInitSyncStatus = async () => {
    const dataSources = dataSource.value?.map(item => ({ id: item.id, pluginId: item.plugin_id })) || [];
    await handleFetchSyncStatus(dataSources);
  };

  /** 数据源是否同步中 */
  const isDataSourceSyncing = (status: string) => ['pending', 'running'].includes(status);

  return {
    dataSourcePlugins,
    dataSource,
    dataSourceSyncStatusMap,
    isConfiguredLocalPlugin,
    isConfiguredGeneralPlugin,
    isConfiguredOtherPlugin,
    localDataSourceId,
    getDataSourceInfo,
    getDataSourceById,
    getDataSourcesByPlugin,
    handleFetchCurrentDataSource,
    handleFetchAllDataSourcePlugins,
    handleFetchSyncStatus,
    handleInitSyncStatus,
    isDataSourceSyncing,
  };
});
