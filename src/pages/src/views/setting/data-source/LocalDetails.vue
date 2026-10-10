<template>
  <bk-loading :loading="isLoading" class="details-info-wrapper user-scroll-y">
    <div class="flex flex-col divide-y divide-[#EAEBF0]">
      <Row :title="$t('基础信息')">
        <LabelContent :label="$t('数据源名称')">{{ dataSourceName || '--' }}</LabelContent>
        <LabelContent :label="$t('是否启用密码规则')">{{ enablePassword ? $t('是') : $t('否') }}</LabelContent>
      </Row>
      <template v-if="enablePassword">
        <Row :title="$t('密码规则')">
          <LabelContent :label="$t('密码长度')">
            <span>{{ passwordRule?.min_length }}~32{{ $t('位') }}</span>
          </LabelContent>
          <LabelContent :label="$t('密码必须包含')">
            <span>{{ passwordMustIncludesMap(passwordRule) }}</span>
          </LabelContent>
          <LabelContent :label="$t('密码不允许')">
            <span class="value" v-if="passwordRule?.not_continuous_count === 0">--</span>
            <span class="value" v-else>
              {{ $t('连续x位出现', { count: passwordRule?.not_continuous_count }) }}
              {{ passwordNotAllowedMap(passwordRule) }}
            </span>
          </LabelContent>
        </Row>
        <Row :title="$t('初始密码设置')">
          <LabelContent :label="$t('修改密码不能重复')">
            <span>{{ passwordInitial?.reserved_previous_password_count }}{{ $t('次') }}</span>
          </LabelContent>
          <LabelContent :label="$t('生成方式')">{{ passwordMethod }}</LabelContent>
          <LabelContent :label="$t('通知方式')">
            {{ notificationMap(passwordInitial?.notification?.enabled_methods) }}
          </LabelContent>
        </Row>
        <Row :title="$t('登录限制')">
          <LabelContent :label="$t('首次强制修改密码')">
            <span>{{ loginLimit?.force_change_at_first_login ? $t('是') : $t('否') }}</span>
          </LabelContent>
          <LabelContent :label="$t('密码试错次数')">
            <span>{{ loginLimit?.max_retries }}{{ $t('次') }}</span>
          </LabelContent>
          <LabelContent :label="$t('锁定时间')">
            <span>{{ loginLimit?.lock_time }}{{ $t('秒') }}</span>
          </LabelContent>
        </Row>
        <Row :title="$t('密码有效期设置')">
          <LabelContent :label="$t('密码有效期')">{{ validTimeText }}</LabelContent>
          <LabelContent :label="$t('到期提醒时间')">
            {{ noticeTimeMap(passwordExpire?.remind_before_expire) }}
          </LabelContent>
          <LabelContent :label="$t('通知方式')">
            {{ notificationMap(passwordExpire?.notification?.enabled_methods) }}
          </LabelContent>
        </Row>
      </template>
      <Row :title="$t('冲突配置')">
        <ConflictConfigDetail :config="usernameGenerateConfig" />
      </Row>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';

import ConflictConfigDetail from '@/components/conflict-config/ConflictConfigDetail.vue';
import Row from '@/components/layouts/ItemRow.vue';
import LabelContent from '@/components/layouts/LabelContent.vue';
import { getDataSourceDetails } from '@/http';
import type {
  DataSourceDetails,
  LocalDataSourcePluginConfig,
  LocalIdpLoginLimit,
  LocalIdpPasswordExpire,
  LocalIdpPasswordInitial,
  LocalIdpPasswordRule,
} from '@/http/types/dataSourceFiles';
import { t } from '@/language/index';
import { noticeTimeMap, notificationMap, passwordMustIncludesMap, passwordNotAllowedMap, VALID_TIME } from '@/utils';

const props = defineProps({
  dataSourceId: {
    type: Number,
  },
});

const isLoading = ref(false);
/** 数据源名称 */
const dataSourceName = ref('');
/** 密码相关配置：取自本地数据源 plugin_config（与 LocalConfig 编辑页同源） */
const enablePassword = ref(false);
const passwordRule = ref<LocalIdpPasswordRule>({} as LocalIdpPasswordRule);
const passwordInitial = ref<LocalIdpPasswordInitial>({} as LocalIdpPasswordInitial);
const passwordExpire = ref<LocalIdpPasswordExpire>({} as LocalIdpPasswordExpire);
const loginLimit = ref<LocalIdpLoginLimit>({} as LocalIdpLoginLimit);
/** 冲突配置（用户名冲突规则）：创建时配置、之后不可更新，详情页只读回显（与 HttpDetails 一致） */
const usernameGenerateConfig = ref<DataSourceDetails['username_generate_config']>({ rule: 'unchanged', prefix: '', suffix: '' });

const passwordMethod = computed(() => (passwordInitial.value?.generate_method === 'random' ? t('随机') : t('固定')));

const validTimeText = computed(() => {
  const matched = VALID_TIME.find(item => item.days === passwordExpire.value?.valid_time);
  return matched?.text || passwordExpire.value?.valid_time || '--';
});

/** 加载数据源详情：名称与密码相关配置均取自数据源详情的 plugin_config */
const fetchDetails = async () => {
  isLoading.value = true;
  try {
    const detailsRes = await getDataSourceDetails(props.dataSourceId);
    const details = detailsRes?.data;
    dataSourceName.value = details?.name || '';
    // 密码相关配置取数：已迁移至数据源详情的 plugin_config（存量数据由后端迁移），为空时保留默认展示
    if (details?.plugin_config && Object.keys(details.plugin_config).length > 0) {
      const pluginConfig = details.plugin_config as LocalDataSourcePluginConfig;
      enablePassword.value = pluginConfig?.enable_password ?? false;
      passwordRule.value = pluginConfig?.password_rule;
      passwordInitial.value = pluginConfig?.password_initial;
      passwordExpire.value = pluginConfig?.password_expire;
      loginLimit.value = pluginConfig?.login_limit;
    }
    usernameGenerateConfig.value = details?.username_generate_config || { rule: 'unchanged', prefix: '', suffix: '' };
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
};

onMounted(fetchDetails);
</script>

<style lang="less" scoped>
.details-info-wrapper {
  :deep(.row-wrapper) {
    padding-bottom: 24px;
  }

  :deep(.label-content .label-key) {
    width: 174px;
  }
}
</style>
