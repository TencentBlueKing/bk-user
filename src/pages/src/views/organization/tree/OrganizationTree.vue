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
  <div data-test-id="opOrganizaData">
    <ul class="tree-menu">
      <li class="tree-first-node" v-for="(item, index) in treeDataList" :key="item.id">
        <div :style="{ 'padding-left': 15 * (treeIndex + 1) + 'px' }"
             :class="{ 'tree-node': true, 'first-tree-node': treeIndex === 0,
                       'expand': item.showChildren, 'active': item.showBackground }">
          <!-- 组织开关图标 -->
          <div class="toggle-icon" v-if="treeIndex !== 0 && treeSearchResult === null" @click="handleClickToggle(item)">
            <i class="icon icon-user-triangle" :class="{ 'hidden': !item.has_children }"></i>
          </div>

          <!-- 目录或组织的图标和名称 -->
          <div class="main-node" @click="handleClickTreeNode(item)">
            <div class="folder-icon" :class="treeIndex === 0 && treeSearchResult === null && 'root-node'">
              <i v-if="treeIndex === 0 && treeSearchResult === null" class="icon user-icon icon-root-node-i"></i>
              <i v-else class="icon icon-user-file-close-01"></i>
            </div>
            <div class="depart-name" v-bk-overflow-tips>{{item.name || item.display_name}}</div>
          </div>

          <!-- 用户目录，扩展操作 -->
          <div class="option" v-if="item.type && treeSearchResult === null">
            <i class="icon bk-icon icon-more" @click.stop="handleClickOption(item, $event)"></i>
            <div v-if="item.showOption" :class="{ 'dropdown-list': true,
                                                  'chang-en': $i18n.locale === 'en' }"
                 @click.stop="item.showOption = false">
              <!-- 本地用户目录添加下级组织 -->
              <div class="specific-menu" v-if="item.type === 'local'">
                <a href="javascript:;" @click="addRootDepartment(item)">{{$t('添加根组织')}}</a>
              </div>
              <!-- 上移 -->
              <div class="specific-menu">
                <a href="javascript:;"
                   :class="{ 'disable': index === 0 }"
                   @click="shiftNodeUp(item, index)"
                   @mouseenter="checkUpTips(item, index)"
                   @mouseleave="closeUpTips(item)">
                  {{$t('上移')}}
                </a>
                <div class="tooltip-content" :class="{ 'show-tooltip-content': item.showShiftUpTips }">
                  <div class="arrow"></div>
                  <p class="inner">{{$t('已经是最顶层')}}</p>
                </div>
              </div>
              <!-- 下移 -->
              <div class="specific-menu">
                <a href="javascript:;"
                   :class="{ 'disable': index === treeDataList.length - 1 }"
                   @click="shiftNodeDown(item, index)"
                   @mouseenter="checkDownTips(item, index)"
                   @mouseleave="closeDownTips(item)">
                  {{$t('下移')}}
                </a>
                <div class="tooltip-content" :class="{ 'show-tooltip-content': item.showShiftDownTips }">
                  <div class="arrow"></div>
                  <p class="inner">{{$t('已经是最顶层')}}</p>
                </div>
              </div>
              <!-- 重命名 -->
              <div class="specific-menu">
                <a href="javascript:;" @click="handleRename(item, 'catalog')">{{$t('重命名')}}</a>
              </div>
            </div>
          </div>

          <!-- 本地用户目录下的组织，扩展操作，包括搜索结果为组织 -->
          <div class="option" v-if="item.isLocalDepartment && noSearchOrSearchDepartment">
            <i class="icon bk-icon icon-more" @click.stop="handleClickOption(item, $event)"></i>
            <div v-if="item.showOption" :class="{ 'dropdown-list': true, 'chang-en': $i18n.locale === 'en' }"
                 @click.stop="item.showOption = false">
              <!-- 添加下级组织 -->
              <div class="specific-menu" v-if="!treeSearchResult">
                <a href="javascript:;"
                   :class="{ 'disable': treeIndex === 9 }"
                   @click="addChild(item)"
                   @mouseenter="checkAddTips(item)"
                   @mouseleave="closeAddTips(item)">
                  {{$t('添加下级组织')}}
                </a>
                <div class="tooltip-content" :class="{ 'show-tooltip-content': item.showAddChildTips }">
                  <div class="arrow"></div>
                  <p class="inner">{{$t('最多只能添加十级')}}</p>
                </div>
              </div>
              <!-- 上移 -->
              <div class="specific-menu" v-if="!treeSearchResult">
                <a href="javascript:;"
                   :class="{ 'disable': index === 0 }"
                   @click="shiftNodeUp(item, index)"
                   @mouseenter="checkUpTips(item, index)"
                   @mouseleave="closeUpTips(item)">
                  {{$t('上移')}}
                </a>
                <div class="tooltip-content" :class="{ 'show-tooltip-content': item.showShiftUpTips }">
                  <div class="arrow"></div>
                  <p class="inner">{{$t('已经是最顶层')}}</p>
                </div>
              </div>
              <!-- 下移 -->
              <div class="specific-menu" v-if="!treeSearchResult">
                <a href="javascript:;"
                   :class="{ 'disable': index === treeDataList.length - 1 }"
                   @click="shiftNodeDown(item, index)"
                   @mouseenter="checkDownTips(item, index)"
                   @mouseleave="closeDownTips(item)">
                  {{$t('下移')}}
                </a>
                <div class="tooltip-content" :class="{ 'show-tooltip-content': item.showShiftDownTips }">
                  <div class="arrow"></div>
                  <p class="inner">{{$t('已经是最底层')}}</p>
                </div>
              </div>
              <!-- 重命名 -->
              <div class="specific-menu">
                <a href="javascript:;" @click="handleRename(item, 'department')">{{$t('重命名')}}</a>
              </div>
              <!-- 复制组织ID -->
              <div class="specific-menu">
                <a href="javascript:;" v-clipboard:copy="item.id" v-clipboard:success="handleCopyIdSuccess"
                   v-clipboard:error="handleCopyIdError">
                  {{$t('复制组织ID')}}
                </a>
              </div>
              <!-- 复制组织名称 -->
              <div class="specific-menu">
                <a href="javascript:;" v-clipboard:copy="item.full_name" v-clipboard:success="handleCopyNameSuccess"
                   v-clipboard:error="handleCopyNameError">
                  {{$t('复制组织名称')}}
                </a>
              </div>
              <!-- 删除 -->
              <div class="specific-menu">
                <a href="javascript:;"
                   :class="['delete', { 'delete-disable': item.has_children }]"
                   @click="deleteDepartment(item, index)"
                   @mouseenter="checkDeleteTips(item)"
                   @mouseleave="closeDeleteTips(item)">
                  {{$t('删除')}}
                </a>
                <div class="tooltip-content" :class="{ 'show-tooltip-content': item.showDeleteTips }">
                  <div class="arrow"></div>
                  <p class="inner">{{$t('非空组织不能删除')}}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="tree-node-loading" v-if="item.showLoading">
          <img src="../../../images/svg/loading.svg" alt="">
          <span class="loading-text">{{$t('加载中')}}</span>
        </div>

        <OrganizationTree
          v-if="item.children && item.children.length"
          v-show="item.showChildren"
          :tree-data-list="item.children"
          :tree-index="treeIndex + 1"
          :tree-search-result="treeSearchResult"
          @handleClickToggle="handleClickToggle"
          @handleClickTreeNode="handleClickTreeNode"
          @handleClickOption="handleClickOption"
          @addChildDepartment="addChildDepartment"
          @handleRename="handleRename"
          @switchNodeOrder="switchNodeOrder"
          @deleteDepartment="deleteDepartment" />

        <!-- 添加根组织 -->
        <div v-if="addDepartmentShow && addDepartmentParentId === item.id" class="new-department">
          <div class="folder-icon">
            <span class="icon icon-user-file-close-01"></span>
          </div>
          <bk-input
            v-focus
            v-model="addDepartmentName"
            ref="addRootDepartment"
            type="text"
            font-size="medium"
            class="adding-input"
            :placeholder="$t('按Enter键确认添加')"
            @enter="confirmAdd(item)"
            @blur="cancelAdd"
            @keydown="handleKeydown"
          ></bk-input>
        </div>
      </li>
    </ul>
  </div>

