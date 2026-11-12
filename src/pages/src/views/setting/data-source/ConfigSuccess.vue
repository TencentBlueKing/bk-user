<template>
  <div class="success-wrapper" v-bkloading="{ isLoading }">
    <div class="content">
      <i class="user-icon icon-duihao-2" />
      <p class="title">{{ title }}</p>
      <QuickLoginConfig
        v-if="isCreate"
        ref="loginConfigRef"
        class="mt-[24px]"
        :data-source-id="props.dataSourceId"
        :is-local="props.isLocal"
        @loading="isLoading = true"
        @ready="isLoading = false"
      />
      <div class="mt-[24px]">
        <bk-button
          v-if="!isLocal"
          class="mr-[8px]"
          theme="primary"
          :disabled="operating"
          @click="handleOperate('dataSource', true)"
        >
          {{ $t('立即同步') }}
        </bk-button>
        <bk-button
          class="mr-[8px]"
          theme="primary"
          :disabled="operating"
          @click="handleOperate('login')"
        >
          {{ $t('登录配置') }}
        </bk-button>
        <bk-button :disabled="operating" @click="handleOperate('organization')">
          {{ $t('查看组织架构') }}
        </bk-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { onMounted, ref } from 'vue';

import QuickLoginConfig from './components/QuickLoginConfig.vue';

import { postOperationsSync } from '@/http/dataSourceFiles';
import router from '@/router';

interface IProps {
  title: string;
  dataSourceId: number;
  /** 本地数据源不展示「立即同步」，账密登录快捷勾选仅本地数据源可用，由父组件按数据源类型传入 */
  isLocal?: boolean;
  /** 是否为新建成功；更新成功沿用原有展示，不出现认证源快捷配置 */
  isCreate?: boolean;
}

const props = withDefaults(defineProps<IProps>(), {
  title: '',
  isLocal: false,
  isCreate: false,
});

const isLoading = ref(true);
const btnLoading = ref(false);
const loginConfigRef = ref<InstanceType<typeof QuickLoginConfig>>();
/** 三个操作按钮的执行中状态，执行中禁用入口 */
const operating = ref(false);

// 三个操作按钮离开本页前都会先保存快捷认证源配置（见 saveBeforeLeave）
const handleSave = async () => {
  btnLoading.value = true;
  try {
    await loginConfigRef.value?.save();
  } catch (error) {
    console.error(error);
  } finally {
    btnLoading.value = false;
  }
};

// 有未保存编辑时先保存；保存失败（如校验不通过）返回 false 留在本页
const saveBeforeLeave = async () => {
  if (!window.changeInput) {
    return true;
  }
  await handleSave();
  return !window.changeInput;
};

// 三个操作按钮共用：先保存快捷认证源配置，再跳转；needSync 为 true 时先触发数据同步
const handleOperate = async (routeName: string, needSync = false) => {
  if (operating.value) return;
  operating.value = true;
  try {
    if (!await saveBeforeLeave()) {
      return;
    }
    if (needSync) {
      const res = await postOperationsSync(props.dataSourceId);
      Message({ theme: res.data.status, message: res.data.summary });
    }
    router.push({ name: routeName });
  } finally {
    operating.value = false;
  }
};

onMounted(() => {
  // 更新成功沿用原有展示，不挂载快捷配置，加载态在这里结束
  if (!props.isCreate) {
    isLoading.value = false;
  }
});
</script>

<style lang="less" scoped>
.success-wrapper {
  position: relative;
  width: 100%;
  height: calc(100vh - var(--header-height) - var(--breadcrumbs-height) - 32px);
  min-height: 400px;
  text-align: center;
  background: #fff;

  .content {
    position: absolute;
    top: 50%;
    left: 50%;
    // 固定为匹配卡片宽度：勾选/取消勾选时内容块宽度不变，避免水平居中位置跳动
    width: 560px;
    transform: translate(-50%, -50%);

    .icon-duihao-2 {
      font-size: 56px;
      color: #2DCB56;
    }

    .title {
      margin: 21px 0 6px;
      font-size: 16px;
      color: #000;
    }
  }
}
</style>
