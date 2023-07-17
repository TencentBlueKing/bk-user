import {
  createRouter,
  createWebHistory,
} from 'vue-router';

export default createRouter({
  history: createWebHistory(window.SITE_URL),
  routes: [
    {
      path: "/",
      name: "organization",
      component: () => import("../views/organization/index.vue"),
    },
    {
      path: "/tenantry",
      name: "tenantry",
      component: () => import("../views/tenantry/index.vue"),
    },
    {
      path: "/source",
      name: "source",
      component: () => import("../views/data-source/index.vue"),
    },
    {
      path: "/audit",
      name: "audit",
      component: () => import("../views/audit/index.vue"),
    },
    {
      path: "/setting",
      name: "setting",
      component: () => import("../views/setting/index.vue"),
    },
  ],
});
