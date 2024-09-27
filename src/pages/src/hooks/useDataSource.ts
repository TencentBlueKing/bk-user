import { Message } from 'bkui-vue';
import { onMounted, reactive, ref } from 'vue';

import {
  getDataSourceList,
  getDataSourcePlugins,
  getDefaultConfig,
  getSyncRecords,
  newDataSource,
  postOperationsSync,
} from '@/http';
import { t } from '@/language/index';
import router from '@/router';

export const useDataSource = () => {
  const dataSourcePlugins = ref([]);
  const dataSource = ref({});
  const currentDataSourceId = ref(null);
  const isLoading = ref(false);

  onMounted(() => {
    initDataSourcePlugins();
  });

  // 初始化数据源插件
  const initDataSourcePlugins = () => {
    isLoading.value = true;
    getDataSourcePlugins().then((res) => {
      dataSourcePlugins.value = res.data;
      initDataSourceList();
    })
      .catch(() => {
        isLoading.value = false;
      });
  };

  // 获取当前数据源
  const initDataSourceList = () => {
    getDataSourceList({ type: 'real' }).then((res) => {
      const firstData = res.data[0];
      dataSource.value = firstData;
      currentDataSourceId.value = firstData?.id ?? null;
      const index = dataSourcePlugins.value?.findIndex(item => item.id === dataSource.value?.plugin_id);
      if (index > -1) {
        dataSourcePlugins.value.unshift(...dataSourcePlugins.value.splice(index, 1));
        initSyncRecords();
      }
    })
      .finally(() => {
        isLoading.value = false;
      });
  };

  // 获取同步数据源状态
  const syncStatus = ref({});
  const initSyncRecords = (customFn: Function = null) => {
    getSyncRecords({ id: currentDataSourceId.value })
      .then((res) => {
        if (res.data?.count === 0) return;
        syncStatus.value = res.data?.results[0];
        if (customFn) customFn(syncStatus.value);
      })
      .catch((error) => {
        console.warn(error);
      });
  };
  // 点击新建数据源
  const handleClick = async (id: string) => {
    if (!currentDataSourceId.value) {
      if (id === 'local') {
        const res = await getDefaultConfig('local');
        newDataSource({
          plugin_id: 'local',
          plugin_config: {
            ...res.data?.config,
          },
        }).then((res) => {
          currentDataSourceId.value = res.data?.id;
          importDialog.isShow = true;
        });
      } else {
        router.push({ name: 'newDataSource', query: { type: id } });
      }
    } else {
      router.push({ name: 'dataSourceConfig', query: id === 'local' ? {} : { type: id } });
    }
  };

  const importDialog = reactive({
    isShow: false,
    loading: false,
    title: t('导入'),
    id: 'local',
  });

  const pollingInterval = ref(null);

  const handleOperationsSync = async () => {
    postOperationsSync(dataSource.value?.id).then((res) => {
      Message({ theme: res.data.status, message: res.data.summary });
      if (pollingInterval.value) return;
      initSyncRecords(stopOperationPollingRule);
      pollingInterval.value = setInterval(() => initSyncRecords(stopOperationPollingRule), 10000);
    });
  };

  const stopPolling = () => {
    if (pollingInterval.value) {
      clearInterval(pollingInterval.value);
      pollingInterval.value = null;
    }
  };

  const stopOperationPollingRule = (data) => {
    if (data.status === 'success') {
      stopPolling();
    }
  }

  const importDataTimePolling = ref(null);

  const handleImportLocalDataSync = () => {
    initSyncRecords(importDataStopRule);
    importDataTimePolling.value = setInterval(() => {
      initSyncRecords(importDataStopRule);
    }, 1000);
  };

  const stopImportDataTimePolling = () => {
    if (importDataTimePolling.value) {
      clearInterval(importDataTimePolling.value);
      importDataTimePolling.value = null;
    }
  };

  const importDataStopRule = (data) => {
    if (data.status === 'success') {
      stopImportDataTimePolling();
    }
  };

  return {
    dataSourcePlugins,
    dataSource,
    currentDataSourceId,
    isLoading,
    initDataSourceList,
    syncStatus,
    initSyncRecords,
    handleClick,
    importDialog,
    handleOperationsSync,
    stopPolling,
    handleImportLocalDataSync,
    stopImportDataTimePolling
  };
};
