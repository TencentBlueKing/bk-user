<template>
  <div class="details-info-wrapper user-scroll-y">
    <ul class="details-info-content" v-if="!isEdit">
      <li class="content-item">
        <div class="item-header">
          <p class="item-title">基本信息</p>
          <bk-button
            outline
            theme="primary"
            :disabled="!isCurrentTenant"
            @click="handleClickEdit">
            编辑
          </bk-button>
        </div>
        <ul class="item-content flex" style="width: 72%">
          <li>
            <span class="key">租户名称：</span>
            <span class="value">{{ state.name }}</span>
          </li>
          <li>
            <span class="key">人员数量：</span>
            <span class="value">{{ userNumberVisible }}</span>
          </li>
          <li>
            <span class="key">租户ID：</span>
            <span class="value">{{ state.id }}</span>
          </li>
          <li>
            <span class="key">更新时间：</span>
            <span class="value">{{ state.updated_at }}</span>
          </li>
          <img v-if="state.logo" :src="state.logo" />
          <img v-else src="@/images/avatar.png" />
        </ul>
      </li>
      <li class="content-item">
        <div class="item-title">管理员</div>
        <bk-table
          class="user-info-table"
          :data="state.managers"
          show-overflow-tooltip
        >
          <template #empty>
            <Empty :is-data-empty="state.isDataEmpty" />
          </template>
          <bk-table-column prop="username" label="用户名" />
          <bk-table-column prop="full_name" label="全名" />
          <bk-table-column prop="email" label="邮箱">
            <template #default="{ row }">
              <span>{{ row.email || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column prop="phone" label="手机号">
            <template #default="{ row }">
              <span>{{ row.phone || '--' }}</span>
            </template>
          </bk-table-column>
        </bk-table>
      </li>
    </ul>
    <EditInfo
      v-else
      :tenants-data="state"
      :managers="state.managers"
      @handleCancel="handleCancel"
      @updateTenantsList="updateTenantsList" />
  </div>
</template>

<script setup lang="ts">
import { computed, defineEmits, defineProps, reactive, watch } from 'vue';

import EditInfo from './EditDetailsInfo.vue';

import Empty from '@/components/Empty.vue';
import { useUser } from '@/store/user';

const userStore = useUser();
const props = defineProps({
  userData: {
    type: Object,
    default: {},
  },
  isEdit: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['updateTenantsList', 'handleCancel', 'changeEdit']);

const state = reactive({
  ...props.userData || {},
  isDataEmpty: false,
});

const userNumberVisible = computed(() => (props?.userData?.feature_flags?.user_number_visible ? '显示' : '隐藏'));
const isCurrentTenant = computed(() => props?.userData?.id && props?.userData?.id === userStore.user.tenant_id);

watch(() => props.userData.managers, (value) => {
  if (value.length > 0) {
    state.managers = props.userData.managers;
    state.isDataEmpty = false;
  } else {
    state.isDataEmpty = true;
  }
});

const handleClickEdit = () => {
  emit('changeEdit', true);
  window.changeInput = true;
};

const handleCancel = () => {
  emit('handleCancel');
  emit('changeEdit', false);
  window.changeInput = false;
};

const updateTenantsList = () => {
  emit('updateTenantsList');
  handleCancel();
};
</script>

<style lang="less" scoped>
@import url("@/css/tenantViewStyle.less");
</style>
