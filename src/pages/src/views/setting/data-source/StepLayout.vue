<template>
  <div>
    <div class="steps-wrapper">
      <bk-steps
        ext-cls="steps"
        :cur-step="step"
        :steps="steps"
      />
    </div>
    <template v-for="(item, index) in steps" :key="index">
      <div v-if="step === index + 1">
        <slot :name="`step-${index + 1}`" />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
interface StepItem {
  title: string;
}

interface IProps {
  /** 步骤配置，数组顺序即步骤顺序 */
  steps: StepItem[];
  /** 当前步骤（从 1 开始）。切步由使用方控制：校验/请求等完成后自行更新，组件不代切 */
  step: number;
}

defineProps<IProps>();
</script>

<style lang="less" scoped>
.steps-wrapper {
  padding: 12px 0;
  text-align: center;
  background: #FAFBFD;
  box-shadow: 0 1px 0 0 #F0F1F5;

  .steps {
    width: 350px;
    margin: auto;
  }
}
</style>
