<template>
  <div class="h-full bg-[#fff]">
    <div class="p-[16px]">
      <div class="flex h-[40px] px-[10px] leading-[40px] bg-[#F0F1F5] rounded-[2px] items-center">
        <i class="bk-sq-icon icon-personal-user text-[16px] text-[#979BA5]" />
        <bk-overflow-title type="tips" class="max-w-[120px] ml-[8px] text-[14px] font-bold">
          {{ currentNaturalUser.full_name }}
        </bk-overflow-title>
        <!-- <bk-overflow-title type="tips" class="min-w-[120px] text-[#979BA5]">
          （{{ currentUserId }}）
        </bk-overflow-title> -->
        <!-- <i class="user-icon icon-edit" /> -->
      </div>
    </div>
    <div class="flex justify-between items-center p-[16px] pt-0">
      <p>
        <span class="mr-[8px] text-[14px]">{{ $t('已关联账号') }}</span>
        <span
          class="inline-block h-[16px] px-[8px] leading-[16px] text-[#979ba5] text-center bg-[#f0f1f5] rounded-[8px]">
          {{ currentNaturalUser.tenant_users?.length }}
        </span>
      </p>
      <!-- <bk-button theme="primary" text class="text-[14px]">
        <i class="user-icon icon-add-2 mr8" />
        新增关联
      </bk-button> -->
    </div>
    <ul>
      <li
        v-for="(item, index) in currentNaturalUser.tenant_users"
        :key="index"
        class="pl-[24px] pr-[12px] hover:bg-[#f0f1f5]"
        :class="{ 'bg-[#e1ecff] hover:bg-[#e1ecff]': currentUserId === item.id }"
        @click="handleClickItem(item)"
      >
        <div class="flex items-center justify-between h-[40px] leading-[40px] cursor-pointer">
          <div class="w-4/5 flex items-center">
            <img
              v-if="item.logo"
              class="inline-block w-[22px] h-[22px] align-middle object-contain"
              :src="item.logo" />
            <i
              v-else
              class="user-icon icon-yonghu p-[3px] text-[16px] text-[#FAFBFD] bg-[#DCDEE5] rounded-[2px]">
            </i>
            <span
              class="inline-block mx-[8px] text-[14px] text-[#313238] text-overflow"
              v-bk-tooltips="{ content: item.full_name }">
              {{ item.full_name }}
            </span>
            <span
              class="inline-block text-[#ff9c01] text-overflow"
              v-bk-tooltips="{ content: `@ ${item.tenant.name}（${item.tenant.id}）` }">
              {{ `@ ${item.tenant.name}（${item.tenant.id}）` }}
            </span>
          </div>
          <bk-tag
            v-if="userInfo.username === item.id"
            type="filled"
            theme="success">
            {{ $t('当前登录') }}
          </bk-tag>
        </div>
      </li>
    </ul>
  </div>
</template>

<script lang="ts" setup>
import { inject, ref } from 'vue';

import { CurrentNaturalUserData } from '@/http/types/personalCenterFiles';
import { useUser } from '@/store';

interface IProps {
  currentUserId: string
  currentNaturalUser: CurrentNaturalUserData
}

const props = defineProps<IProps>();
const emit = defineEmits(['change']);

const user = useUser();
const userInfo = ref(user.user);
const editLeaveBefore = inject<() => Promise<boolean>>('editLeaveBefore');
// 切换关联账号
const handleClickItem = async (item: CurrentNaturalUserData['tenant_users'][number]) => {
  // 如果当前账号与即将切换的账号id相同，则保持原状
  if (props.currentUserId === item.id) return;

  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
  emit('change', item.id);
};

</script>
