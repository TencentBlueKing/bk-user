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
        <PopMenu
          :list="getHeaderMoreMenuList()"
          :click-hide="true"
          :popover-props="{ offset: 15, arrow: false }"
        >
          <bk-button
            class="w-[32px]"
            :loading="resetLoading.all"
            :disabled="disabledSyncBtn || hasResettingInstance"
          >
            <i class="user-icon icon-more"></i>
          </bk-button>
        </PopMenu>
      </template>
    </MainBreadcrumbsDetails>
    <div
      :class="[
        'data-source-card user-scroll-y',
        { 'has-alert': userStore.showAlert },
      ]"
    >
      <div class="flex items-center mb-[16px]">
        <bk-dropdown
          trigger="click"
          :popover-options="{ width: '420' }"
          placement="bottom-start"
        >
          <bk-button
            theme="primary"
          >
            <i class="user-icon icon-add-2 mr-[6px]" />
            {{ $t('添加') }}
          </bk-button>
          <template #content>
            <div class="flex flex-col w-[420px] py-[8px]">
              <button
                v-for="plugin in sortedDataSourcePlugins"
                :key="plugin.id"
                type="button"
                class="flex w-full items-center px-[16px] py-[12px] text-left
                  cursor-pointer bg-white border-0 hover:bg-[#F5F7FA]"
                @click="handleAddDataSource(plugin.id)"
              >
                <span
                  class="flex flex-none w-[24px] h-[24px] mr-[12px]
                    items-center justify-center text-[20px] text-[#979BA5]"
                >
                  <img
                    v-if="plugin.logo && !addMenuLogoErrors[plugin.id]"
                    :src="plugin.logo"
                    :alt="plugin.name"
                    class="w-[24px] h-[24px] object-contain"
                    @error="handlePluginLogoError(plugin.id)"
                  />
                  <i v-else :class="['user-icon', getDataSourceIcon(plugin.id)]" />
                </span>
                <span class="flex flex-col min-w-0">
                  <span class="text-[14px] leading-[22px] text-[#313238]">{{ plugin.name }}</span>
                  <span class="mt-[2px] text-[12px] leading-[18px] text-[#979BA5]">{{ plugin.description }}</span>
                </span>
              </button>
            </div>
          </template>
        </bk-dropdown>
        <span class="ml-[12px] text-[14px] text-[#63656E]">
          {{ $t('共 {count} 个数据源', { count: dataSource.length }) }}
        </span>
      </div>

      <DataSourceItem
        v-for="source in dataSource"
        :key="source.id"
        :data="getInstanceCardData(source)"
        class="data-source-instance"
        @click="handleClickDataSource(source)"
      >
        <template #right>
          <div class="flex items-center" @click.stop>
            <div
              v-if="getDataSourceSyncStatus(source.id)"
              class="mr-[40px]"
            >
              <span
                v-if="!isDataSourceRunning(source.id)"
                :class="['tag-style', dataRecordStatus[getDataSourceSyncStatus(source.id)?.status]?.theme]">
                {{ dataRecordStatus[getDataSourceSyncStatus(source.id)?.status]?.text }}
              </span>
              <span v-else class="flex">
                <img
                  class="h-[19.25px] w-[19.25px] mr-[9.37px]"
                  :src="dataRecordStatus[getDataSourceSyncStatus(source.id)?.status]?.icon"
                />
                <span>{{ dataRecordStatus[getDataSourceSyncStatus(source.id)?.status]?.text }}</span>
              </span>
              <span v-if="!isDataSourceRunning(source.id)">
                {{ getDataSourceSyncStatus(source.id)?.start_at }}
              </span>
            </div>
            <div v-if="source.plugin_id === 'local'" class="flex items-center">
              <bk-button
                class="min-w-[64px]"
                theme="primary"
                :disabled="isDataSourceRunning(source.id) || resetLoading.instances[source.id]"
                @click="handleImport(source)"
              >
                <Upload class="mr-[8px] text-[16px]" />
                {{ $t('导入') }}
              </bk-button>
              <PopMenu
                :list="getMoreMenuList(source)"
                :click-hide="true"
                :popover-props="{ offset: 15, arrow: false }"
              >
                <bk-button class="w-[32px] ml-[8px]">
                  <i class="user-icon icon-more"></i>
                </bk-button>
              </PopMenu>
            </div>
            <div v-else class="flex items-center">
              <bk-pop-confirm
                :content="$t('确认同步？')"
                trigger="click"
                @confirm="handleOperationsSync(source)"
              >
                <bk-button
                  class="min-w-[64px]"
                  theme="primary"
                  :disabled="isDataSourceRunning(source.id) || resetLoading.instances[source.id]"
                  @click.stop
                >
                  {{ $t('同步') }}
                </bk-button>
              </bk-pop-confirm>
              <bk-button
                class="min-w-[64px] ml-[8px]"
                outline
                theme="primary"
                :disabled="resetLoading.instances[source.id]"
                @click.stop="handleEdit(source)"
              >
                {{ $t('编辑') }}
              </bk-button>
              <PopMenu
                :list="getMoreMenuList(source)"
                :click-hide="true"
                :popover-props="{ offset: 15, arrow: false }"
              >
                <bk-button class="w-[32px] ml-[8px]">
                  <i class="user-icon icon-more"></i>
                </bk-button>
              </PopMenu>
            </div>
          </div>
        </template>
        <HttpDetails
          v-if="expandedDetailsMap[source.id] && source.plugin_id !== 'local'"
          :data-source-id="source.id"
        />
      </DataSourceItem>
    </div>
    <!-- 导入 -->
    <ImportDialog
      v-model:is-show="isShowImportDialog"
      :data-source-id="currentImportSourceId"
      @success="handleImportSuccess"
    />
    <!-- 数据更新记录 -->
    <bk-sideslider
      v-model:is-show="updateConfig.isShow"
      :title="updateConfig.title"
      quick-close
      width="960"
      render-directive="if"
      transfer
    >
      <SyncRecords
        :data-source="dataSource"
      />
    </bk-sideslider>
  </div>
</template>

<script setup lang="tsx">
import { InfoBox, Message } from 'bkui-vue';
import { Upload } from 'bkui-vue/lib/icon';
import { storeToRefs } from 'pinia';
import { computed, h, onMounted, reactive, ref } from 'vue';

import HttpDetails from './HttpDetails.vue';

import DataSourceItem from '@/components/DataSourceItem.vue';
import ImportDialog from '@/components/import-dialog/import-dialog.vue';
import MainBreadcrumbsDetails from '@/components/layouts/MainBreadcrumbsDetails.vue';
import PopMenu from '@/components/PopMenu.vue';
import SyncRecords from '@/components/SyncRecords.vue';
import { useInfoBoxContent } from '@/hooks';
import useDataSourceSetting from '@/hooks/useDataSourceSetting';
import { batchDeleteDataSources, deleteDataSources, getRelatedResource, postOperationsSync } from '@/http';
import type { DataSourceItemData } from '@/http/types/dataSourceFiles';
import { t } from '@/language/index';
import router from '@/router';
import { useDataSourceStore, useUser } from '@/store';
import { dataRecordStatus } from '@/utils';

const userStore = useUser();
const dataSourceStore = useDataSourceStore();

const { dataSource, dataSourcePlugins } = storeToRefs(dataSourceStore);

const { startDataSourceSync: otherDataSourceSync } = useDataSourceSetting();
const { startDataSourceSync: localDataSourceSync } = useDataSourceSetting();

const isShowImportDialog = ref(false);
const currentImportSourceId = ref<number>();
const isLoading = ref(false);
const resetLoading = reactive<{
  all: boolean;
  instances: Record<number, boolean>;
}>({
  all: false,
  instances: {},
});
const expandedDetailsMap = ref<Record<number, boolean>>({});
const addMenuLogoErrors = ref<Record<string, boolean>>({});

const updateConfig = reactive({
  isShow: false,
  title: t('数据更新记录'),
});

/** 排序后的数据源插件列表 */
const sortedDataSourcePlugins = computed(() => {
  const configuredPluginIds = new Set(dataSource.value.map(item => item.plugin_id));
  return [...dataSourcePlugins.value].sort((a, b) => {
    if (a.id === 'local' && b.id !== 'local') return -1;
    if (a.id !== 'local' && b.id === 'local') return 1;
    if (configuredPluginIds.has(a.id) && !configuredPluginIds.has(b.id)) return -1;
    if (!configuredPluginIds.has(a.id) && configuredPluginIds.has(b.id)) return 1;
    return 0;
  });
});

// 检查是否有任意数据源正在运行中（用于全部重置按钮）
const disabledSyncBtn = computed(() => dataSource.value.some((item) => {
  const syncStatus = dataSourceStore.dataSourceSyncStatusMap.get(item.id);
  return syncStatus && dataSourceStore.isDataSourceSyncing(syncStatus.status);
}));
const hasResettingInstance = computed(() => Object.values(resetLoading.instances).some(Boolean));
const getInstanceCardData = (source: DataSourceItemData) => {
  const plugin = dataSourcePlugins.value.find(item => item.id === source.plugin_id);
  return {
    ...source,
    logo: plugin?.logo,
    icon: getDataSourceIcon(source.plugin_id),
    name: source.name,
    description: t('类型：{type}', { type: plugin?.name }),
  };
};

const isDataSourceRunning = (dataSourceId: number) => {
  const syncStatus = dataSourceStore.dataSourceSyncStatusMap.get(dataSourceId);
  return syncStatus && dataSourceStore.isDataSourceSyncing(syncStatus.status);
};

const getDataSourceSyncStatus = (dataSourceId: number) => (
  dataSourceStore.dataSourceSyncStatusMap.get(dataSourceId)
);

const getMoreMenuList = (source: DataSourceItemData) => [{
  value: 'reset',
  label: t('重置'),
  disabled: isDataSourceRunning(source.id) || resetLoading.instances[source.id],
  onClick: () => handleResetSingle(source),
}];

const handlePluginLogoError = (pluginId: string) => {
  addMenuLogoErrors.value[pluginId] = true;
};

const getDataSourceIcon = (pluginId: string) => ({
  general: 'icon-http',
  ldap: 'icon-user-directory',
  local: 'icon-shujuku',
}[pluginId] || 'icon-shujuyuanshu');

/**
 * @description 重置单个数据源
 */
const handleResetSingle = async (source: DataSourceItemData) => {
  const relatedResources = (await getRelatedResource(source.id))?.data;
  const { subContent, resetIdpConfig } = useInfoBoxContent(relatedResources, '');

  InfoBox({
    width: 600,
    infoType: 'warning',
    title: t('是否重置数据源？'),
    subTitle: subContent,
    confirmText: t('重置'),
    theme: 'danger',
    onConfirm: async () => {
      try {
        resetLoading.instances[source.id] = true;
        await deleteDataSources({
          id: source.id,
          is_delete_idp: resetIdpConfig.value ? 'True' : 'False',
        });
        await dataSourceStore.handleFetchCurrentDataSource();
        Message({ theme: 'success', message: t('数据源重置成功') });
      } finally {
        resetLoading.instances[source.id] = false;
      }
    },
  });
};

/** @description 重置所有数据源 */
const handleResetAll = async () => {
  InfoBox({
    width: 400,
    infoType: 'warning',
    title: t('是否重置所有数据源？'),
    content: () => h('div', {
      class: 'w-calc(100%_-_64px) flex items-center justify-center',
    }, [
      h('div', {
        class: 'bg-[#F5F7FA] mt-[16px] px-[16px] py-[12px] text-[#494B50]',
      }, t('重置后，所有数据源内的用户信息将同步删除，请谨慎操作')),
    ]),
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
};

const getHeaderMoreMenuList = () => [{
  value: 'reset-all',
  label: t('全部重置'),
  disabled: disabledSyncBtn.value || hasResettingInstance.value || resetLoading.all,
  onClick: handleResetAll,
}];

/** 点击同步 发起同步，并开启syncRecords轮询*/
const handleOperationsSync = async (source: DataSourceItemData) => {
  const res = await postOperationsSync(source.id);
  Message({ theme: res.data.status, message: res.data.summary });
  otherDataSourceSync(source.id, source.plugin_id);
};

// 点击数据源卡片
const handleClickDataSource = (source: DataSourceItemData) => {
  if (source.plugin_id === 'local') return;
  expandedDetailsMap.value[source.id] = !expandedDetailsMap.value[source.id];
};

const handleAddDataSource = (pluginId: string) => {
  router.push({
    name: 'newDataSource',
    query: {
      type: pluginId,
    },
  });
};


const handleEdit = (source: DataSourceItemData) => {
  router.push({
    name: 'newDataSource',
    query: {
      type: source.plugin_id,
      id: source.id,
      name: source.name,
    },
  });
};

const handleImport = (source?: DataSourceItemData) => {
  currentImportSourceId.value = source?.id;
  isShowImportDialog.value = true;
};

const handleImportSuccess = () => {
  router.push({ name: 'organization' });
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
      if (syncStatus && dataSourceStore.isDataSourceSyncing(syncStatus.status)) {
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
  if (router.currentRoute.value.query?.isLink) {
    handleImport(dataSourceStore.getDataSourceInfo('local'));
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

.data-source-instance {
  margin-bottom: 12px;
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
