<template>
  <bk-date-picker
    :model-value="modelValue"
    v-bind="$attrs"
    @change="handleChange">
  </bk-date-picker>
</template>

<script setup lang="ts">
import dayjs from 'dayjs';

// 使用 defineModel 进行双向绑定
const modelValue = defineModel<string>({ default: '' });

/**
 * 去除日期字符串中的时区信息
 * @param dateStr 带时区的日期字符串，如 "2026-01-24 00:00:00 +0800"
 * @returns 不带时区的日期字符串，如 "2026-01-24 00:00:00"
 */
const removeDateTimezone = (dateStr: string): string => {
  if (!dateStr) return '';

  // 去除时区信息（如 +0800, +08:00, -0500 等）
  const cleanedDate = dateStr.replace(/\s*[+-]\d{2}:?\d{2}$/, '').trim();

  // 使用 dayjs 格式化确保格式统一
  const parsedDate = dayjs(cleanedDate);
  return parsedDate.isValid() ? parsedDate.format('YYYY-MM-DD HH:mm:ss') : cleanedDate;
};

// 处理日期变化，去除时区信息
const handleChange = (value: string) => {
  modelValue.value = removeDateTimezone(value);
};
</script>
