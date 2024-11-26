<template>
  <div>
    <!-- 消息通知 -->
    <NoticeComponent v-if="isNoticeEnabled" :api-url="apiUrl" @show-alert-change="showAlertChange" />
    <bk-navigation
      :class="['main-navigation', { 'has-alert': userStore.showAlert }]"
      :hover-width="240"
      navigation-type="top-bottom"
      :need-menu="false"
      :side-title="appName"
      theme-color="#1e2634"
    >
      <template #side-header>
        <div
          style="display: flex; margin-right: 16px; text-decoration: none; align-items: center"
          class="cursor-pointer"
          @click="onGoBack"
        >
          <div class="w-[28px]"><img :src="appLogo" /></div>
          <span class="title-desc">{{ appName}}</span>
        </div>
        <div class="tenant-style" v-if="!isTenant && role !== 'natural_user'">
          <div class="logo">
            <img v-if="userData.logo" :src="userData.logo" alt="">
            <span v-else>{{logoConvert(userData?.name) }}</span>
          </div>
          <bk-overflow-title type="tips" class="tenant-id">{{ userData?.name }}</bk-overflow-title>
          <i
            v-if="role === 'super_manager'"
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
            class="px-[10px]"
            @hide="() => (state.languageDropdown = false)"
            @show="() => (state.languageDropdown = true)"
          >
            <div class="help-info" :class="state.languageDropdown && 'active'">
              <i
                :class="['bk-sq-icon', $i18n.locale === 'en'
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
          <bk-dropdown
            class="px-[10px]"
            @hide="() => (state.helpDropdown = false)"
            @show="() => (state.helpDropdown = true)"
          >
            <div class="help-info" :class="state.helpDropdown && 'active'">
              <i class="user-icon icon-help-document-fill"></i>
            </div>
            <template #content>
              <bk-dropdown-menu>
                <bk-dropdown-item>
                  <a :href="docUrl" target="_blank">{{ $t('产品文档') }}</a>
                </bk-dropdown-item>
                <bk-dropdown-item @click="openVersionLog">
                  <a href="javascript:void(0);">{{ $t('版本日志') }}</a>
                </bk-dropdown-item>
                <bk-dropdown-item>
                  <a :href="feedbackUrl" target="_blank">{{ $t('问题反馈') }}</a>
                </bk-dropdown-item>
              </bk-dropdown-menu>
            </template>
          </bk-dropdown>
          <bk-dropdown
            class="pl-[12px]"
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
    <!-- 版本日志 -->
    <ReleaseNote
      v-model:show="showReleaseNote"
      title-key="version"
      detail-key="content"
      :list="releaseList"
      :loading="releaseLoading"
      :detail="releaseNoteDetail"
      :active="activeVersion" />
  </div>
</template>

<script setup lang="ts">
import { DownShape } from 'bkui-vue/lib/icon';
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute } from 'vue-router';

import NoticeComponent from '@blueking/notice-component';
import ReleaseNote from '@blueking/release-note';

import logo from '../../static/images/logo.png';

import '@blueking/notice-component/dist/style.css';
import '@blueking/release-note/vue3/vue3.css';
import { logout } from '@/common/auth';
import { getTenantInfo, getVersionLogs } from '@/http';
import { t } from '@/language/index';
import router from '@/router';
import { platformConfig, useUser } from '@/store';
import { handleSwitchLocale, logoConvert  } from '@/utils';

const state = reactive({
  logoutDropdown: false,
  helpDropdown: false,
  languageDropdown: false,
});

