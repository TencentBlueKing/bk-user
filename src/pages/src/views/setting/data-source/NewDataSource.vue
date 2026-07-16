<template>
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
        <div class="steps-wrapper">
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
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import Success from './ConfigSuccess.vue';
import CustomJsonSchema from './CustomJsonSchema.vue';
import Http from './HttpConfig.vue';
import Ldap from './LdapConfig.vue';

import DataSourceItem from '@/components/DataSourceItem.vue';
import { DataSourcePluginsItemData } from '@/http/types/dataSourceFiles';
import { t } from '@/language/index';
import { useDataSourceStore, useMainViewStore, useUser } from '@/store';

const store = useMainViewStore();
const dataSourceStore = useDataSourceStore();
store.customBreadcrumbs = false;

const isNotJsonSchemaIds = ['general', 'local', 'ldap'];

const route = useRoute();

const userStore = useUser();

const currentType = ref('');
const dataSourceId = ref(null);

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

const updateSuccess = ({ text, dataSourceId: newDataSourceId }: { text: string; dataSourceId: number }) => {
  successText.value = `${text}${currentPlugins.value.name}${t('成功 ')}`;
  dataSourceId.value = newDataSourceId;
  isSuccess.value = true;
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

// 获取数据源 id
watch(() => route.query.id, (val: string | string[]) => {
  if (val) {
    dataSourceId.value = Array.isArray(val) ? val[0] : val;
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
}
</style>
