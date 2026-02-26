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
          :loading="resetLoading.all"
          @click="handleReset"
          :disabled="disabledSyncBtn || resetLoading.local || resetLoading.external"
        >
          {{ $t('全部重置') }}
        </bk-button>
      </template>
    </MainBreadcrumbsDetails>
    <div
      :class="[
        'data-source-card user-scroll-y',
        { 'has-alert': userStore.showAlert },
      ]"
    >
      <div class="info">
        <i class="user-icon icon-info-i" />
        <span v-if="!dataSource.length">
          {{ $t('当前还没有数据源，需要先选择数据源类型并进行配置') }}
        </span>
        <span v-else-if="isConfiguredLocalPlugin && !isConfiguredGeneralPlugin">
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

      <DataSourceItem
        v-for="(item, index) in visibleDataSourcePlugins"
        :key="index"
        class="!mb-[12px]"
        :data="item"
        :disabled="dataSource.length === 2 && !isDataSourceConfigured(item.id)"
        @click="handleClickDataSource(item.id)"
      >
        <template v-if="isDataSourceConfigured(item.id)" #name-suffix>
          <bk-tag
            theme="success"
            size="small"
            class="ml-[8px]"
          >
            {{ $t('启用') }}
          </bk-tag>
        </template>
        <template v-if="isDataSourceConfigured(item.id)" #right>
          <div class="flex items-center">
            <!-- 同步状态 -->
            <div
              v-if="getDataSourceSyncStatus(item.id)"
              class="mr-[40px]"
            >
              <span
                v-if="!isDataSourceRunning(item.id)"
                :class="['tag-style', dataRecordStatus[getDataSourceSyncStatus(item.id)?.status]?.theme]">
                {{ dataRecordStatus[getDataSourceSyncStatus(item.id)?.status]?.text }}
              </span>
              <span
                v-else
                class="flex"
              >
                <img
                  class="h-[19.25px] w-[19.25px] mr-[9.37px]"
                  :src="dataRecordStatus[getDataSourceSyncStatus(item.id)?.status]?.icon"
                />
                <span>{{ dataRecordStatus[getDataSourceSyncStatus(item.id)?.status]?.text }}</span>
              </span>
              <span v-if="!isDataSourceRunning(item.id)">
                {{ getDataSourceSyncStatus(item.id)?.start_at }}
              </span>
            </div>
            <div
              v-if="item?.id === 'local'"
              class="flex items-center"
            >
              <bk-button
                class="min-w-[64px]"
                theme="primary"
                @click="handleImport"
                :disabled="isDataSourceRunning(item.id) || resetLoading.local"
              >
                <Upload class="mr-[8px] text-[16px]" />
                {{ $t('导入') }}
              </bk-button>
              <PopMenu
                :list="getMoreMenuList(item.id)"
                :click-hide="true"
                :popover-props="{
                  offset: 15,
                  arrow: false,
                }"
              >
                <bk-button class="w-[32px] ml-[8px]">
                  <i class="user-icon icon-more"></i>
                </bk-button>
              </PopMenu>
            </div>
            <div
              v-else
              class="flex items-center"
            >
              <div>
                <bk-pop-confirm
                  ref="popConfirmRef"
                  :content="$t('确认同步？')"
                  trigger="click"
                  @confirm="handleOperationsSync(item.id)"
                >
                  <bk-button
                    class="min-w-[64px]"
                    theme="primary"
                    :disabled="isDataSourceRunning(item.id) || resetLoading.external"
                    @click.stop
                  >
                    {{ $t('同步') }}
                  </bk-button>
                </bk-pop-confirm>
              </div>
              <bk-button
                class="min-w-[64px] ml-[8px]"
                outline
                theme="primary"
                :disabled="resetLoading.external"
                @click.stop="handleEdit(item.id)"
              >
                {{ $t('编辑') }}
              </bk-button>
              <PopMenu
                :list="getMoreMenuList(item.id)"
                :click-hide="true"
                :popover-props="{
                  offset: 15,
                  arrow: false,
                }"
              >
                <bk-button class="w-[32px] ml-[8px]">
                  <i class="user-icon icon-more"></i>
                </bk-button>
              </PopMenu>
            </div>
          </div>
        </template>
        <HttpDetails
          v-if="isDetailsExpanded && item.id !== 'local'"
          :data-source-id="dataSourceStore.getDataSourceInfo(item.id).id"
        />
      </DataSourceItem>

      <!-- 展开/收起按钮 -->
      <p
        v-if="dataSource.length > 1 && sortedDataSourcePlugins.length > dataSource.length"
        class="view-type"
        @click="isExpanded = !isExpanded"
      >
        {{ isExpanded ? $t('收起') : $t('展开全部数据源') }}
        <AngleDownLine :class="['ml-[8px]', { 'up-line': isExpanded }]" />
      </p>
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

