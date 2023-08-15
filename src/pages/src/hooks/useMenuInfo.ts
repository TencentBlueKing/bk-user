import { RouteLocationNormalizedLoaded, RouteRecordRaw, useRoute, useRouter } from "vue-router";
import { computed } from 'vue';

export const useMenuInfo = () => {
  const route = useRoute();
  const router = useRouter();

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

  return {
    activeKey,
    openedKeys,
    handleChangeMenu,
  };
}