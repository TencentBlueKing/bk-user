<template>
  <bk-form form-type="vertical" v-bkloading="{ loading }">
    <div class="switch-tenant" v-if="hasStorage" @click="changeTenant">
      &lt; {{ $t('切换企业') }}
    </div>

    <div class="tenant-logo">
      <img :src="appLogo" />
    </div>

    <section v-if="!hasStorage && !loading">
      <h1 class="login-header">{{ $t('请输入您所属的企业') }}</h1>

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
            class="bk-user-tenant-input"
            clearable
            size="large"
            :placeholder="$t('请输入企业ID或名称')"
            @focus="handleTenantFocus"
            @clear="handleClearTenant"
            @input="debouncedTenantChange"
            @keydown="(value: string, event: KeyboardEvent) => handleTenantKeydown(value, event)">
          </bk-input>
          <template #content>
            <div
              class="tenant-options"
              v-bkloading="{ loading: searchTenantListLoading, mode: 'spin', size: 'mini' }">
              <template v-if="inputTenant">
                <div
                  class="tenant-option-container"
                  v-for="item in searchTenantList"
                  :key="item.id"
                  @click="handleSelectTenant(item)">
                  <div class="tenant-option">
                    <img v-if="item?.logo" class="logo-img small" :src="item?.logo" />
                    <span v-else class="logo small">
                      {{ item?.name?.charAt(0).toUpperCase() }}
                    </span>
                    <span>{{ item.name }} ({{ item.id }})</span>
                  </div>
                </div>
                <div v-if="searchTenantList.length === 0" class="tenant-option-title">{{ $t('未匹配到相应企业，请检查输入内容是否完整和正确') }}</div>
              </template>

              <template v-else-if="tenantList.length">
                <div class="tenant-option-header">
                  <span class="tenant-option-title">{{ $t('最近登录') }}</span>
                  <span class="clear-all-btn" @click="handleClearAllTenants">{{ $t('清空') }}</span>
                </div>
                <div class="tenant-option-container"
                     v-for="item in tenantList"
                     :key="item.id"
                     @click="handleSelectTenant(item)">
                  <div class="tenant-option">
                    <img v-if="item?.logo" class="logo-img small" :src="item?.logo" />
                    <span v-else class="logo small">
                      {{ item?.name?.charAt(0).toUpperCase() }}
                    </span>
                    <span>{{ item.name }} ({{ item.id }})</span>
                  </div>
                  <div class="delete-btn" @click.stop="handleDeleteTenant(item)">
                    <CloseLine />
                  </div>
                </div>
              </template>
            </div>
          </template>
        </bk-popover>

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
        <div class="tenant-tab" v-if="idpList.length > 1">
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

    </section>
    <div
      class="cursor-pointer reset-password"
      v-if="hasStorage && activeIdp?.plugin_id === 'local'"
      @click="handleResetPassword">
      {{ $t('忘记密码？') }}
    </div>

  </bk-form>
</template>

<script setup lang="ts">
import { getGlobalSettings, getIdpList, getTenantList, getSearchTenantList } from '@/http/api';
import { type Ref, onBeforeMount, ref, computed, watch } from 'vue';
import Password from './components/password.vue';
import useAppStore from '@/store/app';
import CustomLogin from './components/custom-login.vue';
import { platformConfig } from '@/store/platformConfig';
import logoPng from '../../static/images/blueking.png';
import { debounce } from 'lodash';
import { CloseLine } from 'bkui-vue/lib/icon';

// 平台配置数据
const platformConfigData = platformConfig();
const appLogo = computed(() => (platformConfigData.appLogo ? platformConfigData.appLogo : logoPng));

// 接口定义
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
  plugin_id: string;
}

/**
 * 应用状态管理
 */
const appStore = useAppStore();
/**
 * 加载状态
 */
const loading = ref(false);
/**
 * 当前选中的企业
 */
const selectedTenant = ref<Tenant | null>(null);
/**
 * 最近登录的企业列表，从 localStorage 中加载
 */
const tenantList = ref<Tenant[]>([]);
/**
 * 是否存在 localStorage 中的企业列表
 */
const hasStorage = ref(!!localStorage.getItem('tenantId'));
/**
 * 输入的企业ID或名称
 */
const inputTenant = ref(null);
/**
 * 企业列表下拉框是否显示
 */
const popoverVisible = ref(false);
/**
 * 搜索的企业列表加载状态
 */
const searchTenantListLoading = ref(false);
/**
 * 企业列表输入框
 */
const tenantInputRef = ref(null);
/**
 * 搜索的企业列表
 */
const searchTenantList = ref<Tenant[]>([]);
/**
 * 认证源列表
 */
const idpList: Ref<Idp[]> = ref([]);
/**
 * 当前认证源
 */
const activeIdp: Ref<Idp> = ref();
/**
 * 全局配置
 */
const settings = ref<Record<string, any>>({});

// 从 localStorage 中加载租户列表
try {
  tenantList.value = JSON.parse(localStorage.getItem('tenantList') || '[]');
  appStore.tenantId = localStorage.getItem('tenantId');
} catch (error) {
  console.error('Failed to load tenant list from localStorage:', error);
}

/**
 * 处理租户搜索
 */
const handleTenantChange = async () => {
  selectedTenant.value = null;
  const id = inputTenant.value?.trim();
  searchTenantList.value = [];
  if (!id) {
    searchTenantListLoading.value = false;
    return;
  }
  popoverVisible.value = true;
  searchTenantListLoading.value = true;
  const res = await getSearchTenantList({
    keyword: id,
  });
  searchTenantList.value = res || [];
  searchTenantListLoading.value = false;
};

/**
 * 监听 inputTenant 的变化，增加 loading，避免 debounce 产生的等待
 */
