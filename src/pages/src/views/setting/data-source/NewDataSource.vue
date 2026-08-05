<template>
  <div>
    <MainBreadcrumbsDetails
      :subtitle="currentPlugins.name"
      @to-back="handleBack"
    />
    <div
      :class="['data-source-card user-scroll-y', { 'has-alert': userStore.showAlert }]"
      v-bkloading="{ loading: isLoading, zIndex: 10 }"
    >
      <DataSourceItem
        v-if="!isSuccess"
        :data="currentPlugins"
        :open-hover="false"
        @click="handleCollapse"
      >
        <template v-if="showContent">
          <div v-if="currentType !== 'local'" class="steps-wrapper">
            <bk-steps
              ext-cls="steps"
              :cur-step="curStep"
              :steps="typeSteps"
            />
          </div>
          <div>
            <Http
              v-if="currentType === 'general'"
              :cur-step="curStep"
              :data-source-id="dataSourceId"
              :is-reset="isReset"
              @update-cur-step="updateCurStep"
              @update-success="updateSuccess" />
            <Ldap
              v-if="currentType === 'ldap'"
              :cur-step="curStep"
              :data-source-id="dataSourceId"
              :is-reset="isReset"
              @update-cur-step="updateCurStep"
              @update-success="updateSuccess" />
            <Local
              v-if="currentType === 'local'"
              :data-source-id="dataSourceId"
              @cancel="handleBack"
              @update-success="updateSuccess"
            />
            <CustomJsonSchema
              v-if="!isNotJsonSchemaIds.includes(currentType)"
              :current-type="currentType"
              :data-source-id="dataSourceId"
              :cur-step="curStep"
              :is-reset="isReset"
              @update-cur-step="updateCurStep"
              @update-success="updateSuccess" />
          </div>
        </template>
      </DataSourceItem>
      <Success
        v-else
        :title="successText"
        :data-source-id="dataSourceId"
        :is-local="isLocal"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import Success from './ConfigSuccess.vue';
import CustomJsonSchema from './CustomJsonSchema.vue';
import Http from './HttpConfig.vue';
import Ldap from './LdapConfig.vue';
import Local from './LocalConfig.vue';

import DataSourceItem from '@/components/DataSourceItem.vue';
import MainBreadcrumbsDetails from '@/components/layouts/MainBreadcrumbsDetails.vue';
import { DataSourcePluginsItemData } from '@/http/types/dataSourceFiles';
import { t } from '@/language/index';
import { useDataSourceStore, useMainViewStore, useUser } from '@/store';

const store = useMainViewStore();
const dataSourceStore = useDataSourceStore();
store.customBreadcrumbs = true;

const isNotJsonSchemaIds = ['general', 'local', 'ldap'];

const route = useRoute();
const router = useRouter();

const userStore = useUser();

const currentType = ref('');
const dataSourceId = ref<number | null>(null);
/** 当前数据源是否为本地数据源，成功页据此隐藏「立即同步」 */
const isLocal = ref(false);

const currentPlugins = ref({} as DataSourcePluginsItemData);
const isLoading = ref(false);

const curStep = ref(1);
const typeSteps = ref([
  { title: t('服务配置') },
  { title: t('字段设置') },
]);

// 切换展示状态
const showContent = ref(true);
// 数据源创建、更新
const successText = ref('新建企业微信数据源成功');
const isSuccess = ref(false);
const isReset = ref(false);

// 切换步骤
const updateCurStep = (value: number) => {
  curStep.value = value;
};
const handleCollapse = () => {
  showContent.value = !showContent.value;
};

const updateSuccess = ({ text, name, dataSourceId: newDataSourceId }: {
  text: string;
  name: string;
  dataSourceId: number;
}) => {
  successText.value = `${text}${name}${t('成功 ')}`;
  dataSourceId.value = newDataSourceId;
  isLocal.value = currentType.value === 'local';
  isSuccess.value = true;
};

const updateDataSourceContext = () => {
  currentPlugins.value = dataSourceStore.dataSourcePlugins
    .find(item => item.id === currentType.value) || {} as DataSourcePluginsItemData;
  store.breadCrumbsTitle = dataSourceId.value === null ? t('添加数据源') : t('编辑数据源');
};

const handleBack = () => {
  router.push({ name: 'dataSource' });
};

const handleInit = async () => {
  try {
    isLoading.value = true;
    await Promise.all([
      dataSourceStore.handleFetchAllDataSourcePlugins(),
      dataSourceStore.handleFetchCurrentDataSource(),
    ]);
    updateDataSourceContext();
  } finally {
    isLoading.value = false;
  }
};

// 获取数据源 id
watch(() => route.query.id, (val: string | string[]) => {
  if (val) {
    dataSourceId.value = Number(Array.isArray(val) ? val[0] : val);
  } else {
    dataSourceId.value = null;
  }
}, {
  deep: true,
  immediate: true,
});

// 获取数据源类型
watch(() => route.query.type, (val: string | string[]) => {
  if (val) {
    currentType.value = Array.isArray(val) ? val[0] : val;
  }
}, {
  deep: true,
  immediate: true,
});

onMounted(() => {
  // 初始化数据源列表 - 若直接在新建/编辑页刷新，store中没有数据源列表
  handleInit();
});

onUnmounted(() => {
  store.breadCrumbsTitle = '';
});
</script>

<style lang="less" scoped>
.has-alert {
  height: calc(100vh - 144px) !important;
}

.data-source-card {
  height: calc(100vh - 92px);
  padding: 16px 24px;

  .steps-wrapper {
    padding: 12px 0;
    text-align: center;
    background: #FAFBFD;
    box-shadow: 0 1px 0 0 #F0F1F5;

    .steps {
      width: 350px;
      margin: auto;
    }
  }

  .data-source-name-row {
    margin-bottom: 0;
    border-bottom: 1px solid #EAEBF0;
    box-shadow: none;
  }
}
</style>
