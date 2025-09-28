<template>
  <div
    v-if="bindInfo.type"
    class="flex items-center">
    <i
      class="mr-[8px]"
      :class="fieldLabelMap[bindInfo.type]?.icon || ''">
    </i>
    <span class="text-[#4D4F56] mr-[36px]">
      {{ fieldLabelMap[bindInfo.type]?.label || '' }}
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
            {{ bindInfo.wx_userid || '--' }}
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
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue';

import { getWechatBindStatus, putWechatUnbind, wechatBinding } from '@/http/personalCenterFiles';
import { WechatBindStatusData } from '@/http/types/personalCenterFiles';
import { t } from '@/language';
import { useUser } from '@/store/user';

const userStore = useUser();
const bindInfo = reactive<WechatBindStatusData>({
  type: '' as WechatBindStatusData['type'],
  wx_userid: '',
});

const isBinding = computed(() => (bindInfo.type && bindInfo.wx_userid));

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

/** 获取微信绑定状态 */
const handleFetchBindStatus = async () => {
  try {
    const res = await getWechatBindStatus(userStore.user.username);
    bindInfo.type = res.data.type;
    bindInfo.wx_userid = res.data.wx_userid;
    // 若已有绑定状态，停止轮询
    if (bindInfo.type && bindInfo.wx_userid) {
      stopPolling();
    }
  } catch (err) {
    console.error(err);
    stopPolling();
  }
};

/** 绑定微信 */
const handleBinding = async () => {
  const res = await wechatBinding(userStore.user.username);
  window.open(res.data?.url, '_blank');
  // 清除轮询
  stopPolling();
  // 再次发起轮询
  startPolling();
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
  // 获取最新状态
  handleFetchBindStatus();
};

const popoverRef = ref();
const handleCancel = () => {
  popoverRef.value.hide();
};

const interval = ref(null);
const startPolling = () => {
  interval.value = setInterval(handleFetchBindStatus, 5000);
};
const stopPolling = () => {
  clearInterval(interval.value);
};

onMounted(() => {
  handleFetchBindStatus();
  // 页面初始化开启轮询
  startPolling();
});

onUnmounted(() => {
  stopPolling();
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
.wecom-icon {
  background-image: url('../../../../images/wecom.svg');
  display: inline-block;
  width: 14px;
  height: 14px;
  background-size: contain;
  background-position: center;
}
</style>
