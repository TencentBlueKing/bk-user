<template>
  <bk-form form-type="vertical" v-bkloading="{ loading }">
    <div class="switch-tenant" v-if="hasStorage" @click="changeTenant">
      < {{ $t('切换企业') }}
    </div>

    <div class="tenant-logo">
      <img :src="appLogo" />
    </div>

    <section v-if="!hasStorage && !loading">

      <h1 class="login-header">{{ $t('请选择您所属的企业') }}</h1>

      <bk-form-item ref="tenantInputRef">
        <bk-popover
          trigger="manual"
          :is-show="popoverVisible"
          :arrow="false"
          :width="400"
          theme="light"
          placement="bottom-start"
          ext-cls="tenant-popover"
          @clickoutside="handleClickOutside"
        >
          <bk-input
            v-model="inputTenant"
            clearable
            size="large"
            :placeholder="$t('请输入企业ID或名称')"
            @focus="handleTenantFocus"
            @clear="handleClearTenant"
            @keydown="debouncedTenantChange">
          </bk-input>
          <template #content>
            <div class="tenant-options">
              <div class="tenant-option"
                   v-bkloading="{ loading: tenantOptionsLoading }"
                   v-for="item in tenantOptions"
                   :key="item.id"
                   @click="handleSelectTenant(item)">
                {{ item.name }} ({{ item.id }})
              </div>

              <template v-if="tenantList.length && tenantOptions.length === 0">
                <div class="tenant-option-title">{{ $t('上次登录') }}</div>
                <div class="tenant-option" v-for="item in tenantList" :key="item.id" @click="handleSelectTenant(item)">
                  {{ item.name }} ({{ item.id }})
                </div>
              </template>
            </div>
          </template>
        </bk-popover>

        <span class="tenant-input-error" v-if="searchTenantEmpty && !selectedTenant?.id">{{ $t('未匹配到相应企业') }}</span>
      </bk-form-item>

      <bk-form-item>
        <bk-button
          theme="primary"
          size="large"
          class="confirm-btn"
          :disabled="!selectedTenant?.id"
          @click="confirmTenant">
          {{ $t('确定') }}
        </bk-button>
      </bk-form-item>
      <div class="tenant-password">
        <span class="cursor-pointer" @click="protocolVisible = true">{{ $t('用户协议') }} ></span>
      </div>
    </section>

    <section v-else-if="hasStorage">
      <div class="tenant-header">
        <img v-if="selectedTenant?.logo" class="logo-img" :src="selectedTenant?.logo" />
        <span v-else class="logo">
          {{ selectedTenant?.name?.charAt(0).toUpperCase() }}
        </span>
        <bk-overflow-title class="inline-flex tenant-name">
          {{ selectedTenant?.name }} ({{ selectedTenant?.id }})
        </bk-overflow-title>
      </div>

      <section v-if="idpList.length">
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
      <!-- 未完成用户登录配置 -->
      <section v-else>
        <div class="empty-container">
          <img class="empty-img" src="../images/empty.png" />
          <div class="empty-text">{{ $t('该企业未完成用户登录配置') }}</div>
        </div>
      </section>

      <div class="tenant-password">
        <span class="cursor-pointer" @click="protocolVisible = true">{{ $t('用户协议') }} ></span>
        <span
          class="cursor-pointer"
          v-if="activeIdp?.plugin_id === 'local'"
          @click="handleResetPassword">
          {{ $t('忘记密码？') }}
        </span>
      </div>
      <div class="language-switcher">
        <div class="language-select" style="display: flex">
          <p class="language-item" :class="{ active: activeTab === 'zh-cn' }" @click="handleSwitchLocale('zh-cn')">
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
</template>

<script setup lang="ts">
import { getGlobalSettings, getIdpList, getTenantList, searchTenantList } from '@/http/api';
import { type Ref, onBeforeMount, ref, watch, computed } from 'vue';
import Password from './components/password.vue';
import Protocol from './components/protocol.vue';
import useAppStore from '@/store/app';
import CustomLogin from './components/custom-login.vue';
import { platformConfig } from '@/store/platformConfig';
import I18n, { t } from '@/language/index';
import Cookies from 'js-cookie';
import logoPng from '../../static/images/blueking.png';
import { debounce } from 'lodash';

const  platformConfigData = platformConfig();
const appLogo = computed(() => (platformConfigData.appLogo ? platformConfigData.appLogo : logoPng));
const activeTab = ref(I18n.global.locale.value);


interface Item {
  id: string;
  name: string;
}

interface Tenant extends Item {
  logo: string;
}

interface Idp {
  id: string;
  name: string;
  plugin_id: string
}


const appStore = useAppStore();
const loading = ref(false);
// 选中的租户
const selectedTenant = ref<Tenant | null>(null);
// localStorage 中存储的租户列表
const tenantList = ref<Tenant[]>([]);
// 是否存在登录过的租户
const hasStorage = ref(!!localStorage.getItem('tenantId'));
// 是否显示租户选择弹窗
const popoverVisible = ref(false);
// 搜索租户结果是否为空
const searchTenantEmpty = ref(false);
// 租户选择弹窗是否加载中
const tenantOptionsLoading = ref(false);
// 租户选择输入框
const tenantInputRef = ref(null);

/**
 * 输入搜索出的租户
 */
