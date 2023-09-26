<template>
  <bk-form form-type="vertical">
    <section v-if="!tenantVisible && !hasStorage">
      <h1 class="login-header">请选择登录公司</h1>

      <bk-form-item>
        <bk-input
          size="large"
          placeholder="填写公司ID"
          v-model="tenantId"
          @blur="handleGetTenant"
          @enter="handleGetTenant">
        </bk-input>
      </bk-form-item>

      <div v-if="tenant">
        <h2 class="tenant-content">我们为您在平台找到了以下公司</h2>
        <div class="tenant-list">
          <img v-if="tenant.logo" :src="tenant.logo" />
          <span v-else class="logo">
            {{ tenant.name.charAt(0).toUpperCase() }}
          </span>
          {{ tenant.name }}
          <Done class="tenant-check" />
        </div>
      </div>
      <h2 class="tenant-content" v-else-if="tenant !== null">暂无匹配公司</h2>

      <bk-form-item style="margin: 42px 0 0;">
        <bk-checkbox v-model="trust">信任该电脑并保存公司ID</bk-checkbox>
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
        <img v-if="tenant?.logo" :src="tenant?.logo" />
        <span v-else class="logo">
          {{ tenant?.name.charAt(0).toUpperCase() }}
        </span>
        {{ tenant?.name }}
        <bk-popover v-if="changList.length" trigger="click" theme="light" placement="bottom" ext-cls="tenant-popover">
          <div class="tenant-change">
            <Transfer class="bk-icon" />
            <span>切换公司</span>
          </div>
          <template #content>
            <section class="content-list cursor-pointer">
              <div class="item" v-for="item in changList" :key="item.id" @click="handleChange(item)">
                {{ item.name }}
              </div>
              <div class="add" @click="addTenant">新增公司</div>
            </section>
          </template>
        </bk-popover>
        <div v-else class="tenant-change" @click="addTenant">
          <Transfer class="bk-icon" />
          <span>切换公司</span>
        </div>
      </div>

      <div class="tenant-tab">
        <!-- <span class="tab-item active" v-for="item in tenant?.idps" :key="item.id">
          {{ item.name }}登录
        </span> -->

        <span class="tab-item active">
          帐密登录
        </span>
      </div>

      <Password :idp-id="tenant?.idps[0].id" />

      <div>
        <span class="cursor-pointer">用户协议 ></span>
      </div>
    </section>
  </bk-form>
</template>

<script setup lang="ts">
import { getTenant, getTenantList, getVisible, signIn } from '@/http/api';
import { Done, Transfer } from 'bkui-vue/lib/icon';
import { type Ref, onBeforeMount, ref, watch, computed } from 'vue';
import Password from './components/password.vue';

interface Tenant {
  id: string;
  logo: string;
  name: string;
  idps: Idp[];
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

const tenantId = ref('');
const tenantIdList: Ref<string[]> = ref([]);
const tenantList = ref<Tenant[]>([]);
try {
  tenantIdList.value = JSON.parse(localStorage.getItem('tenantIdList') || '[]');
} catch (error) {
  console.log(error);
}
const tenant: Ref<Tenant> = ref(null);
const handleGetTenant = () => {
  if (tenantId.value) {
    getTenant(tenantId.value).then((res) => {
      tenant.value = res;
    });
  } else {
    tenant.value = null;
  }
};

const trust = ref(true);

// 确认登录公司
const confirmTenant = () => {
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
  signIn({ tenant_id: tenantId.value });
};

const tenantVisible = ref(false);
const hasStorage = ref(!!localStorage.getItem('tenantId'));
if (hasStorage.value) {
  tenantId.value = localStorage.getItem('tenantId');
  getTenant(tenantId.value).then((res) => {
    tenant.value = res;
  });
}

// 新增公司
const addTenant = () => {
  hasStorage.value = false;
  tenantId.value = '';
  tenant.value = null;
};

const changList = computed(() => tenantList.value.filter(item => item.id !== tenantId.value));
const handleChange = (item: Tenant) => {
  tenantId.value = item.id;
  tenant.value = item;
  confirmTenant();
};

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
  });
});

</script>

<style lang="less" scoped>
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
  height: 32px;
  margin-bottom: 24px;

  .tab-item {
    margin-right: 24px;
    cursor: pointer;
    padding-bottom: 10px;

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
</style>

<style>
.cursor-pointer {
  cursor: pointer;
}
</style>
