<template>
  <bk-form v-show="!isAdminShow" form-type="vertical" v-bkloading="{ loading }">
    <div class="tenant-logo">
      <img :src="appLogo"/>
    </div>

    <section v-if="!hasStorage && !loading">

      <h1 class="login-header">{{ $t('请选择租户与用户来源') }}</h1>

      <bk-form-item>
        <bk-select
          ref="selectRef"
          size="large"
          filterable
          input-search
          allow-create
          :placeholder="$t('请选择租户或输入租户ID')"
          @change="handleTenantChange">
          <bk-option
            v-for="item in showOptions"
            class="tenant-option"
            :id="item.id"
            :key="item.id"
            :name="`${item.name} (${item.id})`">
              <div class="options-show">
                <span>{{ `${item.name} (${item.id})` }}</span>
                <bk-tag v-if="inputTenant?.name" size="small">{{ $t('隐藏租户') }}</bk-tag>
              </div>
          </bk-option>
        </bk-select>
        <span v-if="inputTenant !== null && !inputTenant?.name">{{ $t('暂无匹配租户') }}</span>
      </bk-form-item>

      <bk-form-item>
        <bk-select
          size="large"
          filterable
          :placeholder="$t('请选择用户来源')"
          v-model="userGroup"
        >
          <bk-option
            v-for="item in userGroupList"
            class="tenant-option"
            :id="item.id"
            :key="item.id"
            :name="item.name + $t('成员')">
            {{ `${item.name}${$t('成员')}`}}
          </bk-option>
        </bk-select>
      </bk-form-item>

      <bk-form-item style="margin: -12px 0 20px;">
        <bk-checkbox v-model="trust">{{ $t('记住我的选择') }}</bk-checkbox>
      </bk-form-item>

      <bk-form-item>
        <bk-button
          theme="primary"
          size="large"
          style="width: 100%"
          :disabled="!tenant || !userGroup"
          @click="confirmTenant">
          {{ $t('确认') }}
        </bk-button>
      </bk-form-item>
      <div class="tenant-password">
        <span class="cursor-pointer" @click="protocolVisible = true">{{ $t('用户协议') }} ></span>
      </div>
    </section>

    <section v-else-if="hasStorage">
      <bk-link v-if="hasBuiltin && hasRealUser" @click.prevent="isAdminShow = true" class="admin-login">
        {{ $t('管理员登录') }} >
      </bk-link>
      <div class="tenant-header">
        <img v-if="tenant?.logo" class="logo-img" :src="tenant?.logo" />
        <span v-else class="logo">
          {{ tenant?.name?.charAt(0).toUpperCase() }}
        </span>
        <bk-overflow-title class="inline-flex tenant-name">
          {{ tenant?.name }} / {{ userGroupName }}
        </bk-overflow-title>
        <bk-popover
          v-if="storageTenantList.length && !isOnlyOneTenant"
          trigger="click" theme="light"
          placement="bottom"
          ext-cls="tenant-popover">
          <div class="tenant-change">
            <Transfer class="bk-icon" />
            <span>{{ $t('切换') }}</span>
          </div>
          <template #content>
            <section class="content-list cursor-pointer">
              <div
                class="item"
                v-for="item in storageTenantList"
                :key="item.id"
                @click="handleChangeStorageTenant(item)">
                <span class="item-name">{{ item.name }} / {{ getUserGroupName(item) }}</span>
                <close class="delete-icon" @click.stop="deleteStorageTenant(item)"/>
              </div>
              <div class="add" @click="addTenant">{{ $t('其他租户或用户来源') }}</div>
            </section>
          </template>
        </bk-popover>
        <div v-else-if="!isOnlyOneTenant" class="tenant-change" @click="addTenant">
          <Transfer class="bk-icon" />
          <span>{{ $t('切换') }}</span>
        </div>
      </div>

      <section v-if="hasRealUser">
        <div class="tenant-tab">
          <div
            class="tab-item"
            v-for="item in idpList"
            :class="activeIdp.id === item.id ? 'active' : ''"
            :key="item.id"
            @click="handleChangeIdp(item)">
            {{ item.name }}
          </div>
        </div>

        <Password v-if="activeIdp?.plugin_id === 'local'" :idp-id="activeIdp.id" />
        <custom-login v-else :idp-id="activeIdp.id"></custom-login>
      </section>

      <section v-else-if="!hasRealUser && hasBuiltin">
        <h2 class="h2-title">{{ $t('该租户未完成用户登录的配置，请以管理员模式登录') }}</h2>
        <Password
          v-if="activeIdp?.plugin_id === 'local'"
          is-admin
          :idp-id="activeIdp.id"
        />
      </section>

      <section v-else-if="!hasRealUser && !hasBuiltin" class="unset">
        <div class="unset-logo">
          <img src="../../static/images/unset.svg" />
        </div>
        <div class="unset-header">
          {{ $t(userGroupName === '本租户' ? '当前' : '协同') }}{{ $t('租户未完成用户登录配置，无法登录') }}
        </div>
        <div v-if="userGroupName !== '本租户'" class="unset-content">{{`${$t('协同租户：')}${userGroupName}`}}</div>
      </section>

      <div class="tenant-password">
        <span class="cursor-pointer" @click="protocolVisible = true">{{ $t('用户协议') }} ></span>
        <span
          class="cursor-pointer"
          v-if="hasRealUser && activeIdp?.plugin_id === 'local'"
          @click="handleResetPassword">
          {{ $t('忘记密码？') }}
        </span>
      </div>
      <div class="language-switcher">
        <div class="language-select" style="display: flex">
          <p class="language-item" :class="{ active: activeTab === 'zh-cn' }"  @click="handleSwitchLocale('zh-cn')"> 
            <span id="ch" class="text-active ">中文</span>
          </p>
          <p class="language-item " :class="{ active: activeTab === 'en' }" @click="handleSwitchLocale('en')">
            <span id="en" class="text-active">English</span>
          </p>
        </div>
      </div>
    </section>
    <Protocol v-if="protocolVisible" @close="protocolVisible = false" />
  </bk-form>
  <div v-show="isAdminShow" style="margin-top: -28px">
    <bk-link class="admin-back" @click.prevent="isAdminShow = false">&lt; {{ $t('返回上一级') }}</bk-link>
    <h1 class="admin-title">{{ $t('管理员登录') }}</h1>
    <span class="admin-desc"> {{ tenant?.name }} / {{ userGroupName }} </span>
    <Password is-admin :idp-id="appStore.manageIdpId"></Password>
  </div>
