<template>
  <bk-loading :loading="isLoading" class="details-info-wrapper user-scroll-y">
    <ul class="details-info-content" v-if="openPasswordLogin">
      <li class="content-item">
        <div class="item-header">
          <p class="item-title">密码规则</p>
          <bk-button outline theme="primary" @click="handleClickEdit">
            编辑
          </bk-button>
        </div>
        <ul class="item-content flex">
          <li>
            <span class="key">密码长度：</span>
            <span class="value">{{ passwordRule?.min_length }}~32位</span>
          </li>
          <li>
            <span class="key">密码试错次数：</span>
            <span class="value">{{ passwordRule?.max_retries }}次</span>
          </li>
          <li>
            <span class="key">密码必须包含：</span>
            <span class="value">{{ passwordMustIncludesMap(passwordRule) }}</span>
          </li>
          <li>
            <span class="key">锁定时间：</span>
            <span class="value">{{ passwordRule?.lock_time }}秒</span>
          </li>
          <li>
            <span class="key">密码不允许：</span>
            <span class="value" v-if="passwordRule?.not_continuous_count === 0">--</span>
            <span class="value" v-else>
              连续{{ passwordRule?.not_continuous_count }}位出现
              {{ passwordNotAllowedMap(passwordRule) }}
            </span>
          </li>
          <li>
            <span class="key">密码有效期：</span>
            <span class="value">{{ validTimeMap(passwordRule?.valid_time) }}</span>
          </li>
        </ul>
      </li>
      <li class="content-item">
        <div class="item-header">
          <p class="item-title">密码设置</p>
        </div>
        <ul class="item-content">
          <li>
            <span class="key">初始密码获取方式：</span>
            <span class="value">{{ passwordMethod }}</span>
          </li>
          <li>
            <span class="key">初始密码通知方式：</span>
            <span class="value">{{ notificationMap(passwordInitial?.notification?.enabled_methods) }}</span>
          </li>
          <li>
            <span class="key">密码到期提醒时间：</span>
            <span class="value">{{ noticeTimeMap(passwordExpire?.remind_before_expire) }}</span>
          </li>
          <li>
            <span class="key">密码到期通知方式：</span>
            <span class="value">{{ notificationMap(passwordExpire?.notification?.enabled_methods) }}</span>
          </li>
        </ul>
      </li>
    </ul>
    <div class="details-info-box" v-else>
      <bk-exception
        type="empty"
        description="暂未开通账密登录">
        <bk-button theme="primary" @click="handleClickEdit">
          去开通
        </bk-button>
      </bk-exception>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

import { getDataSourceDetails } from '@/http/dataSourceFiles';
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
const passwordMethod = computed(() => (passwordInitial.value?.generate_method === 'random' ? '随机' : '固定'));

onMounted(async () => {
  try {
    isLoading.value = true;
    const res = await getDataSourceDetails(currentId.value);
    openPasswordLogin.value = res.data?.plugin_config?.enable_account_password_login;
    passwordRule.value = res.data?.plugin_config?.password_rule;
    passwordInitial.value = res.data?.plugin_config?.password_initial;
    passwordExpire.value = res.data?.plugin_config?.password_expire;
    plugin.value = res.data?.plugin;
  } catch (e) {
    isLoading.value = false;
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
