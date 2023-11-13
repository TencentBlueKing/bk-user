<template>
  <bk-form form-type="vertical">
    <section v-if="!hasStorage">
      <h1 class="login-header">请选择登录租户</h1>

      <bk-form-item>
        <bk-input
          v-if="!tenantVisible"
          size="large"
          placeholder="填写租户ID"
          v-model="tenantId"
          @blur="handleGetTenant"
          @enter="handleGetTenant">
        </bk-input>

        <bk-select v-else size="large" filterable @change="handleTenantChange">
          <bk-option
            v-for="item in allTenantList"
            class="tenant-option"
            :id="item.id"
            :key="item.id"
            :value="item.id">
            {{ item.name }}
          </bk-option>
        </bk-select>
      </bk-form-item>

      <template v-if="!tenantVisible">
        <div v-if="tenant">
          <h2 class="tenant-content">我们为你在平台找到了以下租户</h2>
          <div class="tenant-list">
            <img v-if="tenant.logo" class="logo-img" :src="tenant.logo" />
            <span v-else class="logo">
              {{ tenant.name.charAt(0).toUpperCase() }}
            </span>
            {{ tenant.name }}
            <Done class="tenant-check" />
          </div>
        </div>
        <h2 class="tenant-content" v-else-if="tenant !== null">暂无匹配租户</h2>
      </template>

      <bk-form-item style="margin: 42px 0 0;">
        <bk-checkbox v-model="trust">信任该电脑并保存租户ID</bk-checkbox>
      </bk-form-item>

      <bk-form-item>
        <bk-button
          theme="primary"
          size="large"
          style="width: 100%"
          :disabled="!tenant"
          @click="confirmTenant">
          确认并登录
        </bk-button>
      </bk-form-item>
    </section>

    <section v-else-if="hasStorage">
      <div class="tenant-logo">
        <img src="../../static/images/blueking.png" />
      </div>

      <div class="tenant-header">
        <img v-if="tenant?.logo" class="logo-img" :src="tenant?.logo" />
        <span v-else class="logo">
          {{ tenant?.name.charAt(0).toUpperCase() }}
        </span>
        {{ tenant?.name }}
        <bk-popover v-if="changList.length" trigger="click" theme="light" placement="bottom" ext-cls="tenant-popover">
          <div class="tenant-change">
            <Transfer class="bk-icon" />
            <span>切换租户</span>
          </div>
          <template #content>
            <section class="content-list cursor-pointer">
              <div class="item" v-for="item in changList" :key="item.id" @click="handleChange(item)">
                {{ item.name }}
              </div>
              <div class="add" @click="addTenant">新增租户</div>
            </section>
          </template>
        </bk-popover>
        <div v-else class="tenant-change" @click="addTenant">
          <Transfer class="bk-icon" />
          <span>切换租户</span>
        </div>
      </div>

      <div class="tenant-tab">
        <div
          class="tab-item"
          v-for="item in idps.slice(0, 1)"
          :class="activeIdp.id === item.id ? 'active' : ''"
          :key="item.id"
          @click="activeIdp = item">
          {{ item.name }}登录
        </div>
      </div>

      <Password v-if="activeIdp?.plugin.id === 'local'" :idp-id="activeIdp.id" />

      <div>
        <span class="cursor-pointer" @click="protocolVisible = true">用户协议 ></span>
      </div>

      <Protocol v-if="protocolVisible" @close="protocolVisible = false" />
    </section>
  </bk-form>
</template>

<script setup lang="ts">
import { getAllTenantList, getIdpList, getTenant, getTenantList, getVisible, signIn } from '@/http/api';
import { Done, Transfer } from 'bkui-vue/lib/icon';
import { type Ref, onBeforeMount, ref, watch, computed } from 'vue';
import Password from './components/password.vue';
import Protocol from './components/protocol.vue';

interface Tenant {
  id: string;
  logo: string;
  name: string;
}

interface Idp {
  id: string;
  name: string;
  plugin: Plugin
}

interface Plugin {
  id: string;
  name: string;
  category: Category;
}

