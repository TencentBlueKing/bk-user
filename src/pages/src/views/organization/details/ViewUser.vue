<template>
  <ul class="details-content">
    <li>
      <div class="details-content-info">
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('用户ID') }}：</span>
          <span class="details-content-value">{{ userData.id }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('用户名') }}：</span>
          <span class="details-content-value">{{ userData.username }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('姓名') }}：</span>
          <span class="details-content-value">{{ userData.full_name }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('邮箱') }}：</span>
          <span class="details-content-value">{{ userData.email || '--' }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('手机号') }}：</span>
          <span class="details-content-value">{{ userData.phone || '--' }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('所属组织') }}：</span>
          <span class="details-content-value" v-if="userData.departments.length > 0"
            v-bk-tooltips="{content: (userData.organization_paths || []).join('\n'),
            placement: 'top',
            disabled: userData.departments.length === 0}"
          >
            <!-- {{ formatConvert(userData.departments) }} -->
            {{detail.organization_paths}}
            {{ userData.departments.join('、') || '--' }}
          </span>
          <span class="details-content-value" v-else>{{ '--' }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('直属上级') }}：</span>
          <span class="details-content-value" v-if="(detail.leaders || []).length > 0">
            {{ formatConvert(detail.leaders) || '--' }}
          </span>
          <span class="details-content-value" v-else>{{ '--' }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('账号过期时间') }}：</span>
          <span class="details-content-value">{{ detail.account_expired_at }}</span>
        </div>
        <CustomFieldsView :extras="detail.extras" />
      </div>
      <img v-if="userData.logo" class="user-logo" :src="detail.logo" alt="" />
      <img v-else class="user-logo" src="@/images/avatar.png" alt="" />
    </li>
  </ul>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

import CustomFieldsView from '@/components/custom-fields/view.vue';
import { dateConvert, formatConvert } from '@/utils';

defineProps({
  userData: {
    type: Object,
    default: () => ({}),
  },
  detail: {
    type: Object,
    default: () => ({})
  }
});
</script>

<style lang="less" scoped>
@import url("@/css/viewUser.less");
</style>
