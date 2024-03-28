<template>
  <bk-loading class="set-department-wrapper" :loading="basicLoading">
    <div class="department-content">
      <div class="all-department">
        <!-- 搜索框 -->
        <div class="king-input-search">
          <bk-input
            v-model="searchKey"
            type="search"
          />
        </div>
        <!-- 组织树 -->
        <div class="department-tree-wrapper">
          <Tree
            :tree-data="treeDataList"
            :search-key="searchKey"
            @checkedList="checkedList" />
        </div>
      </div>
    </div>
    <div class="selected-department">
      <div class="selected-title">
        <p>{{ $t('已选择') }}
          <span class="tenant">{{ tenantCount }}</span>
          {{ $t('个租户') }}，<span class="department">{{ departmentCount }}</span>
          {{ $t('个组织') }}，<span class="user">{{ userCount }}</span>
          {{ $t('个用户') }}
        </p>
        <bk-button text theme="primary" @click="clearAll">{{ $t('清空') }}</bk-button>
      </div>
      <div class="selected-content" data-test-id="list_selDepartmentsData">
        <ul v-if="selectedDepartments.length">
          <li class="selected-list" v-for="(item) in selectedDepartments" :key="item.id">
            <div>
              <i :class="getNodeIcon(item.type)" />
              <span class="title">{{item.name}}</span>
            </div>
            <i class="bk-sq-icon icon-close-fill" @click="deleteSelected(item)"></i>
          </li>
        </ul>
      </div>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">
import { defineProps, onMounted, ref, watch } from 'vue';

import Tree from './Tree.vue';

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
const treeDataList = ref([]);
// 设置所在组织： 已选择的组织List
const selectedDepartments = ref([]);
const tenantCount = ref(0);
const departmentCount = ref(0);
const userCount = ref(0);

watch(() => selectedDepartments.value, (val) => {
  const counts = { tenant: 0, department: 0, user: 0 };
  val.forEach(({ type }) => {
    if (Object.prototype.hasOwnProperty.call(counts, type)) {
      counts[type] += 1;
    }
  });

  tenantCount.value = counts.tenant;
  departmentCount.value = counts.department;
  userCount.value = counts.user;
});

onMounted(() => {
  basicLoading.value = true;
  if (props.initialDepartments.length) {
    selectedDepartments.value = JSON.parse(JSON.stringify(props.initialDepartments));
  }
  initDepartmentTree();
});

const initDepartmentTree = () => {
  try {
    setTimeout(() => {
      basicLoading.value = false;
    }, 600);
  } catch (e) {
    console.warn(e);
  }
};

const checkedList = (list: any) => {
  selectedDepartments.value = list;
};

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

const deleteSelected = (item: any) => {
  selectedDepartments.value = selectedDepartments.value.filter(k => k !== item);
};

const clearAll = () => {
  selectedDepartments.value = [];
};
</script>

<style lang="less" scoped>
.set-department-wrapper {
  display: flex;
  width: 721px;
}

.department-content {
  width: 50%;
  border-right: 1px solid #dcdee5;

  .all-department {
    height: 100%;

    .king-input-search {
      padding: 0 24px;
    }

    .department-tree-wrapper {
      height: calc(100% - 32px);
      padding: 12px 24px;
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

  .selected-title {
    display: flex;
    padding: 0 24px;
    font-size: 12px;
    line-height: 32px;
    justify-content: space-between;
    align-items: center;

    span {
      font-weight: 700;
    }

    .tenant {
      color: #3A84FF;
    }

    .department {
      color: #2DCB56;
    }

    .user {
      color: #FF9C01;
    }
  }

  .selected-content {
    height: calc(100% - 32px);
    padding: 12px 24px;
    overflow-y: auto;
  }
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  line-height: 36px;

  div {
    display: flex;
    align-items: center;

    i {
      margin-right: 12px;
      font-size: 18px;
      color: #A3C5FD;
    }
  }

  .icon-close-fill {
    font-size: 16px;
    color: #C4C6CC;
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
