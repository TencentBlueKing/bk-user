<template>
  <div v-bkloading="{ loading: isLoading, zIndex: 10 }">
    <MainBreadcrumbsDetails>
      <template #right v-if="dataSource.length > 0">
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
          :loading="resetLoading"
          @click="handleReset"
          :disabled="disabledSyncBtn"
        >
          {{ $t('全部重置') }}
        </bk-button>
      </template>
    </MainBreadcrumbsDetails>
    <div
      :class="['data-source-card user-scroll-y', { 'has-alert': userStore.showAlert }]"
      v-if="dataSource.length > 0"
    >
      <div class="info">
        <i class="user-icon icon-info-i" />
        <span v-if="isConfiguredLocalPlugin && !isConfiguredGeneralPlugin">
          {{ $t('当前已配置「{source}」，支持同时配置 1 个「{target}」', { source: $t('本地数据源'), target: $t('外部数据源') }) }}
        </span>
        <span v-else-if="isConfiguredGeneralPlugin && !isConfiguredLocalPlugin">
          {{ $t('当前已配置「{source}」，支持同时配置 1 个「{target}」', { source: $t('HTTP 数据源'), target: $t('本地数据源') }) }}
        </span>
        <span v-else-if="isConfiguredLocalPlugin && isConfiguredGeneralPlugin">
          {{ $t('仅支持同时配置 1 个「{local}」和 1 个「{external}」，切换外部数据源将会清除原配置数据源', {
            local: $t('本地数据源'),
            external: $t('外部数据源'),
          }) }}
        </span>
      </div>
      <DataSourceCard
        :plugins="dataSourcePlugins"
        :data-source="dataSource"
        :config="true"
        :show-content="showContent"
        @handle-collapse="handleCollapse">
        <template #right>
          <div class="flex items-center">
            <div class="mr-[40px]" v-if="syncStatus">
              <span
                v-if="!disabledSyncBtn"
                :class="['tag-style', dataRecordStatus[syncStatus?.status]?.theme]">
                {{ dataRecordStatus[syncStatus?.status]?.text }}
              </span>
              <span v-else class="flex">
                <img :src="dataRecordStatus[syncStatus?.status]?.icon" class="h-[19.25px] w-[19.25px] mr-[9.37px]" />
                <span>{{ dataRecordStatus[syncStatus?.status]?.text }}</span>
              </span>
              <span v-if="!disabledSyncBtn">
                {{ syncStatus?.start_at }}
              </span>
            </div>
            <div v-if="dataSource?.plugin_id === 'local'" class="flex items-center">
              <bk-button
                class="min-w-[64px]"
                theme="primary"
                @click="handleImport"
                :disabled="disabledSyncBtn || resetLoading"
              >
                <Upload class="mr-[8px] text-[16px]" />
                {{ $t('导入') }}
              </bk-button>
              <bk-dropdown
                trigger="click"
                @click.stop
              >
                <bk-button class="w-[32px] ml-[8px]">
                  <i class="user-icon icon-more"></i>
                </bk-button>
                <template #content>
                  <bk-dropdown-menu>
                    <bk-dropdown-item @click="handleReset">
                      <span>{{ $t('重置') }}</span>
                    </bk-dropdown-item>
                  </bk-dropdown-menu>
                </template>
              </bk-dropdown>
            </div>
            <div class="flex items-center" v-else>
              <div>
                <bk-pop-confirm
                  ref="popConfirmRef"
                  :content="$t('确认同步？')"
                  trigger="click"
                  @confirm="handleOperationsSync"
                >
                  <bk-button
                    class="min-w-[64px]"
                    theme="primary"
                    @click.stop
                    :disabled="disabledSyncBtn"
                  >
                    {{ $t('同步') }}
                  </bk-button>
                </bk-pop-confirm>
              </div>
              <bk-button
                class="min-w-[64px] ml-[8px]"
                outline
                theme="primary"
                @click="handleEdit"
              >
                {{ $t('编辑') }}
              </bk-button>
              <bk-dropdown
                trigger="click"
                @click.stop
              >
                <bk-button class="w-[32px] ml-[8px]">
                  <i class="user-icon icon-more"></i>
                </bk-button>
                <template #content>
                  <bk-dropdown-menu>
                    <bk-dropdown-item @click="handleReset">
                      <span>{{ $t('重置') }}</span>
                    </bk-dropdown-item>
                  </bk-dropdown-menu>
                </template>
              </bk-dropdown>
            </div>
          </div>
        </template>
        <template #content v-if="showContent">
          <HttpDetails :data-source-id="dataSource?.id" />
        </template>
      </DataSourceCard>
    </div>
    <div :class="['data-source-card user-scroll-y', { 'has-alert': userStore.showAlert }]" v-else>
      <div class="info" v-if="!dataSource?.id">
        <i class="user-icon icon-info-i" />
        <span>{{ $t('当前还没有数据源，需要先选择数据源类型并进行配置') }}</span>
      </div>
      <DataSourceCard
        :plugins="dataSourcePlugins"
        @handle-collapse="handleClick" />
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
              :content="$t('针对相同用户覆盖更新相应的字段值，包括所属部门、所属上级等')"
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
      v-model:is-show="updateConfig.isShow"
      :title="updateConfig.title"
      quick-close
      width="960"
      render-directive="if"
      transfer
    >
      <SyncRecords :data-source="dataSource" />
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts"> import axios from 'axios';
import { InfoBox, Message } from 'bkui-vue';
import { InfoLine, Upload } from 'bkui-vue/lib/icon';
import Cookies from 'js-cookie';
import { storeToRefs } from 'pinia';
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute } from 'vue-router';

