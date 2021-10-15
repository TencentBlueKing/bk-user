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
  <transition name="fade">
    <div class="export-container">
      <div class="export-main-content" v-bkloading="{ isLoading: basicLoading }">
        <div class="department-content">
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
          <div class="department-result">
            <!-- 搜索结果 -->
            <div class="search-content-container" v-if="searchStatus">
              <template v-if="searchList.length">
                <p v-for="(item, index) in searchList"
                   :key="index" class="search-item"
                   :class="[item.disabled && 'disabled', index === selectedIndex && 'selected']"
                   @click.stop="selectSearchItem(item)">
                  <bk-checkbox :value="item.isChecked" :disabled="item.disabled" class="king-checkbox"></bk-checkbox>
                  <span class="search-item-text">{{item.name}}</span>
                </p>
                <p class="search-item" v-if="searchList.length >= searchLength">{{$t('完善关键字搜索更多内容')}}</p>
              </template>
              <div v-else class="no-search-result">
                <p>{{$t('搜索结果为空！')}}</p>
                <p>{{$t('建议检查关键字是否准确')}}</p>
              </div>
            </div>
            <!-- 组织树 -->
            <div class="department-tree-wrapper" v-else>
              <ExportTree :tree-data-list="treeDataList"
                          @handleClickToggle="handleClickToggle"
                          @selectItem="selectItem" />
            </div>
          </div>
        </div>
        <div class="selected-department">
          <h4 class="depart-title">
            {{$t('已选择列表')}}({{selectedDepartments.length}})
            <span class="clear" @click="clearSelected">{{$t('清空')}}</span>
          </h4>
          <div class="selected-content" data-test-id="list_selDepartmentsData">
            <ul v-if="selectedDepartments.length" class="selected-list-wrapper">
              <li class="selected-list" v-for="(item, index) in selectedDepartments" :key="index">
                <span class="title" v-bk-overflow-tips>{{item.name}}</span>
                <i class="icon-user--close" @click="deleteSelected(item, index)"></i>
              </li>
            </ul>
          </div>
          <div class="submit-btn">
            <bk-button theme="primary" class="operate-btn" @click="handleExport">
              {{$t('确定')}}
            </bk-button>
            <bk-button theme="default" class="operate-btn" @click="handleCancelExport">
              {{$t('取消')}}
            </bk-button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import ExportTree from '@/components/organization/ExportTree';

