import { acceptHMRUpdate, defineStore } from 'pinia';

export const useMainViewStore = defineStore('mainView', {
  state: () => ({
    breadCrumbsTitle: '',
    customBreadcrumbs: false,
    hasPadding: true,
  }),
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useMainViewStore, import.meta.hot));
}
