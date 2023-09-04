import { computed, inject } from 'vue';
import { RouteLocationNormalizedLoaded, RouteRecordRaw, useRoute, useRouter } from 'vue-router';

export const useMenuInfo = () => {
  const route = useRoute();
  const router = useRouter();
  const editLeaveBefore = inject('editLeaveBefore');

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