const tenantOptions = ref<Tenant[]>([]);

/**
 * 输入搜索出的租户
 */
const inputTenant = ref(null);

/**
 * 从 localStorage 中加载租户列表
 */
try {
  tenantList.value = JSON.parse(localStorage.getItem('tenantList') || '[]');
  appStore.tenantId = localStorage.getItem('tenantId');
} catch (error) {
  console.log(error);
}

/**
 * 选择/输入租户
 * @param id 租户ID
 */
const handleTenantChange = async () => {
  const id = inputTenant.value;
  console.log('handleTenantChange', id);
  searchTenantEmpty.value = false;
  if (!id) {
    tenantOptions.value = [];
    return;
  }
  tenantOptionsLoading.value = true;
  // popoverVisible.value = false;
  const res = await searchTenantList({
    keyword: id,
  });
  if (res?.length === 0) {
    searchTenantEmpty.value = true;
    popoverVisible.value = false;
    tenantOptions.value = [];
  } else {
    tenantOptions.value = res || [];
    popoverVisible.value = true;
  }
  tenantOptionsLoading.value = false;
};

// 使用 debounce 包装 handleTenantChange 函数，设置 300ms 的延迟
const debouncedTenantChange = debounce(handleTenantChange, 300);

const handleTenantFocus = () => {
  popoverVisible.value = true;
};

const handleClickOutside = ({ event }: { event: Event }) => {
  const target = event.target as HTMLElement;
  if (tenantInputRef.value?.$el.contains(target)) {
    return;
  }
  popoverVisible.value = false;
};

/**
 * 清空租户
 */
const handleClearTenant = () => {
  inputTenant.value = null;
  searchTenantEmpty.value = false;
  popoverVisible.value = false;
  selectedTenant.value = null;
  tenantOptions.value = [];
};

/**
 * 选择租户
 * @param item 租户
 */
const handleSelectTenant = (item: Tenant) => {
  selectedTenant.value = item;
  inputTenant.value = `${item.name}（${item.id}）`;
  popoverVisible.value = false;
};

/**
 * 认证源列表
 */
const idpList: Ref<Idp[]> = ref([]);

/**
 * 当前选中认证源
 */
const activeIdp: Ref<Idp> = ref();


/**
 * 确认登录租户
 */
const confirmTenant = () => {
  const selectedTenantId = selectedTenant.value?.id;
  if (!selectedTenantId) {
    return;
  }
  appStore.tenantId = selectedTenantId;
  localStorage.setItem('tenantId', selectedTenantId);
  if (!tenantList.value.find(item => item.id === selectedTenantId)) {
    tenantList.value.push(selectedTenant.value);
  }
  localStorage.setItem('tenantList', JSON.stringify(tenantList.value));
  hasStorage.value = true;
  getIdps();
};

/**
 * 获取认证源列表
 */
const getIdps = async () => {
  const res = await getIdpList(appStore.tenantId);
  [activeIdp.value] = res;
  idpList.value = res;
  handleChangeIdp(activeIdp.value);
  loading.value = false;
};

/**
 * 切换租户
 */
const changeTenant = () => {
  hasStorage.value = false;
  appStore.tenantId = '';
  selectedTenant.value = null;
  inputTenant.value = null;
};

const handleChangeIdp = (idp: Idp) => {
  activeIdp.value = idp;
};

const protocolVisible = ref(false);

const settings = ref({});

/**
 * 从 localStorage 中加载租户列表
 */
onBeforeMount(async () => {
  loading.value = true;
  getTenantList({
    tenant_ids: tenantList.value.map(item => item.id).join(','),
  }).then((res) => {
    tenantList.value = res;
  });
  if (hasStorage.value) {
    selectedTenant.value = tenantList.value.find(item => item.id === appStore.tenantId);
    getIdps();
  }
  settings.value = await getGlobalSettings();
  loading.value = false;
});

/**
 * 重置密码
 */
const handleResetPassword = () => {
  // 确认环境变量后补充路径
  window.location.href = `${settings.value.bk_user_url}/password/?tenantId=${appStore.tenantId}`;
};

/**
 * 语言切换
 * @param locale 语言
 */
const handleSwitchLocale = (locale: string) => {
  activeTab.value = locale;
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
</script>

<style lang="postcss" scoped>
.switch-tenant {
  font-size: 14px;
  color: #4D4F56;
  line-height: 22px;
  margin-bottom: 6px;
  cursor: pointer;
}

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

.tenant-input-error {
  color: #E71818;
  font-size: 14px;
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
  height: 40px;
  line-height: 40px;
  padding-left: 20px;
  background: #F0F5FF;
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
  font-size: 14px;
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
.confirm-btn {
  width: 100%;
  margin-top: 8px;
}
.tenant-options {
  font-size: 12px;
  line-height: 32px;
  margin: -8px 0;
  min-height: 32px;
}
.tenant-option-title {
  color: #979BA5;
}
.tenant-option {
  height: 32px;
  margin: 0 -12px;
  padding: 0 12px;
  cursor: pointer;

  &:hover {
    background: #f5f7fa;
  }
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

.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.empty-img {
  width: 200px;
  height: 200px;
  margin: 20px 0;
}
.empty-text {
  height: 22px;
  font-size: 14px;
  color: #313238;
  line-height: 22px;
  margin-bottom: 20px;
}
</style>