<script setup lang="tsx"> import axios from 'axios';
import { InfoBox, Message } from 'bkui-vue';
import { AngleDownLine, InfoLine, Upload } from 'bkui-vue/lib/icon';
import Cookies from 'js-cookie';
import { storeToRefs } from 'pinia';
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute } from 'vue-router';

import HttpDetails from './HttpDetails.vue';

import DataSourceItem from '@/components/DataSourceItem.vue';
import MainBreadcrumbsDetails from '@/components/layouts/MainBreadcrumbsDetails.vue';
import PopMenu from '@/components/PopMenu.vue';
import SyncRecords from '@/components/SyncRecords.vue';
import { useInfoBoxContent } from '@/hooks';
import useDataSourceSetting from '@/hooks/useDataSourceSetting';
import { batchDeleteDataSources, deleteDataSources, getDefaultConfig, getRelatedResource, newDataSource, postOperationsSync } from '@/http';
import { t } from '@/language/index';
import router from '@/router';
import { useDataSourceStore, useUser } from '@/store';
import { dataRecordStatus } from '@/utils';
const route = useRoute();

const userStore = useUser();
const dataSourceStore = useDataSourceStore();

const {
  dataSource,
  dataSourcePlugins,
  isConfiguredLocalPlugin,
  isConfiguredGeneralPlugin,
} = storeToRefs(dataSourceStore);

/** 是否展开显示所有数据源 */
const isExpanded = ref(false);

const { startDataSourceSync: otherDataSourceSync } = useDataSourceSetting();
const { startDataSourceSync: localDataSourceSync } = useDataSourceSetting();

const isLoading = ref(false);
/**
 * 重置loading状态
 * @property all - 全部重置
 * @property local - 本地数据源重置
 * @property external - 外部数据源重置
 */
const resetLoading = reactive({
  all: false,
  local: false,
  external: false,
});
const isDetailsExpanded = ref(false);
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

const updateConfig = reactive({
  isShow: false,
  title: t('数据更新记录'),
});

/** 排序后的数据源插件列表 */
const sortedDataSourcePlugins = computed(() => {
  const plugins = [...dataSourcePlugins.value];
  const configuredPluginIds = dataSource.value.map(item => item.plugin_id);

  return plugins.sort((a, b) => {
    const aIsLocal = a.id === 'local';
    const bIsLocal = b.id === 'local';
    const aIsConfigured = configuredPluginIds.includes(a.id);
    const bIsConfigured = configuredPluginIds.includes(b.id);

    // 本地数据源优先
    if (aIsLocal && !bIsLocal) return -1;
    if (!aIsLocal && bIsLocal) return 1;

    // 已配置的排在前面
    if (aIsConfigured && !bIsConfigured) return -1;
    if (!aIsConfigured && bIsConfigured) return 1;

    // 其他保持原顺序
    return 0;
  });
});

/** 过滤后显示的数据源列表 */
const visibleDataSourcePlugins = computed(() => {
  // 如果没有已配置的数据源，显示所有
  if (dataSource.value.length < 2) {
    return sortedDataSourcePlugins.value;
  }

  // 如果已展开，显示所有
  if (isExpanded.value) {
    return sortedDataSourcePlugins.value;
  }

  // 折叠状态下，只显示已配置的数据源
  return sortedDataSourcePlugins.value.filter(plugin => isDataSourceConfigured(plugin.id));
});

// 检查是否有任意数据源正在运行中（用于全部重置按钮）
const disabledSyncBtn = computed(() => dataSourceStore.dataSource.some((item) => {
  const syncStatus = dataSourceStore.dataSourceSyncStatusMap.get(item.id);
  return syncStatus && isDataSourceSyncing(syncStatus.status);
}));

/** 数据源是否同步中 */
const isDataSourceSyncing = (status: string) => ['pending', 'running'].includes(status);

/** 判断数据源是否已配置 */
// eslint-disable-next-line max-len
const isDataSourceConfigured = (pluginId: string) => dataSourceStore.dataSource.map(item => item.plugin_id).includes(pluginId);

// 检查指定数据源是否正在运行中（用于单个数据源的操作按钮）
const isDataSourceRunning = (pluginId: string) => {
  const dataSourceInfo = dataSourceStore.getDataSourceInfo(pluginId);
  if (!dataSourceInfo?.id) return false;
  const syncStatus = dataSourceStore.dataSourceSyncStatusMap.get(dataSourceInfo.id);
  return syncStatus && isDataSourceSyncing(syncStatus.status);
};

// 获取指定数据源的同步状态
const getDataSourceSyncStatus = (pluginId: string) => {
  const dataSourceInfo = dataSourceStore.getDataSourceInfo(pluginId);
  if (!dataSourceInfo?.id) return null;

  return dataSourceStore.dataSourceSyncStatusMap.get(dataSourceInfo.id);
};

const getMoreMenuList = (pluginId: string) => [{
  value: 'reset',
  label: t('重置'),
  disabled: isDataSourceRunning(pluginId)
    || resetLoading[pluginId === 'local' ? 'local' : 'external'],
  onClick: () => handleReset('single', pluginId),
}];

