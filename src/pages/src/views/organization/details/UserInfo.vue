<template>
  <div class="user-info-wrapper user-scroll-y">
    <header>
      <bk-checkbox v-model="isSearchCurrentDepartment">
        仅显示本级用户（<span>23</span>）
      </bk-checkbox>
      <bk-input
        class="header-right"
        v-model="searchVal"
        placeholder="搜索用户名、全名"
        type="search"
      />
    </header>
    <bk-table
      class="user-info-table"
      :data="tableData"
      :pagination="pagination"
      settings
      :border="['outer']"
    >
      <bk-table-column prop="username" label="用户名">
        <template #default="{ row }">
          <bk-button text theme="primary" @click="handleClick('view', row)">
            {{ row.username }}
          </bk-button>
        </template>
      </bk-table-column>
      <bk-table-column prop="full_name" label="全名"></bk-table-column>
      <bk-table-column prop="status" label="状态">
        <template #default="{ row }">
          <div>
            <img :src="statusIcon[row.status]?.icon" class="account-status-icon" />
            <span>{{ statusIcon[row.status]?.text }}</span>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column prop="phone" label="手机号"></bk-table-column>
      <bk-table-column prop="email" label="邮箱"></bk-table-column>
      <bk-table-column prop="department_name" label="组织"></bk-table-column>
      <bk-table-column label="操作">
        <template #default="{ row }">
          <bk-button
            theme="primary"
            text
            class="mr8"
            @click="handleClick('edit', row)"
          >
            编辑
          </bk-button>
        </template>
      </bk-table-column>
    </bk-table>
    <!-- 查看/编辑用户 -->
    <bk-sideslider
      ext-cls="details-edit-wrapper"
      :width="640"
      :is-show="detailsConfig.isShow"
      :title="detailsConfig.title"
      :before-close="handleBeforeClose"
      quick-close
    >
      <template #header>
        <span>{{ detailsConfig.title }}</span>
        <div v-if="isView">
          <bk-button
            outline
            theme="primary"
            @click="handleClick('edit')">
            编辑
          </bk-button>
          <bk-button>重置</bk-button>
          <bk-button>删除</bk-button>
        </div>
      </template>
      <ViewUser v-if="isView" />
      <EditUser
        v-else
        @handleCancelEdit="handleCancelEdit" />
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import { computed, inject, reactive, ref } from 'vue';

import EditUser from './EditUser.vue';
import ViewUser from './ViewUser.vue';

import { statusIcon } from '@/utils';

const editLeaveBefore = inject('editLeaveBefore');
const isSearchCurrentDepartment = ref(false);
const searchVal = ref('');

const detailsConfig = reactive({
  isShow: false,
  title: '',
  type: '',
});

const tableData = [
  {
    username: 'lululi',
    full_name: 'lululi',
    status: 'normal',
    email: 'lululi@qq.com',
    phone: '18123456789',
    department_name: '总公司',
  },
  {
    username: 'helloword',
    full_name: 'helloword',
    status: 'disabled',
    email: 'helloword@qq.com',
    phone: '18123456789',
    department_name: '总公司',
  },
];

const pagination = {
  conut: tableData.length,
  limit: 10,
};

const enumData = {
  view: {
    title: '用户详情',
    type: 'view',
  },
  edit: {
    title: '编辑用户',
    type: 'edit',
  },
};

const isView = computed(() => detailsConfig.type === 'view');

const handleClick = (type: string, item: any) => {
  detailsConfig.title = enumData[type].title;
  detailsConfig.type = enumData[type].type;
  detailsConfig.isShow = true;
};

const handleCancelEdit = () => {
  detailsConfig.type = 'view';
  detailsConfig.title = '公司详情';
};

const handleBeforeClose = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
    detailsConfig.isShow = false;
  } else {
    detailsConfig.isShow = false;
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
};
</script>

<style lang="less" scoped>
.user-info-wrapper {
  width: 100%;
  height: calc(100vh - 140px);
  padding: 24px;

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .header-right {
      width: 400px;
    }
  }

  :deep(.user-info-table) {
    .bk-table-head {
      table thead th {
        text-align: center;
      }

      .table-head-settings {
        border-right: none;
      }
    }

    .bk-table-footer {
      padding: 0 15px;
      background: #fff;
    }

    .account-status-icon {
      width: 16px;
      height: 16px;
      margin-right: 5px;
      vertical-align: middle;
    }
  }
}

.details-edit-wrapper {
  :deep(.bk-sideslider-title) {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px 0 50px !important;

    .bk-button {
      padding: 5px 17px !important;
    }
  }

  :deep(.bk-modal-content) {
    overflow-y: auto;

    &::-webkit-scrollbar {
      width: 4px;
      background-color: transparent;
    }

    &::-webkit-scrollbar-thumb {
      background-color: #dcdee5;
      border-radius: 4px;
    }

    &:hover {
      &::-webkit-scrollbar-thumb {
        background-color: #979ba5;
      }
    }
  }
}
</style>
