import 'vue-router';

declare module 'vue-router' {
  interface RouteMeta {
    routeParentName?: string, // 父级路由名称
    submenuId?: string, // submenu 激活状态
    activeMenu?: string, // menu 激活状态
    navName?: string, // 设置面包屑 name
    isMenu?: boolean, // 判断是否为 bk-menu 导航，若是则不显示返回按钮
    showBack?: boolean, // 用于判断是否显示面包屑返回按钮
  }
}

export {};
