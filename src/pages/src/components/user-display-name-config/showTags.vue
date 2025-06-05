<template>
  <div>
    <ul ref="listContainer">
      <li
        v-for="(item, index) in data"
        :key="item.value"
        @mouseover="handleMouseEnter(index)"
        @mouseleave="handleMouseLeave"
        @dragstart="isDragging = true"
        @dragend="isDragging = false"
        :class="[typeColorMap[item.type] ,'show-tag']">
        <span>{{ item.label }}</span>
        <i
          v-if="curHoverIndex === index && !isDragging"
          class="bk-sq-icon icon-close-fill text-[#979BA5] text-[14px] absolute -top-[5px]"
          @click="handleDeleteItem(index)">
        </i>
      </li>
    </ul>
  </div>
</template>

<script lang="ts" setup>
import Sortable from 'sortablejs';
import { onMounted, ref } from 'vue';

interface IProps {
  data: {
    type: 'field' | 'symbol'
    value: number | string
    label: number | string
  }[]
}
defineProps<IProps>();
const emit = defineEmits(['delete', 'sort']);
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

onMounted(() => {
  if (listContainer.value) {
    new Sortable(listContainer.value, {
      animation: 150,
      onEnd: (e: { oldIndex: number; newIndex: number; }) => {
        console.log(e)
        emit('sort', {
          oldIndex: e.oldIndex,
          newIndex: e.newIndex,
        });
      },
    });
  }
});

</script>

<style lang="less" scoped>
.show-tag {
  display: inline-block;
  margin-right: 4px;
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
