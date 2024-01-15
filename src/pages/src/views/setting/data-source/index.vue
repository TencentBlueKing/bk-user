<template>
  <div class="data-source-wrapper">
    <div class="info">
      <i class="user-icon icon-info-i" />
      <span>当前还没有数据源，需要先选择数据源类型并进行配置</span>
    </div>
    <DataSourceCard
      v-for="(item, index) in dataList"
      :key="index" :list="item"
      @click="handleClick(item)"
    />
    <!-- 导入 -->
    <bk-dialog
      :is-show="importDialog.isShow"
      :title="importDialog.title"
      :quick-close="false"
      :width="640"
      @closed="closed"
    >
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
      </bk-upload>
      <template #footer>
        <div class="footer-wrapper">
          <div class="footer-left">
            <bk-checkbox v-model="uploadInfo.overwrite">
              {{ $t('允许对同名用户覆盖更新') }}
            </bk-checkbox>
            <bk-popover
              ext-cls="popover-wrapper"
              :content="$t('勾选覆盖用户信息将会对数据源中存在、但文件中不存在的成员执行删除操作，请谨慎选择。')"
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
              {{ $t('确定') }}
            </bk-button>
            <bk-button
              class="w-[64px]"
              @click="closed">
              {{ $t('取消') }}
            </bk-button>
          </div>
        </div>
      </template>
    </bk-dialog>
  </div>
</template>

<script setup lang="ts">
import axios from 'axios';
import { Message } from 'bkui-vue';
import { reactive, ref } from 'vue';

import DataSourceCard from '@/components/layouts/DataSourceCard.vue';
import { t } from '@/language/index';
import router from '@/router';

const dataList = ref([
  {
    id: 'local',
    name: '本地数据源',
    logo: 'user-icon icon-shujuku',
    description: '支持导入本地文件，并对文件内数据进行增删改等操作',
    isShow: false,
  },
  {
    id: 'general',
    name: 'HTTP 数据源',
    logo: 'user-icon icon-http',
    description: '支持对接通用 HTTP 数据源的插件，用户需要在服务方提供“用户数据”及“部门数据”API',
    isShow: false,
  },
]);

const handleClick = (item) => {
  if (item.id === 'local') {
    importDialog.isShow = true;
  } else {
    router.push({ name: 'newDataSource', params: item });
  }
};

const importDialog = reactive({
  isShow: false,
  loading: false,
  title: t('导入'),
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
    textTips.value = t('文件大小超出限制');
  } else {
    isError.value = false;
    textTips.value = t('上传成功');
  }
  uploadInfo.file = data.file;
};

const exceed = () => {
  Message({ theme: 'error', message: t('最多上传1个文件，如需更新，请先删除已上传文件') });
};

const getSize = (value) => {
  const size = value / 1024;
  return `${parseFloat(size.toFixed(2))}KB`;
};

const handleUploadRemove = (file) => {
  uploadRef.value?.handleRemove(file);
  uploadInfo.file = {};
};

// 导入用户
const confirmImportUsers = async () => {
  if (!uploadInfo.file.name) {
    return Message({ theme: 'warning', message: t('请选择文件再上传') });
  }
  if (isError.value) {
    return Message({ theme: 'warning', message: t('文件大小超出限制，请重新上传') });
  };

  try {
    importDialog.loading = true;
    const formData = new FormData();
    formData.append('file', uploadInfo.file);
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-CSRFToken': Cookies.get(window.CSRF_COOKIE_NAME),
        'x-requested-with': 'XMLHttpRequest',
      },
      withCredentials: true,
    };
    const url = `${window.AJAX_BASE_URL}/api/v1/web/data-sources/${props.dataSourceId}/operations/import/`;
    const res = await axios.post(url, formData, config);
    Message({
      theme: res.data.data.status === 'success' ? 'success' : 'error',
      message: res.data.data.summary,
    });
  } catch (e) {
    Message({ theme: 'error', message: e.response.data.error.message });
  } finally {
    importDialog.loading = false;
    importDialog.isShow = false;
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
.data-source-wrapper {
  padding: 16px 24px;

  .info {
    margin-bottom: 16px;

    i {
      font-size: 14px;
      color: #979BA5;
    }
  }
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
  flex: 1;
  align-items: center;

  .icon-excel {
    margin-right: 14px;
    font-size: 26px;
    color: #3A84FF;
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
