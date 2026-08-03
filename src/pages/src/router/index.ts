import { createRouter, createWebHashHistory, createWebHistory } from 'vue-router';

import { routes } from './routes';

const router = createRouter({
  history: process.env.BK_DESIGN_PREVIEW === 'true'
    ? createWebHashHistory()
    : createWebHistory(window.SITE_URL),
  routes,
});

export default router;