type Category = 'enterprise' | 'social';

const allTenantList: Ref<Tenant[]> = ref([]);
const tenantId = ref('');
const tenantIdList: Ref<string[]> = ref([]);
const tenantList = ref<Tenant[]>([]);

// 选择租户
const handleTenantChange = (id: string) => {
  tenant.value = allTenantList.value.find(item => item.id === id);
  tenantId.value = id;
};
try {
  tenantIdList.value = JSON.parse(localStorage.getItem('tenantIdList') || '[]');
} catch (error) {
  console.log(error);
}
const tenant: Ref<Tenant> = ref(null);

// 通过租户ID获取租户信息
const handleGetTenant = () => {
  if (tenantId.value) {
    getTenant(tenantId.value).then((res) => {
      tenant.value = res;
    })
      .catch((error) => {
        tenant.value = error.data;
      });
  } else {
    tenant.value = null;
  }
};

const trust = ref(true);
const idps: Ref<Idp[]> = ref([]);
const activeIdp: Ref<Idp> = ref();

// 确认登录租户
const confirmTenant = async () => {
  if (trust.value) {
    localStorage.setItem('tenantId', tenantId.value);
    if (!tenantIdList.value.includes(tenantId.value)) {
      tenantIdList.value = tenantIdList.value.concat(tenantId.value);
      localStorage.setItem('tenantIdList', JSON.stringify(tenantIdList.value));
    }
    hasStorage.value = true;
  } else {
    hasStorage.value = true;
  }
  signInAndFetchIdp();
};

// 存在登录过的租户，要先signIn，再获取idp列表
const signInAndFetchIdp = async () => {
  await signIn({ tenant_id: tenantId.value });
  const res = await getIdpList();
  idps.value = res;
  [activeIdp.value] = res;
};

const tenantVisible = ref(false);
const hasStorage = ref(!!localStorage.getItem('tenantId'));

// 存在登录过的租户
if (hasStorage.value) {
  tenantId.value = localStorage.getItem('tenantId');
  getTenant(tenantId.value).then((res) => {
    tenant.value = res;
  });
  signInAndFetchIdp();
}

// 新增租户
const addTenant = () => {
  hasStorage.value = false;
  tenantId.value = '';
  tenant.value = null;
};

const changList = computed(() => tenantList.value.filter(item => item.id !== tenantId.value));
// 切换已登录过租户
const handleChange = (item: Tenant) => {
  tenantId.value = item.id;
  tenant.value = item;
  confirmTenant();
};

const protocolVisible = ref(false);

watch(
  () => tenantIdList.value,
  (val) => {
    if (val.length === 0) return;
    getTenantList(val.join(',')).then((res) => {
      tenantList.value = res;
    });
  },
  { immediate: true },
);
onBeforeMount(() => {
  getVisible().then((res) => {
    tenantVisible.value = res.tenant_visible;
    if (res.tenant_visible) {
      getAllTenantList().then((res) => {
        allTenantList.value = res;
      });
    }
  });
});

</script>

<style lang="postcss" scoped>
.login-header {
  height: 42px;
  font-weight: 700;
  font-size: 32px;
  color: #313238;
  margin-bottom: 32px;
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
}

.tenant-change {
  position: absolute;
  right: 20px;
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

.content-list {
  font-weight: 400;
  font-size: 14px;
  color: #494B50;
  letter-spacing: 0;
  text-align: center;
  min-width: 120px;

  .item {
    line-height: 36px;
    cursor: pointer;
    margin: 0 -14px;
    padding: 0 14px;

    &:hover {
      color: #3A84FF;
      background: #F5F6F9;
    }
  }

  .add {
    border-top: 1px solid #E5E5E5;
    background: #FAFBFD;
    color: #3A84FF;
    line-height: 22px;
    padding: 8px 0;
    cursor: pointer;
    margin: 0 -14px -7px;
  }
}
.tenant-option {
  height: 36px;
  font-size: 14px;
}
</style>

<style>
.cursor-pointer {
  cursor: pointer;
}
</style>
