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
      <LabelContent v-for="(item, key) in jsonSchemaProperties" :label="item.title">{{ authSourceData.plugin_config[key]}}</LabelContent>
      <LabelContent :label="$t('登录模式')">{{ $t('仅用于登录') }}</LabelContent>
      <LabelContent :label="$t('登录认证匹配')">
        <div class="content-matching">
          <bk-exception
            v-if="onDataSources.length === 0"
            class="exception-part"
            type="empty"
            scene="part"
            :description="$t('暂无数据源匹配')"
          />
          <div v-else v-for="(item, index) in onDataSources" :key="index">
            <div class="field-rules">
              <dl>
                <dt>{{ $t('数据源字段') }}：</dt>
                <bk-overflow-title
                  type="tips"
                  class="source-field"
                  v-for="(val, i) in item.field_compare_rules"
                  :key="i">
                  {{ val.target_field }}
                </bk-overflow-title>
              </dl>
              <dl>
                <dt>{{ $t('认证源字段') }}：</dt>
                <bk-overflow-title
                  type="tips"
                  class="source-field"
                  v-for="(val, i) in item.field_compare_rules"
                  :key="i">
                  {{ val.source_field }}
                </bk-overflow-title>
              </dl>
            </div>
            <span class="or" v-if="index !== 0">or</span>
          </div>
        </div>
      </LabelContent>
    </ViewRow>
  </bk-loading>
</template>

<script setup lang="ts">
import { defineEmits, defineProps, onMounted, ref } from 'vue';

import LabelContent from '@/components/layouts/LabelContent.vue';
import ViewRow from '@/components/layouts/ViewRow.vue';
import { getDataSourceList, getIdpsDetails, getIdpsPluginsConfig } from '@/http';
import { copy } from '@/utils';

const props = defineProps({
  currentId: {
    type: String,
    default: '',
  },
  authDetailsId: {
    type: String,
    default: '',
  },
});
const emit = defineEmits(['updateRow']);
const isLoading = ref(false);
const authSourceData = ref({});
const onDataSources = ref([]);
const notDataSources = ref([]);
const jsonSchemaProperties = ref({});
const getJsonSchema = () => {
  getIdpsPluginsConfig(props?.authDetailsId).then((res) => {
    jsonSchemaProperties.value = res.data?.json_schema.properties;
  });
};
onMounted(async () => {
  isLoading.value = true;
  try {
    const [authRes, dataRes] = await Promise.all([
      getIdpsDetails(props?.currentId),
      getDataSourceList(''),
    ]);
    authSourceData.value = authRes.data;
    getJsonSchema();
    emit('updateRow', authSourceData.value);
    processMatchRules(dataRes.data);
  } catch (error) {
    console.warn(error);
  } finally {
    isLoading.value = false;
  }
});

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
</script>

<style lang="less" scoped>
.details-wrapper {
  padding: 28px 40px;

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
    background: #F5F7FA;

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

    .field-rules {
      display: flex;
      padding: 12px 24px;
      border-radius: 2px;

      dl {
        width: 50%;

        dt {
          font-size: 14px;
          line-height: 22px;
          color: #979BA5;
        }

        .source-field {
          width: 120px;
          font-size: 14px;
          line-height: 22px;
          color: #313238;
        }
      }
    }
  }
}
</style>