import HttpDetails from './HttpDetails.vue';

import DataSourceCard from '@/components/layouts/DataSourceCard.vue';
import MainBreadcrumbsDetails from '@/components/layouts/MainBreadcrumbsDetails.vue';
import SyncRecords from '@/components/SyncRecords.vue';
import { useInfoBoxContent } from '@/hooks';
import useDataSourceSetting from '@/hooks/useDataSourceSetting';
import { deleteDataSources, getDefaultConfig, getRelatedResource, newDataSource, postOperationsSync } from '@/http';
import { t } from '@/language/index';
import router from '@/router';
import { useDataSourceStore, useSyncStatus, useUser } from '@/store';
import { dataRecordStatus, RUNNING_FIELDS } from '@/utils';
const route = useRoute();

const userStore = useUser();
const syncStatusStore = useSyncStatus();
const dataSourceStore = useDataSourceStore();

const {
  dataSource,
  dataSourcePlugins,
  isConfiguredLocalPlugin,
  isConfiguredGeneralPlugin,
} = storeToRefs(dataSourceStore);
/**
 * more-data-source-todo
 * 1. dataSource的处理 当前由单一数据源扩展到多数据源，需要处理dataSource在template与script中的使用
 * 2. syncStatus的处理 当前由单一数据源扩展到多数据源，需要处理syncStatus在template与script中的使用
 */
const syncStatus = computed(() => syncStatusStore.syncStatus);
const disabledSyncBtn = computed(() => RUNNING_FIELDS.includes(syncStatus.value?.status));

const { startDataSourceSync: otherDataSourceSync } = useDataSourceSetting();
const { startDataSourceSync: localDataSourceSync } = useDataSourceSetting();

const isLoading = ref(false);
const resetLoading = ref(false);
const showContent = ref(false);
const uploadInfo = reactive({
  file: {},
  overwrite: false,
  incremental: true,
});
const uploadRef = ref();
const isHover = ref(false);
const textTips = ref('');
const isError = ref(false);

const importDialog = reactive({
  isShow: false,
  loading: false,
  title: t('导入'),
  id: 'local',
});


// 重置数据源
const handleReset = async () => {
  try {
    resetLoading.value = true;
    const res = await getRelatedResource(dataSource.value?.id);
    const { subContent, resetIdpConfig } = useInfoBoxContent(res.data, '');

    InfoBox({
      width: 600,
      infoType: 'warning',
      title: t('是否重置数据源？'),
      subTitle: subContent,
      confirmText: t('重置'),
      theme: 'danger',
      onConfirm: () => {
        resetLoading.value = true;
        const resetConfig = resetIdpConfig.value ? 'True' : 'False';
        if (dataSource.value?.id) {
          deleteDataSources({ id: dataSource.value.id, is_delete_idp: resetConfig }).then(() => {
            Message({ theme: 'success', message: t('数据源重置成功') });
            // 重置数据源后，重新获取当前数据源信息
            dataSourceStore.handleFetchCurrentDataSource();
          })
            .finally(() => resetLoading.value = false);
        }
      },
    });
  } catch (e) {
    console.warn(e);
  } finally {
    resetLoading.value = false;
  }
};

/** 点击同步 发起同步，并开启syncRecords轮询*/
const handleOperationsSync = async () => {
  const res = await postOperationsSync(dataSourceStore.newDataSourceId);
  Message({ theme: res.data.status, message: res.data.summary });
  otherDataSourceSync(dataSourceStore.newDataSourceId);
};

