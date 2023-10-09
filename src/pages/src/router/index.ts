import { createRouter, createWebHistory } from 'vue-router';

export default createRouter({
  history: createWebHistory(window.SITE_URL),
  routes: [
    {
      path: '/',
      name: 'organization',
      component: () => import('@/views/organization/index.vue'),
    },
    {
      path: '/tenant',
      name: 'tenant',
      redirect: {
        name: 'tenantInfo',
      },
      meta: {
        navName: '集团概览',
      },
      component: () => import('@/views/tenant/index.vue'),
      children: [
        {
          path: 'info',
          name: 'tenantInfo',
          meta: {
            routeParentName: 'tenant',
            navName: '集团概览',
            isMenu: true,
          },
          component: () => import('@/views/tenant/group-details/index.vue'),
        },
        // {
        //   path: "setting",
        //   name: "globalSetting",
        //   meta: {
        //     routeParentName: "tenant",
        //     navName: "全局设置",
        //     isMenu: true,
        //   },
        // },
      ],
    },
    {
      path: '/data-source',
      name: 'dataSource',
      redirect: {
        name: 'local',
      },
      meta: {
        navName: '数据源管理',
      },
      component: () => import('@/views/data-source/index.vue'),
      children: [
        {
          path: '',
          name: '',
          meta: {
            routeParentName: 'data-source',
            navName: '数据源管理',
            activeMenu: 'local',
          },
          component: () => import('@/views/data-source/LocalCompany.vue'),
          children: [
            {
              path: 'local',
              name: 'local',
              meta: {
                routeParentName: 'dataSource',
                navName: '数据源管理',
                activeMenu: 'local',
              },
              component: () => import('@/views/data-source/LocalDataSource.vue'),
            },
            {
              path: 'sync-records',
              name: 'syncRecords',
              meta: {
                routeParentName: 'dataSource',
                navName: '数据源管理',
                activeMenu: 'local',
              },
              component: () => import('@/views/data-source/SyncRecords.vue'),
            },
            {
              path: 'other',
              name: 'other',
              meta: {
                routeParentName: 'dataSource',
                navName: '数据源管理',
                activeMenu: 'local',
              },
              component: () => import('@/views/data-source/OtherDataSource.vue'),
            },
          ],
        },
        {
          path: 'details/:id',
          name: 'dataConfDetails',
          meta: {
            routeParentName: 'dataSource',
            navName: '数据源详情',
            activeMenu: 'local',
          },
          component: () => import('@/views/data-source/local-details/index.vue'),
        },
        {
          path: 'config/:type/:id?',
          name: 'newLocal',
          meta: {
            routeParentName: 'dataSource',
            navName: '新建数据源',
            activeMenu: 'local',
          },
          component: () => import('@/views/data-source/new-data/index.vue'),
        },
      ],
    },
    {
      path: '/auth-source',
      name: 'authSource',
      component: () => import('@/views/auth-source/index.vue'),
    },
    {
      path: '/auth-source/new',
      name: 'newAuthSource',
      meta: {
        navName: '新建认证源',
      },
      component: () => import('@/views/auth-source/new-data/NewConfig.vue'),
    },
    {
      path: '/audit',
      name: 'audit',
      component: () => import('@/views/audit/index.vue'),
    },
    {
      path: '/setting',
      name: 'setting',
      redirect: {
        name: 'userFields',
      },
      meta: {
        navName: '用户字段设置',
      },
      component: () => import('@/views/setting/index.vue'),
      children: [
        {
          path: 'fields',
          name: 'userFields',
          meta: {
            routeParentName: 'setting',
            navName: '用户字段设置',
            isMenu: true,
          },
          component: () => import('@/views/setting/FieldSetting.vue'),
        },
        {
          path: 'login',
          name: 'login',
          meta: {
            routeParentName: 'setting',
            navName: '登录设置',
            isMenu: true,
          },
          component: () => import('@/views/setting/LoginSetting.vue'),
        },
        {
          path: 'account',
          name: 'account',
          meta: {
            routeParentName: 'setting',
            navName: '账号设置',
            isMenu: true,
          },
          component: () => import('@/views/setting/AccountSetting.vue'),
        },
      ],
    },
    {
      path: '/personal-center',
      name: 'personalCenter',
      component: () => import('@/views/personal-center/index.vue'),
    },
  ],
});
