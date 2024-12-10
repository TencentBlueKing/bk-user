<template>
  <bk-loading :loading="isLoading" class="details-info-wrapper user-scroll-y">
    <div v-if="isPluginConfig">
      <div v-if="pluginId !== 'ldap'">
        <Row :title="$t('服务配置')">
          <div class="flex">
            <div class="flex-1">
              <LabelContent :label="$t('服务地址')">{{ serverConfig.server_base_url }}</LabelContent>
              <LabelContent :label="$t('用户数据 API 路径')">{{ serverConfig.user_api_path }}</LabelContent>
              <div class="query-params" v-if="serverConfig.user_api_query_params?.length">
                <span class="key">{{ $t('查询参数') }}：</span>
                <div class="value">
                  <bk-tag v-for="(item, index) in serverConfig.user_api_query_params" :key="index">
                    {{item.key}}：{{item.value}}
                  </bk-tag>
                </div>
              </div>
              <LabelContent :label="$t('组织数据 API 路径')">{{ serverConfig.department_api_path }}</LabelContent>
              <div class="query-params" v-if="serverConfig.department_api_query_params?.length">
                <span class="key">{{ $t('查询参数') }}：</span>
                <div class="value">
                  <bk-tag v-for="(item, index) in serverConfig.department_api_query_params" :key="index">
                    {{item.key}}：{{item.value}}
                  </bk-tag>
                </div>
              </div>
            </div>
            <div class="flex-1">
              <LabelContent :label="$t('分页请求每页数量')">{{ serverConfig.request_timeout }}</LabelContent>
              <LabelContent :label="$t('请求超时时间')">{{ serverConfig.request_timeout }}{{ $t('秒') }}</LabelContent>
              <LabelContent :label="$t('重试次数')">{{ serverConfig.retries }}{{ $t('次') }}</LabelContent>
            </div>
          </div>
        </Row>
        <Row :title="$t('认证配置')">
          <LabelContent :label="$t('认证方式')">{{ authConfig.method }}</LabelContent>
          <template v-if="authConfig.method === 'bearer_token'">
            <LabelContent label="Token">************</LabelContent>
          </template>
          <template v-else>
            <LabelContent :label="$t('用户名')">{{ authConfig.username }}</LabelContent>
            <LabelContent :label="$t('密码')">******</LabelContent>
          </template>
        </Row>
        <Row :title="$t('字段设置')">
          <LabelContent :label="$t('字段映射')">
            <div v-for="(item, index) in fieldMapping" :key="index">
              <span>{{ item.target_field }}</span>
              <span>=</span>
              <span>{{ item.source_field }}</span>
            </div>
          </LabelContent>
        </Row>
        <Row :title="$t('同步配置')">
          <LabelContent :label="$t('同步周期')">
            <span class="value" v-for="(item, index) in SYNC_CONFIG_LIST" :key="index">
              <span v-if="item.value === syncConfig.sync_period">{{ item.label }}</span>
            </span>
          </LabelContent>
        </Row>
      </div>
      <div v-if="pluginId === 'ldap'">
        <Row :title="$t('服务配置')">
          <div class="flex">
            <div class="flex-1">
              <LabelContent :label="$t('LDAP 服务地址')">{{ serverConfig.server_url }}</LabelContent>
              <LabelContent :label="$t('Bind DN')">{{ serverConfig.bind_dn }}</LabelContent>
              <LabelContent :label="$t('Bind DN 密码')">{{ serverConfig.bind_password }}</LabelContent>
              <LabelContent :label="$t('根目录 (Base DN)')">{{ serverConfig.base_dn }}</LabelContent>
            </div>
            <div class="flex-1">
              <LabelContent :label="$t('分页请求每页数量')">{{ serverConfig.page_size }}</LabelContent>
              <LabelContent :label="$t('请求超时时间')">{{ serverConfig.request_timeout }}{{ $t('秒') }}</LabelContent>
            </div>
          </div>
        </Row>
        <Row :title="$t('数据配置')">
          <LabelContent :label="$t('用户对象类')">{{ dataConfig.user_object_class }}</LabelContent>
          <LabelContent :label="$t('用户 Base DN')">
            <div v-for="(item, index) in dataConfig.user_search_base_dns" :key="index">{{ item }}</div>
          </LabelContent>
          <LabelContent :label="$t('部门对象类')">{{ dataConfig.dept_object_class }}</LabelContent>
          <LabelContent :label="$t('部门 Base DN')">
            <div v-for="(item, index) in dataConfig.dept_search_base_dns" :key="index">{{ item }}</div>
          </LabelContent>
        </Row>
        <Row :title="$t('字段设置')">
          <LabelContent :label="$t('字段映射')">
            <div v-for="(item, index) in fieldMapping" :key="index">
              <span>{{ item.target_field }}</span>
              <span>=</span>
              <span>{{ item.source_field }}</span>
            </div>
          </LabelContent>
        </Row>
        <Row :title="$t('用户组信息')" v-if="userGroupConfig.enabled">
          <LabelContent :label="$t('用户组对象类')">{{ userGroupConfig.object_class }}</LabelContent>
          <LabelContent :label="$t('用户组 Base DN')">
            <div v-for="(item, index) in userGroupConfig.search_base_dns" :key="index">{{ item }}</div>
          </LabelContent>
          <LabelContent :label="$t('用户组成员字段')">{{ userGroupConfig.group_member_field }}</LabelContent>
        </Row>
        <Row :title="$t('Leader 信息')" v-if="leaderConfig.enabled">
          <LabelContent :label="$t('Leader 字段名')">{{ leaderConfig.leader_field }}</LabelContent>
        </Row>
        <Row :title="$t('同步配置')">
          <LabelContent :label="$t('同步周期')">
            <span class="value" v-for="(item, index) in SYNC_CONFIG_LIST" :key="index">
              <span v-if="item.value === syncConfig.sync_period">{{ item.label }}</span>
            </span>
          </LabelContent>
        </Row>
      </div>
    </div>
    <div class="details-info-box" v-else>
      <bk-button theme="primary" @click="handleClickEdit">
        {{ $t('编辑') }}
      </bk-button>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';

import Row from '@/components/layouts/ItemRow.vue';
import LabelContent from '@/components/layouts/LabelContent.vue';
import { getDataSourceDetails, getFields } from '@/http';
import router from '@/router';
import { SYNC_CONFIG_LIST } from '@/utils';

const props = defineProps({
  dataSourceId: {
    type: Number,
  },
});

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
// 数据配置
const dataConfig = ref({});
// 数据配置
const userGroupConfig = ref({});
// 数据配置
const leaderConfig = ref({});

const isPluginConfig = ref(true);

const pluginId = ref('');

onMounted(async () => {
  try {
    isLoading.value = true;
    const res = await getDataSourceDetails(props.dataSourceId);
    const fieldList = await getFields();

    pluginId.value = res.data?.plugin?.id;

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
      dataConfig.value = res.data?.plugin_config?.data_config;
      userGroupConfig.value = res.data?.plugin_config?.user_group_config;
      leaderConfig.value = res.data?.plugin_config?.leader_config;
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
    name: 'newDataSource',
    query: {
      type: plugin.value?.id,
      id: props.dataSourceId,
    },
  });
};
</script>

<style lang="less" scoped>
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

.row-wrapper {
  padding: 0 24px 24px;
  margin-bottom: 0;
  border-bottom: 1px solid #EAEBF0;

  &:last-child {
    padding-bottom: 24px;
    border-bottom: none;
  }
}

::v-deep .label-content .label-key {
  width: 174px !important;
}
</style>
