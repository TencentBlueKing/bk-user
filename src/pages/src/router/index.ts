import { createRouter, createWebHistory } from 'vue-router';

import { t } from '@/language/index';

export default createRouter({
  history: createWebHistory(window.SITE_URL),
  routes: [
    {
      path: '/',
      name: 'tenant',
      component: () => import('@/views/tenant/index.vue'),
    },
    {
      path: '/organization',
      name: 'organization',
      component: () => import('@/views/organization/index.vue'),
    },
    {
      path: '/virtual-account',
      name: 'virtual-account',
      component: () => import('@/views/virtual-account/index.vue'),
    },
    {
      path: '/setting',
      name: 'setting',
      redirect: {
        name: 'admin',
      },
      meta: {
        navName: t('设置'),
      },
      component: () => import('@/views/setting/index.vue'),
      children: [
        {
          path: 'admin',
          name: 'admin',
          meta: {
            routeParentName: 'setting',
            navName: t('管理员配置'),
            isMenu: true,
          },
          component: () => import('@/views/setting/AdminSetting.vue'),
        },
        {
          path: 'data-source',
          name: 'dataSource',
          meta: {
            routeParentName: 'setting',
            navName: t('数据源配置'),
            activeMenu: 'dataSource',
          },
          component: () => import('@/views/setting/data-source/ConfigList.vue'),
        },
        {
          path: 'new',
          name: 'newDataSource',
          meta: {
            routeParentName: 'setting',
            navName: t('数据源配置'),
            activeMenu: 'dataSource',
          },
          component: () => import('@/views/setting/data-source/NewDataSource.vue'),
        },
        {
          path: 'collaboration',
          name: 'collaboration',
          meta: {
            routeParentName: 'setting',
            navName: t('跨租户协同'),
            isMenu: true,
            hiddenBoxShadow: true,
          },
          component: () => import('@/views/setting/cross-tenant-collaboration/index.vue'),
        },
        {
          path: 'fields',
          name: 'field',
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
          path: 'fma',
          name: 'fma',
          meta: {
            routeParentName: 'setting',
            navName: t('MFA设置'),
            isMenu: true,
          },
          component: () => import('@/views/setting/MFASetting.vue'),
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
        {
          path: 'basics',
          name: 'basics',
          meta: {
            routeParentName: 'setting',
            navName: t('基础设置'),
            isMenu: true,
          },
          component: () => import('@/views/setting/BasicsSetting.vue'),
        },
      ],
    },
    {
      path: '/personal-center',
      name: 'personalCenter',
      component: () => import('@/views/personal-center/index.vue'),
    },
    {
      path: '/password/:tenantId?',
      name: 'password',
      component: () => import('@/views/reset-password/index.vue'),
    },
    {
      path: '/reset-password/:token?',
      name: 'resetPassword',
      component: () => import('@/views/reset-password/newPassword.vue'),
    },
    {
      path: '/recycle',
      name: 'recycle',
      component: () => import('@/views/recycle/index.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'notFound',
      component: () => import('@/views/NotFound.vue'),
    },
  ],
});
