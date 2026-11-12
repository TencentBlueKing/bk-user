<template>
  <bk-dialog
    :is-show="isShow"
    :width="640"
    render-directive="if"
    :quick-close="false"
    :before-close="handleBeforeClose"
    @closed="handleClosed"
  >
    <template #header>
      <div class="login-config-header">
        <span class="login-config-title">{{ $t('登录配置') }}</span>
        <span class="login-config-subtitle">{{ dataSourceName }}</span>
      </div>
    </template>
    <div class="login-config-body" :class="{ 'is-loading': isLoading }" v-bkloading="{ isLoading }">
      <QuickLoginConfig
        ref="loginConfigRef"
        :data-source-id="props.dataSourceId"
        :data-source-name="props.dataSourceName"
        :is-local="props.isLocal"
        :enable-remove="true"
        layout="dialog"
        :visible="props.isShow"
        @loading="isLoading = true"
        @ready="isLoading = false"
      />
    </div>
    <template #footer>
      <div class="login-config-footer">
        <bk-button
          theme="primary"
          :loading="btnLoading"
          @click="handleConfirm"
        >
          {{ $t('确认') }}
        </bk-button>
        <bk-button @click="handleCancel">
          {{ $t('取消') }}
        </bk-button>
      </div>
    </template>
  </bk-dialog>
</template>

<script setup lang="ts">
import { inject, ref } from 'vue';

import QuickLoginConfig from './QuickLoginConfig.vue';

interface IProps {
  isShow: boolean;
  dataSourceId: number;
  /** 数据源名称（弹窗副标题、匹配卡片标题） */
  dataSourceName: string;
  /** 仅本地数据源可勾选账密登录 */
  isLocal: boolean;
}

const props = defineProps<IProps>();
const emit = defineEmits<{
  'update:isShow': [value: boolean];
  /** 保存成功，父级据此刷新登录方式标签 */
  success: [];
}>();
const editLeaveBefore = inject<() => Promise<boolean>>('editLeaveBefore');

const isLoading = ref(true);
const btnLoading = ref(false);
const loginConfigRef = ref<InstanceType<typeof QuickLoginConfig>>();

const handleConfirm = async () => {
  btnLoading.value = true;
  try {
    await loginConfigRef.value?.save();
    emit('success');
    emit('update:isShow', false);
  } catch (error) {
    console.error(error);
  } finally {
    btnLoading.value = false;
  }
};

// 关闭前有未保存编辑时按项目惯例弹离开确认（main.ts 全局注入），X/esc 与取消按钮共用
const handleBeforeClose = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
  }
  if (enableLeave) {
    window.changeInput = false;
  }
  return enableLeave;
};

const handleCancel = async () => {
  if (await handleBeforeClose()) {
    emit('update:isShow', false);
  }
};

// X/esc 经 before-close 放行后的收尾：同步父级 isShow，否则再次点击「登录配置」不会触发重置/加载
const handleClosed = () => {
  emit('update:isShow', false);
};
</script>

<style lang="less" scoped>
.login-config-header {
  display: flex;
  align-items: baseline;

  .login-config-title {
    font-size: 20px;
    font-weight: 700;
    color: var(--title-color);
  }

  .login-config-subtitle {
    margin-left: 12px;
    padding-left: 12px;
    border-left: 1px solid var(--border-color);
    font-size: 14px;
    color: var(--gray-color);
  }
}

.login-config-body {
  text-align: left;

  // loading 时撑出转圈空间，内容态高度自适应
  &.is-loading {
    min-height: 200px;
  }
}

.login-config-footer {
  text-align: right;
}
</style>
