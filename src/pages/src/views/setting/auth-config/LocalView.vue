<template>
  <div v-bkloading="{ loading: isLoading, zIndex: 9 }" class="details-info-wrapper user-scroll-y">
    <div v-if="openPasswordLogin">
      <ViewRow :title="$t('基础信息')">
        <LabelContent :label="$t('名称')"></LabelContent>
        <LabelContent :label="$t('是否启用')"></LabelContent>
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
        <LabelContent :label="$t('密码有效期')">
          <span>{{ validTimeMap(passwordRule?.valid_time) }}</span>
        </LabelContent>
        <LabelContent :label="$t('密码试错次数')">
          <span>{{ passwordRule?.min_length }}~32{{ $t('位') }}</span>
        </LabelContent>
        <LabelContent :label="$t('锁定时间')">
          <span>{{ passwordRule?.lock_time }}{{ $t('秒') }}</span>
        </LabelContent>
      </ViewRow>
      <ViewRow :title="$t('密码设置')">
        <LabelContent :label="$t('初始密码获取方式')">{{ passwordMethod }}</LabelContent>
        <LabelContent :label="$t('初始密码通知方式')">
          {{ notificationMap(passwordInitial?.notification?.enabled_methods) }}
        </LabelContent>
        <LabelContent :label="$t('密码到期提醒时间')">
          {{ noticeTimeMap(passwordExpire?.remind_before_expire) }}
        </LabelContent>
        <LabelContent :label="$t('密码到期通知方式')">
          {{ notificationMap(passwordExpire?.notification?.enabled_methods) }}
        </LabelContent>
      </ViewRow>
    </div>
    <div class="details-info-box" v-else>
      <bk-exception
        type="empty"
        :description="$t('暂未开通账密登录')">
      </bk-exception>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineProps, onMounted, ref } from 'vue';

import LabelContent from '@/components/layouts/LabelContent.vue';
import ViewRow from '@/components/layouts/ViewRow.vue';
import { getDataSourceDetails } from '@/http';
import { t } from '@/language/index';
import { noticeTimeMap, notificationMap, passwordMustIncludesMap, passwordNotAllowedMap, validTimeMap } from '@/utils';

const props = defineProps({
  currentId: {
    type: String,
    default: '',
  },
});

const isLoading = ref(false);
const openPasswordLogin = ref(true);
const passwordRule = ref({});
const passwordInitial = ref({});
const passwordExpire = ref({});
const plugin = ref({});

const passwordMethod = computed(() => (passwordInitial.value?.generate_method === 'random' ? t('随机') : t('固定')));

onMounted(async () => {
  try {
    isLoading.value = true;
    const res = await getDataSourceDetails(props.currentId);
    openPasswordLogin.value = res.data?.plugin_config?.enable_account_password_login;
    passwordRule.value = res.data?.plugin_config?.password_rule;
    passwordInitial.value = res.data?.plugin_config?.password_initial;
    passwordExpire.value = res.data?.plugin_config?.password_expire;
    plugin.value = res.data?.plugin;
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
});
</script>

<style lang="less" scoped>
.details-info-wrapper {
  height: calc(100vh - 52px);
  padding: 28px 40px;

  .row-wrapper {
    padding-bottom: 24px;
    border-bottom: 1px solid #EAEBF0;
  }
}

::v-deep .label-content .label-key {
  width: 150px !important;
}

::v-deep .details-info-box {
  width: 100%;
  height: 100%;
  min-height: 500px;
  background: #fff;

  .bk-exception {
    .bk-exception-description {
      margin-top: -30px;
      font-size: 24px;
      color: #63656E;
    }

    .bk-button {
      width: 88px;
    }
  }
}
</style>
