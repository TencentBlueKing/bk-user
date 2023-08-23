<template>
  <div class="login-setting-content user-scroll-y">
    <div class="setting-item">
      <p class="item-title">登录方式设置</p>
      <bk-form class="setting-form" form-type="vertical">
        <bk-form-item label="基本登录" description="至少选择一种默认方式">
          <bk-checkbox-group>
            <bk-checkbox
              class="hover-checkbox"
              v-for="item in state.basicLogin"
              :key="item.value"
              :label="item.name"
            >
              {{ item.name }}
              <bk-tag theme="info" v-if="item.default">默认</bk-tag>
            </bk-checkbox>
          </bk-checkbox-group>
        </bk-form-item>
        <bk-form-item label="个人社交账号登录">
          <bk-checkbox-group>
            <bk-checkbox
              v-for="item in state.accountLogin"
              :key="item.value"
              :label="item.name"
            >
              {{ item.name }}
            </bk-checkbox>
          </bk-checkbox-group>
        </bk-form-item>
      </bk-form>
    </div>
    <div class="setting-item">
      <p class="item-title">MFA设置</p>
      <bk-form class="setting-form" form-type="vertical">
        <bk-form-item label="MFA认证方式">
          <bk-checkbox-group>
            <bk-checkbox label="手机号+验证码" />
            <bk-checkbox label="邮箱+验证码" />
          </bk-checkbox-group>
        </bk-form-item>
        <div class="item-flex">
          <bk-form-item label="强制开启MFA" description="强制开启MFA">
            <bk-switcher v-model="state.openMFA" theme="primary" size="large" />
          </bk-form-item>
          <bk-form-item label="启用范围">
            <i class="user-icon icon-plus-fill"> 添加范围</i>
          </bk-form-item>
        </div>
        <div class="item-flex">
          <bk-form-item label="动态信任策略" description="动态信任策略">
            <bk-switcher v-model="state.openMFA" theme="primary" size="large" />
          </bk-form-item>
          <bk-form-item label="信任天数">
            <bk-radio-group v-model="state.days">
              <bk-radio-button
                v-for="item in state.daysList"
                :key="item.value"
                :label="item.name"
              />
            </bk-radio-group>
          </bk-form-item>
        </div>
      </bk-form>
    </div>
    <div class="setting-btn">
      <bk-button theme="primary" class="mr8">保存</bk-button>
      <bk-button>重置</bk-button>
    </div>
  </div>
</template>

<script setup lang="tsx">
import { reactive } from 'vue';

const state = reactive({
  basicLogin: [
    { name: '账密登录（本地）', value: '1', default: false },
    { name: 'OpenLDAP登录', value: '2', default: false },
    { name: 'MAD登录', value: '3', default: false },
    { name: '企业微信登录', value: '4', default: false },
    { name: '手机号+验证码', value: '5', default: false },
    { name: '邮箱+验证码', value: '6', default: false },
  ],
  accountLogin: [
    { name: '微信', value: 'weixin' },
    { name: 'QQ', value: 'qq' },
    { name: 'Google', value: 'google' },
  ],
  openMFA: true,
  days: '3天',
  daysList: [
    { name: '3天', value: 3 },
    { name: '7天', value: 7 },
    { name: '14天', value: 14 },
    { name: '30天', value: 30 },
    { name: '60天', value: 60 },
  ],
});
</script>

<style lang="less" scoped>
.login-setting-content {
  height: calc(100vh - 104px);
  padding: 24px;

  .setting-item {
    margin-bottom: 16px;
    background: #fff;
    border-radius: 2px;
    box-shadow: 0 2px 4px 0 #1919290d;

    .item-title {
      padding: 16px 0 16px 24px;
      font-size: 14px;
      font-weight: 700;
    }

    .setting-form {
      margin-left: 64px;

      .item-flex {
        display: flex;

        .bk-form-item {
          width: 145px;

          .icon-plus-fill {
            font-size: 14px;
            color: #3a84ff;
          }
        }
      }
    }
  }

  .setting-btn {
    button {
      width: 88px;
    }
  }
}
</style>
