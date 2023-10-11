<template>
  <bk-loading class="set-department-wrapper" :loading="basicLoading">
    <div class="department-content">
      <div class="all-department">
        <!-- 搜索框 -->
        <bk-input
          v-model="searchKey"
          class="king-input-search"
          placeholder="搜索组织"
          :clearable="true"
          :left-icon="'bk-icon icon-search'"
          @input="handleInput"
          @clear="clearSearchKey"
          @left-icon-click="handleSearchDepartment">
        </bk-input>
        <div class="department-content-wrapper">
          <!-- 搜索结果 -->
          <div class="search-content-container" v-if="searchStatus">
            <template v-if="searchList.length">
              <div class="search-content">
                <p
                  v-for="(item, index) in searchList" class="search-item"
                  :class="index === selectedIndex && 'selected'" :key="item.id" @click="selectItem(item)">
                  <input type="checkbox" class="checkbox" :checked="item.isChecked" />{{item.name}}
                </p>
                <p v-if="searchList.length >= searchLength" class="search-item">完善关键字搜索更多内容</p>
              </div>
            </template>
            <div v-else class="no-search-result">
              <Empty
                :is-search-empty="!searchList.length"
                @handleEmpty="clearSearchKey" />
            </div>
          </div>
          <!-- 组织树 -->
          <div class="department-tree-wrapper" v-else>
            <Tree :tree-data="treeDataList" />
          </div>
        </div>
      </div>
    </div>
    <div class="selected-department">
      <div>已选择</div>
      <div class="selected-content" data-test-id="list_selDepartmentsData">
        123
        <ul v-if="selectedDepartments.length">
          <li class="selected-list" v-for="(item, index) in selectedDepartments" :key="item.id">
            <span class="title">{{item.name}}</span>
            <i class="icon-user-close" @click="deleteSelected(item, index)"></i>
          </li>
        </ul>
      </div>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">
import { defineProps, onMounted, ref, watch } from 'vue';

import Tree from './Tree.vue';

import Empty from '@/components/Empty.vue';
import {
  getTenantOrganizationList,
} from '@/http/organizationFiles';

const props = defineProps({
  currentCategoryId: {
    type: Number,
    required: true,
  },
  initialDepartments: {
    type: Array,
    default: () => ([]),
  },
});

const basicLoading = ref(false);
const searchKey = ref('');
const searchStatus = ref(false);
const searchList = ref([]);
const selectedIndex = ref(null);
const treeDataList = ref([]);
// 设置所在组织： 已选择的组织List
const selectedDepartments = ref([]);

watch(() => selectedDepartments.value, (val) => {
  console.log('val', val);
});

onMounted(() => {
  basicLoading.value = true;
  if (props.initialDepartments.length) {
    selectedDepartments.value = JSON.parse(JSON.stringify(props.initialDepartments));
  }
  initDepartmentTree();
});

const initDepartmentTree = async () => {
  try {
    const res = await getTenantOrganizationList();
    treeDataList.value = res.data;
  } catch (e) {
    console.warn(e);
  } finally {
    basicLoading.value = false;
  }
};

const handleInput = () => {
  selectedIndex.value = null;
};

const clearSearchKey = () => {
  searchList.value = [];
  searchKey.value = '';
  initDepartmentTree();
};

const handleSearchDepartment = () => {
  console.log('搜索组织名');
};
</script>

<style lang="less" scoped>
.set-department-wrapper {
  display: flex;
  width: 721px;
}

.department-content {
  width: 50%;
  padding-right: 24px;
  border-right: 1px solid #dcdee5;

  .all-department {
    height: 100%;

    .department-content-wrapper {
      height: calc(100% - 32px);
      overflow-y: auto;

      &::-webkit-scrollbar {
        width: 4px;
        background-color: transparent;
      }

      &::-webkit-scrollbar-thumb {
        background-color: #dcdee5;
        border-radius: 4px;
      }
    }
  }
}

.selected-department {
  width: 50%;
  padding-left: 24px;
}

// .depart-title {
//   position: relative;
//   height: 42px;
//   padding-left: 24px;
//   font-size: 14px;
//   font-weight: 500;
//   line-height: 42px;
//   color: rgb(49 50 56 / 100%);
//   background: #fafbfd;
//   border: 1px solid #dcdee5;
//   border-right: none;
//   border-left: none;

//   .clear {
//     position: absolute;
//     top: 13px;
//     right: 24px;
//     font-size: 12px;
//     line-height: 16px;
//     color: rgb(58 132 255 / 100%);
//     cursor: pointer;
//   }
// }

.department-infor {
  height: 276px;
  overflow: hidden;
  overflow-y: auto;
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
    height: 200px;
    padding-right: 24px;
  }
}

.selected-department {
  // .depart-title {
  //   padding-left: 15px;
  // }
}

.selected-content {
  height: 330px;
  padding-top: 15px;
  overflow: hidden;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 4px;
    background-color: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background-color: #dcdee5;
    border-radius: 4px;
  }
}

.selected-list {
  position: relative;
  height: 36px;
  padding: 0 24px 0 15px;
  font-size: 14px;
  font-weight: 400;
  line-height: 36px;
  color: rgb(115 121 135 / 100%);

  .title {
    display: block;
    width: calc(100% - 24px);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .icon-user-close {
    position: absolute;
    top: 13px;
    right: 24px;
    font-size: 10px;
    cursor: pointer;
  }
}

.checkbox {
  display: inline-block;
  width: 14px;
  height: 14px;
  margin: 0 4px;
  vertical-align: middle;
  cursor: pointer;
  background: #fff;
  background-image: url('@/images/icon.png');
  background-position: 0 -95px;
  outline: none;
  visibility: visible;
  appearance: none;

  &:checked {
    background-position: -33px -95px;
  }
}
</style>
