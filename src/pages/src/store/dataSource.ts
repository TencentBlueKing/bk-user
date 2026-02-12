import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

import { getDataSourceList, getDataSourcePlugins, getSyncRecords } from '@/http/dataSourceFiles';
import { DataSourceItemData, DataSourcePluginsItemData } from '@/http/types/dataSourceFiles';

export const useDataSourceStore = defineStore('dataSource', () => {
  const dataSource = ref<DataSourceItemData[]>([]);
  const dataSourcePlugins = ref<DataSourcePluginsItemData[]>([]);
  const dataSourceSyncStatusMap = ref<Map<number, string>>(new Map());

  /** 新建的数据源ID */
  const newDataSourceId = ref(null);

  /** 是否已配置本地数据源插件 */
  const isConfiguredLocalPlugin = computed(() => dataSource.value.some(item => item.plugin_id === 'local'));

  /** 是否已配置通用数据源插件 */
  const isConfiguredGeneralPlugin = computed(() => dataSource.value.some(item => item.plugin_id === 'general'));

  /** 本地数据源ID */
  const localDataSourceId = computed(() => getDataSourceInfo('local')?.id);

  /** 设置新建的数据源ID */
  const setNewDataSourceId = (id: number) => {
    newDataSourceId.value = id;
  };

  /** 清空新建的数据源ID */
  const clearNewDataSourceId = () => {
    newDataSourceId.value = null;
  };

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
   * @param dataSourceIds 要获取同步状态的数据源ID列表
   */
  const handleFetchSyncStatus = async (dataSourceIds: number[]) => {
    if (!dataSourceIds || dataSourceIds.length === 0) return;

    // 并发获取所有目标数据源的同步记录
    const results = await Promise.all(dataSourceIds.map(id => getSyncRecords(id)));

    // 将每个数据源的最新状态存入 Map
    results.forEach((res, index) => {
      const dataSourceId = dataSourceIds[index];
      const status = res.data.results?.[0]?.status || '';
      dataSourceSyncStatusMap.value.set(dataSourceId, status);
    });
  };

  /** 获取指定数据源信息 */
  const getDataSourceInfo = (pluginId: string) => dataSource.value.find(item => item.plugin_id === pluginId);

  /**
   * 初始化所有已配置数据源的同步状态
   */
  const handleInitSyncStatus = async () => {
    const dataSourceIds = dataSource.value?.map(item => item.id) || [];
    await handleFetchSyncStatus(dataSourceIds);
  };

  return {
    dataSourcePlugins,
    dataSource,
    dataSourceSyncStatusMap,
    isConfiguredLocalPlugin,
    isConfiguredGeneralPlugin,
    localDataSourceId,
    newDataSourceId,
    getDataSourceInfo,
    handleFetchCurrentDataSource,
    handleFetchAllDataSourcePlugins,
    handleFetchSyncStatus,
    handleInitSyncStatus,
    setNewDataSourceId,
    clearNewDataSourceId,
  };
});
