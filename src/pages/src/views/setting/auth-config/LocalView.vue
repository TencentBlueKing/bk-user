<template>
  <div v-bkloading="{ loading: isLoading, zIndex: 9 }" class="details-info-wrapper">
    <ViewRow :title="$t('基础信息')">
      <LabelContent :label="$t('名称')">{{ idpsName }}</LabelContent>
      <LabelContent :label="$t('是否启用')">
        {{ idpsStatus ? $t('是') : $t('否') }}
      </LabelContent>
    </ViewRow>
    <ViewRow :title="$t('密码规则')">
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
    </ViewRow>
    <ViewRow :title="$t('初始密码设置')">
      <LabelContent :label="$t('修改密码不能重复')">
        <span>{{ passwordInitial?.reserved_previous_password_count }}{{ $t('次') }}</span>
      </LabelContent>
      <LabelContent :label="$t('生成方式')">{{ passwordMethod }}</LabelContent>
      <LabelContent :label="$t('通知方式')">
        {{ notificationMap(passwordInitial?.notification?.enabled_methods) }}
      </LabelContent>
    </ViewRow>
    <ViewRow :title="$t('登录限制')">
      <LabelContent :label="$t('首次强制修改密码')">
        <span>{{ loginLimit?.force_change_at_first_login ? $t('是') : $t('否') }}</span>
      </LabelContent>
      <LabelContent :label="$t('密码试错次数')">
        <span>{{ loginLimit?.max_retries }}{{ $t('次') }}</span>
      </LabelContent>
      <LabelContent :label="$t('锁定时间')">
        <span>{{ loginLimit?.lock_time }}{{ $t('秒') }}</span>
      </LabelContent>
    </ViewRow>
    <ViewRow :title="$t('密码到期提醒')">
      <LabelContent :label="$t('密码有效期')">{{ passwordExpire?.valid_time }}</LabelContent>
      <LabelContent :label="$t('提醒时间')">
        {{ noticeTimeMap(passwordExpire?.remind_before_expire) }}
      </LabelContent>
      <LabelContent :label="$t('通知方式')">
        {{ notificationMap(passwordExpire?.notification?.enabled_methods) }}
      </LabelContent>
    </ViewRow>
  </div>
</template>

<script setup lang="ts">
import { computed, defineProps, onMounted, ref } from 'vue';

import LabelContent from '@/components/layouts/LabelContent.vue';
import ViewRow from '@/components/layouts/ViewRow.vue';
import { getLocalIdps } from '@/http';
import { t } from '@/language/index';
import { noticeTimeMap, notificationMap, passwordMustIncludesMap, passwordNotAllowedMap } from '@/utils';

const props = defineProps({
  currentId: {
    type: String,
    default: '',
  },
});

const isLoading = ref(false);
const idpsName = ref({});
const idpsStatus = ref(true);
const passwordRule = ref({});
const passwordInitial = ref({});
const passwordExpire = ref({});
const loginLimit = ref({});

const passwordMethod = computed(() => (passwordInitial.value?.generate_method === 'random' ? t('随机') : t('固定')));

onMounted(async () => {
  try {
    isLoading.value = true;
    const res = await getLocalIdps(props.currentId);
    idpsName.value = res.data?.name;
    idpsStatus.value = res.data?.plugin_config?.enable_password;
    passwordRule.value = res.data?.plugin_config?.password_rule;
    passwordInitial.value = res.data?.plugin_config?.password_initial;
    passwordExpire.value = res.data?.plugin_config?.password_expire;
    loginLimit.value = res.data?.plugin_config?.login_limit;
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
});
</script>

<style lang="less" scoped>
.details-info-wrapper {
  padding: 28px 40px;

  .row-wrapper {
    padding-bottom: 24px;
    border-bottom: 1px solid #EAEBF0;

    &:last-child {
      border-bottom: none !important;
    }
  }
}
</style>
