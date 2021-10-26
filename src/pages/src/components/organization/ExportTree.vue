<!--
  - Tencent is pleased to support the open source community by making Bk-User 蓝鲸用户管理 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
  -
  - License for Bk-User 蓝鲸用户管理:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->
<template>
  <div data-test-id="list_treeData">
    <ul class="child-node">
      <li class="vue-tree-item" v-for="item in treeDataList" :key="item.id">
        <div :style="{ 'padding-left': 15 * (treeIndex + 1) + 'px' }"
             :class="['tree-node', { 'down': item.showChildren, 'first-tree-node': treeIndex === 0 }]">
          <!-- 开关 icon == -->
          <p class="unfold-icon" @click.stop="handleClickToggle(item)">
            <i class="icon icon-user-triangle" :class="{ 'hidden': !item.has_children }"></i>
            <i class="tree-file icon-user-file-close-01"></i>
          </p>
          <!-- 组织名称 -->
          <span class="name-text" v-bk-overflow-tips @click.stop="handleClickToggle(item)">{{item.name}}</span>
          <!-- checkbox -->
          <template v-if="item.disabled">
            <i :class="['check-icon', 'disabled']" @click.stop></i>
          </template>
          <template v-else>
            <i :class="['check-icon', { 'icon-user-sure': item.isChecked }]" @click.stop="checkItem(item)"></i>
          </template>
        </div>
        <div class="tree-node-loading" v-if="item.showLoading">
          <img src="../../images/svg/loading.svg" alt="">
        </div>
        <ExportTree
          v-if="item.showChildren && item.children"
          :tree-data-list="item.children"
          :tree-index="treeIndex + 1"
          @selectItem="selectItem"
          @handleClickToggle="handleClickToggle" />
      </li>
    </ul>
  </div>

</template>

<script>
export default {
  name: 'ExportTree',
  props: {
    treeDataList: {
      type: Array,
      default() {
        return [];
      },
    },
    treeIndex: {
      type: Number,
      default: 0,
    },
  },
  methods: {
    // 展开子级
    handleClickToggle(item) {
      this.$emit('handleClickToggle', item);
    },
    // 复选框勾选的数据
    checkItem(item) {
      this.$emit('selectItem', item);
    },
    // 组件内调用组件，需要抛出数据两次
    selectItem(item) {
      this.$emit('selectItem', item);
    },
  },
};
</script>

<style lang="scss" scoped>
.tree-node {
  display: flex;
  align-items: center;
  position: relative;
  padding-left: 20px;
  line-height: 36px;
  font-size: 14px;
  font-weight: 400;
  color: rgba(115, 121, 135, 1);
  cursor: pointer;
  transition: all .3s ease;

  &.first-tree-node {
    padding-left: 20px !important;
  }

  &.down .unfold-icon .icon-user-triangle {
    transition: all .3s ease;
    transform: rotate(0);
  }

  &:hover,
  &.active {
    color: #4b8fff;
    background: #e1ecff;

    > .unfold-icon > .icon-user-triangle,
    > .unfold-icon > .tree-file {
      &::before {
        color: #4b8fff;
      }
    }
  }

  > .unfold-icon {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    width: 40px;
    height: 36px;

    > .icon-user-triangle {
      display: inline-block;
      vertical-align: middle;
      margin-right: 4px;
      opacity: 1;
      font-size: 10px;
      transform: rotate(-90deg);
      transition: all .3s ease;

      &::before {
        color: #c6d0d9;
      }

      &.hidden {
        opacity: 0;
      }
    }

    > .tree-file {
      display: inline-block;
      vertical-align: middle;
      margin-right: 6px;
      font-size: 18px;

      &::before {
        color: #c6d0d9;
      }
    }
  }

  > .name-text {
    flex-shrink: 0;
    width: calc(100% - 84px);
    font-size: 14px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  > .check-icon {
    position: absolute;
    right: 24px;
    top: 50%;
    transform: translateY(-50%);
    display: block;
    width: 18px;
    height: 18px;
    background: rgba(255, 255, 255, 1);
    border: 1px solid rgba(151, 155, 165, 1);
    border-radius: 50%;

    &.icon-user-sure {
      font-size: 20px;
      width: auto;
      height: auto;
      border-radius: 0;
      border: none;
      background: none;

      &::before {
        color: #3a84ff;
      }
    }

    &.disabled {
      background: #ebeefa;
      cursor: not-allowed;
    }
  }
}

.tree-node-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 32px;
  animation: tree-opacity .3s;

  > img {
    width: 20px;
  }
}
</style>
