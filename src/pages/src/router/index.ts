import { createRouter, createWebHistory } from 'vue-router';

import { routes } from './routes';

export default createRouter({
  history: createWebHistory(window.SITE_URL),
  routes: routes.filter(route => route.meta?.manager === false),
});
