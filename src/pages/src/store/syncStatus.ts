import { defineStore } from 'pinia';

export const useSyncStatus = defineStore('syncStatus', {
  state: () => ({
    syncStatus: {},
  }),
  actions: {
    setSyncStatus(syncStatus: any) {
      this.syncStatus = syncStatus;
    },
  },
});
