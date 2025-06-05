<template>
  <div class="select-container">
    <li v-if="title" class="h-[32px] leading-[32px] px-[12px]">
      <span class="text-[#979BA5]">{{ title }}</span>
      <i
        v-if="tips"
        class="user-icon icon-info-i text-[16px] ml-[5px]"
        v-bk-tooltips="tips">
      </i>
    </li>
    <ul class="select-list">
      <li
        v-for="(item, index) in options"
        :key="index"
        :class="[
          item?.disabled && 'option-disabled',
          item?.hide && 'hidden',
        ]"
        @click="handleClickOption(item)">
        <i v-if="item?.icon" :class="[item.icon || '', 'mr-[5px]']"></i>
        <span>{{ item?.value }}</span>
      </li>
    </ul>
  </div>
</template>

<script lang="ts" setup>
import { IOption } from './type';

interface IProps {
  title: string
  tips?: string
  options: IOption[],
}
defineProps<IProps>();
const emit = defineEmits(['change']);

const handleClickOption = (option: IOption) => {
  if (option.disabled) return;
  emit('change', option);
};
</script>

<style lang="less" scoped>
.select-container {
  width: 160px;
  height: 232px;
  max-height: 232px;
  font-size: 12px;
  display: flex;
  flex-direction: column;

  .select-list {
    overflow-y: auto;
    flex: 1;
    min-height: 0;
    &::-webkit-scrollbar {
      width: 4px;
      height: 4px;
    }

    &::-webkit-scrollbar-thumb {
      background: #dde4eb;
      border-radius: 20px;
      box-shadow: inset 0 0 6px hsla(0,0%,80%,.3);
    }
    li {
      height: 32px;
      line-height: 32px;
      color: #4D4F56;
      cursor: pointer;
      padding-inline: 12px;
      user-select: none;
      &:hover {
        background-color: #E1ECFF;
      }
    }
    .option-disabled {
      color: #C4C6CC;
      cursor: not-allowed;
      &:hover {
        background-color: unset;
      }
    }
}

}

</style>