// 切换展示状态
const handleCollapse = () => {
  showContent.value = !showContent.value;
};

const handleEdit = () => {
  router.push({ name: 'newDataSource', query: { type: dataSource.value?.plugin_id, id: dataSource.value?.id } });
};

const handleImport = () => {
  importDialog.isShow = true;
};

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

// 点击新建数据源
const handleClick = async (id: string) => {
  if (dataSourceStore.dataSource.length < 2) {
    if (id === 'local') {
      const res = await getDefaultConfig('local');
      const newDataSourceData = await newDataSource({
        plugin_id: 'local',
        plugin_config: {
          ...res.data?.config,
        },
      });
      dataSourceStore.setNewDataSourceId(newDataSourceData.data?.id);
      importDialog.isShow = true;
    } else {
      router.push({ name: 'newDataSource', query: { type: id } });
    }
  } else {
    router.push({ name: 'dataSourceConfig', query: id === 'local' ? {} : { type: id } });
  }
};

// 数据源导出模板
const handleExportTemplate = () => {
  const url = `${window.AJAX_BASE_URL}/api/v3/web/data-sources/${dataSourceStore.localDataSourceId}/operations/download_template/`;
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
    formData.append('overwrite', uploadInfo.overwrite);
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-CSRFToken': Cookies.get(window.CSRF_COOKIE_NAME),
        'x-requested-with': 'XMLHttpRequest',
      },
      withCredentials: true,
    };
    const url = `${window.AJAX_BASE_URL}/api/v3/web/data-sources/${dataSourceStore.localDataSourceId}/operations/import/`;
    await axios.post(url, formData, config);
    Message({ theme: 'success', message: t('导入成功') });
    localDataSourceSync(dataSourceStore.newDataSourceId);
    dataSourceStore.handleFetchCurrentDataSource();
  } catch (e) {
    Message({ theme: 'error', message: e.response.data.error.message });
  } finally {
    importDialog.isShow = false;
    importDialog.loading = false;
  }
};

const closed = async () => {
  importDialog.isShow = false;
  if (dataSourceStore.newDataSourceId) {
    // 删除新创建的数据源
    await deleteDataSources({ id: dataSourceStore.newDataSourceId });
    dataSourceStore.clearNewDataSourceId();
    // 刷新当前数据源
    await dataSourceStore.handleFetchCurrentDataSource();
    uploadInfo.file = {};
    uploadInfo.overwrite = false;
    uploadInfo.incremental = true;
  }
};

const updateConfig = reactive({
  isShow: false,
  title: t('数据更新记录'),
});

const changeLog = () => {
  updateConfig.isShow = true;
};

const handleInit = async () => {
  try {
    isLoading.value = true;
    await Promise.all([
      dataSourceStore.handleFetchAllDataSourcePlugins(),
      dataSourceStore.handleFetchCurrentDataSource(),
    ]);
  } finally {
    isLoading.value = false;
  }
};

onMounted(async () => {
  await handleInit();
  /** 是否从快速导入跳转过来，是的话则默认打开导入弹框 */
  if (route.query?.isLink) {
    handleImport();
  }
});
</script>

<style lang="less" scoped>
.has-alert {
  height: calc(100vh - 144px) !important;
}

.data-source-card {
  height: calc(100vh - 92px);
  padding: 16px 24px;

  .info {
    margin-bottom: 16px;

    i {
      font-size: 14px;
      color: #979BA5;
    }
  }

  .tag-style {
    .tag-style();
  }
  .success {
    .success();
  }
  .danger {
    .danger();
  }
  .warning {
    .warning();
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

::v-deep .card-header {
  &:hover {
    border: 1px solid #A3C5FD;
  }
}

.import-status-dialog {
  ::v-deep .bk-modal-header {
    height: 0px;
  }
  ::v-deep .bk-dialog-header {
    padding: 0px;
    height: 0px;
  }
  ::v-deep .bk-dialog-footer {
    border: none;
    background-color: #fff;
  }
  ::v-deep .bk-modal-footer {
    padding-top: 4px;
    padding-bottom: 24px;
  }
}

.tag-style() {
  display: inline-block;
  height: 22px;
  padding: 0 10px;
  margin-right: 4px;
  font-size: 12px;
  line-height: 22px;
  border-radius: 2px;
}

.success() {
  color: #14a568;
  background-color: #e4faf0;
  border-color: #14a5684d;
}

.danger() {
  color: #ea3636;
  background-color: #feebea;
  border-color: #ea35364d;
}

.warning() {
  color: #fe9c00;
  background-color: #fff1db;
  border-color: #fea5004d;
}
</style>
