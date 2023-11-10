<template>
  <bk-loading :loading="isLoading" class="user-info-wrapper user-scroll-y">
    <header>
      <div>
        <template v-if="pluginId === 'local'">
          <bk-button theme="primary" class="mr8" @click="handleClick('add')">
            <i class="user-icon icon-add-2 mr8" />
            新建用户
          </bk-button>
          <bk-button class="mr8 w-[64px]" @click="importDialog.isShow = true">导入</bk-button>
          <bk-button class="w-[64px]" @click="handleExport">导出</bk-button>
        </template>
      </div>
      <bk-input
        class="header-right"
        v-model="searchVal"
        placeholder="搜索用户名"
        type="search"
        clearable
        @enter="handleEnter"
        @clear="handleClear" />
    </header>
    <bk-table
      class="user-info-table"
      :data="users"
      :border="['outer']"
      remote-pagination
      :pagination="pagination"
      show-overflow-tooltip
      @page-limit-change="pageLimitChange"
      @page-value-change="pageCurrentChange"
    >
      <template #empty>
        <Empty
          :is-data-empty="isDataEmpty"
          :is-search-empty="isEmptySearch"
          :is-data-error="isDataError"
          @handleEmpty="handleClear"
          @handleUpdate="handleClear"
        />
      </template>
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
      <bk-table-column label="操作" v-if="pluginId === 'local'">
        <template #default="{ row }">
          <bk-button
            theme="primary"
            text
            class="mr8"
            @click="handleClick('edit', row)"
          >
            编辑
          </bk-button>
          <!-- <bk-button theme="primary" text class="mr8">
            重置密码
          </bk-button>
          <bk-button theme="primary" text>
            删除
          </bk-button> -->
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
            @click="handleClick('edit', detailsConfig)">
            编辑
          </bk-button>
          <!-- <bk-button>重置</bk-button>
          <bk-button>删除</bk-button> -->
        </div>
      </template>
      <template #default>
        <ViewUser v-if="isView" :users-data="detailsConfig.usersData" />
        <EditUser
          v-else
          :type="detailsConfig.type"
          :users-data="detailsConfig.usersData"
          :current-id="detailsConfig.id"
          :data-source-id="dataSourceId"
          @handleCancelEdit="handleCancelEdit"
          @updateUsers="updateUsers" />
      </template>
    </bk-sideslider>
    <!-- 导入 -->
    <bk-dialog
      :is-show="importDialog.isShow"
      :title="importDialog.title"
      :quick-close="false"
      :width="640"
      @closed="closed"
    >
      <div class="import-dialog-header">
        <div class="mb-[24px]">
          <span>更新方式</span>
          <bk-radio-group
            v-model="uploadInfo.incremental"
            type="card"
          >
            <bk-radio-button :label="true">增量更新</bk-radio-button>
            <bk-radio-button :label="false">全量更新</bk-radio-button>
          </bk-radio-group>
        </div>
        <span>上传用户信息</span>
      </div>
      <bk-upload
        ref="uploadRef"
        accept=".xlsx,.xls"
        with-credentials
        :limit="1"
        :size="10"
        :multiple="false"
        :custom-request="customRequest"
        @exceed="exceed">
        <template #file="{ file }">
          <div
            :class="['excel-file', { 'excel-file-error': isError }]"
            @mousemove="isHover = true"
            @mouseleave="isHover = false">
            <i class="user-icon icon-excel" />
            <div class="file-text">
              <div
                v-overflow-tips
                class="text-overflow">
                {{ file.name }}
              </div>
              <p class="text-overflow file-status">
                <i v-if="!isError" class="user-icon icon-check-line" />
                {{ textTips }}
              </p>
            </div>
            <div class="file-operations">
              <span v-if="!isHover">{{ getSize(file.size) }}</span>
              <i v-else class="user-icon icon-delete" @click="handleUploadRemove(file)" />
            </div>
          </div>
        </template>
        <template #tip>
          <div class="mt-[8px]">
            <span>支持 Excel 文件，文件小于 10 M，下载</span>
            <bk-button text theme="primary" @click="handleExportTemplate">模版文件</bk-button>
          </div>
        </template>
      </bk-upload>
      <template #footer>
        <div class="footer-wrapper">
          <div class="footer-left">
            <bk-checkbox v-model="uploadInfo.overwrite">
              允许对同名用户覆盖更新
            </bk-checkbox>
            <bk-popover
              ext-cls="popover-wrapper"
              content="勾选覆盖用户信息将会对数据源中存在、但文件中不存在的成员执行删除操作，请谨慎选择。"
              placement="top"
              width="280"
            >
              <InfoLine class="info" />
            </bk-popover>
          </div>
          <div>
            <bk-button
              theme="primary"
              class="w-[64px] mr-[8px]"
              :loading="importDialog.loading"
              @click="confirmImportUsers">
              确定
            </bk-button>
            <bk-button
              class="w-[64px]"
              @click="closed">
              取消
            </bk-button>
          </div>
        </div>
      </template>
    </bk-dialog>
  </bk-loading>
