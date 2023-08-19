<template>
  <div class="details-info-wrapper user-scroll-y">
    <ul class="details-info-content">
      <li class="content-item">
        <div class="item-header">
          <p class="item-title">账号信息</p>
          <bk-button outline theme="primary" @click="handleClickEdit">
            编辑
          </bk-button>
        </div>
        <ul class="item-content">
          <li v-for="(item, index) in state.accountInfo" :key="index">
            <span class="key">{{ accountMap[item.key] }}：</span>
            <span class="value">{{ item.value }}</span>
          </li>
        </ul>
      </li>
      <li class="content-item">
        <div class="item-header">
          <p class="item-title">密码规则</p>
        </div>
        <ul class="item-content flex">
          <li v-for="(item, index) in state.passwordRule" :key="index">
            <span class="key">{{ accountMap[item.key] }}：</span>
            <span class="value">{{ item.value }}</span>
          </li>
        </ul>
      </li>
      <li class="content-item">
        <div class="item-header">
          <p class="item-title">密码设置</p>
        </div>
        <ul class="item-content">
          <li v-for="(item, index) in state.passwordSetting" :key="index">
            <span class="key">{{ accountMap[item.key] }}：</span>
            <span class="value">{{ item.value }}</span>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<script setup lang="tsx">
import { reactive } from "vue";
import router from "@/router";

const accountMap = {
  account_validity: "账号有效期",
  account_expiration_notice_time: "账号到期提醒时间",
  account_expiration_notice_method: "账号到期提醒方式",
  password_length: "密码长度",
  max_trail_times_list: "密码试错次数",
  password_must_includes: "密码必须包含",
  auto_unlock_seconds: "锁定时间",
  password_rult_length: "密码不允许",
  frozen: "冻结",
  password_valid_days_list: "密码有效期",
  init_password_method: "初始密码获取方式",
  init_password_notice_method: "初始密码通知方式",
  password_expiration_notice_time: "密码到期提醒时间",
  password_expiration_notice_method: "密码到期通知方式",
}
const state = reactive({
  accountInfo: [
    {
      key: 'account_validity',
      value: "永久",
    },
    {
      key: 'account_expiration_notice_time',
      value: ["1天", "7天"],
    },
    {
      key: 'account_expiration_notice_method',
      value: "邮箱",
    },
  ],
  passwordRule: [
    {
      key: "password_length",
      value: "8-32位",
    },
    {
      key: "max_trail_times_list",
      value: "3次",
    },
    {
      key: "password_must_includes",
      value: ["小写字母", "大写字母", "数字"],
    },
    {
      key: "auto_unlock_seconds",
      value: "600秒",
    },
    {
      key: "password_rult_length",
      value: ["连续8位出现", "连续字母序"],
    },
    {
      key: "frozen",
      value: "连续180天未登录自动冻结",
    },
    {
      key: "password_valid_days_list",
      value: "一个月",
    },
  ],
  passwordSetting: [
    {
      key: 'init_password_method',
      value: "固定",
    },
    {
      key: 'init_password_notice_method',
      value: ["邮箱", "短信"],
    },
    {
      key: 'password_expiration_notice_time',
      value: ["1天", "7天", "15天"],
    },
    {
      key: 'password_expiration_notice_method',
      value: ["邮箱"],
    },
  ],
});

const handleClickEdit = () => {
  router.push({
    name: "newLocal",
  });
}
</script>

<style lang="less" scoped>
@import "@/css/tenantViewStyle.less";
</style>
