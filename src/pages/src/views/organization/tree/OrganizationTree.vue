<template>
  <div class="organization-tree-wrapper">
    <div class="tree-main">
      <bk-tree
        :data="treeData"
        label="name"
        children="children"
        :node-content-action="['selected', 'expand', 'click', 'collapse']"
        @node-click="handleNodeClick"
      >
        <template #nodeAction="item">
          <span v-if="!item.__attr__.isRoot" style="color: #979ba5;">
            <DownShape v-if="item.__attr__.hasChild && item.__attr__.isOpen" />
            <RightShape
              v-if="item.__attr__.hasChild && !item.__attr__.isOpen"
            />
          </span>
        </template>
        <template #nodeType="item">
          <i
            class="user-icon icon-homepage"
            v-if="item.__attr__.isRoot && item.default"
          />
          <span
            class="icon-text"
            v-else-if="item.__attr__.isRoot && !item.default"
          >
            {{ item.name.charAt(0).toUpperCase() }}
          </span>
          <i class="bk-sq-icon icon-file-close" v-else />
        </template>
        <template #node="item">
          <span>{{ item.name }}</span>
        </template>
        <template #nodeAppend="item">
          <span class="user-number">{{ item.id }}</span>
          <bk-dropdown
            trigger="click"
            placement="bottom-start"
            ref="dropdownMenu"
          >
            <i class="user-icon icon-more"></i>
            <template #content>
              <bk-dropdown-menu>
                <bk-dropdown-item
                  v-for="(child, index) in submenu"
                  :key="index"
                  @click="handleClick(child.type, item)">
                  {{ child.name }}
                </bk-dropdown-item>
              </bk-dropdown-menu>
            </template>
          </bk-dropdown>
        </template>
      </bk-tree>
    </div>
  </div>
</template>

<script setup lang="ts">
import { DownShape, RightShape } from 'bkui-vue/lib/icon';
import { reactive, ref } from 'vue';

import { copy } from '@/utils';

const emits = defineEmits(['changeNode']);

const dropdownMenu = ref();

const submenu = [
  {
    name: '复制组织ID',
    type: 'id',
  },
  {
    name: '复制组织名称',
    type: 'name',
  },
];

const treeData = reactive([
  {
    name: '总公司',
    title: '总公司',
    expanded: true,
    id: 2,
    default: true,
    type: 'local',
    children: [
      {
        name: '深圳公司',
        title: '深圳公司',
        id: 3,
        children: [{ name: '测试组织', title: '测试组织', id: 4 }],
      },
      {
        title: '上海分公司',
        name: '上海分公司',
        id: 5,
        children: [{ name: '测试组织', title: '测试组织', id: 6 }],
      },
    ],
  },
  {
    name: 'test',
    title: 'test',
    id: 7,
    default: false,
    type: 'ldap',
    children: [
      {
        title: 'test1',
        name: 'test1',
        id: 8,
        children: [],
      },
    ],
  },
]);
const handleNodeClick = (node: any) => {
  emits('changeNode', node);
};
const handleClick = (type: string, item: any) => {
  copy(item[type]);
};
</script>

<style lang="less" scoped>
.organization-tree-wrapper {
  width: 280px;
  height: 100%;
  min-width: 280px;
  background: #fff;
  box-shadow: 0 2px 4px 0 #0000001a, 0 2px 4px 0 #1919290d;

  .tree-main {
    height: calc(100% - 52px);
  }
}

:deep(.bk-tree) {
  height: 100%;

  .bk-node-row {
    .bk-tree-node {
      height: 36px;
      line-height: 36px;
    }

    &:hover {
      background: #f0f1f5;

      .icon-homepage {
        color: #c4c6cc;
      }

      .icon-more {
        display: block;
        font-size: 18px;
      }

      .user-number {
        display: none;
      }
    }
  }

  .bk-node-row.is-selected {
    background-color: #e1ecff;

    .bk-node-text {
      color: #3a84ff;
    }

    .icon-homepage {
      color: #3a84ff;
    }

    .icon-text {
      background: #3a84ff;
    }

    .icon-more {
      display: block;
      font-size: 18px;
    }

    .user-number {
      display: none;
    }
  }

  .icon-homepage {
    padding-right: 5px;
    font-size: 18px;
    color: #c4c6cc;
  }

  .icon-text {
    width: 18px;
    height: 18px;
    margin-right: 5px;
    font-weight: 700;
    line-height: 18px;
    color: #fff;
    text-align: center;
    background: #c4c6cc;
    border-radius: 4px;
  }

  .icon-file-close {
    padding-right: 5px;
    font-size: 18px;
    color: #a3c5fd;
  }

  .bk-node-row.is-selected:hover {
    background-color: #e1ecff;
  }

  .bk-tree-node {
    padding: 0 12px;

    .bk-node-text {
      color: #63656e;
    }

    .user-number {
      font-size: 12px;
      color: #c4c6cc;
    }

    .icon-more {
      display: none;
    }
  }
}
</style>
