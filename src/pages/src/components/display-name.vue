<template>
  <bk-user-display-name v-if="!isAdmin" :user-id="userId"></bk-user-display-name>
  <span v-else>{{ userStore.admin?.username }}</span>
</template>

<script lang="ts" setup>
import { computed } from 'vue';

import { useUser } from '@/store';

/**
 * @description 用于内置管理员展示的特殊处理
 * @example admin使用bk-user-display-name会展示为admin(admin) 这里直接展示admin
 */

interface IProps {
  userId: string
}

const props = defineProps<IProps>();
const userStore = useUser();

const isAdmin = computed(() => userStore.admin?.id === props.userId);
</script>