const userStore = useUser();
const  platformConfigData = platformConfig();
const headerNav = ref([]);
const role = computed(() => userStore.user.role);
const appName = computed(() => platformConfigData.i18n.productName);
const appLogo = computed(() => (platformConfigData.appLogo ?  platformConfigData.appLogo : logo));
const userInfo = computed(() => {
  const baseNav = [
    { name: t('组织架构'), path: 'organization' },
    { name: t('虚拟账号'), path: 'virtual-account' },
    { name: t('操作历史'), path: 'operations-history' },
    { name: t('设置'), path: 'setting' },
  ];

  // 根据变量开启或隐藏虚拟账号页面
  if (window.ENABLE_VIRTUAL_USER === 'False') {
    baseNav?.splice(1, 1);
  }
  if (role.value === 'super_manager' && !isTenant.value) {
    headerNav.value = baseNav;
  } else if (role.value === 'tenant_manager') {
    headerNav.value = baseNav;
  } else if (role.value === 'natural_user') {
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

const toIndividualCenter = () => {
  router.push({
    name: 'personalCenter',
  });
};

const toTenant = () => {
  router.push({ name: 'tenant' });
  headerNav.value = [];
};
const userData = ref({});
const initTenantInfo = async () => {
  const res = await getTenantInfo();
  userData.value = res.data;
};
onMounted(() => {
  if (role.value && role.value !== 'natural_user') {
    initTenantInfo();
  }
});

const onGoBack = () => {
  if (role.value === 'super_manager' && route.name !== 'tenant') {
    router.push({ name: 'tenant' });
    headerNav.value = [];
  } else if (role.value === 'tenant_manager' && route.name !== 'organization') {
    router.push({ name: 'organization' });
  } else if (role.value === 'natural_user') return;
};

// 产品文档
const docUrl = window.BK_USER_DOC_URL;

// 问题反馈
const feedbackUrl = window.BK_USER_FEEDBACK_URL;

// 消息通知配置信息
const apiUrl = `${window.AJAX_BASE_URL}/api/v3/web/notices/announcements/`;
const isNoticeEnabled = window.ENABLE_BK_NOTICE !== 'False';
// 公告列表change事件回调
const showAlertChange = (isShow: boolean) => {
  userStore.setShowAlert(isShow);
};

// 版本日志配置信息
const showReleaseNote = ref(false);
const releaseNoteDetail = ref('');
const releaseLoading = ref(false);
const releaseList = ref([]);
const activeVersion = ref('');
// 获取版本日志
const openVersionLog = async () => {
  showReleaseNote.value = true;
  releaseLoading.value = true;
  try {
    const { data } = await getVersionLogs();
    releaseList.value = data;
    [releaseNoteDetail.value, activeVersion.value] = [data[0].content, data[0].version];
  } catch (e) {
    console.warn(e);
  } finally {
    releaseLoading.value = false;
  }
};
</script>

<style lang="less" scoped>
.has-alert {
  height: calc(100vh - 40px);
}

.main-navigation {
  min-width: 1280px;

  :deep(.bk-navigation-header) {
    background-color: #0e1525;

    .bk-navigation-title {
      // min-width: 280px;
      overflow: initial;


      .tenant-style {
        display: flex;
        height: 16px;
        padding-left: 16px;
        border-left: 1px solid #40454E;
        align-items: center;

        .logo {
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
          max-width: 300px;
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

  :deep(.bk-navigation-wrapper) {
    height: calc(100vh - 52px);
    overflow-y: auto;

    &::-webkit-scrollbar {
      width: 4px;
      background-color: transparent;
    }

    &::-webkit-scrollbar-thumb {
      background-color: #dcdee5;
      border-radius: 4px;
    }
  }

  :deep(.navigation-container) {
    min-width: 1200px;

    .container-content {
      padding: 0 !important;
      overflow-y: hidden !important;
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
    color: #c2cee5;
  }

  &.main-navigation-nav--active {
    color: #fff;
  }
}

.main-navigation-right {
  color: #96a2b9;

  .bk-dropdown {
    .help-info {
      padding: 2px;
      cursor: pointer;
      border-radius: 50%;
    }

    .active {
      background: #252f43;

      .bk-sq-icon, .user-icon {
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
      // color: #3a84ff;
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

    .bk-sq-icon, .user-icon {
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
