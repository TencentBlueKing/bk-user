<template>
  <div>
    <div
      :class="[
        'flex items-center justify-between p-[16px] mb-[2px] bg-white rounded-sm shadow-sm cursor-pointer',
        'border border-white transition-all',
        { 'hover:border-[1px] hover:border-solid hover:border-[#A3C5FD]': openHover && !disabled},
        { 'hover:border-white': disabled }
      ]"
      v-bk-tooltips="{
        content: $t('若需切换数据源需要先对当前已选数据源进行重置操作'),
        delay: 300,
        offset: 0,
        disabled: !disabled,
      }"
      @click="handleCardClick"
    >
      <div class="flex items-center">
        <img
          v-if="data.logo"
          :src="data.logo"
          :class="[
            'w-[24px] h-[24px] mr-[12px]',
            { 'opacity-50': disabled }
          ]"
          :alt="data.name"
        />
        <div>
          <p
            :class="[
              'text-[14px] leading-[22px] flex items-center',
              disabled ? 'text-[#C4C6CC]' : 'text-[#313238]'
            ]">
            {{ data.name }}
            <slot name="name-suffix" :item="data"></slot>
          </p>
          <p
            v-if="data.description" :class="[
              'text-[12px] leading-[18px]',
              disabled ? 'text-[#C4C6CC]' : 'text-[#979BA5]'
            ]">
            {{ data.description }}
          </p>
        </div>
      </div>

      <!-- 右侧插槽 -->
      <slot name="right" :item="data"></slot>
    </div>
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips } from 'bkui-vue';

interface CardItem {
  id?: string | number;
  logo?: string;
  name: string;
  description?: string;
  [key: string]: any;
}

interface Props {
  /** 卡片数据 */
  data: CardItem;
  /** 是否禁用 */
  disabled?: boolean;
  openHover?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  openHover: true,
});

const emit = defineEmits<{
  click: [data: CardItem];
}>();

/** 处理卡片点击 */
const handleCardClick = () => {
  if (props.disabled) return;
  emit('click', props.data);
};
</script>

<style scoped>
/* Tailwind CSS 已处理所有样式，无需额外 CSS */
</style>
