<template>
  <bk-loading class="details-wrapper" :loading="isLoading">
    <div class="details-type">
      <img :src="authSourceData.plugin?.logo">
      <div>
        <p class="title">{{ authSourceData.plugin?.name }}</p>
        <p class="subtitle">{{ authSourceData.plugin?.description }}</p>
      </div>
    </div>
    <div class="details-url" v-if="authSourceData.callback_uri">
      <p class="title">{{ $t('回调地址') }}</p>
      <div class="content">
        <p>{{ authSourceData.callback_uri }}</p>
        <i class="user-icon icon-copy" @click="copy(authSourceData.callback_uri)" />
      </div>
    </div>
    <ViewRow :title="$t('认证源信息')" class="mt-[24px]">
      <LabelContent :label="$t('名称')">{{ authSourceData.name }}</LabelContent>
      <LabelContent :label="$t('是否启用')">{{ authSourceData.status === 'enabled' ? $t('是') : $t('否') }}</LabelContent>
      <LabelContent :label="$t('企业 ID')">{{ authSourceData.plugin_config?.corp_id }}</LabelContent>
      <LabelContent label="Agent ID">{{ authSourceData.plugin_config?.agent_id }}</LabelContent>
      <LabelContent label="Secret">**********</LabelContent>
      <LabelContent :label="$t('登录模式')">{{ $t('仅用于登录') }}</LabelContent>
      <LabelContent :label="$t('生效范围')">
        <EffectiveScopeView :source-ids="scopeIds" />
      </LabelContent>
      <LabelContent :label="$t('登录认证匹配')">
        <div class="content-matching">
          <bk-exception
            v-if="onDataSources.length === 0"
            class="exception-part"
            type="empty"
            scene="part"
            :description="$t('暂无数据源匹配')"
          />
          <template v-else>
            <DataSourceMatchViewCard
              v-for="item in onDataSources"
              :key="item.data_source_id"
              :data-source-name="item.data_source_name"
              :field-compare-rules="item.field_compare_rules"
            />
          </template>
        </div>
      </LabelContent>
    </ViewRow>
  </bk-loading>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';

import DataSourceMatchViewCard from './DataSourceMatchViewCard.vue';
import EffectiveScopeView from './EffectiveScopeView.vue';

import LabelContent from '@/components/layouts/LabelContent.vue';
import ViewRow from '@/components/layouts/ViewRow.vue';
import { getDataSourceList, getIdpsDetails } from '@/http';
import { copy } from '@/utils';

interface IProps {
  idpId: string;
}

const props = defineProps<IProps>();
const emit = defineEmits(['detail-loaded']);

const isLoading = ref(false);
const authSourceData = ref({});
const scopeIds = ref<number[]>([]);
const onDataSources = ref([]);
const notDataSources = ref([]);

const processMatchRules = (list) => {
  const dataSourceIds = authSourceData.value.data_source_match_rules.map(item => item.data_source_id);
  onDataSources.value = list
    .filter(val => dataSourceIds.includes(val.id))
    .map(val => ({
      data_source_id: val.id,
      data_source_name: val.name,
      field_compare_rules: authSourceData.value.data_source_match_rules
        .find(item => item.data_source_id === val.id).field_compare_rules,
    }));
  notDataSources.value = list
    .filter(val => !dataSourceIds.includes(val.id) && val.plugin_id === 'local')
    .map(val => ({
      data_source_id: val.id,
      data_source_name: val.name,
    }));
};

onMounted(async () => {
  isLoading.value = true;
  try {
    const [authRes, dataRes] = await Promise.all([
      getIdpsDetails(props?.idpId),
      getDataSourceList(),
    ]);
    authSourceData.value = authRes.data;
    scopeIds.value = authSourceData.value.data_source_match_rules?.map(item => item.data_source_id) || [];
    emit('detail-loaded', authSourceData.value);
    processMatchRules(dataRes.data);
  } catch (error) {
    console.warn(error);
  } finally {
    isLoading.value = false;
  }
});
</script>

<style lang="less" scoped>
.details-wrapper {
  padding: 28px 40px;

  /* 本页认证源信息各 LabelContent 的 label 统一 12px（LabelContent 为共用组件，仅在页面级覆写） */
  :deep(.label-key) {
    font-size: 12px;
    flex-shrink: 0;
  }

  /* 登录认证匹配的表格内容较宽，须允许 value 收缩，否则会把 label 挤窄且自身撑出容器 */
  :deep(.label-value) {
    min-width: 0;
  }

  .details-type {
    display: flex;
    padding: 10px 0;
    margin-bottom: 24px;
    background: #F5F7FA;
    border-radius: 2px;
    align-items: center;

    img {
      width: 24px;
      height: 24px;
      margin: 0 15px;
    }

    .title {
      font-size: 14px;
      color: #313238;
    }

    .subtitle {
      font-size: 12px;
      color: #979BA5;
    }
  }

  .details-url {
    padding-bottom: 24px;
    border-bottom: 1px solid #EAEBF0;

    .title {
      margin-bottom: 12px;
      font-size: 14px;
      font-weight: 700;
      line-height: 22px;
      color: #63656E;
    }

    .content {
      display: flex;
      padding: 8px 12px;
      color: #313238;
      word-wrap: break-word;
      background: #F0F5FF;
      align-items: center;
      justify-content: space-between;
      overflow-wrap: break-word;

      p {
        width: 70%;
      }

      i {
        font-size: 14px;
        color: #3A84FF;
        cursor: pointer;
      }
    }
  }

  .content-matching {
    width: 100%;

    ::v-deep .exception-part {
      position: relative;

      .bk-exception-img {
        width: 340px;
        height: 170px;
      }

      .bk-exception-description {
        position: absolute;
        bottom: 0;
        font-size: 14px;
      }
    }
  }
}
</style>
