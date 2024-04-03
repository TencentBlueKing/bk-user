<template>
  <div v-bkloading="{ loading: isLoading, zIndex: 9 }">
    <MainBreadcrumbsDetails>
      <template #right v-if="dataSource?.id">
        <bk-button
          class="mr-[12px]"
          hover-theme="primary"
          @click="changeLog"
        >
          {{ $t('数据变更记录') }}
        </bk-button>
        <bk-button
          class="min-w-[64px]"
          hover-theme="primary"
          @click="handleReset"
        >
          {{ $t('重置') }}
        </bk-button>
      </template>
    </MainBreadcrumbsDetails>
    <div class="data-source-card" v-if="dataSource?.id">
      <DataSourceCard
        :plugins="dataSourcePlugins"
        :data-source="dataSource"
        :config="true"
        :show-content="showContent"
        @handleCollapse="handleCollapse">
        <template #right>
          <div class="flex items-center">
            <div class="mr-[40px]" v-if="syncStatus">
              <bk-tag :theme="dataRecordStatus[syncStatus?.status]?.theme">
                {{ dataRecordStatus[syncStatus?.status]?.text }}
              </bk-tag>
              <span>{{ syncStatus?.start_at }}</span>
            </div>
            <div v-if="dataSource?.plugin_id === 'local'">
              <bk-button
                class="min-w-[64px]"
                theme="primary"
                @click="handleImport"
              >
                <Upload class="mr-[8px] text-[16px]" />
                {{ $t('导入') }}
              </bk-button>
            </div>
            <div v-else>
              <bk-button
                v-if="showContent"
                class="min-w-[64px]"
                outline
                theme="primary"
                @click="handleEdit"
              >
                {{ $t('编辑') }}
              </bk-button>
              <bk-button
                v-else
                class="min-w-[64px]"
                theme="primary"
                @click="handleSync"
              >
                {{ $t('同步') }}
              </bk-button>
            </div>
          </div>
        </template>
        <template #content v-if="showContent">
          <HttpDetails :data-source-id="dataSource?.id" />
        </template>
      </DataSourceCard>
    </div>
    <div class="data-source-card" v-else>
      <div class="info" v-if="!dataSource?.id">
        <i class="user-icon icon-info-i" />
        <span>当前还没有数据源，需要先选择数据源类型并进行配置</span>
      </div>
      <DataSourceCard
        :plugins="dataSourcePlugins"
        @handleCollapse="handleClick" />
    </div>
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
        <template #tip>
          <div class="mt-[8px]">
            <span>{{ $t('支持 Excel 文件，文件小于 10 M，下载') }}</span>
            <bk-button text theme="primary" @click="handleExportTemplate">{{ $t('模版文件') }}</bk-button>
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
              {{ $t('导入') }}
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
    <!-- 数据更新记录 -->
    <bk-sideslider
      v-model:isShow="updateConfig.isShow"
      :title="updateConfig.title"
      quick-close
      width="960"
      transfer
    >
      <SyncRecords :data-source="dataSource" />
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import axios from 'axios';
import { InfoBox, Message } from 'bkui-vue';
import { InfoLine } from 'bkui-vue/lib/icon';
import Cookies from 'js-cookie';
import { h, reactive, ref } from 'vue';

import HttpDetails from './HttpDetails.vue';

import DataSourceCard from '@/components/layouts/DataSourceCard.vue';
import MainBreadcrumbsDetails from '@/components/layouts/MainBreadcrumbsDetails.vue';
import SyncRecords from '@/components/SyncRecords.vue';
import { useDataSource } from '@/hooks';
import { deleteDataSources, getRelatedResource, postOperationsSync } from '@/http';
import { t } from '@/language/index';
import router from '@/router';
import { dataRecordStatus } from '@/utils';

const {
  dataSourcePlugins,
  dataSource,
  currentDataSourceId,
  isLoading,
  initDataSourceList,
  syncStatus,
  initSyncRecords,
  handleClick,
  importDialog,
} = useDataSource();

// 重置数据源
const handleReset = async () => {
  try {
    const res = await getRelatedResource(dataSource.value?.id);
    InfoBox({
      width: 480,
      infoType: 'warning',
      title: t('是否重置数据源？'),
      subTitle: h('div', {
        style: {
          textAlign: 'left',
          lineHeight: '24px',
        },
      }, [
        h('p', {
          style: {
            marginBottom: '12px',
          },
        }, t('重置后，该数据源内的用户信息将同步删除:')),
        h('p', [
          t('1.本租户下的数据：共计'),
          `${res.data?.own_department_count}个组织，`,
          `${res.data?.own_user_count}个用户。`,
        ]),
        h('p', [
          t('2.分享给其他租户的数据：涉及'),
          `${res.data?.shared_to_tenant_count}个租户，共计`,
          `${res.data?.shared_to_department_count}个组织，`,
          `${res.data?.shared_to_user_count}个用户。`,
        ]),
      ]),
      confirmText: t('重置'),
      theme: 'danger',
      onConfirm: () => {
        if (dataSource.value?.id) {
          deleteDataSources(dataSource.value.id).then(() => {
            Message({ theme: 'success', message: t('数据源重置成功') });
            initDataSourceList();
          });
        }
      },
    });
  } catch (e) {
    console.warn(e);
  }
};

// 切换展示状态
const showContent = ref(false);
const handleCollapse = () => {
  showContent.value = !showContent.value;
};

const handleEdit = () => {
  router.push({ name: 'newDataSource', query: { type: dataSource.value?.plugin_id, id: dataSource.value?.id } });
};

const handleImport = () => {
  importDialog.isShow = true;
};

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

// 数据源导出模板
const handleExportTemplate = () => {
  const url = `${window.AJAX_BASE_URL}/api/v1/web/data-sources/${currentDataSourceId.value}/operations/download_template/`;
  window.open(url);
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
    const url = `${window.AJAX_BASE_URL}/api/v1/web/data-sources/${currentDataSourceId.value}/operations/import/`;
    const res = await axios.post(url, formData, config);
    if (res.data.data.status === 'success') {
      importDialog.isShow = false;
      InfoBox({
        width: 640,
        height: 284,
        infoType: 'success',
        title: t('导入成功'),
        confirmText: t('查看组织架构'),
        cancelText: t('关闭'),
        onConfirm: () => {},
        onClosed: () => {
          initDataSourceList();
          initSyncRecords();
        },
      });
    } else {
      Message({ theme: 'error', message: res.data.data.summary });
    }
  } catch (e) {
    Message({ theme: 'error', message: e.response.data.error.message });
  } finally {
    importDialog.loading = false;
  }
};

const closed = () => {
  importDialog.isShow = false;
  if (!dataSource.value?.id) {
    deleteDataSources(currentDataSourceId.value).then(() => {
      initDataSourceList();
      uploadInfo.file = {};
      uploadInfo.overwrite = false;
      uploadInfo.incremental = true;
    });
  }
};

const updateConfig = reactive({
  isShow: false,
  title: t('数据更新记录'),
});

const changeLog = () => {
  updateConfig.isShow = true;
};

// 同步数据源
const handleSync = (e) => {
  e.cancelBubble = true;
  postOperationsSync(dataSource.value?.id).then((res) => {
    Message({ theme: res.data.status, message: res.data.summary });
    initSyncRecords();
  });
};
</script>

<style lang="less" scoped>
.data-source-card {
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

::v-deep .card-header {
  &:hover {
    border: 1px solid #A3C5FD;
  }
}
</style>
