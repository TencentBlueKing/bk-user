import { acceptHMRUpdate, defineStore } from 'pinia';

export const useMenu = defineStore('useMenu', {
  state: () => ({
    toggleCollapsed: false,
    hoverCollapsed: true,
    menuCountMap: {
      todos: 0,
      tickets: 0,
    },
  }),
  getters: {
    // 切换展开/收起
    collapsed: state => state.toggleCollapsed && state.hoverCollapsed,
    // 处于 hover 展开
    isHover: state => state.toggleCollapsed && (state.hoverCollapsed === false),
  },
  actions: {
    toggle() {
      this.toggleCollapsed = !this.toggleCollapsed;
    },
    mouseenter() {
      this.hoverCollapsed = false;
    },
    mouseleave() {
      this.hoverCollapsed = true;
    },
  },
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useMenu, import.meta.hot));
}
