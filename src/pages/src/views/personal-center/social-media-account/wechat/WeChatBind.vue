<template>
  <div class="flex items-center">
    <i
      class="mr-[8px] mt-[4px]"
      :class="fieldLabelMap[type]?.icon || ''">
    </i>
    <span class="text-[#4D4F56] mr-[36px]">
      {{ fieldLabelMap[type]?.label || '' }}
    </span>

    <div class="flex items-center">
      <template v-if="!isBinding">
        <span class="text-[#313238] mr-[12px]">
          --
        </span>
        <bk-button
          theme="primary"
          text
          @click="handleBinding">
          <i class="user-icon icon-link text-[#3A84FF] mr-[4px]"></i>
          {{ $t('绑定') }}
        </bk-button>
      </template>
      <bk-popover
        v-else
        ref="popoverRef"
        theme="light"
        placement="right-start">
        <div class="flex items-center">
          <span class="text-[#313238] mr-[12px]">
            {{ wx_userid || '--' }}
          </span>
          <bk-tag
            theme="success"
            class="!cursor-pointer">
            {{ $t('已绑定') }}
          </bk-tag>
        </div>
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
import { computed, ref } from 'vue';

import { putWechatUnbind, wechatBinding } from '@/http/personalCenterFiles';
import { WechatBindStatusData } from '@/http/types/personalCenterFiles';
import { t } from '@/language';
import { useUser } from '@/store/user';

// eslint-disable-next-line vue/prop-name-casing
const props = defineProps<WechatBindStatusData>();

const emit = defineEmits(['bind', 'unbind']);
const userStore = useUser();

const isBinding = computed(() => (props.type && props.wx_userid));

type FieldLabelMap = Record<WechatBindStatusData['type'], {
  icon: string
  label: string
}>;
const fieldLabelMap: FieldLabelMap = {
  mp: {
    icon: 'wechat-icon',
    label: t('微信公众号消息通知'),
  },
  wecom: {
    icon: 'wecom-icon',
    label: t('企业微信消息通知'),
  },
};

/** 绑定微信 */
const handleBinding = async () => {
  const res = await wechatBinding(userStore.user.username);
  window.open(res.data?.url, '_blank');
  emit('bind');
};

/** 解除微信绑定 */
const handleUnbind = async () => {
  await putWechatUnbind(userStore.user.username);
  Message({
    theme: 'success',
    message: t('解绑成功'),
  });
  // 隐藏popover
  handleCancel();
  emit('unbind');
};

const popoverRef = ref();
const handleCancel = () => {
  popoverRef.value.hide();
};
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
.wecom-icon {
  background-image: url('../../../../images/wecom.svg');
  display: inline-block;
  width: 14px;
  height: 14px;
  background-size: contain;
  background-position: center;
}
</style>
