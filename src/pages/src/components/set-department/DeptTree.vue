<template>
  <bk-tree
    class="tree-container"
    ref="treeRef"
    :data="treeData"
    node-key="id"
    label="name"
    children="children"
    show-checkbox
    :node-content-action="['selected', 'expand', 'click', 'collapse']"
    :offset-left="0"
    :search="searchKey"
    @node-checked="nodeChecked"
  >
    <template #nodeType="item">
      <i :class="getNodeIcon(item.type)" />
    </template>
    <template #node="item">
      <span v-overflow-title>{{ item.name }}</span>
    </template>
  </bk-tree>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

defineProps({
  treeData: {
    type: Array,
    default: () => ([]),
  },
  searchKey: {
    type: String,
    default: '',
  },
});

const emit = defineEmits(['checkedList']);

const getNodeIcon = (type: string) => {
  switch (type) {
    case 'tenant':
      return 'user-icon icon-homepage';
    case 'department':
      return 'bk-sq-icon icon-file-close';
    default:
      return 'bk-sq-icon icon-personal-user';
  }
};

const nodeChecked = (list: any) => {
  emit('checkedList', list);
};
</script>

<style lang="less" scoped>
i {
  margin: 0 6px;
  font-size: 18px;
  color: #A3C5FD;
}

.tree-container {
  height: 100%;

  ::v-deep .bk-container {
    .is-selected {
      i {
        color: #4b8fff;
      }
    }

    .bk-node-row {
      .bk-tree-node {
        height: 36px;
        line-height: 36px;
      }

      &:hover {
        background: #f0f1f5;
      }
    }

    .bk-node-row.is-selected:hover {
      background-color: #ebf2ff;
    }
  }
}
</style>
