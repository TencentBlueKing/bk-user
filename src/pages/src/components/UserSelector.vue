<template>
  <BkUserSelector
    v-model="value"
    :api-base-url="apiBaseUrl"
    :tenant-id="userStore.user.tenant_id"
    :multiple="multiple"
    :user-group="userGroup"
    :user-group-name="userGroupName"
  />

</template>

<script lang="ts" setup>
import { computed, ref } from 'vue';

import BkUserSelector from '@blueking/bk-user-selector';

import '@blueking/bk-user-selector/vue3/vue3.css';
import { useUser } from '@/store';
const value = defineModel<string | string[]>('value');
defineProps({
  multiple: {
    type: Boolean,
    default: true,
  },
});
const userStore = useUser();
const apiBaseUrl = ref(window.BK_USER_WEB_APIGW_URL);

// 用户组名称
const userGroupName = ref('内置管理员');
const userGroup = computed(() => [
  {
    id: userStore.admin?.bk_username,
    name: userStore.admin?.username,
  },
]);
</script>