export default {
  components: {
    ExportTree,
  },
  props: {
    showing: {
      type: Boolean,
      default: false,
    },
    departments: {
      type: Array,
      required: true,
    },
    id: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      treeDataList: [],
      // 设置所在组织： 已选择的组织List
      selectedDepartments: [],
      searchKey: '',
      searchLength: 40,
      selectedIndex: null,
      searchStatus: false,
      searchList: [],
      basicLoading: false,
    };
  },
  mounted() {
    this.initDepartmentTree();
  },
  methods: {
    initDepartmentTree() {
      for (let i = 0; i < this.departments.length; i++) {
        if (this.departments[i].id === this.id) {
          const list = JSON.parse(JSON.stringify(this.departments[i].departments));
          list.forEach((item) => {
            this.filterTreeNode(item, false, []);
          });
          this.treeDataList = list;
          break;
        }
      }
    },
    filterTreeNode(node, disabled, ancestors) {
      // 是否选中
      this.$set(node, 'isChecked', false);
      // 展示子级
      this.$set(node, 'showChildren', false);
      this.$set(node, 'showLoading', false);
      // 是否禁用
      this.$set(node, 'disabled', disabled);
      this.$set(node, 'ancestors', ancestors);

      for (let i = 0; i < this.selectedDepartments.length; i++) {
        if (this.selectedDepartments[i].id === node.id) {
          this.$set(node, 'isChecked', true);
          this.selectedDepartments.splice(i, 1, node);
          break;
        }
      }
      if (node.children && node.children.length) {
        node.children.forEach((item) => {
          this.filterTreeNode(item, disabled, [...ancestors, { id: node.id }]);
        });
      }
    },
    // 展开对应的组织
    async handleClickToggle(node) {
      if ((node.children && node.children.length) || node.has_children === false) {
        node.showChildren = !node.showChildren;
        return;
      }
      // 有子节点，但是还没加载 children 数据
      try {
        node.showLoading = true;
        const res = await this.$store.dispatch('organization/getDataById', { id: node.id });
        res.data.children.forEach((child) => {
          let disabled = false;
          if (node.isChecked === true || node.disabled === true) {
            disabled = true;
          }
          this.filterTreeNode(child, disabled, [...node.ancestors, { id: node.id }]);
        });
        this.$set(node, 'children', res.data.children);
        node.showChildren = !node.showChildren;
      } catch (e) {
        console.warn(e);
      } finally {
        node.showLoading = false;
      }
    },
    // 点击组织 checkbox
    selectItem(item) {
      item.isChecked = !item.isChecked;
      // 控制子组织是否禁用选择
      if (item.children && item.children.length > 0) {
        item.children.forEach((child) => {
          this.filterChildren(child, item.isChecked);
        });
      }

      if (item.isChecked) {
        // 选中时，在右侧增加选中的组织信息
        this.selectedDepartments.push(item);
      } else {
        // 如果是取消选择，就要在 selectedDepartments 中删除
        for (let i = 0; i < this.selectedDepartments.length; i++) {
          if (this.selectedDepartments[i].id === item.id) {
            this.selectedDepartments.splice(i, 1);
            break;
          }
        }
      }
    },
    // 选择组织后过滤下级组织不可选
    filterChildren(item, bool) {
      item.disabled = bool;
      item.isChecked = false;
      // 如果选中时，有子组织也被选中，selectedDepartments 中需要删除相应子组织
      this.deleteChildFromSelected(item);
      if (item.children && item.children.length > 0) {
        item.children.forEach((child) => {
          this.filterChildren(child, bool);
        });
      }
    },
    deleteChildFromSelected(item) {
      for (let i = 0; i < this.selectedDepartments.length; i++) {
        if (this.selectedDepartments[i].id === item.id) {
          this.selectedDepartments.splice(i, 1);
          return;
        }
      }
    },
    // 删除对应的组织
    deleteSelected(item, index) {
      item.isChecked = false;
      if (this.searchList.length) {
        this.selectedDepartments.splice(index, 1);
        this.searchList.forEach((item) => {
          this.filterSearch(item);
        });
      } else {
        this.recoverDisabled(item);
        this.selectedDepartments.splice(index, 1);
      }
    },
    // 删除组织后，恢复子节点的 disable
    recoverDisabled(item) {
      if (item.children && item.children.length) {
        item.children.forEach((child) => {
          this.$set(child, 'disabled', false);
          if (child.children && child.children.length) {
            this.recoverDisabled(child);
          }
        });
      }
    },
    // 清空所选组织
    clearSelected() {
      this.selectedDepartments.forEach((item) => {
        item.isChecked = false;
        this.recoverDisabled(item);
      });
      this.selectedDepartments = [];
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
        } else if (!this.searchList[index].disabled) {
          this.selectSearchItem(this.searchList[index]);
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
        const searchPanelPosInfo = document.querySelector('.department-result').getBoundingClientRect();
        const activeItemPosInfo = document.querySelector('.search-item.selected').getBoundingClientRect();
        const minY = searchPanelPosInfo.top;
        const maxY = minY + 404;
        const topIsVisible = activeItemPosInfo.top >= minY && activeItemPosInfo.top < maxY;
        const bottomIsVisible = activeItemPosInfo.top + 36 >= minY && activeItemPosInfo.top + 36 < maxY;
        if (!(topIsVisible && bottomIsVisible)) {
          document.querySelector('.search-item.selected').scrollIntoView({
            block: type,
          });
        }
      });
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
          id: this.id,
          keyword,
          withAncestors: true,
          searchLength: this.searchLength,
        });
        const originList = res.data;
        if (!originList.length) {
          this.messageWarn(this.$t('没有找到相关的结果'));
          return;
        }
        originList.forEach(item => this.filterSearch(item));
        this.searchList = originList;
      } catch (e) {
        console.warn(e);
      } finally {
        this.searchStatus = true;
        this.basicLoading = false;
        this.selectedIndex = null;
      }
    },
    filterSearch(item) {
      item.isChecked = false;
      item.disabled = false;
      for (let i = 0; i < this.selectedDepartments.length; i++) {
        const selectedId = this.selectedDepartments[i].id;
        if (selectedId === item.id) {
          // 判断已选择的是不是搜索项
          item.isChecked = true;
          this.selectedDepartments.splice(i, 1, item);
          break;
        } else if (item.ancestors) {
          // 判断已选择的是不是搜索项的祖先
          // 如果已选择列表有搜索项的祖先，搜索项将被禁用选择
          // 如果后台没有返回 ancestors 就无法保证只导出父节点
          const ancestors = item.ancestors;
          for (let j = 0; j < ancestors.length; j++) {
            if (selectedId === ancestors[j].id) {
              item.disabled = true;
              break;
            }
          }
        }
      }
    },
    selectSearchItem(item) {
      if (item.disabled) {
        return;
      }
      item.isChecked = !item.isChecked;

      if (item.isChecked) {
        // 选中时，在右侧增加选中的组织信息
        this.selectedDepartments.push(item);
        // 看下已经存在的选项是否是新选项的子集，如果是就 uncheck 掉 如果存在选项没有 ancestors 字段说明不在搜索结果里不去处理
        const toDeleteIndex = [];
        for (let i = 0; i < this.selectedDepartments.length; i++) {
          const selectedId = this.selectedDepartments[i].id;
          if (selectedId !== item.id && this.selectedDepartments[i].ancestors) {
            for (let j = 0; j < this.selectedDepartments[i].ancestors.length; j++) {
              if (this.selectedDepartments[i].ancestors[j].id === item.id) {
                this.selectedDepartments[i].isChecked = false;
                toDeleteIndex.unshift(i);
                break;
              }
            }
          }
        }
        toDeleteIndex.forEach((index) => {
          this.selectedDepartments.splice(index, 1);
        });
      } else {
        // 如果是取消选择，就要在 selectedDepartments 中删除
        for (let i = 0; i < this.selectedDepartments.length; i++) {
          if (this.selectedDepartments[i].id === item.id) {
            this.selectedDepartments.splice(i, 1);
            break;
          }
        }
      }

      this.searchList.forEach((item) => {
        this.filterSearch(item);
      });
    },
    // 清空搜索的内容
    clearSearchKey() {
      this.searchList = [];
      this.searchKey = '';
      this.searchStatus = false;
      this.treeDataList.forEach((item) => {
        this.filterCheckStatus(item);
      });
    },
    filterCheckStatus(node) {
      node.isChecked = false;
      node.disabled = false;
      for (let i = 0; i < this.selectedDepartments.length; i++) {
        if (this.selectedDepartments[i].id === node.id) {
          node.isChecked = true;
          this.selectedDepartments.splice(i, 1, node);
          if (node.children && node.children.length) {
            node.children.forEach((child) => {
              this.filterDisabled(child);
            });
          }
          return;
        }
      }
      if (node.has_children === true && node.children) {
        node.children.forEach((item) => {
          this.filterCheckStatus(item);
        });
      }
    },
    filterDisabled(node) {
      this.$set(node, 'disabled', true);
      if (node.children && node.children.length) {
        node.children.forEach((child) => {
          this.filterDisabled(child);
        });
      }
    },
    // 确定
    handleExport() {
      if (!this.selectedDepartments.length) {
        this.$bkMessage({
          message: this.$t('请选择组织'),
          theme: 'warning',
        });
        return;
      }
      this.$emit('update:showing', false);
      // 导出的下载链接
      let url = window.AJAX_URL;
      if (url.endsWith('/')) {
        // 去掉末尾的斜杠
        url = url.slice(0, url.length - 1);
      }
      if (!url.startsWith('http')) {
        // tips: 后端提供的 SITE_URL 需以 / 开头
        url = window.location.origin + url;
      }
      url = `${url}/api/v2/categories/${this.id}/export/?department_ids=${this.selectedDepartments.map(item => item.id).join(',')}`;
      window.open(url);
    },
    // 取消
    handleCancelExport() {
      this.$emit('update:showing', false);
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../../../scss/mixins/scroller';
.export-container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 2000;
  background: rgba(0, 0, 0, .6);

  > .export-main-content {
    display: flex;
    width: 721px;
    height: 480px;
    background: #fff;
    border-radius: 2px;

    > .department-content {
      width: 361px;
      height: 100%;
      border-right: 1px solid #dcdee5;
    }

    > .selected-department {
      width: 360px;
      height: 100%;
    }
  }
}

