<template>
  <ul class="details-content">
    <li>
      <div class="details-content-info">
        <div class="details-content-item">
          <span class="details-content-key">用户名：</span>
          <span class="details-content-value">{{ usersData.username }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">全名：</span>
          <span class="details-content-value">{{ usersData.full_name }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">邮箱：</span>
          <span class="details-content-value">{{ usersData.email }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">手机号：</span>
          <span class="details-content-value">{{ usersData.phone }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">所属组织：</span>
          <span class="details-content-value" v-if="usersData.departments.length > 0">
            {{ formatConvert(usersData.departments) }}
          </span>
          <span class="details-content-value" v-else>{{ '--' }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">直属上级：</span>
          <span class="details-content-value" v-if="usersData.leaders.length > 0">
            {{ formatConvert(usersData.leaders) }}
          </span>
          <span class="details-content-value" v-else>{{ '--' }}</span>
        </div>
      </div>
      <img v-if="usersData.logo" class="user-logo" :src="usersData.logo" alt="" />
      <img v-else class="user-logo" src="@/images/avatar.png" alt="" />
    </li>
  </ul>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

import { formatConvert } from '@/utils';

defineProps({
  usersData: {
    type: Object,
    default: () => ({}),
  },
});
</script>

<style lang="less" scoped>
@import url("@/css/viewUser.less");
</style>
