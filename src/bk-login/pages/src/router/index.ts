import {
  createRouter,
  createWebHistory,
} from 'vue-router';

// const HomeDemo = () => import(/* webpackChunkName: "HomeDemo" */ '../views/home-demo.vue');
const Home = () => import(/* webpackChunkName: "Home" */ '../views/home.vue');
const User = () => import(/* webpackChunkName: "Home" */ '../views/user.vue');

export default createRouter({
  history: createWebHistory(''),
  routes: [
    {
      path: `${window.SITE_URL}/`,
      component: Home,
      name: 'Login',
    },
    {
      path: `${window.SITE_URL}/plain/`,
      component: Home,
      name: 'LoginPlain',
    },
    {
      path: `${window.SITE_URL}/page/users/`,
      component: User,
      name: 'User',
    },
  ],
});