</template>

<script setup lang="ts">
import { getGlobalSettings, getIdpList, getTenantList } from '@/http/api';
import { Transfer, Close} from 'bkui-vue/lib/icon';
import { type Ref, onBeforeMount, ref, watch, computed } from 'vue';
import Password from './components/password.vue';
import Protocol from './components/protocol.vue';
import useAppStore from '@/store/app';
import CustomLogin from './components/custom-login.vue';
import { platformConfig } from '@/store/platformConfig';
import I18n, { t } from '@/language/index';
import Cookies from 'js-cookie';

const  platformConfigData = platformConfig()
const appLogo = computed(() => platformConfigData.appLogo);
const activeTab = ref(I18n.global.locale.value)


interface Item {
  id: string;
  name: string;
}

interface Tenant extends Item {
  name: string;
  logo: string;
  collaboration_tenants: Item[];
}

interface Idp {
  id: string;
  name: string;
  plugin_id: string
  data_source_type: DataSourceType
}

type DataSourceType = 'builtin_management' | 'real';

const appStore = useAppStore();
const loading = ref(false);
const allTenantList: Ref<Tenant[]> = ref([]);
const tenantMap = ref({});
const tenantList = ref<Tenant[]>([]);
const hasStorage = ref(!!localStorage.getItem('userGroup'));

/**
 * 选中的用户群
 */
const userGroup = ref(null);

/**
 * 输入搜索出的租户
 */
