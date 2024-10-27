import { defineStore } from 'pinia';

export const useSyncStatus = defineStore('syncStatus', {
  state: () => ({
    syncStatus: {},
    isRefresh: true,
  }),
  actions: {
    setSyncStatus(syncStatus: any) {
      this.syncStatus = syncStatus;
    },
    setRefresh(isRefresh: boolean) {
      this.isRefresh = isRefresh;
    },
  },
});
