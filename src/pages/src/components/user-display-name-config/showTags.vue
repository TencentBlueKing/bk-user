<template>
  <div>
    <ul ref="listContainer">
      <template
        v-for="(item, index) in data"
        :key="item.value"
      >
        <bk-popover
          v-if="item.type === 'symbol'"
          trigger="click"
          theme="light display-name-config-no-padding-popover"
          placement="bottom-start"
          :arrow="false">
          <li
            @mouseover="handleMouseEnter(index)"
            @mouseleave="handleMouseLeave"
            @dragstart="isDragging = true"
            @dragend="isDragging = false"
            :class="[typeColorMap[item.type] ,'show-tag']">
            <span>{{ getCurIdLabel(item.value) }}</span>
            <i
              v-if="curHoverIndex === index && !isDragging"
              class="bk-sq-icon icon-close-fill text-[#979BA5] text-[14px] absolute -top-[5px]"
              @click="handleDeleteItem(index)">
            </i>
          </li>
          <template #content>
            <SelectPanel
              :title="$t('符号')"
              :options="symbolOptions"
              :active-value="item.value"
              @change="(option) => handleSymbolChange(option, index)" />
          </template>
        </bk-popover>
        <li
          v-else
          @mouseover="handleMouseEnter(index)"
          @mouseleave="handleMouseLeave"
          @dragstart="isDragging = true"
          @dragend="isDragging = false"
          :class="[typeColorMap[item.type] ,'show-tag']">
          <span>{{ getCurIdLabel(item.value) }}</span>
          <i
            v-if="curHoverIndex === index && !isDragging"
            class="bk-sq-icon icon-close-fill text-[#979BA5] text-[14px] absolute -top-[5px]"
            @click="handleDeleteItem(index)">
          </i>
        </li>
      </template>
    </ul>
  </div>
</template>

<script lang="ts" setup>
import Sortable from 'sortablejs';
import { onMounted, ref } from 'vue';

import SelectPanel from './select-panel/selectPanel.vue';

interface IProps {
  data: {
    type: 'field' | 'symbol'
    value: number | string
    label: number | string
  }[]
  valueMap: {
    id: number | string
    value: number | string
  }[]
  symbolOptions: any[]
}
const props = defineProps<IProps>();
const emit = defineEmits(['delete', 'sort', 'symbolReplace']);
const listContainer = ref<HTMLElement>();
const typeColorMap = {
  field: 'bg-[#FDEED8]',
  symbol: 'bg-[#DAF6E5]',
};

const curHoverIndex = ref();
const isDragging = ref(false);
const handleMouseEnter = (index: number) => {
  curHoverIndex.value = index;
};

const handleMouseLeave = () => {
  curHoverIndex.value = null;
};

const handleDeleteItem = (index: number) => {
  emit('delete', index);
  handleMouseLeave();
};

const getCurIdLabel = (id: string | number) => props.valueMap.find(item => item.id === id)?.value || '';

const handleSymbolChange = (option, index) => {
  emit('symbolReplace', option, index);
};

onMounted(() => {
  if (listContainer.value) {
    new Sortable(listContainer.value, {
      animation: 150,
      onEnd: (e: { oldDraggableIndex: number; newDraggableIndex: number; }) => {
        emit('sort', {
          oldIndex: e.oldDraggableIndex,
          newIndex: e.newDraggableIndex,
        });
      },
    });
  }
});

</script>

<style lang="less" scoped>
ul {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.show-tag {
  display: inline-block;
  border-radius: 2px;
  height: 32px;
  line-height: 32px;
  padding: 0 8px 0 8px;
  cursor: pointer;
  user-select: none;
  color: #313238;
  font-size: 12px;
}

</style>
