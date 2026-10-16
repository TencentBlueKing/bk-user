import { onUnmounted } from 'vue';

import { useDataSourceImport } from './useDataSourceImport';
import useDataSourceSetting from './useDataSourceSetting';

import { useDataSourceStore } from '@/store';

export interface ImportTaskResult {
  success: boolean;
  /** 失败原因：仅接口同步返回 failed 时携带；轮询到的失败无 summary，由调用方兜底文案 */
  summary?: string;
}

/**
 * 本地数据源 Excel 导入任务：导入接口为异步任务（async_run），
 * 返回 pending/running 时轮询同步状态，importTask 的 Promise 在任务出最终结果后才兑现
 */
export const useDataSourceImportTask = () => {
  const dataSourceStore = useDataSourceStore();
  const { uploadImport } = useDataSourceImport();

  let resolveTask: ((result: ImportTaskResult) => void) | null = null;
  let pollingDataSourceId: number | null = null;

  // 轮询结束（同步记录无 summary）后按任务最终状态兑现挂起的 Promise
  const { startDataSourceSync, stopDataSourceSync } = useDataSourceSetting(() => {
    const status = pollingDataSourceId
      ? dataSourceStore.dataSourceSyncStatusMap.get(pollingDataSourceId)?.status
      : undefined;
    resolveTask?.({ success: status === 'success' });
    resolveTask = null;
    pollingDataSourceId = null;
  });

  const importTask = async (dataSourceId: number, file: File, overwrite = false): Promise<ImportTaskResult> => {
    const res = await uploadImport(dataSourceId, file, overwrite);
    const { status, summary } = res.data.data;
    // 接口 HTTP 200 但业务失败（如 Excel 内容错误）也需按失败处理，否则会误报成功
    if (status === 'failed') return { success: false, summary };
    if (status === 'success') return { success: true };
    // pending/running：任务已提交但未结束，轮询同步状态，结束后由回调兑现
    pollingDataSourceId = dataSourceId;
    return new Promise((resolve) => {
      resolveTask = resolve;
      startDataSourceSync(dataSourceId, 'local');
    });
  };

  // 卸载时停止轮询并释放挂起的 Promise，避免调用方 loading 卡死
  onUnmounted(() => {
    stopDataSourceSync();
    resolveTask?.({ success: false });
    resolveTask = null;
    pollingDataSourceId = null;
  });

  return { importTask };
};
