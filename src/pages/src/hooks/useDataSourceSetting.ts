import { storeToRefs } from 'pinia';
import { onUnmounted, ref } from 'vue';

import { useDataSourceStore } from '@/store';

export default function useDataSourceSetting(callback?: Function) {
  const dataSourceStore = useDataSourceStore();
  const { dataSourceSyncStatusMap } = storeToRefs(dataSourceStore);

  // 存储当前的定时器 ID
  let timerId: ReturnType<typeof setInterval> | null = null;

  // 轮询是否激活
  const isActive = ref(false);

  /**
   * 检查数据源同步状态是否已完成
   * @param dataSourceId 数据源 ID
   * @returns 是否已完成
   */
  const isStatusCompleted = (dataSourceId: number) => {
    const status = dataSourceSyncStatusMap.value.get(dataSourceId);
    return status === 'success' || status === 'failed';
  };

  /**
   * 轮询获取数据源的同步状态
   * @param dataSourceId 要轮询的数据源 ID
   */
  const startDataSourceSync = (dataSourceId: number) => {
    // 如果已经在轮询中，先停止
    if (isActive.value) {
      stopDataSourceSync();
    }

    if (!dataSourceId) {
      console.warn('未找到要轮询的数据源 ID');
      return;
    }

    // 定义轮询回调函数
    const pollingCallback = async () => {
      await dataSourceStore.handleFetchSyncStatus([dataSourceId]);

      // 检查数据源是否已完成同步
      const isCompleted = isStatusCompleted(dataSourceId);

      // 如果完成了，自动停止轮询并执行回调
      if (isCompleted && isActive.value) {
        stopDataSourceSync();
        callback?.();
      }
    };

    // 立即执行一次获取状态
    dataSourceStore.handleFetchSyncStatus([dataSourceId]).then(() => {
      // 检查是否需要开启轮询
      const status = dataSourceSyncStatusMap.value.get(dataSourceId);
      const needPolling = status === 'pending' || status === 'running';

      if (needPolling) {
        // 开启轮询
        timerId = setInterval(pollingCallback, 5000);
        isActive.value = true;
      } else {
        callback?.();
      }
    });
  };

  /**
   * 停止轮询数据源同步状态
   */
  const stopDataSourceSync = () => {
    if (timerId) {
      clearInterval(timerId);
      timerId = null;
      callback?.();
    }
    isActive.value = false;
  };

  // 组件卸载时清理定时器
  onUnmounted(() => {
    stopDataSourceSync();
  });

  return {
    isActive,
    startDataSourceSync,
    stopDataSourceSync,
  };
};
