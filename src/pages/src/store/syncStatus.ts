import { defineStore } from 'pinia';

import { SyncRecords } from '@/http/types/dataSourceFiles';

export const useSyncStatus = defineStore('syncStatus', {
  state: () => ({
    syncStatus: {} as SyncRecords['results'][number],
    isRefresh: true,
  }),
  actions: {
    setSyncStatus(syncStatus: SyncRecords['results'][number]) {
      this.syncStatus = syncStatus;
    },
    setRefresh(isRefresh: boolean) {
      this.isRefresh = isRefresh;
    },
  },
});