const inputTenant = ref(null);
/**
 * 选择/输入租户
 * @param id 租户ID
 */
const handleTenantChange = async (id: string) => {
  // 清空时清空输入租户名称 
  if (!id) {
    inputTenant.value = null;
    return;
  }
  let selected = allTenantList.value.find(item => item.id === id) || inputTenant.value?.find(item => item.id === id);
  if (!selected) {
    const res = await getTenantList({
      tenant_ids: id,
    });
    const searchResult = res[0];
    selected = searchResult;
    inputTenant.value = searchResult;
  } else {
    inputTenant.value = null;
  }
  tenant.value = selected;
  appStore.tenantId = id;
  userGroup.value = null;
};
try {
  tenantMap.value = JSON.parse(localStorage.getItem('tenantMap') || '{}');
} catch (error) {
  console.log(error);
}
const tenant: Ref<Tenant> = ref(null);

const trust = ref(true);

/**
 * 认证源列表
 */
const idpList: Ref<Idp[]> = ref([]);

/**
 * 当前选中认证源
 */
const activeIdp: Ref<Idp> = ref();

/**
 * 是否有实名用户
 */
const hasRealUser = ref(false);

/**
 * 是否有内置管理员认证源
 */
const hasBuiltin = ref(false);

/**
 * 确认登录租户
 */
const confirmTenant = () => {
  if (trust.value) {
    localStorage.setItem('tenantId', appStore.tenantId);
    localStorage.setItem('userGroup', userGroup.value);
    tenantMap.value[appStore.tenantId] = userGroup.value;
    localStorage.setItem('tenantMap', JSON.stringify(tenantMap.value));
  } else {
    // 取消记住选择，需要删除原来已经记住的租户
    tenantMap.value = Object.fromEntries(Object.entries(tenantMap.value).filter(([key]) => key !== appStore.tenantId));
    localStorage.setItem('tenantMap', JSON.stringify(tenantMap.value));
    // 如果tenantMap为空，清除localStorage tenantId，否则设置为第一个
    if (Object.keys(tenantMap.value).length === 0) {
      localStorage.removeItem('tenantId');
    } else {
      localStorage.setItem('tenantId', Object.keys(tenantMap.value)[0]);
    }
  }
  hasStorage.value = true;
  getIdps();
};

/**
 * 获取认证源列表
 */
const getIdps = async () => {
  const res = await getIdpList(
    appStore.tenantId,
    userGroup.value,
  );
  const manageIdp = res.find(item => item.data_source_type === 'builtin_management');
  if (manageIdp) {
    appStore.manageIdpId = manageIdp.id;
    hasBuiltin.value = true;
  } else {
    appStore.manageIdpId = '';
    hasBuiltin.value = false;
  }
  hasRealUser.value = res.some(item => item.data_source_type === 'real');
  idpList.value = res.filter((item) => {
    if (hasRealUser.value) {
      return item.data_source_type !== 'builtin_management';
    }
    // 如果没有实名认证源，就不用过滤内置管理员认证源
    return true;
  });
  [activeIdp.value] = idpList.value;
  handleChangeIdp(activeIdp.value);
  loading.value = false;
};

// 存在登录过的租户
if (hasStorage.value) {
  appStore.tenantId = localStorage.getItem('tenantId');
  userGroup.value = localStorage.getItem('userGroup');
  getTenantList({
    tenant_ids: appStore.tenantId,
  }).then((res) => {
    tenant.value = res[0];
  });
  getIdps();
}

// 新增租户
const addTenant = () => {
  hasStorage.value = false;
  appStore.tenantId = '';
  tenant.value = null;
  userGroup.value = null;
  inputTenant.value = null;
};

/**
 * 本地存储的租户列表
 */
const storageTenantList = computed(() => tenantList.value.filter(item => item.id !== appStore.tenantId));

/**
 * 切换已登录过租户
 * @param item 租户
 */
const handleChangeStorageTenant = (item: Tenant) => {
  appStore.tenantId = item.id;
  tenant.value = item;
  userGroup.value = tenantMap.value[item.id];
  confirmTenant();
};