</template>

<script setup lang="ts">
import axios from 'axios';
import { Message } from 'bkui-vue';
import { InfoLine } from 'bkui-vue/lib/icon';
import Cookies from 'js-cookie';
import { computed, defineProps, inject, onMounted, reactive, ref, watch } from 'vue';

import EditUser from './EditUser.vue';
import ViewUser from './ViewUser.vue';

import Empty from '@/components/Empty.vue';
import { getDataSourceUserDetails, getDataSourceUsers } from '@/http/dataSourceFiles';
import { formatConvert } from '@/utils';

const props = defineProps({
  dataSourceId: {
    type: Number,
  },
  pluginId: {
    type: String,
    default: '',
  },
});

const editLeaveBefore = inject('editLeaveBefore');
const searchVal = ref('');
const detailsConfig = reactive({
  isShow: false,
  title: '',
  type: '',
  usersData: {
    username: '',
    full_name: '',
    department_ids: [],
    leader_ids: [],
    email: '',
    phone_country_code: '+86',
    phone: '',
    logo: '',
  },
  id: '',
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

watch(
  () => detailsConfig.isShow,
  () => {
    if (!detailsConfig.isShow) {
      detailsConfig.usersData = {
        username: '',
        full_name: '',
        department_ids: [],
        leader_ids: [],
        email: '',
        phone_country_code: '+86',
        phone: '',
        logo: '',
      };
    }
  },
);

const isView = computed(() => detailsConfig.type === 'view');

onMounted(() => {
  getUsers();
});

const isLoading = ref(false);
const isDataEmpty = ref(false);
const isEmptySearch = ref(false);
const isDataError = ref(false);

const pagination = reactive({
  current: 1,
  count: 0,
  limit: 10,
});

const users = ref([]);

const getUsers = async () => {
  try {
    isLoading.value = true;
    isDataEmpty.value = false;
    isEmptySearch.value = false;
    isDataError.value = false;
    const params = {
      id: props.dataSourceId,
      username: searchVal.value,
      page: pagination.current,
      pageSize: pagination.limit,
    };
    const res = await getDataSourceUsers(params);
    if (res.data.count === 0) {
      searchVal.value === '' ? isDataEmpty.value = true : isEmptySearch.value = true;
    }
    pagination.count = res.data.count;
    users.value = res.data.results;
  } catch (error) {
    isDataError.value = true;
  } finally {
    isLoading.value = false;
  }
};

const handleClick = async (type: string, item?: any) => {
  if (type !== 'add') {
    const res = await getDataSourceUserDetails(item.id);
    detailsConfig.usersData = res.data;
    detailsConfig.id = item.id;
  }
  detailsConfig.title = enumData[type].title;
  detailsConfig.type = enumData[type].type;
  detailsConfig.isShow = true;
};

const handleCancelEdit = () => {
  window.changeInput = false;
  if (detailsConfig.type === 'add') {
    detailsConfig.isShow = false;
  } else {
    detailsConfig.type = 'view';
    detailsConfig.title = '用户详情';
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

const updateUsers = (value, text) => {
  detailsConfig.isShow = false;
  searchVal.value = value;
  getUsers();
  Message({
    theme: 'success',
    message: text,
  });
};

const handleEnter = () => {
  pagination.current = 1;
  getUsers();
};

const handleClear = () => {
  searchVal.value = '';
  pagination.current = 1;
  getUsers();
};

const pageLimitChange = (limit) => {
  pagination.limit = limit;
  pagination.current = 1;
  getUsers();
};
const pageCurrentChange = (current) => {
  pagination.current = current;
  getUsers();
};

const importDialog = reactive({
  isShow: false,
  loading: false,
  title: '批量新增用户',
});

const uploadInfo = reactive({
  file: {},
  overwrite: false,
  incremental: true,
});

const uploadRef = ref();
const isHover = ref(false);
const textTips = ref('');
const isError = ref(false);

const customRequest = (data) => {
  if (data.file.size > (10 * 1024 * 1024)) {
    isError.value = true;
    textTips.value = '文件大小超出限制';
  } else {
    isError.value = false;
    textTips.value = '上传成功';
  }
  uploadInfo.file = data.file;
};

const exceed = () => {
  Message({ theme: 'error', message: '最多上传1个文件，如需更新，请先删除已上传文件' });
};

const getSize = (value) => {
  const size = value / 1024;
  return `${parseFloat(size.toFixed(2))}KB`;
};

const handleUploadRemove = (file) => {
  uploadRef.value?.handleRemove(file);
  uploadInfo.file = {};
};

// 导出指定的本地数据源用户数据
const handleExport = () => {
  const url = `${window.AJAX_BASE_URL}/api/v1/web/data-sources/${props.dataSourceId}/operations/export/`;
  window.open(url);
};

// 数据源导出模板
const handleExportTemplate = () => {
  const url = `${window.AJAX_BASE_URL}/api/v1/web/data-sources/${props.dataSourceId}/operations/download_template/`;
  window.open(url);
};

const confirmImportUsers = async () => {
  try {
    if (!uploadInfo.file.name) {
      return Message({ theme: 'warning', message: '请选择文件再上传' });
    }
    if (isError.value) {
      return Message({ theme: 'warning', message: '文件大小超出限制,请重新上传' });
    };
    importDialog.loading = true;
    const formData = new FormData();
    formData.append('file', uploadInfo.file);
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-CSRFToken': Cookies.get(window.CSRF_COOKIE_NAME),
        'x-requested-with': 'XMLHttpRequest',
      },
    };
    axios.defaults.withCredentials = true;
    const url = `${window.AJAX_BASE_URL}/api/v1/web/data-sources/${props.dataSourceId}/operations/import/`;
    const res = await axios.post(url, {
      overwrite: uploadInfo.overwrite,
      incremental: uploadInfo.incremental,
      file: formData.get('file'),
    }, config);
    const theme = res.data.data.status === 'success' ? 'success' : 'error';
    Message({ theme, message: res.data.data.summary });
    importDialog.isShow = false;
    getUsers();
  } catch (e) {
    const { message } = e.response.data.error;
    Message({ theme: 'error', message });
  } finally {
    importDialog.loading = false;
  }
};

const closed = () => {
  importDialog.isShow = false;
  uploadInfo.file = {};
  uploadInfo.overwrite = false;
  uploadInfo.incremental = true;
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

::v-deep .bk-modal-content {
  &::-webkit-scrollbar {
    width: 4px;
    background-color: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background-color: #dcdee5;
    border-radius: 4px;
  }

  .bk-upload-list {
    margin-bottom: 24px;
  }
}

::v-deep .bk-upload-list__item {
  padding: 0;
  border: none;
}

.excel-file-error {
  background: rgb(254 221 220 / 40%);
  border-color: #ff5656 !important;

  .file-status {
    color: #ff5656 !important;
  }
}

.excel-file {
  display: flex;
  padding: 10px;
  overflow: hidden;
  font-size: 12px;
  border: 1px solid #c4c6cc;
  flex: 1;
  align-items: center;

  .icon-excel {
    margin-right: 14px;
    font-size: 26px;
    color: #2dcb56;
  }

  .file-text {
    flex: 1;
    overflow: hidden;
  }

  .file-status {
    color: #2dcb56;
  }

  .file-operations {
    span {
      font-weight: 700;
    }

    .icon-delete {
      margin-left: 12px;
      font-size: 16px;
      cursor: pointer;
    }
  }
}

.footer-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;

  .footer-left {
    display: flex;
    align-items: center;
  }

  .info {
    margin-left: 5px;
    font-size: 16px;
    color: #979BA5;
    cursor: pointer;
  }
}
</style>
