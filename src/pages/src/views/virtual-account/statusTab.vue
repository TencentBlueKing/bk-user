<template>
  <div class="h-[32px] bg-[#EAEBF0] rounded-[2px] flex justify-center p-[4px] text-[12px] relative">
    <div
      class="absolute h-[24px] bg-[#FFFFFF] rounded-[2px] transition-all duration-300 ease-in-out"
      :style="{
        width: `calc(${100 / tabList.length}% - 8px)`,
        left: `calc(${(active * 100) / tabList.length}% + 4px)`
      }">
    </div>
    <div
      v-for="(item, index) in tabList"
      :key="index"
      class="rounded-[2px] px-[12px] flex items-center justify-center cursor-pointer relative z-10"
      :class="active === index && 'text-[#3A84FF]'"
      @click="handleActiveChange(index)"
    >
      <img :src="item.icon" class="inline-block h-[14px] w-[14px] mr-[2px]" />
      <span>{{ item.label }}</span>
    </div>
  </div>
</template>

<script lang="ts" setup>
import normalImg from '@/images/normal.svg';
import unknownImg from '@/images/unknown.svg';
import { t } from '@/language/index';

const active = defineModel<number>('active', { default: 0 });

const tabList = [
  {
    icon: normalImg,
    label: t('启用账号'),
  },
  {
    icon: unknownImg,
    label: t('停用账号'),
  },
];

const handleActiveChange = (value: number) => {
  active.value = value;
};
</script>
