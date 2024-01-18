<template>
  <ul class="details-content">
    <li>
      <div class="details-content-info">
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('用户名') }}：</span>
          <span class="details-content-value">{{ usersData.username }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('全名') }}：</span>
          <span class="details-content-value">{{ usersData.full_name }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('邮箱') }}：</span>
          <span class="details-content-value">{{ usersData.email || '--' }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('手机号') }}：</span>
          <span class="details-content-value">{{ usersData.phone || '--' }}</span>
        </div>
        <div class="details-content-item">
          <bk-overflow-title type="tips" class="details-content-key">{{ $t('所属组织') }}：</bk-overflow-title>
          <bk-overflow-title class="details-content-value" type="tips">
            {{ paths }}
          </bk-overflow-title>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('直属上级') }}：</span>
          <span class="details-content-value" v-if="usersData.leaders.length > 0">
            {{ formatConvert(usersData.leaders) }}
          </span>
          <span class="details-content-value" v-else>{{ '--' }}</span>
        </div>
        <CustomFieldsView :extras="usersData.extras" />
      </div>
      <img v-if="usersData.logo" class="user-logo" :src="usersData.logo" alt="" />
      <img v-else class="user-logo" src="@/images/avatar.png" alt="" />
    </li>
  </ul>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

import CustomFieldsView from '@/components/custom-fields/view.vue';
import { formatConvert } from '@/utils';

defineProps({
  usersData: {
    type: Object,
    default: () => ({}),
  },
  paths: {
    type: String,
    default: '',
  },
});
</script>

<style lang="less" scoped>
@import url("@/css/viewUser.less");
</style>
