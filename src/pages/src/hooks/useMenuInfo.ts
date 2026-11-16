import { computed, inject, watch } from 'vue';
import { RouteLocationNormalizedLoaded, RouteRecordRaw, useRoute, useRouter } from 'vue-router';

import { useMainViewStore } from '@/store';

export const useMenuInfo = () => {
  const route = useRoute();
  const router = useRouter();
  const editLeaveBefore = inject('editLeaveBefore');
  const store = useMainViewStore();

  // 获取 menu 相关配置
  const { children } = route.matched[0];
  const routes = computed(() => children.reduce((routes: RouteRecordRaw[], route) => (
    routes.concat([route, ...route.children || []])
  ), []));

  // 获取 menu 默认激活信息
  const activeMenu = computed<RouteLocationNormalizedLoaded | RouteRecordRaw | undefined>(() => {
    const { activeMenu } = route.meta;
    if (activeMenu) {
      return routes.value.find((route: RouteRecordRaw) => route.name === activeMenu);
    }

    return route;
  });

  // 标题只在切换路由记录时重置；放在 computed 里会被同页面 query 变化（如编辑数据源切页签）触发，覆盖掉页面自定义标题
  watch(() => route.name, () => {
    store.breadCrumbsTitle = route.meta.navName;
  }, { immediate: true });

  const activeKey = computed(() => activeMenu.value?.name as string | undefined);
  const openedKeys = computed(() => (activeMenu.value?.meta?.submenuId ? [activeMenu.value.meta.submenuId] : []));

  /** menu 点击事件 */
  const handleChangeMenu = ({ key }: any) => {
    if (key === route.name) return;
    router.push({ name: key });
  };


  router.beforeEach(async (to, from, next) => {
    let enableLeave = true;
    if (window.changeInput) {
      enableLeave = await editLeaveBefore();
    }
    if (!enableLeave) {
      return Promise.resolve(enableLeave);
    }
    next();
  });

  return {
    activeKey,
    openedKeys,
    handleChangeMenu,
  };
};
