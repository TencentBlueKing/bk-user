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
  <div class="set-department-wrapper" v-bkloading="{ isLoading: basicLoading }">
    <div class="department-content">
      <h4 class="depart-title">{{$t('待选择列表')}}</h4>
      <div class="all-department">
        <!-- 搜索框 -->
        <bk-input v-model="searchKey"
                  class="king-input-search"
                  style="margin: 24px 24px 20px;width: calc(100% - 48px);"
                  :placeholder="$t('搜索组织')"
                  :clearable="true"
                  :left-icon="'bk-icon icon-search'"
                  @input="handleInput"
                  @keydown="handleKeydown"
                  @clear="clearSearchKey"
                  @left-icon-click="handleSearchDepartment">
        </bk-input>
        <div class="department-content-wrapper">
          <!-- 搜索结果 -->
          <div class="search-content-container" v-if="searchStatus">
            <template v-if="searchList.length">
              <div class="search-content">
                <p v-for="(item, index) in searchList" class="search-item"
                   :class="index === selectedIndex && 'selected'" :key="item.id" @click="selectItem(item)">
                  <input type="checkbox" class="checkbox" :checked="item.isChecked" />{{item.name}}
                </p>
                <p v-if="searchList.length >= searchLength" class="search-item">{{$t('完善关键字搜索更多内容')}}</p>
              </div>
            </template>
            <div v-else class="no-search-result">
              <p>{{$t('搜索结果为空！')}}</p>
              <p>{{$t('建议检查关键字是否准确')}}</p>
            </div>
          </div>
          <!-- 组织树 -->
          <div class="department-tree-wrapper" v-else>
            <ExportTree v-if="treeDataList" :tree-data-list="treeDataList"
                        @handleClickToggle="handleClickToggle"
                        @selectItem="selectItem" />
          </div>
        </div>
      </div>
    </div>
    <div class="selected-department">
      <h4 class="depart-title">
        {{$t('已选择列表')}}({{selectedDepartments.length}})
        <span class="clear" @click="clearSelected">{{$t('清空')}}</span>
      </h4>
      <div class="selected-content" data-test-id="list_selDepartmentsData">
        <ul v-if="selectedDepartments.length">
          <li class="selected-list" v-for="(item, index) in selectedDepartments" :key="item.id">
            <span class="title" v-bk-overflow-tips>{{item.name}}</span>
            <i class="icon-user-close" @click="deleteSelected(item, index)"></i>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import ExportTree from '@/components/organization/ExportTree';

