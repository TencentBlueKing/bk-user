<template functional>
  <div :class="['horizontal-item', props.extCls || '']">
    <div class="label" :class="props.required ? 'is-required' : ''">
      {{ props.label ? `${props.label}` : ''}}
    </div>
    <div class="content">
      <slot />
      <slot name="append" />
    </div>
  </div>
</template>
<style lang="postcss" scoped>
.horizontal-item {
  position: relative;
  margin-top: 20px;
  margin-bottom: 16px;
  display: flex;
  align-items: flex-start;
  .label {
    position: relative;
    width: 130px;
    line-height: 20px;
    font-size: 14px;
    color: #63656E;
    text-align: left;
    &.is-required:after {
      height: 8px;
      line-height: 1;
      content: "*";
      color: #ea3636;
      font-size: 12px;
      font-weight: normal;
      position: relative;
      display: inline-block;
      vertical-align: middle;
      top: -4px;
    }
  }
  .content {
    flex: 1;
    max-width: calc(100% - 134px);
  }
}
</style>