watch(inputTenant, (value) => {
  searchTenantListLoading.value = true;
  if (tenantList.value.length === 0 && !value) {
    popoverVisible.value = false;
  }
}, {
  immediate: true,
});

// 使用 debounce 包装 handleTenantChange 函数，设置 500ms 的延迟
const debouncedTenantChange = debounce(handleTenantChange, 500);

/**
 * 处理租户输入框焦点
 */
const handleTenantFocus = () => {
  searchTenantListLoading.value = true;
  if (tenantList.value.length) {
    popoverVisible.value = true;
  }
  // 处理组件库的 bug，loading 不设置隐藏会遮挡下拉框
  setTimeout(() => {
    searchTenantListLoading.value = false;
  }, 100);
};

/**
 * 处理点击外部事件
 */
const handleClickOutside = ({ event }: { event: Event }) => {
  const target = event.target as HTMLElement;
  if (tenantInputRef.value?.$el.contains(target)) {
    return;
  }
  popoverVisible.value = false;
};

/**
 * 清空租户输入
 */
const handleClearTenant = () => {
  inputTenant.value = null;
  popoverVisible.value = false;
  selectedTenant.value = null;
  searchTenantList.value = [];
};

/**
 * 选择租户
 * @param item 租户信息
 */
const handleSelectTenant = (item: Tenant) => {
  selectedTenant.value = item;
  inputTenant.value = `${item.name}（${item.id}）`;
  popoverVisible.value = false;
  searchTenantList.value = [];
};

/**
 * 删除单个租户
 * @param item 租户信息
 */
const handleDeleteTenant = (item: Tenant) => {
  tenantList.value = tenantList.value.filter(i => i.id !== item.id);
  localStorage.setItem('tenantList', JSON.stringify(tenantList.value));

  // 如果删除的是当前登录的租户，需要重新登录
  if (localStorage.getItem('tenantId') === item.id || appStore.tenantId === item.id) {
    appStore.tenantId = '';
    localStorage.removeItem('tenantId');
    hasStorage.value = false;
  }

  // 如果删除后没有租户，则隐藏下拉框
  if (tenantList.value.length === 0) {
    popoverVisible.value = false;
  }
};

/**
 * 清空所有最近登录的租户
 */
const handleClearAllTenants = () => {
  tenantList.value = [];
  localStorage.removeItem('tenantList');
  localStorage.removeItem('tenantId');
  hasStorage.value = false;
  appStore.tenantId = '';
  selectedTenant.value = null;
  inputTenant.value = null;
  popoverVisible.value = false;
};

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
 * 切换企业
 */
const changeTenant = () => {
  hasStorage.value = false;
  appStore.tenantId = '';
  selectedTenant.value = null;
  inputTenant.value = null;
  popoverVisible.value = false;
  searchTenantList.value = [];
};

/**
 * 切换认证源
 * @param idp 认证源信息
 */
const handleChangeIdp = (idp: Idp) => {
  activeIdp.value = idp;
};

/**
 * 重置密码
 */
const handleResetPassword = () => {
  window.location.href = `${settings.value.bk_user_url}/password/?tenantId=${appStore.tenantId}`;
};

// 组件挂载前初始化
onBeforeMount(async () => {
  loading.value = true;
  // 兼容之前版本，之前版本没有 tenantList 数据
  if (appStore.tenantId && !tenantList.value.length) {
    tenantList.value = [{
      id: appStore.tenantId,
      name: '',
      logo: '',
    }];
  }
  if (tenantList.value.length) {
    getTenantList({
      tenant_ids: tenantList.value.map(item => item.id).join(','),
    }).then((res) => {
      tenantList.value = res;
      if (hasStorage.value) {
        selectedTenant.value = tenantList.value.find(item => item.id === appStore.tenantId);
        getIdps();
      }
    });
  }
  settings.value = await getGlobalSettings();
  loading.value = false;
});

/**
 * 处理租户输入框按键
 */
const handleTenantKeydown = (value: string, event: KeyboardEvent) => {
  // 判断是否为回车键
  if (event.key === 'Enter') {
    if (searchTenantList.value.length === 1) {
      handleSelectTenant(searchTenantList.value[0]);
      confirmTenant();
    }
  }
};
</script>

<style lang="postcss" scoped>
.switch-tenant {
  font-size: 14px;
  color: #4D4F56;
  line-height: 22px;
  margin-bottom: 6px;
  cursor: pointer;
  margin-top: -28px;
}

.login-header {
  height: 28px;
  font-size: 20px;
  color: #313238;
  margin-top: 32px;
  margin-bottom: 12px;
}

.tenant-input-error {
  color: #E71818;
  font-size: 14px;
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

  &.small {
    width: 16px;
    font-size: 11px;
    line-height: 16px;
    margin-right: 0;
  }
}

.logo-img {
  width: 24px;
  margin-right: 4px;
  vertical-align: middle;
  padding-bottom: 4px;

  &.small {
    width: 16px;
  }
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

.reset-password {
  margin-top: -14px;
  text-align: right;
  font-size: 14px;
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

.tenant-option-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tenant-option-title {
  color: #979BA5;
}

.clear-all-btn {
  cursor: pointer;
  color: #979BA5;

  &:hover {
    color: #3A84FF;
  }
}

.tenant-option-container {
  height: 32px;
  margin: 0 -12px;
  padding: 0 12px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;

  &:hover {
    background: #f5f7fa;

    .delete-btn {
      opacity: 1;
    }
  }
}

.delete-btn {
  opacity: 0;
  cursor: pointer;
  color: #979BA5;
  padding: 0 6px;
  margin-top: 1px;

  &:hover {
    color: #3A84FF;
  }
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
