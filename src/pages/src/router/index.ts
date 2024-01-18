import { createRouter, createWebHistory } from 'vue-router';

import { t } from '@/language/index';

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
        navName: t('租户概览'),
      },
      component: () => import('@/views/tenant/index.vue'),
      children: [
        {
          path: 'info',
          name: 'tenantInfo',
          meta: {
            routeParentName: 'tenant',
            navName: t('租户概览'),
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
        navName: t('数据源管理'),
      },
      component: () => import('@/views/data-source/index.vue'),
      children: [
        {
          path: '',
          name: '',
          meta: {
            routeParentName: 'data-source',
            navName: t('数据源管理'),
            activeMenu: 'local',
          },
          component: () => import('@/views/data-source/LocalCompany.vue'),
          children: [
            {
              path: 'local',
              name: 'local',
              meta: {
                routeParentName: 'dataSource',
                navName: t('数据源管理'),
                activeMenu: 'local',
              },
              component: () => import('@/views/data-source/LocalDataSource.vue'),
            },
            {
              path: 'sync-records/:type?',
              name: 'syncRecords',
              meta: {
                routeParentName: 'dataSource',
                navName: t('数据源管理'),
                activeMenu: 'local',
              },
              component: () => import('@/views/data-source/SyncRecords.vue'),
            },
            {
              path: 'other',
              name: 'other',
              meta: {
                routeParentName: 'dataSource',
                navName: t('数据源管理'),
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
            navName: t('数据源详情'),
            activeMenu: 'local',
          },
          component: () => import('@/views/data-source/local-details/index.vue'),
        },
        {
          path: 'config/:type/:id?',
          name: 'newLocal',
          meta: {
            routeParentName: 'dataSource',
            navName: t('新建数据源'),
            activeMenu: 'local',
          },
          component: () => import('@/views/data-source/new-data/index.vue'),
        },
      ],
    },
    {
      path: '/auth-source',
      name: 'authSource',
      meta: {
        navName: t('认证源管理'),
      },
      component: () => import('@/views/auth-source/index.vue'),
      children: [
        {
          path: '',
          name: 'authSourceList',
          meta: {
            routeParentName: 'authSource',
            navName: t('认证源管理'),
          },
          component: () => import('@/views/auth-source/List.vue'),
        },
        {
          path: 'new',
          name: 'newAuthSource',
          meta: {
            routeParentName: 'authSource',
            navName: t('新建认证源'),
          },
          component: () => import('@/views/auth-source/new-data/index.vue'),
        },
        {
          path: 'edit/:type/:id',
          name: 'editAuthSource',
          meta: {
            routeParentName: 'authSource',
            navName: t('编辑认证源'),
            showBack: true,
          },
          component: () => import('@/views/auth-source/edit-data/index.vue'),
        },
      ],
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
        navName: t('用户字段设置'),
      },
      component: () => import('@/views/setting/index.vue'),
      children: [
        {
          path: 'fields',
          name: 'userFields',
          meta: {
            routeParentName: 'setting',
            navName: t('用户字段设置'),
            isMenu: true,
          },
          component: () => import('@/views/setting/FieldSetting.vue'),
        },
        {
          path: 'login',
          name: 'login',
          meta: {
            routeParentName: 'setting',
            navName: t('登录设置'),
            isMenu: true,
          },
          component: () => import('@/views/setting/LoginSetting.vue'),
        },
        {
          path: 'account',
          name: 'account',
          meta: {
            routeParentName: 'setting',
            navName: t('账号设置'),
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
    {
      path: '/:pathMatch(.*)*',
      name: 'notFound',
      component: () => import('@/views/NotFound.vue'),
    },
  ],
});
