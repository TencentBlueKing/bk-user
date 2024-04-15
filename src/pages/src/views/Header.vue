<template>
  <bk-navigation
    class="main-navigation"
    :hover-width="240"
    navigation-type="top-bottom"
    :need-menu="false"
    :side-title="$t('蓝鲸用户管理')"
    theme-color="#1e2634"
  >
    <template #side-header>
      <div
        style="display: flex; margin-right: 16px; text-decoration: none; align-items: center"
      >
        <i class="user-icon icon-user-logo-i" />
        <span class="title-desc">{{ $t('蓝鲸用户管理') }}</span>
      </div>
      <div class="tenant-style" v-if="!isTenant">
        <span class="logo">{{ logoConvert(userStore.user?.tenant_id) }}</span>
        <span class="tenant-id">{{ userStore.user?.tenant_id }}</span>
        <i
          v-if="userStore.user?.role === 'super_manager'"
          class="user-icon icon-shezhi"
          @click="toTenant"
        />
      </div>
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
          @hide="() => (state.languageDropdown = false)"
          @show="() => (state.languageDropdown = true)"
        >
          <div class="help-info language" :class="state.languageDropdown && 'active'">
            <i :class="['bk-sq-icon', $i18n.locale === 'en'
              ? 'icon-yuyanqiehuanyingwen' : 'icon-yuyanqiehuanzhongwen']" />
          </div>
          <template #content>
            <bk-dropdown-menu>
              <div v-for="(item, index) in languageNav" :key="index">
                <bk-dropdown-item
                  :class="[{ 'active-item': $i18n.locale === item.language }]"
                  @click="handleSwitchLocale(item.language)">
                  <i :class="item.icon" style=" margin-right: 5px;font-size: 16px;"></i>
                  <span>{{ item.name }}</span>
                </bk-dropdown-item>
              </div>
            </bk-dropdown-menu>
          </template>
        </bk-dropdown>
        <!-- <bk-dropdown
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
            <span class="help-info-name">{{ userInfo.display_name }}</span>
            <DownShape class="help-info-icon" />
          </div>
          <template #content>
            <bk-dropdown-menu ext-cls="dropdown-menu-box">
              <bk-dropdown-item
                v-if="!isTenant"
                :class="{ 'active-item': isPersonalCenter }"
                @click="toIndividualCenter">
                {{ $t('个人中心') }}
              </bk-dropdown-item>
              <bk-dropdown-item @click="logout">{{ $t('退出登录') }}</bk-dropdown-item>
            </bk-dropdown-menu>
          </template>
        </bk-dropdown>
      </div>
    </template>
    <router-view></router-view>
  </bk-navigation>
</template>

<script setup lang="ts">
import { DownShape } from 'bkui-vue/lib/icon';
import Cookies from 'js-cookie';
import { computed, reactive, ref } from 'vue';
import { useRoute } from 'vue-router';

import { logout } from '@/common/auth';
import I18n, { t } from '@/language/index';
import router from '@/router';
import { useUser } from '@/store/user';
import { logoConvert } from '@/utils';

const state = reactive({
  logoutDropdown: false,
  helpDropdown: false,
  languageDropdown: false,
});

const userStore = useUser();
const headerNav = ref([]);

const userInfo = computed(() => {
  const { role } = userStore.user;
  const baseNav = [
    { name: t('组织架构'), path: 'organization' },
    { name: t('虚拟账号'), path: 'virtual-account' },
    { name: t('设置'), path: 'setting' },
  ];
  if (role === 'super_manager' && !isTenant.value) {
    headerNav.value = baseNav;
  } else if (role === 'tenant_manager') {
    headerNav.value = baseNav;
  } else if (role === 'natural_user') {
    router.push({ name: 'personalCenter' });
  }
  return userStore.user;
});

const route = useRoute();
const isPersonalCenter = computed(() => route.name === 'personalCenter');
const isTenant = computed(() => route.name === 'tenant');

const languageNav = reactive([
  {
    name: '中文',
    icon: 'bk-sq-icon icon-yuyanqiehuanzhongwen',
    language: 'zh-cn',
  },
  {
    name: 'English',
    icon: 'bk-sq-icon icon-yuyanqiehuanyingwen',
    language: 'en',
  },
]);
// const helpNav = reactive([
//   {
//     name: t('产品文档'),
//     url: '',
//   },
//   {
//     name: t('版本日志'),
//     url: '',
//   },
//   {
//     name: t('问题反馈'),
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

const handleSwitchLocale = (locale: string) => {
  const api = `${window.BK_COMPONENT_API_URL}/api/c/compapi/v2/usermanage/fe_update_user_language/`;
  const scriptId = 'jsonp-script';
  const prevJsonpScript = document.getElementById(scriptId);
  if (prevJsonpScript) {
    document.body.removeChild(prevJsonpScript);
  }
  const script = document.createElement('script');
  script.type = 'text/javascript';
  script.src = `${api}?language=${locale}`;
  script.id = scriptId;
  document.body.appendChild(script);

  Cookies.set('blueking_language', locale, {
    expires: 3600,
    path: '/',
    domain: window.BK_DOMAIN,
  });
  I18n.global.locale.value = locale as any;
  document.querySelector('html')?.setAttribute('lang', locale);
  window.location.reload();
};

const toTenant = () => {
  router.push({ name: 'tenant' });
  headerNav.value = [];
};
</script>

<style lang="less" scoped>
.main-navigation {
  min-width: 1200px;

  :deep(.bk-navigation-header) {
    background-color: #0e1525;

    .bk-navigation-title {
      min-width: 280px;
      overflow: initial;


      .tenant-style {
        display: flex;
        height: 16px;
        padding-left: 16px;
        border-left: 1px solid #40454E;
        align-items: center;

        .logo {
          display: inline-block;
          width: 16px;
          font-size: 12px;
          font-weight: 700;
          line-height: 16px;
          color: #fff;
          text-align: center;
          background: #1CAB88;
          border-radius: 4px;
        }

        .tenant-id {
          margin: 0 8px 0 4px;
          color: #FFF;
        }

        .icon-shezhi {
          font-size: 14px;
          color: #3A84FF;
          cursor: pointer;
        }
      }
    }

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
  // margin: 0 10px;
  color: #96a2b9;

  .bk-dropdown {
    // padding: 0 10px;

    .help-info {
      padding: 5px;
      cursor: pointer;
      border-radius: 50%;
    }

    .language {
      margin: 0 10px;
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

.active-item {
  color: #3a84ff !important;
  background-color: #E1ECFF;

  &:hover {
    background-color: #E1ECFF !important;
  }
}
</style>
