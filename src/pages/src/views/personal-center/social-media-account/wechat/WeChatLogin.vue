<template>
  <div class="flex items-center">
    <i class="wechat-icon mr-[8px]"></i>
    <span class="text-[#4D4F56] mr-[36px]">
      {{ $t('微信登录') }}
    </span>

    <div class="flex items-center">
      <span class="text-[#313238] mr-[12px]">Ericlee</span>
      <bk-button
        v-if="bindInfo.isBind"
        theme="primary"
        text
        @click="handleBinding">
        <i class="user-icon icon-link text-[#3A84FF] mr-[4px]"></i>
        {{ $t('绑定') }}
      </bk-button>
      <bk-popover
        v-else
        ref="popoverRef"
        theme="light"
        placement="right-start">
        <bk-tag
          theme="success"
          class="!cursor-pointer">
          {{ $t('已绑定') }}
        </bk-tag>
        <template #content>
          <div class="w-[190px] text-[14px]">
            <span class="text-[#4D4F56]">
              {{ $t('当前账号已绑定，可手动进行账号的解绑') }}
            </span>
            <div class="flex justify-end">
              <bk-button
                class="mr-[12px]"
                theme="primary"
                text
                @click="handleUnbind">
                {{ $t('解除绑定') }}
              </bk-button>
              <bk-button
                theme="primary"
                text
                @click="handleCancel">
                {{ $t('取消') }}
              </bk-button>
            </div>
          </div>
        </template>
      </bk-popover>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { Message } from 'bkui-vue';
import { onMounted, reactive, ref } from 'vue';

import { getWechatBindStatus, putWechatUnbind, wechatBinding } from '@/http/personalCenterFiles';
import { WechatBindingData } from '@/http/types/personalCenterFiles';
import { t } from '@/language';
import { useUser } from '@/store/user';

const userStore = useUser();
const bindInfo = reactive<WechatBindingData & { isBind: boolean }>({
  isBind: false,
  bind_type: '' as WechatBindingData['bind_type'],
  bind_url: '',
});

/** 获取微信绑定状态 */
const handleFetchBindStatus = async () => {
  const res = await getWechatBindStatus(userStore.user.username);
  console.log(res);
};

/** 绑定微信 */
const handleBinding = async () => {
  const res = await wechatBinding(userStore.user.username);
  console.log(res);
};

/** 解除微信绑定 */
const handleUnbind = async () => {
  const res = await putWechatUnbind(userStore.user.username);
  Message({
    theme: 'success',
    message: t('解绑成功'),
  });
  console.log(res);
};

const popoverRef = ref();
const handleCancel = () => {
  popoverRef.value.hide();
};

onMounted(() => {
  handleFetchBindStatus();
});
</script>

<style lang="less" scoped>
.wechat-icon {
  background-image: url('../../../../images/wechat.svg');
  display: inline-block;
  width: 14px;
  height: 14px;
  background-size: contain;
  background-position: center;
}
</style>
