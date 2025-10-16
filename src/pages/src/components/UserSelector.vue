<template>
  <BkUserSelector
    v-model="value"
    :api-base-url="apiBaseUrl"
    :tenant-id="userStore.user.tenant_id"
    :multiple="multiple"
  />

</template>

<script lang="ts" setup>
import { ref } from 'vue';

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
</script>
