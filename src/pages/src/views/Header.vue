<template>
  <bk-navigation
    class="main-navigation"
    :hover-width="240"
    navigation-type="top-bottom"
    :need-menu="false"
    :side-title="'蓝鲸用户管理'"
    theme-color="#1e2634"
  >
    <template #side-header>
      <RouterLink
        style="display: flex; align-items: center; text-decoration: none;"
        :to="{ name: 'organization' }"
      >
        <i class="user-icon icon-user-logo-i" />
        <span class="title-desc">蓝鲸用户管理</span>
      </RouterLink>
    </template>
    <template #header>
      <div class="main-navigation-left">
        <span v-for="(item, index) in headerNav" :key="index">
          <RouterLink
            active-class="main-navigation-nav--active"
            class="main-navigation-nav"
            :to="{ name: item.path }"
          >
            {{ item.name }}
          </RouterLink>
        </span>
      </div>
      <div class="main-navigation-right">
        <!-- <bk-dropdown
          @hide="() => (state.languageDropdown = false)"
          @show="() => (state.languageDropdown = true)"
        >
          <div class="help-info" :class="state.languageDropdown && 'active'">
            <i class="bk-sq-icon icon-yuyanqiehuanzhongwen"></i>
          </div>
          <template #content>
            <bk-dropdown-menu>
              <bk-dropdown-item v-for="(item, index) in languageNav" :key="index">
                <i :class="item.icon" style=" margin-right: 5px;font-size: 16px;"></i>
                <span>{{ item.name }}</span>
              </bk-dropdown-item>
            </bk-dropdown-menu>
          </template>
        </bk-dropdown>
        <bk-dropdown
          @hide="() => (state.helpDropdown = false)"
          @show="() => (state.helpDropdown = true)"
        >
          <div class="help-info" :class="state.helpDropdown && 'active'">
            <span class="help-info-name">
              <HelpDocumentFill />
            </span>
          </div>
          <template #content>
            <bk-dropdown-menu>
              <bk-dropdown-item v-for="(item, index) in helpNav" :key="index" @click="toLink(item)">
                {{ item.name }}
              </bk-dropdown-item>
            </bk-dropdown-menu>
          </template>
        </bk-dropdown> -->
        <bk-dropdown
          placement="bottom-end"
          @hide="() => (state.logoutDropdown = false)"
          @show="() => (state.logoutDropdown = true)"
        >
          <div
            :class="['help-info', { 'active-username': state.logoutDropdown }, { 'active-route': isPersonalCenter }]">
            <span class="help-info-name">{{ userInfo.username }}</span>
            <DownShape class="help-info-icon" />
          </div>
          <template #content>
            <bk-dropdown-menu ext-cls="dropdown-menu-box">
              <bk-dropdown-item
                :class="{ 'active': isPersonalCenter }"
                @click="toIndividualCenter">
                个人中心
              </bk-dropdown-item>
              <bk-dropdown-item @click="logout">退出登录</bk-dropdown-item>
            </bk-dropdown-menu>
          </template>
        </bk-dropdown>
      </div>
    </template>
    <router-view></router-view>
    <Login />
  </bk-navigation>
</template>

<script setup lang="ts">
import { DownShape } from 'bkui-vue/lib/icon';
import { computed, reactive } from 'vue';
import { useRoute } from 'vue-router';

import { logout } from '@/common/auth';
import Login from '@/components/layouts/Login.vue';
import router from '@/router';
import { useUser } from '@/store/user';

const state = reactive({
  logoutDropdown: false,
  helpDropdown: false,
  languageDropdown: false,
});

const userStore = useUser();
const userInfo = computed(() => userStore.user);

const route = useRoute();
const isPersonalCenter = computed(() => route.name === 'personalCenter');

const headerNav = reactive([
  {
    name: '组织架构',
    path: 'organization',
  },
  {
    name: '数据源管理',
    path: 'dataSource',
  },
  {
    name: '认证源管理',
    path: 'authSource',
  },
  {
    name: '租户管理',
    path: 'tenant',
  },
  // {
  //   name: "审计",
  //   path: "audit",
  // },
  {
    name: '设置',
    path: 'setting',
  },
]);
// const languageNav = reactive([
//   {
//     name: '中文',
//     icon: 'bk-sq-icon icon-yuyanqiehuanzhongwen',
//   },
//   {
//     name: 'English',
//     icon: 'bk-sq-icon icon-yuyanqiehuanyingwen',
//   },
// ]);
// const helpNav = reactive([
//   {
//     name: '产品文档',
//     url: '',
//   },
//   {
//     name: '版本日志',
//     url: '',
//   },
//   {
//     name: '问题反馈',
//     url: '',
//   },
// ]);
// const toLink = (item: any) => {
//   window.open(item.url, '_blank');
// };
const toIndividualCenter = () => {
  router.push({
    name: 'personalCenter',
  });
};
</script>

<style lang="less" scoped>
.main-navigation {
  min-width: 1200px;

  :deep(.bk-navigation-header) {
    background-color: #0e1525;

    .icon-user-logo-i {
      font-size: 28px;
      color: #458df4;
    }

    .title-desc {
      color: #eaebf0;
    }
  }

  :deep(.navigation-container) {
    min-width: 1200px;

    .container-content {
      padding: 0 !important;
    }
  }

  :deep(.header-right) {
    justify-content: space-between;
  }
}

.main-navigation-left {
  margin-left: 20px;
  font-size: 14px;
  line-height: 52px;
}

.main-navigation-nav {
  display: inline-block;
  padding: 0 16px;
  color: #96a2b9;
  text-decoration: none;

  &:hover {
    color: #d3d9e4;
  }

  &.main-navigation-nav--active {
    color: #fff;
  }
}

.main-navigation-right {
  margin: 0 10px;
  color: #96a2b9;

  .bk-dropdown {
    padding: 0 10px;

    .help-info {
      padding: 5px;
      border-radius: 50%;
    }

    .active {
      background: #252f43;

      .bk-sq-icon, .help-info-name {
        color: #3a84ff;
      }
    }

    .active-username {
      color: #3a84ff;
      cursor: pointer;

      .help-info-icon {
        display: inline-block;
        transform: rotate(180deg);
        transition: all 0.2s;
      }
    }

    .active-route {
      color: #3a84ff;
    }

    .help-info-icon {
      vertical-align: middle;
    }

    .help-info-name {
      padding-right: 4px;
      font-size: 14px;

      span {
        font-size: 16px;
        vertical-align: middle;
      }
    }

    .bk-sq-icon {
      font-size: 16px;
    }
  }
}

.dropdown-menu-box {
  .active {
    color: #3a84ff;
    background-color: #E1ECFF;

    &:hover {
      background-color: #E1ECFF;
    }
  }
}
</style>