.department-content {
  .department-result {
    height: calc(100% - 76px);
    overflow: hidden;
    overflow-y: auto;

    @include scroller($backgroundColor: #e6e9ea, $width: 4px);
  }
}

.selected-department {
  position: relative;

  .depart-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px;
    height: 80px;
    font-size: 14px;
    line-height: 20px;
    font-weight: bold;
    color: #63656e;

    .clear {
      font-size: 14px;
      line-height: 20px;
      color: #3a84ff;
      cursor: pointer;
    }
  }

  .submit-btn {
    position: absolute;
    bottom: 25px;
    left: 29px;

    .operate-btn {
      margin-right: 10px;

      &:last-child {
        margin-right: 0;
      }
    }
  }
}

.search-content-container {
  display: flex;
  flex-flow: column;
  padding-left: 24px;

  .search-item {
    display: flex;
    align-items: center;
    padding: 4px 0;
    margin-right: 24px;
    cursor: pointer;
    font-size: 14px;
    line-height: 21px;
    color: #63656e;

    .king-checkbox {
      flex-shrink: 0;
      padding: 0 6px;
    }

    &.selected,
    &:hover {
      background: #e1ecff;
      border-radius: 2px;
    }

    &.disabled {
      cursor: not-allowed;

      &.selected {
        background: #f0f1f5;
      }
    }
  }

  .no-search-result {
    display: flex;
    flex-flow: column;
    justify-content: center;
    align-items: center;
    height: 300px;
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

.selected-content {
  position: relative;
  height: 343px;
  overflow: hidden;
  overflow-y: auto;

  @include scroller($backgroundColor: #e6e9ea, $width: 4px);
}

.selected-list {
  position: relative;
  padding: 0 24px 0 24px;
  height: 28px;
  line-height: 28px;
  font-size: 14px;
  font-weight: 400;
  color: #63656e;

  .title {
    display: block;
    max-width: 294px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .icon-user--close {
    position: absolute;
    right: 24px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 18px;
    cursor: pointer;

    &::before {
      color: #c4c6cc;
    }
  }
}
</style>
