<template>
  <div @click.stop>
    <bk-popover
      ref="popoverRef"
      placement="bottom"
      theme="light zIndexSet"
      trigger="click"
      v-bind="popoverProps"
    >
      <template #content>
        <div class="flex flex-col">
          <bk-button
            v-for="item in filteredList"
            :key="item.value"
            text
            :disabled="item.disabled"
            class="!py-[6px] text-[12px]"
            @click="handleClick(item)"
          >
            {{ $t(item.label) }}
          </bk-button>
        </div>
      </template>
      <slot></slot>
    </bk-popover>
  </div>
</template>

<script lang="ts" setup>
import { PopoverPropTypes } from 'bkui-vue/lib/popover';
import { computed, ref } from 'vue';

type ListItem<T = any> = {
  value: number | string
  label: string
  disabled?: boolean
  onClick?: (rowData: T) => void
};
interface IProps<T = any> {
  list?: ListItem[]
  /** 当前操作行的数据，用于listItem中onClick事件参数 */
  rowData?: T
  /** 在某些场景下，操作项可能相互影响（如展示A则隐藏B），因此允许传入自定义过滤规则 */
  filterRule?: (rowData: T) => ListItem[]
  clickHide?: boolean
  popoverProps?: Partial<PopoverPropTypes>
}
const props = withDefaults(defineProps<IProps>(), {
  clickHide: false,
});

const popoverRef = ref();
const filteredList = computed(() => {
  if (props?.filterRule && typeof props.filterRule === 'function') {
    return props.filterRule(props?.rowData);
  }
  return props.list || [];
});

const handleClick = (item: ListItem) => {
  if (item.onClick) {
    item.onClick(props?.rowData);
  }
  if (props.clickHide) {
    (popoverRef.value as any)?.hide();
  }
};
</script>

<style lang="less">
.zIndexSet {
  z-index: 2000 !important;
}
</style>
