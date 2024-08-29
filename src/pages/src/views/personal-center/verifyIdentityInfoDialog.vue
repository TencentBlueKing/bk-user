<template>
  <bk-dialog
    v-model:is-show="isShow"
    render-directive="if"
    :close-icon="false"
    :quick-close="false">
    <template #header>
      <div class="pt-[20px] pl-[20px]">
        <span class="font-black text-[30px]">{{ dialogTitle }}</span>
        <div class="text-xs mt-[10px] text-[#8a8b92]">
          <slot name="header-tips"></slot>
          {{ headerTips }}
        </div>
      </div>
    </template>
    <template #default>
      <bk-tab v-model:active="active" type="unborder-card" ext-cls="verify-identity-info-tab-panel">
        <bk-tab-panel
          v-for="item in Panels"
          :key="item.name"
          :label="item.label"
          :name="item.name">
          <slot :name="item.slotName"></slot>
        </bk-tab-panel>
      </bk-tab>
    </template>
    <template #footer>
      <slot name="footer"></slot>
    </template>
  </bk-dialog>
</template>

<script setup lang="ts">
import { computed, defineModel, defineProps, ref } from 'vue';

import { OpenDialogActive, OpenDialogMode, OpenDialogType } from './openDialogType';

import { t } from '@/language/index';

const props = defineProps({
  // 邮箱或手机号 用于显示title
  type: {
    type: String,
  },
  // 编辑或验证
  mode: {
    type: String,
  },
  headerTips: {
    type: String,
    default: '',
  },
});

const isShow = defineModel<boolean>('isShow', { required: true });
const active = defineModel<OpenDialogActive>('active', { required: true });

const dialogTitle = computed(() => {
  if (props.mode === OpenDialogMode.Edit) {
    return props.type === OpenDialogType.email ? t('编辑邮箱') : t('编辑手机号');
  }
  if (props.mode === OpenDialogMode.Verify) {
    return props.type === OpenDialogType.email ? t('邮箱验证') : t('手机号验证');
  }
  return '';
});

const Panels = ref([
  {
    label: t('继承数据源'),
    name: OpenDialogActive.inherit,
    slotName: OpenDialogActive.inherit,
  },
  {
    label: t('自定义'),
    name: OpenDialogActive.custom,
    slotName: OpenDialogActive.custom,
  },
]);

</script>

<style lang="less">
.verify-identity-info-tab-panel {
  margin-top: -10px;
  height: 170px;
  .bk-tab-header {
    justify-content: center;
  }
}
</style>