const handleChangeIdp = (idp: Idp) => {
  activeIdp.value = idp;
};

const protocolVisible = ref(false);

const isOnlyOneTenant = ref(false);

const settings = ref({});

watch(
  () => tenantMap.value,
  (val) => {
    if (Object.keys(val).length === 0) return;
    getTenantList({
      tenant_ids: Object.keys(val).join(','),
    }).then((res) => {
      tenantList.value = res;
    });
  },
  {
    immediate: true,
    deep: true,
  },
);

/**
 * 加载租户列表
 */
onBeforeMount(async () => {
  loading.value = true;
  getTenantList({}).then((res) => {
    allTenantList.value = res;
  })
    .finally(() => {
      loading.value = false;
    });
  settings.value = await getGlobalSettings();
});

/**
 * 用户群列表
 */
const userGroupList = computed(() => {
  let currentTenant = allTenantList.value.find(item => item.id === appStore.tenantId);
  // 通过输入搜索出来的租户，匹配不到用户群，需要从inputTenant获取
  if (inputTenant.value) {
    currentTenant = inputTenant.value;
  }
  const list = currentTenant?.collaboration_tenants || [];
  const current = [{
    id: appStore.tenantId,
    name: '本租户',
  }];
  return current.concat(list);
});

const handleResetPassword = () => {
  // 确认环境变量后补充路径
  window.location.href = `${settings.value.bk_user_url}/password/?tenantId=${appStore.tenantId}`;
};

/**
 * 用户群名称
 */
const userGroupName = computed(() => {
  if (userGroup.value === appStore.tenantId) {
    return '本租户';
  }
  const list = tenant.value?.collaboration_tenants || [];
  const current = list.find(item => item.id === userGroup.value);
  return current?.name || '';
});

/**
 * 获取存储的租户对应的用户群名称
 */
const getUserGroupName = (tenant: Tenant) => {
  const userGroupId = tenantMap.value[tenant.id];
  if (userGroupId === tenant.id) {
    return '本租户';
  }
  return userGroupId
};

/**
 * 管理员登录
 */
const isAdminShow = ref(false);

/**
 * 删除快捷切换项
 */
const deleteStorageTenant = (item: any) => {
  const obj = storageTenantList.value.find(i => i.id === item.id);
  tenantMap.value = Object.fromEntries(Object.entries(tenantMap.value).filter(([key]) => key !== obj.id));
  localStorage.setItem('tenantMap', JSON.stringify(tenantMap.value));
}

const selectRef = ref()

/**
 * 下拉框中的值展示
 */

const showOptions = computed(() => {
  const options = inputTenant.value?.name ? [inputTenant.value]:allTenantList.value
  inputTenant.value?.name && selectRef.value?.showPopover()
  return options
})

// 语言切换
const handleSwitchLocale = (locale: string) => {
  activeTab.value = locale
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
  // window.location.reload();
};
</script>

<style lang="postcss" scoped>
.login-header {
  height: 28px;
  font-size: 20px;
  color: #313238;
  margin-top: 32px;
  margin-bottom: 12px;
}

.tenant-input {
  flex-grow: 1;
}

.tenant-button {
  margin-left: 8px;
  width: 72px;
  height: 40px;
}

.tenant-content {
  font-size: 20px;
  color: #313238;
  line-height: 28px;
}

.tenant-list {
  position: relative;
  background: #E1ECFF;
  height: 40px;
  font-size: 16px;
  line-height: 40px;
  margin: 15px 0;
  padding-left: 20px;
}

.tenant-check {
  position: absolute;
  right: 8px;
  top: 4px;
  font-size: 32px;
  color: #3A84FF;
}

.logo {
  display: inline-block;
  width: 24px;
  margin-right: 8px;
  font-size: 16px;
  font-weight: 700;
  line-height: 24px;
  color: #fff;
  text-align: center;
  background-color: #3A84FF;
  border-radius: 4px;
  flex-shrink: 0;
}

