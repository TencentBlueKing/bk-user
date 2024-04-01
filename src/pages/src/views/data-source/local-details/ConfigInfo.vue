<template>
  <bk-loading :loading="isLoading" class="details-info-wrapper user-scroll-y">
    <ul class="details-info-content" v-if="isPluginConfig">
      <li class="content-item">
        <div class="item-header">
          <p class="item-title">{{ $t('服务配置') }}</p>
          <bk-button outline theme="primary" @click="handleClickEdit">
            {{ $t('编辑') }}
          </bk-button>
        </div>
        <ul class="item-content" style="display: flex">
          <div class="w-[50%]">
            <li>
              <span class="key">{{ $t('服务地址') }}：</span>
              <span class="value">{{ serverConfig.server_base_url }}</span>
            </li>
            <li>
              <span class="key">{{ $t('用户数据 API 路径') }}：</span>
              <span class="value">{{ serverConfig.user_api_path }}</span>
            </li>
            <div class="query-params" v-if="serverConfig.user_api_query_params?.length">
              <span class="key">{{ $t('查询参数') }}：</span>
              <div class="value">
                <bk-tag v-for="(item, index) in serverConfig.user_api_query_params" :key="index">
                  {{item.key}}：{{item.value}}
                </bk-tag>
              </div>
            </div>
            <li>
              <span class="key">{{ $t('部门数据 API 路径') }}：</span>
              <span class="value">{{ serverConfig.department_api_path }}</span>
            </li>
            <div class="query-params" v-if="serverConfig.department_api_query_params?.length">
              <span class="key">{{ $t('查询参数') }}：</span>
              <div class="value">
                <bk-tag v-for="(item, index) in serverConfig.department_api_query_params" :key="index">
                  {{item.key}}：{{item.value}}
                </bk-tag>
              </div>
            </div>
          </div>
          <div class="w-[50%]">
            <li>
              <span class="key">{{ $t('分页请求每页数量') }}：</span>
              <span class="value">{{ serverConfig.page_size }}</span>
            </li>
            <li>
              <span class="key">{{ $t('请求超时时间') }}：</span>
              <span class="value">{{ serverConfig.request_timeout }}{{ $t('秒') }}</span>
            </li>
            <li>
              <span class="key">{{ $t('重试次数') }}：</span>
              <span class="value">{{ serverConfig.retries }}{{ $t('次') }}</span>
            </li>
          </div>
        </ul>
      </li>
      <li class="content-item">
        <div class="item-header">
          <p class="item-title">{{ $t('认证配置') }}</p>
        </div>
        <ul class="item-content">
          <li>
            <span class="key">{{ $t('认证方式') }}：</span>
            <span class="value">{{ authConfig.method }}</span>
          </li>
          <li v-if="authConfig.method === 'bearer_token'">
            <span class="key">Token：</span>
            <span class="value">************</span>
          </li>
          <template v-else>
            <li>
              <span class="key">{{ $t('用户名') }}：</span>
              <span class="value">{{ authConfig.username }}</span>
            </li>
            <li>
              <span class="key">{{ $t('密码') }}：</span>
              <span class="value">******</span>
            </li>
          </template>
        </ul>
      </li>
      <li class="content-item">
        <div class="item-header">
          <p class="item-title">{{ $t('字段设置') }}</p>
        </div>
        <ul class="item-content">
          <li>
            <span class="key">{{ $t('字段映射') }}：</span>
            <div class="value">
              <div v-for="(item, index) in fieldMapping" :key="index">
                <span>{{ item.target_field }}</span>
                <span>=</span>
                <span>{{ item.source_field }}</span>
              </div>
            </div>
          </li>
        </ul>
      </li>
      <li class="content-item">
        <div class="item-header">
          <p class="item-title">{{ $t('同步配置') }}</p>
        </div>
        <ul class="item-content">
          <li>
            <span class="key">{{ $t('同步周期') }}：</span>
            <span class="value" v-for="(item, index) in SYNC_CONFIG_LIST" :key="index">
              <span v-if="item.value === syncConfig.sync_period">{{ item.label }}</span>
            </span>
          </li>
        </ul>
      </li>
    </ul>
    <div class="details-info-box" v-else>
      <bk-button theme="primary" @click="handleClickEdit">
        {{ $t('编辑') }}
      </bk-button>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

import { getDataSourceDetails, getFields } from '@/http';
import router from '@/router';
import { SYNC_CONFIG_LIST } from '@/utils';

const route = useRoute();
const isLoading = ref(false);
const plugin = ref({});
// 服务配置
const serverConfig = ref({});
// 鉴权配置
const authConfig = ref({});
// 字段映射
const fieldMapping = ref([]);
// 同步配置
const syncConfig = ref({});

const isPluginConfig = ref(true);

const currentId = computed(() => route.params.id);

onMounted(async () => {
  try {
    isLoading.value = true;
    const res = await getDataSourceDetails(currentId.value);
    const fieldList = await getFields();

    res.data?.field_mapping?.forEach((item) => {
      [...fieldList?.data?.builtin_fields, ...fieldList?.data?.custom_fields]?.forEach((demo) => {
        if (item.target_field === demo.name) {
          fieldMapping.value.push({
            target_field: demo.display_name,
            mapping_operation: item.mapping_operation,
            source_field: item.source_field,
          });
        }
      });
    });

    if (JSON.stringify(res.data?.plugin_config) === '{}') {
      isPluginConfig.value = false;
    } else {
      serverConfig.value = res.data?.plugin_config?.server_config;
      authConfig.value = res.data?.plugin_config?.auth_config;
      isPluginConfig.value = true;
    }
    syncConfig.value = res.data?.sync_config;
    plugin.value = res.data?.plugin;
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
});

const handleClickEdit = () => {
  router.push({
    name: 'newLocal',
    params: {
      type: plugin.value?.id,
      id: currentId.value,
    },
  });
};
</script>

<style lang="less" scoped>
@import url("@/css/tenantViewStyle.less");

.query-params {
  position: relative;
  display: flex;
  max-width: 650px;
  min-width: 325px;
  padding: 10px 0;
  margin-left: 90px;
  background: #FAFBFD;
  border: 1px solid #EAEBF0;
  border-radius: 2px;

  &::after {
    position: absolute;
    top: -14px;
    left: 27px;
    z-index: 1;
    width: 0;
    height: 0;
    border: 7px solid transparent;
    border-bottom-color: #EAEBF0;
    content: '';
  }

  &::before{
    position: absolute;
    top: -13px;
    left: 27px;
    z-index: 2;
    width: 0;
    height: 0;
    border: 7px solid transparent;
    border-bottom: 7px solid #FAFBFD;
    content: '';
  }

  .key {
    min-width: 90px;
    font-size: 14px;
    line-height: 26px;
    text-align: right;
  }
}

.details-info-box {
  display: flex;
  width: 100%;
  height: 100%;
  min-height: 500px;
  background: #fff;
  justify-content: center;
  align-items: center;

  .bk-button {
    width: 88px;
  }
}
</style>