</template>

<script>
export default {
  name: 'OrganizationTree',
  directives: {
    focus: {
      inserted(el) {
        const input = el.getElementsByTagName('input')[0];
        if (input) {
          input.focus();
        }
      },
    },
  },
  props: {
    treeDataList: {
      type: Array,
      default: [],
    },
    treeIndex: {
      type: Number,
      default: 0,
    },
    treeSearchResult: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      // 根目录新增组织
      addDepartmentShow: false,
      addDepartmentParentId: '',
      addDepartmentName: '',
    };
  },
  computed: {
    noSearchOrSearchDepartment() {
      return Boolean(!this.treeSearchResult || (this.treeSearchResult && this.treeSearchResult.groupType === 'department'));
    },
  },
  methods: {
    handleClickToggle(item) {
      this.$emit('handleClickToggle', item);
    },
    handleClickTreeNode(item) {
      const isSearchProfile = this.treeSearchResult && this.treeSearchResult.type !== 'department';
      this.$emit('handleClickTreeNode', item, isSearchProfile);
    },
    handleClickOption(item, event) {
      this.$emit('handleClickOption', item, event);
    },

    // 上移、下移
    switchNodeOrder(param) {
      this.$emit('switchNodeOrder', param);
    },
    shiftNodeUp(item, index) {
      item.showShiftUpTips = false;
      if (index !== 0) {
        this.$emit('switchNodeOrder', { item, index, type: 'up' });
      }
    },
    checkUpTips(item, index) {
      if (index === 0) {
        this.$set(item, 'showShiftUpTips', true);
      }
    },
    closeUpTips(item) {
      item.showShiftUpTips = false;
    },
    shiftNodeDown(item, index) {
      item.showShiftDownTips = false;
      if (index !== this.treeDataList.length - 1) {
        this.$emit('switchNodeOrder', { item, index, type: 'down' });
      }
    },
    checkDownTips(item, index) {
      if (index === this.treeDataList.length - 1) {
        this.$set(item, 'showShiftDownTips', true);
      }
    },
    closeDownTips(item) {
      item.showShiftDownTips = false;
    },

    // 重命名
    handleRename(item, type) {
      this.$emit('handleRename', item, type);
    },

    // 复制id或名称
    handleCopyIdSuccess() {
      this.messageSuccess(this.$t('复制id成功'));
    },
    handleCopyIdError() {
      this.messageError(this.$t('复制id失败'));
    },
    handleCopyNameSuccess() {
      this.messageSuccess(this.$t('复制组织名称成功'));
    },
    handleCopyNameError() {
      this.messageError(this.$t('复制组织名称失败'));
    },

    // 删除组织节点
    deleteDepartment(item, index) {
      if (item.has_children) {
        item.showDeleteTips = false;
        return;
      }
      this.$emit('deleteDepartment', item, index);
    },
    checkDeleteTips(item) {
      if (item.has_children) {
        this.$set(item, 'showDeleteTips', true);
      }
    },
    closeDeleteTips(item) {
      item.showDeleteTips = false;
    },

    // 添加子组织
    addChild(item) {
      item.showAddChildTips = false;
      if (this.treeIndex === 9) {
        return;
      }
      this.$emit('addChildDepartment', item);
    },
    checkAddTips(item) {
      if (this.treeIndex === 9) {
        this.$set(item, 'showAddChildTips', true);
      }
    },
    closeAddTips(item) {
      item.showAddChildTips = false;
    },
    addChildDepartment(item) {
      this.$emit('addChildDepartment', item);
    },

    // 添加根组织
    addRootDepartment(item) {
      item.showChildren = true;
      this.addDepartmentShow = true;
      this.addDepartmentParentId = item.id;
    },
    cancelAdd() {
      this.addDepartmentShow = false;
      this.addDepartmentParentId = '';
      this.addDepartmentName = '';
    },
    handleKeydown(value, event) {
      if (event.code === 'Escape') {
        this.cancelAdd();
      }
    },
    async confirmAdd(item) {
      const name = this.addDepartmentName.trim();
      if (!name) {
        this.cancelAdd();
        return;
      }
      try {
        this.$emit('showTreeLoading');
        const params = {
          name: this.addDepartmentName,
          category_id: this.addDepartmentParentId,
        };
        const res = await this.$store.dispatch('organization/addDepartment', params);
        const newDepartment = res.data;
        newDepartment.isNewDeparment = true;
        this.$parent.filterTreeData(newDepartment, item, item.type === 'local');
        item.children.push(newDepartment);
        this.cancelAdd();
        this.$emit('handleClickTreeNode', newDepartment);
      } catch (e) {
        console.warn(e);
        this.$refs.addRootDepartment[0].$el.getElementsByTagName('input')[0].focus();
      } finally {
        this.$emit('closeTreeLoading');
      }
    },
  },
};
</script>