/**
 * @description 重置数据源
 * @param type 重置类型：全部重置或单个重置，默认全部重置
 * @param pluginId 若为单个重置，需传入对应的PluginId
 */
const handleReset = async (type: 'all' | 'single' = 'all', pluginId?: string) => {
  if (type === 'single') {
    const singleKey = pluginId === 'local' ? 'local' : 'external' as const;
    const currentDataSourceId = dataSourceStore.getDataSourceInfo(pluginId)?.id;
    const res = await getRelatedResource(currentDataSourceId);
    const { subContent, resetIdpConfig } = useInfoBoxContent(res.data, '');

    InfoBox({
      width: 600,
      infoType: 'warning',
      title: t('是否重置数据源？'),
      subTitle: subContent,
      confirmText: t('重置'),
      theme: 'danger',
      onConfirm: async () => {
        const resetConfig = resetIdpConfig.value ? 'True' : 'False';
        if (currentDataSourceId) {
          try {
            resetLoading[singleKey] = true;
            await deleteDataSources({ id: currentDataSourceId, is_delete_idp: resetConfig });
            Message({ theme: 'success', message: t('数据源重置成功') });
            // 重置数据源后，重新获取当前数据源信息
            dataSourceStore.handleFetchCurrentDataSource();
          } finally {
            resetLoading[singleKey] = false;
          }
        }
      },
    });
  } else {
    InfoBox({
      width: 400,
      infoType: 'warning',
      title: t('是否重置所有数据源？'),
      content: () => (
        <div class="w-calc(100%_-_64px) flex items-center justify-center">
          <div class="bg-[#F5F7FA] mt-[16px] px-[16px] py-[12px] text-[#494B50]">
            {t('重置后，所有数据源内的用户信息将同步删除，请谨慎操作')}
          </div>
        </div>
      ),
      confirmText: t('重置'),
      cancelText: t('取消'),
      theme: 'danger',
      onConfirm: async () => {
        try {
          resetLoading.all = true;
          await batchDeleteDataSources(null);
          Message({ theme: 'success', message: t('数据源重置成功') });
          // 重置数据源后，重新获取当前数据源信息
          dataSourceStore.handleFetchCurrentDataSource();
        } finally {
          resetLoading.all = false;
        }
      },
    });
  }
};

/** 点击同步 发起同步，并开启syncRecords轮询*/
const handleOperationsSync = async (pluginId: string) => {
  const currentDataSourceId = dataSourceStore.getDataSourceInfo(pluginId)?.id;
  const res = await postOperationsSync(currentDataSourceId);
  Message({ theme: res.data.status, message: res.data.summary });
  otherDataSourceSync(currentDataSourceId, pluginId);
};

// 点击数据源卡片
const handleClickDataSource = async (pluginId: string) => {
  // 判断数据源是否已配置
  const isConfigured = isDataSourceConfigured(pluginId);

  if (isConfigured) {
    // 已配置的数据源：展开/收起详情（仅限非 local 数据源）
    if (pluginId === 'local') return;
    isDetailsExpanded.value = !isDetailsExpanded.value;
  } else {
    // 未配置的数据源：执行新建/配置逻辑
    if (dataSourceStore.dataSource.length < 2) {
      if (pluginId === 'local') {
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
        router.push({ name: 'newDataSource', query: { type: pluginId } });
      }
    }
  }
};

const handleEdit = (dataSourcePlugin: string) => {
  const dataSourceId = dataSourceStore.getDataSourceInfo(dataSourcePlugin)?.id;
  router.push({ name: 'newDataSource', query: { type: dataSourcePlugin, id: dataSourceId } });
};

const handleImport = () => importDialog.isShow = true;

const customRequest = (data: { file: { size?: any; }; }) => {
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

const getSize = (value: number) => {
  const size = value / 1024;
  return `${parseFloat(size.toFixed(2))}KB`;
};

const handleUploadRemove = (file: any) => {
  uploadRef.value?.handleRemove(file);
  uploadInfo.file = {};
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
    localDataSourceSync(dataSourceStore.newDataSourceId, 'local');
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
    await dataSourceStore.handleInitSyncStatus();

    // 初始化完成后，对状态为 pending/running 的数据源启动对应的轮询
    dataSourceStore.dataSource.forEach((item) => {
      const syncStatus = dataSourceStore.dataSourceSyncStatusMap.get(item.id);
      if (syncStatus && isDataSourceSyncing(syncStatus.status)) {
        if (item.plugin_id === 'local') {
          localDataSourceSync(item.id, item.plugin_id);
        } else {
          otherDataSourceSync(item.id, item.plugin_id);
        }
      }
    });
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

.view-type {
  font-size: 14px;
  text-align: center;
  cursor: pointer;

  .up-line {
    transform: rotate(180deg);
  }
}
</style>
