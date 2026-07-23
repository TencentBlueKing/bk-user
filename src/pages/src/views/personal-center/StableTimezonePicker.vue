<template>
  <DatePickerTimezonePicker
    v-bind="$attrs"
    :value="value"
    @update:value="handleUpdate"
  >
    <template #option="{ option }">
      <div
        class="bk-timezone-picker-option"
        :class="{ 'is-selected': option.label === value }"
        @pointerdown="handleOptionPointerDown(option.label)"
      >
        <span class="option-name">
          {{ isBrowserTimezoneOption(option) ? `${t('浏览器时区')} ` : '' }}{{ option.label }}
        </span>
        <span
          v-if="option.country || option.abbreviation"
          class="option-country"
        >
          {{ option.country || '' }}, {{ option.abbreviation || '' }}
        </span>
        <span
          v-if="option.utc"
          class="option-utc"
        >
          {{ option.utc }}
        </span>
      </div>
    </template>
  </DatePickerTimezonePicker>
</template>

<script setup lang="ts">
import {
  CommonTimezoneOptions,
  getTimezoneInfoByValue,
  TimezonePicker as DatePickerTimezonePicker,
} from '@blueking/date-picker';

import { t } from '@/language';

interface TimezoneOption {
  abbreviation?: string
  country?: string
  countryCode?: string
  label: string
  utc?: string
}

defineOptions({
  name: 'StableTimezonePicker',
  inheritAttrs: false,
});

defineProps<{
  value: string
}>();

const emit = defineEmits<{
  (e: 'update:value', value: string, info?: TimezoneOption): void
}>();

const browserTimezoneOption = CommonTimezoneOptions[0]?.options?.[0];
let pointerDownTimezone = '';

/**
 * 记录用户实际点击的时区。
 * BKSelect 在路由重新进入后可能将已点击选项解析为 undefined，需要用点击值恢复。
 */
const handleOptionPointerDown = (value: string) => {
  pointerDownTimezone = value;
};

const handleUpdate = (value: unknown, info?: TimezoneOption) => {
  const nextValue = typeof value === 'string' ? value : pointerDownTimezone;
  pointerDownTimezone = '';

  // 未捕获到有效选项时不覆盖当前时区，避免页面出现空值。
  if (typeof nextValue !== 'string') return;

  emit('update:value', nextValue, info || getTimezoneInfoByValue(nextValue));
};

const isBrowserTimezoneOption = (option: TimezoneOption) => option === browserTimezoneOption;
</script>
