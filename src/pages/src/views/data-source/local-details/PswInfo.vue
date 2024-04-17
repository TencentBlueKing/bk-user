<template>
  <bk-loading :loading="isLoading" class="details-info-wrapper user-scroll-y">
    <ul class="details-info-content" v-if="openPasswordLogin">
      <li class="content-item">
        <div class="item-header">
          <p class="item-title">{{ $t('密码规则') }}</p>
          <bk-button outline theme="primary" @click="handleClickEdit">
            {{ $t('编辑') }}
          </bk-button>
        </div>
        <ul class="item-content flex">
          <li>
            <span class="key">{{ $t('密码长度') }}：</span>
            <span class="value">{{ passwordRule?.min_length }}~32{{ $t('位') }}</span>
          </li>
          <li>
            <span class="key">{{ $t('密码试错次数') }}：</span>
            <span class="value">{{ passwordRule?.max_retries }}{{ $t('次') }}</span>
          </li>
          <li>
            <bk-overflow-title class="key" type="tips">{{ $t('密码必须包含') }}：</bk-overflow-title>
            <span class="value">{{ passwordMustIncludesMap(passwordRule) }}</span>
          </li>
          <li>
            <span class="key">{{ $t('锁定时间') }}：</span>
            <span class="value">{{ passwordRule?.lock_time }}{{ $t('秒') }}</span>
          </li>
          <li>
            <bk-overflow-title class="key" type="tips">{{ $t('密码不允许') }}：</bk-overflow-title>
            <span class="value" v-if="passwordRule?.not_continuous_count === 0">--</span>
            <span class="value" v-else>
              {{ $t('连续x位出现', { count: passwordRule?.not_continuous_count }) }}
              {{ passwordNotAllowedMap(passwordRule) }}
            </span>
          </li>
          <li>
            <span class="key">{{ $t('密码有效期') }}：</span>
            <span class="value">{{ validTimeMap(passwordRule?.valid_time) }}</span>
          </li>
        </ul>
      </li>
      <li class="content-item">
        <div class="item-header">
          <p class="item-title">{{ $t('密码设置') }}</p>
        </div>
        <ul :class="['item-content', { 'en': $i18n.locale === 'en' }]">
          <li>
            <bk-overflow-title class="key" type="tips">{{ $t('初始密码获取方式') }}：</bk-overflow-title>
            <span class="value">{{ passwordMethod }}</span>
          </li>
          <li>
            <bk-overflow-title class="key" type="tips">{{ $t('初始密码通知方式') }}：</bk-overflow-title>
            <span class="value">{{ notificationMap(passwordInitial?.notification?.enabled_methods) }}</span>
          </li>
          <li>
            <bk-overflow-title class="key" type="tips">{{ $t('密码到期提醒时间')}}：</bk-overflow-title>
            <span class="value">{{ noticeTimeMap(passwordExpire?.remind_before_expire) }}</span>
          </li>
          <li>
            <bk-overflow-title class="key" type="tips">{{ $t('密码到期通知方式') }}：</bk-overflow-title>
            <span class="value">{{ notificationMap(passwordExpire?.notification?.enabled_methods) }}</span>
          </li>
        </ul>
      </li>
    </ul>
    <div class="details-info-box" v-else>
      <bk-exception
        type="empty"
        :description="$t('暂未开通账密登录')">
        <bk-button theme="primary" @click="handleClickEdit">
          {{ $t('去开通') }}
        </bk-button>
      </bk-exception>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

import { getDataSourceDetails } from '@/http';
import { t } from '@/language/index';
import router from '@/router';
import { noticeTimeMap, notificationMap, passwordMustIncludesMap, passwordNotAllowedMap, validTimeMap } from '@/utils';

const route = useRoute();
const isLoading = ref(false);
const openPasswordLogin = ref(true);
const passwordRule = ref({});
const passwordInitial = ref({});
const passwordExpire = ref({});
const plugin = ref({});

const currentId = computed(() => route.params.id);
const passwordMethod = computed(() => (passwordInitial.value?.generate_method === 'random' ? t('随机') : t('固定')));

onMounted(async () => {
  try {
    isLoading.value = true;
    const res = await getDataSourceDetails(currentId.value);
    openPasswordLogin.value = res.data?.plugin_config?.enable_password;
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

::v-deep .details-info-box {
  width: 100%;
  height: 100%;
  min-height: 500px;
  background: #fff;

  .bk-exception {
    .bk-exception-img {
      width: 720px;
      height: 360px;
    }

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