<style lang="scss" scoped>
li.tree-first-node {
  font-size: 14px;
  font-weight: 400;
  color: rgba(115, 121, 135, 1);
  line-height: 36px;

  @keyframes tree-opacity {
    0% {
      opacity: 0;
    }

    100% {
      opacity: 1;
    }
  }

  > .tree-node {
    display: flex;
    align-items: center;
    position: relative;
    padding: 0 36px 0 20px;
    transition: all .3s ease;

    > .toggle-icon {
      flex-shrink: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      width: 16px;
      height: 16px;
      margin-right: 2px;
      cursor: pointer;

      > .icon-user-triangle {
        opacity: 1;
        font-size: 12px;
        transform: rotate(-90deg);
        transition: all .3s ease;

        &::before {
          color: #979ba5;
        }

        &.hidden {
          opacity: 0;
        }
      }
    }

    > .main-node {
      width: calc(100% - 18px);
      flex-shrink: 1;
      display: flex;
      align-items: center;
      cursor: pointer;

      > .folder-icon {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-right: 8px;
        width: 20px;
        height: 20px;

        &.root-node {
          border-radius: 2px;
          background: #c4c6cc;
        }
        // 根节点 icon
        .icon-root-node-i {
          font-size: 12px;
          background: #c4c6cc;

          &::before {
            color: #fff;
            background: #c4c6cc;
          }
        }
        // 组织节点 icon
        .icon-user-file-close-01 {
          font-size: 18px;

          &::before {
            color: #a3c5fd;
          }
        }
      }

      > .depart-name {
        width: calc(100% - 28px);
        font-size: 14px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    > .option {
      display: none;
      align-items: center;
      position: absolute;
      top: 0;
      right: 0;
      width: 34px;
      height: 36px;

      > .icon-more {
        font-size: 20px;
        cursor: pointer;
      }

      > .dropdown-list {
        position: fixed;
        top: -1000px;
        left: -1000px;
        width: 174px;
        background: #fff;
        border-radius: 2px;
        border: 1px solid #dcdee5;
        box-shadow: 0 2px 6px rgba(51, 60, 72, .1);
        z-index: 1000000;
        // 英文
        &.chang-en {
          .specific-menu {
            a {
              padding: 0 10px;
              white-space: normal;
              line-height: 28px;
            }

            .tooltip-content {
              width: 180px;
            }
          }
        }
        // 添加下级组织
        .specific-menu {
          position: relative;

          .tooltip-content {
            opacity: 0;
            position: absolute;
            left: 94px;
            top: 2px;
            padding: 0 5px;
            font-size: 12px;
            line-height: 32px;
            width: 110px;
            text-align: center;
            background: #333;
            color: #fff;
            border-radius: 3px;
            z-index: 2000;
            transition: all .3s ease;

            &.show-tooltip-content {
              opacity: 1;
            }

            .arrow {
              position: absolute;
              top: 50%;
              left: -1px;
              width: 8px;
              height: 8px;
              border-top: 1px solid #333;
              border-left: 1px solid #333;
              transform: rotate(-45deg) translateY(-50%);
              z-index: 10;
              background: #333;
            }
          }

          a {
            padding-left: 20px;
            font-size: 14px;
            display: block;
            color: #737987;
            line-height: 36px;
            text-decoration: none;
            white-space: nowrap;

            &.delete {
              color: #ec4848;
            }

            &:hover {
              color: #3b84ff;
              background: #e1ecff;
            }

            &.disable {
              cursor: not-allowed;
              color: #c4c6cc;
            }

            &.delete-disable {
              color: #c4c6cc;
              cursor: not-allowed;
            }
          }
        }
      }
    }

    .add-button {
      display: none;
      align-items: center;
      position: absolute;
      top: 0;
      right: 0;
      width: 34px;
      height: 36px;

      > .icon-plus {
        padding: 4px;
        font-size: 12px;
        font-weight: bold;
        cursor: pointer;
      }
    }

    &.first-tree-node {
      padding-left: 20px !important;
    }

    &.expand > .toggle-icon > .icon-user-triangle {
      transition: all .3s ease;
      transform: rotate(0);
    }

    &:hover {
      background: #f0f1f5;

      > .option,
      .add-button {
        display: flex;
      }
    }

    &.active {
      color: #4b8fff;
      background: #e1ecff;

      > .main-node > .folder-icon {
        .icon-user-file-close-01 {
          &::before {
            color: #4b8fff;
          }
        }

        .icon-root-node-i::before {
          background: #3a84ff !important;
        }

        &.root-node {
          background: #3a84ff;
        }
      }

      > .option {
        display: flex;
      }
    }
  }

  > .new-department {
    position: relative;
    display: flex;
    align-items: center;
    padding-left: 35px;
    padding-right: 20px;
    height: 36px;

    > .folder-icon {
      display: flex;
      justify-content: center;
      align-items: center;
      position: absolute;
      left: 48px;
      top: 8px;
      width: 20px;
      height: 20px;
      z-index: 10;

      > .icon-user-file-close-01 {
        font-size: 18px;

        &::before {
          color: #c4c6cc;
        }
      }
    }

    > .adding-input {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 32px;
      line-height: initial;

      /deep/ .bk-form-input {
        padding-left: 41px;
      }
    }
  }

  > .tree-node-loading {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 32px;
    animation: tree-opacity .3s;

    > img {
      width: 14px;
    }

    > .loading-text {
      font-size: 12px;
      padding-left: 4px;
      color: #a3c5fd;
    }
  }
}
</style>
