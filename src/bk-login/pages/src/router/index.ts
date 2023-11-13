import {
  createRouter,
  createWebHistory,
} from 'vue-router';

// const HomeDemo = () => import(/* webpackChunkName: "HomeDemo" */ '../views/home-demo.vue');
const Home = () => import(/* webpackChunkName: "Home" */ '../views/home.vue');
const User = () => import(/* webpackChunkName: "Home" */ '../views/user.vue');

export default createRouter({
  history: createWebHistory(window.SITE_URL),
  routes: [
    {
      path: '/',
      component: Home,
    },
    {
      path: '/plain/',
      component: Home,
    },
    {
      path: '/page/users/',
      component: User,
    },
  ],
});