export default {
  components: {
    ExportTree,
  },
  props: {
    currentCategoryId: {
      type: Number,
      required: true,
    },
    // [{ id, name }]
    initialDepartments: {
      type: Array,
      default() {
        return [];
      },
    },
  },
  data() {
    return {
      treeDataList: null,
      // 设置所在组织： 已选择的组织List
      selectedDepartments: [],
      searchKey: '',
      searchStatus: false,
      // 指定返回的最大组织长度
      searchLength: 40,
      selectedIndex: null,
      searchList: [],
      currParent: [],
      currChildren: [],
      basicLoading: true,
    };
  },
  watch: {
    'selectedDepartments'(val) {
      this.$emit('getDepartments', val);
    },
  },
  created() {
    if (this.initialDepartments.length) {
      this.selectedDepartments = JSON.parse(JSON.stringify(this.initialDepartments));
    }
    this.initDepartmentTree();
  },
  methods: {
    async initDepartmentTree() {
      try {
        const { data: departments } = await this.$store.dispatch('organization/getOrganizationTree');
        for (let i = 0; i < departments.length; i++) {
          if (departments[i].id === this.currentCategoryId) {
            const list = JSON.parse(JSON.stringify(departments[i].departments));
            list.forEach((item) => {
              this.filterTreeNode(item);
            });
            this.treeDataList = list;
            break;
          }
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.basicLoading = false;
      }
    },
    filterTreeNode(node) {
      // 是否选中
      this.$set(node, 'isChecked', false);
      // 展示子级
      this.$set(node, 'showChildren', false);
      this.$set(node, 'showLoading', false);

      for (let i = 0; i < this.selectedDepartments.length; i++) {
        if (this.selectedDepartments[i].id === node.id) {
          this.$set(node, 'isChecked', true);
          this.selectedDepartments.splice(i, 1, node);
          break;
        }
      }
      if (node.children && node.children.length) {
        node.children.forEach((item) => {
          this.filterTreeNode(item);
        });
      }
    },
    // 展开对应的组织
    async handleClickToggle(item) {
      if ((item.children && item.children.length) || item.has_children === false) {
        item.showChildren = !item.showChildren;
        return;
      }
      try {
        item.showLoading = true;
        const res = await this.$store.dispatch('organization/getDataById', { id: item.id });
        res.data.children.forEach((child) => {
          this.filterTreeNode(child);
        });
        this.$set(item, 'children', res.data.children);
        item.showChildren = !item.showChildren;
      } catch (e) {
        console.warn(e);
      } finally {
        item.showLoading = false;
      }
    },

    handleInput() {
      this.selectedIndex = null;
    },
    handleKeydown(value, e) {
      const index = this.selectedIndex;
      const length = this.searchList.length;
      const code = e.code;
      if (code === 'NumpadEnter' || code === 'Enter') {
        if (index === null) {
          this.handleSearchDepartment();
        } else {
          this.selectItem(this.searchList[index]);
        }
      } else if (code === 'ArrowUp') {
        if (index === null || index === 0) {
          this.selectedIndex = length - 1;
        } else {
          this.selectedIndex -= 1;
        }
        this.calculateScroll('start');
      } else if (code === 'ArrowDown') {
        if (index === null || index === length - 1) {
          this.selectedIndex = 0;
        } else {
          this.selectedIndex += 1;
        }
        this.calculateScroll('end');
      }
    },
    calculateScroll(type) {
      this.$nextTick(() => {
        const searchPanelPosInfo = document.querySelector('.search-content-container').getBoundingClientRect();
        const activeItemPosInfo = document.querySelector('.search-item.selected').getBoundingClientRect();
        const minY = searchPanelPosInfo.top;
        const maxY = minY + 276;
        const topIsVisible = activeItemPosInfo.top >= minY && activeItemPosInfo.top < maxY;
        const bottomIsVisible = activeItemPosInfo.top + 36 >= minY && activeItemPosInfo.top + 36 < maxY;
        if (!(topIsVisible && bottomIsVisible)) {
          document.querySelector('.search-item.selected').scrollIntoView({
            block: type,
          });
        }
      });
    },
    // 点击组织 checkbox
    selectItem(item) {
      item.isChecked = !item.isChecked;
      if (item.isChecked === true) {
        // 选中
        this.selectedDepartments.push(item);
      } else {
        // 取消选中
        for (let i = 0; i < this.selectedDepartments.length; i++) {
          if (this.selectedDepartments[i].id === item.id) {
            this.selectedDepartments.splice(i, 1);
            break;
          }
        }
      }
    },
    // 删除选中的组织
    deleteSelected(item, index) {
      item.isChecked = false;
      this.selectedDepartments.splice(index, 1);
    },
    // 清空选中的组织
    clearSelected() {
      this.selectedDepartments.forEach((item) => {
        item.isChecked = false;
      });
      this.selectedDepartments = [];
    },
    // 清空搜索的内容
    clearSearchKey() {
      this.searchList = [];
      this.searchKey = '';
      this.searchStatus = false;
      this.treeDataList.forEach((node) => {
        this.filterCheckStatus(node);
      });
    },
    filterCheckStatus(node) {
      node.isChecked = false;
      for (let i = 0; i < this.selectedDepartments.length; i++) {
        if (this.selectedDepartments[i].id === node.id) {
          node.isChecked = true;
          this.selectedDepartments.splice(i, 1, node);
          break;
        }
      }
      if (node.has_children === true && node.children) {
        node.children.forEach((item) => {
          this.filterCheckStatus(item);
        });
      }
    },

    // 搜索对应的组织名称
    async handleSearchDepartment() {
      const keyword = this.searchKey.trim();
      if (!keyword) {
        this.clearSearchKey();
        return;
      }
      try {
        this.basicLoading = true;
        const res = await this.$store.dispatch('organization/searchDataByCategory', {
          id: this.currentCategoryId,
          keyword,
          searchLength: this.searchLength,
        });
        const originList = res.data;
        if (!originList.length) {
          this.messageWarn(this.$t('没有找到相关的结果'));
          this.searchList = [];
        } else {
          originList.forEach(node => this.filterCheckStatus(node));
          this.searchList = originList;
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.basicLoading = false;
        this.searchStatus = true;
        this.selectedIndex = null;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../../scss/mixins/scroller';

.set-department-wrapper {
  display: flex;
  width: 721px;
}

.department-content {
  width: 361px;
  border-right: 1px solid #dcdee5;
}

.selected-department {
  width: 360px;
}

.depart-title {
  position: relative;
  padding-left: 24px;
  height: 42px;
  font-size: 14px;
  color: rgba(49, 50, 56, 1);
  line-height: 42px;
  font-weight: 500;
  background: #fafbfd;
  border: 1px solid #dcdee5;
  border-left: none;
  border-right: none;

  .clear {
    position: absolute;
    right: 24px;
    top: 13px;
    font-size: 12px;
    color: rgba(58, 132, 255, 1);
    line-height: 16px;
    cursor: pointer;
  }
}

.department-infor {
  height: 276px;
  overflow: hidden;
  overflow-y: auto;
}

.department-tree-wrapper,
.search-content-container {
  height: 276px;
  overflow: hidden;
  overflow-y: auto;

  @include scroller($backgroundColor: #e6e9ea, $width: 4px);
}

.search-content-container {
  padding-left: 24px;

  > .search-content {
    display: flex;
    flex-flow: column;

    > .search-item {
      display: flex;
      align-items: center;
      padding: 4px 0;
      margin-right: 24px;
      cursor: pointer;

      input {
        flex-shrink: 0;
      }

      &.selected,
      &:hover {
        background: #e1ecff;
      }
    }
  }

  > .no-search-result {
    display: flex;
    flex-flow: column;
    justify-content: center;
    align-items: center;
    height: 200px;
    padding-right: 24px;

    p {
      text-align: center;
      font-size: 12px;
      line-height: 18px;
      color: #63656e;

      &:last-child {
        color: #c4c6cc;
      }
    }
  }
}

.selected-department {
  .depart-title {
    padding-left: 15px;
  }
}

.selected-content {
  padding-top: 15px;
  height: 330px;
  overflow: hidden;
  overflow-y: auto;

  @include scroller($backgroundColor: #e6e9ea, $width: 4px);
}

.selected-list {
  position: relative;
  padding: 0 24px 0 15px;
  height: 36px;
  line-height: 36px;
  font-size: 14px;
  font-weight: 400;
  color: rgba(115, 121, 135, 1);

  .title {
    display: block;
    width: calc(100% - 24px);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .icon-user-close {
    position: absolute;
    right: 24px;
    top: 13px;
    font-size: 10px;
    cursor: pointer;
  }
}

.checkbox {
  margin: 0 4px;
  display: inline-block;
  vertical-align: middle;
  width: 14px;
  height: 14px;
  outline: none;
  visibility: visible;
  cursor: pointer;
  background: #fff;
  background-image: url('../../images/icon.png');
  background-position: 0 -95px;
  appearance: none;

  &:checked {
    background-position: -33px -95px;
  }
}
</style>