.logo-img {
  width: 24px;
  margin-right: 4px;
  vertical-align: middle;
  padding-bottom: 4px;
}

.admin-login {
  font-size: 14px;
  color: #63656E;
  position: absolute;
  right: 0;
  top: -22px;
  cursor: pointer;
}

.tenant-logo {
  text-align: center;
  img {
    height: 32px;
  }
}

.tenant-header {
  position: relative;
  color: #313238;
  font-size: 16px;
  height: 52px;
  line-height: 52px;
  padding-left: 20px;
  background: #F0F5FF;
  border: 1px solid #A3C5FD;
  border-radius: 2px;
  margin: 32px 0 24px;

  .tenant-name {
    width: 280px;
  }
}

.tenant-change {
  position: absolute;
  right: 12px;
  top: 0;
  height: 100%;
  display: flex;
  align-items: center;
  color: #3A84FF;
  font-size: 14px;
  cursor: pointer;

  .bk-icon {
    margin-right: 4px;
    font-size: 18px;
  }
}

.tenant-tab {
  font-size: 14px;
  color: #63656E;
  line-height: 22px;
  margin-bottom: 24px;
  width: 400px;
  overflow-x: auto;
  white-space: nowrap;

  .tab-item {
    margin-right: 24px;
    cursor: pointer;
    padding-bottom: 10px;
    display: inline-block;

    &.active {
      color: #3A84FF;
      font-size: 16px;
      font-weight: 700;
      border-bottom: 2px solid #3A84FF;
    }
  }
}

.tenant-password {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: -14px;
}

.content-list {
  font-weight: 400;
  font-size: 14px;
  color: #494B50;
  letter-spacing: 0;
  text-align: center;
  min-width: 120px;

  .item {
    position: relative;
    line-height: 36px;
    cursor: pointer;
    margin: 0 -14px;
    padding: 0 14px;

    &:hover {
      color: #3A84FF;
      background: #F5F6F9;
      .delete-icon {
        display: inline-block !important;
      }
    }
    .item-name {
      margin-right: 10px;
    }
    .delete-icon {
      color: #d9dadf;
      display: none !important;
      cursor: pointer;
      position: absolute;
      right: 5px;
    }
  }

  .add {
    border-top: 1px solid #E5E5E5;
    background: #FAFBFD;
    color: #3A84FF;
    line-height: 22px;
    padding: 8px 0;
    cursor: pointer;
    margin: 0 -12px -7px;
  }
}
.tenant-option {
  height: 36px;
  font-size: 14px;
}
.h2-title {
  font-size: 16px;
  color: #313238;
  line-height: 24px;
  margin-bottom: 16px;
}
.unset {
  text-align: center;
  color: #313238;
  margin-bottom: 20px;

  .unset-logo {
    img {
      height: 120px;
    }
  }
  .unset-header {
    font-size: 16px;
    line-height: 22px;
    padding: 8px 0;
  }
  .unset-content {
    font-size: 14px;
  }
}
.admin-back {
  display: inline-block;
  font-size: 14px;
  padding-bottom: 16px;
}
.admin-title {
  font-size: 24px;
  font-weight: bold;
  color: #313238;
  margin-bottom: 12px;
}
.admin-desc {
  display: inline-block;
  height: 22px;
  line-height: 22px;
  font-size: 14px;
  color: #63656E;
  margin-bottom: 24px;
}
.options-show {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.language-item {
  width: 70px;
  text-align: center;
  background: #f5f7fa;
  transform: skew(-15deg, 0deg);
  display: inline-block;
  height: 24px;
  cursor: pointer;
  .text-active {
    display: block;
    width: 70px;
    height: 24px;
    line-height: 24px;
    font-size: 12px;
    transform: skew(15deg, 0deg);
}
}
.language-switcher {
  display: flex;
  border-radius: 2px;
  height: 24px;
  line-height: 24px;
  justify-content: end;
  text-align: right;
  margin-top: 23px;
}
.active {
  background: #e1ecff;
  .text-active {
    color: #3a84ff;
  }
}
</style>
