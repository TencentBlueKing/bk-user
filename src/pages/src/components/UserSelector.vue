<template>
  <BkUserSelector
    v-if="showAdmin"
    v-model="value"
    :api-base-url="apiBaseUrl"
    :tenant-id="userStore.user.tenant_id"
    :multiple="multiple"
    :user-group="userGroup"
    :user-group-name="userGroupName"
    :exclude-user-ids="excludeUserIds"
  />
  <BkUserSelector
    v-else
    v-model="value"
    :api-base-url="apiBaseUrl"
    :tenant-id="userStore.user.tenant_id"
    :multiple="multiple"
    :exclude-user-ids="excludeUserIds"
  />
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue';

import BkUserSelector from '@blueking/bk-user-selector';

import '@blueking/bk-user-selector/vue3/vue3.css';
import { t } from '@/language';
import { useUser } from '@/store';

interface UserSelectorProps {
  multiple?: boolean;
  showAdmin?: boolean;
  excludeUserIds?: string[];
}

const value = defineModel<string | string[]>('value');
withDefaults(defineProps<UserSelectorProps>(), {
  multiple: true,
  showAdmin: true,
  excludeUserIds: () => [],
});
const userStore = useUser();
const apiBaseUrl = ref(window.BK_USER_WEB_APIGW_URL);

// 用户组名称
const userGroupName = ref(t('内置管理员'));
const userGroup = computed(() => [
  {
    id: userStore.admin?.id,
    name: userStore.admin?.username,
  },
]);
</script>
