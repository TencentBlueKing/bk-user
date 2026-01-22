import { createRouter, createWebHistory } from 'vue-router';

import { routes } from './routes';

const router = createRouter({
  history: createWebHistory(window.SITE_URL),
  routes,
});

export default router;
