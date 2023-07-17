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
        <bk-dropdown
          @hide="() => (state.languageDrodown = false)"
          @show="() => (state.languageDrodown = true)"
        >
          <div class="help-info" :class="state.languageDrodown && 'active'">
            <i class="bk-sq-icon icon-yuyanqiehuanzhongwen"></i>
          </div>
          <template #content>
            <bk-dropdown-menu>
              <bk-dropdown-item v-for="(item, index) in languageNav" :key="index">
                <i :class="item.icon" style="fontSize: 16px; margin-right: 5px;"></i>
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
        </bk-dropdown>
        <bk-dropdown
          @hide="() => (state.logoutDropdown = false)"
          @show="() => (state.logoutDropdown = true)"
        >
          <div class="help-info">
            <span class="help-info-name">{{ userInfo.username }}</span>
            <DownShape class="help-info-icon" />
          </div>
          <template #content>
            <bk-dropdown-menu>
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
import { ref, reactive } from "vue";
import { useUser } from "@/store/user";
import { logout } from "@/common/auth";
import { DownShape, HelpDocumentFill } from "bkui-vue/lib/icon";
import Login from "@/components/layouts/Login.vue";

const state = reactive({
  logoutDropdown: false,
  helpDropdown: false,
  languageDrodown: false,
});
const user = useUser();
const userInfo = ref(user.user);
const headerNav = reactive([
  {
    name: "组织架构",
    path: "organization",
  },
  {
    name: "数据源管理",
    path: "datasource",
  },
  {
    name: "租户管理",
    path: "tenantry",
  },
  {
    name: "审计",
    path: "audit",
  },
  {
    name: "设置",
    path: "setting",
  },
]);
const languageNav = reactive([
  {
    name: "中文",
    icon: "bk-sq-icon icon-yuyanqiehuanzhongwen",
  },
  {
    name: "English",
    icon: "bk-sq-icon icon-yuyanqiehuanyingwen",
  },
]);
const helpNav = reactive([
  {
    name: "产品文档",
    url: "",
  },
  {
    name: "版本日志",
    url: "",
  },
  {
    name: "问题反馈",
    url: "",
  },
]);
const toLink = (item: any) => {
  window.open(item.url, "_blank");
};
</script>

<style lang="less" scoped>
.main-navigation {
  :deep(.bk-navigation-header) {
    background-color: #0e1525;
    .icon-user-logo-i {
      color: #458df4;
      font-size: 28px;
    }
    .title-desc {
      color: #eaebf0;
    }
  }
  :deep(.container-content) {
    padding: 0 !important;
  }

  :deep(.header-right) {
    justify-content: space-between;
  }
}

.main-navigation-left {
  font-size: 14px;
  margin-left: 20px;
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
  color: #96a2b9;
  margin: 0px 10px;
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
    .help-info-icon {
      vertical-align: middle;
    }
    &:hover {
      color: #3a84ff;
      cursor: pointer;
      .help-info-icon {
        display: inline-block;
        transition: all 0.2s;
        transform: rotate(180deg);
      }
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
</style>
