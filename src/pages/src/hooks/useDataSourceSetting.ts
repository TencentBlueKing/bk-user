import { storeToRefs } from 'pinia';
import { onUnmounted, ref } from 'vue';

import { useDataSourceStore } from '@/store';

export default function useDataSourceSetting(callback?: Function) {
  const dataSourceStore = useDataSourceStore();
  const { dataSourceSyncStatusMap } = storeToRefs(dataSourceStore);

  // 存储各数据源当前的定时器（key: 数据源 ID），支持多个数据源同时轮询
  const timerMap = new Map<number, ReturnType<typeof setInterval>>();

  // 轮询是否激活（有任一数据源在轮询即为激活）
  const isActive = ref(false);

  // 根据 timerMap 是否为空同步 isActive
  const updateActive = () => {
    isActive.value = timerMap.size > 0;
  };

  /**
   * 检查数据源同步状态是否已完成
   * @param dataSourceId 数据源 ID
   * @returns 是否已完成
   */
  const isStatusCompleted = (dataSourceId: number) => {
    const status = dataSourceSyncStatusMap.value.get(dataSourceId)?.status;
    return status === 'success' || status === 'failed';
  };

  /**
   * 轮询获取数据源的同步状态
   * @param dataSourceId 要轮询的数据源 ID
   * @param pluginId 数据源的插件 ID
   */
  const startDataSourceSync = (dataSourceId: number, pluginId: string) => {
    if (!dataSourceId || !pluginId) {
      console.warn('未找到要轮询的数据源 ID 或插件 ID');
      return;
    }

    // 该数据源已在轮询中，先停止（重新开始轮询）
    if (timerMap.has(dataSourceId)) {
      stopDataSourceSync(dataSourceId);
    }

    // 定义轮询回调函数
    const pollingCallback = async () => {
      await dataSourceStore.handleFetchSyncStatus([{ id: dataSourceId, pluginId }]);

      // 检查数据源是否已完成同步
      const isCompleted = isStatusCompleted(dataSourceId);

      // 如果完成了，自动停止该数据源的轮询并执行回调
      if (isCompleted && timerMap.has(dataSourceId)) {
        stopDataSourceSync(dataSourceId);
        callback?.();
      }
    };

    // 立即执行一次获取状态
    dataSourceStore.handleFetchSyncStatus([{ id: dataSourceId, pluginId }]).then(() => {
      // 检查是否需要开启轮询
      const status = dataSourceSyncStatusMap.value.get(dataSourceId)?.status;
      const needPolling = status === 'pending' || status === 'running';

      if (needPolling) {
        // 防重入：异步返回前若已创建过该数据源的定时器，不再重复创建
        if (!timerMap.has(dataSourceId)) {
          timerMap.set(dataSourceId, setInterval(pollingCallback, 5000));
          updateActive();
        }
      } else {
        callback?.();
      }
    });
  };

  /**
   * 停止轮询数据源同步状态
   * @param dataSourceId 可选，指定要停止的数据源 ID；不传则停止所有数据源的轮询
   */
  const stopDataSourceSync = (dataSourceId?: number) => {
    if (dataSourceId !== undefined) {
      const timerId = timerMap.get(dataSourceId);
      if (timerId) {
        clearInterval(timerId);
        timerMap.delete(dataSourceId);
      }
      updateActive();
      return;
    }

    // 未指定数据源 ID，停止全部轮询
    timerMap.forEach(timerId => clearInterval(timerId));
    timerMap.clear();
    updateActive();
  };

  // 组件卸载时清理所有定时器
  onUnmounted(() => {
    stopDataSourceSync();
  });

  return {
    isActive,
    startDataSourceSync,
    stopDataSourceSync,
  };
};
