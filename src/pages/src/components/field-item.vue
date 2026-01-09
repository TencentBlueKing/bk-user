<template>
  <div
    class="flex items-center w-full"
    :style="containerStyle"
  >
    <template v-if="$slots.field">
      <slot name="field"></slot>
    </template>
    <template v-else>
      <div
        class="shrink-0"
        :style="fieldStyle"
      >
        {{ fieldValue }}{{ fieldSplitCode }}
      </div>
    </template>

    <template v-if="$slots.value">
      <slot name="value"></slot>
    </template>
    <template v-else>
      <template v-if="isLabelOverflow">
        <OverflowTitle
          :style="labelStyle"
          type="tips"
        >
          {{ value || emptyPlaceholder }}
        </OverflowTitle>
      </template>
      <template v-else>
        <span :style="labelStyle">
          {{ value || emptyPlaceholder }}
        </span>
      </template>
    </template>
  </div>
</template>

<script lang="ts" setup>
import { OverflowTitle } from 'bkui-vue';
import type { CSSProperties } from 'vue';
import { computed } from 'vue';

interface IProps {
  /** 组件总高度(默认30) */
  containerHeight?: number | string;
  /** 右侧值(value)为空时展示(默认'--') */
  emptyPlaceholder?: string;
  /** 左侧字段(key)文本颜色(默认#63656e) */
  fieldColor?: string;
  /** 左侧字段(key)文本方向(默认right) */
  fieldDirection?: 'center' | 'left' | 'right';
  /** 左侧字段(key)文字大小(默认14) */
  fieldSize?: number | string;
  /** 分隔符(默认：) */
  fieldSplitCode?: string;
  /** 左侧字段(key)展示 */
  fieldValue?: number | string;
  /** 左侧字段(key)文本宽度(默认100，英文环境下自动翻倍) */
  fieldWidth?: number | string;
  /** 右侧值(value)是否使用OverflowTitle(默认使用) */
  isLabelOverflow?: boolean;
  /** 右侧值(value)展示 */
  value?: number | string;
  /** 右侧值(value)文字颜色 */
  valueColor?: string;
  /** 右侧值(value)最大宽度(默认220) */
  valueMaxWidth?: number | string;
  /** 右侧值(value)文字大小 */
  valueSize?: number | string;
}

const props = withDefaults(defineProps<IProps>(), {
  containerHeight: 30,
  fieldSplitCode: '：',
  fieldDirection: 'right',
  fieldWidth: 100,
  fieldColor: '#63656e',
  fieldSize: 14,
  isLabelOverflow: true,
  emptyPlaceholder: '--',
  valueMaxWidth: 220,
  valueSize: 14,
});

const containerStyle = computed<CSSProperties>(() => ({
  height: parseCss(props.containerHeight),
}));

const fieldStyle = computed<CSSProperties>(() => ({
  textAlign: props.fieldDirection,
  width: parseCss(props.fieldWidth),
  color: props.fieldColor,
  fontSize: parseCss(props.fieldSize),
  lineHeight: parseCss(props.containerHeight),
}));

const labelStyle = computed<CSSProperties>(() => ({
  maxWidth: parseCss(props.valueMaxWidth),
  fontSize: parseCss(props.valueSize),
  color: parseCss(props.valueColor),
  lineHeight: parseCss(props.containerHeight),
}));

const parseCss = (v: number | string) => (typeof v === 'string' ? v : `${v}px`);
</script>
