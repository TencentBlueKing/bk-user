<template>
  <div class="user-info-wrapper user-scroll-y">
    <header>
      <div>
        <bk-button theme="primary" class="mr8" @click="handleClick('add')">
          <i class="user-icon icon-add-2 mr8" />
          新建用户
        </bk-button>
        <bk-button class="mr8" style="width: 64px;">导入</bk-button>
        <!-- <bk-button>导出</bk-button> -->
      </div>
      <bk-input class="header-right" v-model="searchVal" type="search" />
    </header>
    <bk-table
      class="user-info-table"
      :data="tableData"
      :border="['outer']"
      show-overflow-tooltip
    >
      <bk-table-column prop="username" label="用户名">
        <template #default="{ row }">
          <bk-button text theme="primary" @click="handleClick('view', row)">
            {{ row.username }}
          </bk-button>
        </template>
      </bk-table-column>
      <bk-table-column prop="full_name" label="全名"></bk-table-column>
      <bk-table-column prop="phone" label="手机号"></bk-table-column>
      <bk-table-column prop="email" label="邮箱"></bk-table-column>
      <bk-table-column prop="departments" label="所属组织">
        <template #default="{ row }">
          <span>{{ formatConvert(row.departments) }}</span>
        </template>
      </bk-table-column>
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
          <bk-button theme="primary" text class="mr8">
            重置密码
          </bk-button>
          <bk-button theme="primary" text>
            删除
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
            @click="handleClick('edit', detailsConfig.usersData)">
            编辑
          </bk-button>
          <bk-button>重置</bk-button>
          <bk-button>删除</bk-button>
        </div>
      </template>
      <template #default>
        <ViewUser v-if="isView" :users-data="detailsConfig.usersData" />
        <EditUser
          v-else
          :type="detailsConfig.type"
          :users-data="detailsConfig.usersData"
          @handleCancelEdit="handleCancelEdit" />
      </template>
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import { computed, inject, reactive, ref } from 'vue';

import EditUser from './EditUser.vue';
import ViewUser from './ViewUser.vue';

const editLeaveBefore = inject('editLeaveBefore');
const searchVal = ref('');
const detailsConfig = reactive({
  isShow: false,
  title: '',
  type: '',
  usersData: {
    username: '',
    full_name: '',
    department_ids: '',
    leader_ids: '',
    email: '',
    phone_country_code: '+86',
    phone: '',
    logo: '',
  },
});

const enumData = {
  add: {
    title: '新建用户',
    type: 'add',
  },
  view: {
    title: '用户详情',
    type: 'view',
  },
  edit: {
    title: '编辑用户',
    type: 'edit',
  },
};

const tableData = [
  {
    id: '1',
    username: 'Loretta Wolfe',
    full_name: 'Larry Carlson',
    phone: '13122334455',
    email: '13122334455@qq.com',
    departments: [
      {
        id: 1,
        name: 'IEG',
      },
      {
        id: 2,
        name: '技术运营部',
      },
    ],
  },
  {
    id: '2',
    username: 'Jeanette Stephens',
    full_name: 'Bettie Ramos',
    phone: '13122334455',
    email: '13122334455@qq.com',
    departments: [
      {
        id: 1,
        name: 'IEG',
      },
      {
        id: 2,
        name: '技术运营部',
      },
    ],
  },
];

const isView = computed(() => detailsConfig.type === 'view');

const handleClick = (type: string, item?: any) => {
  // if (type !== "add") {
  //   detailsConfig.usersData = res.data;
  // }
  detailsConfig.title = enumData[type].title;
  detailsConfig.type = enumData[type].type;
  detailsConfig.isShow = true;
};

const handleCancelEdit = () => {
  if (detailsConfig.type === 'add') {
    detailsConfig.isShow = false;
  } else {
    detailsConfig.type = 'view';
    detailsConfig.title = '公司详情';
    window.changeInput = false;
  }
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

const formatConvert = (data) => {
  const departments = data?.map(item => item.name).join('/') || '--';
  return departments;
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
      width: 320px;
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
