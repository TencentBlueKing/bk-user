<!--
  - Tencent is pleased to support the open source community by making Bk-User 蓝鲸用户管理 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
  -
  - License for Bk-User 蓝鲸用户管理:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->
<template>
  <div v-if="connectionInfo" class="catalog-setting-step set-connection">

    <!-- 连接地址 -->
    <CommonInput
      keyword="connection_url"
      :info="defaultConnection"
      :input-bus="inputBus"
      :title="$t('连接地址')"
      :is-need="true"
      :placeholder="`${$t('例如')}：ldap://127.0.0.1:389`"
      @hasError="handleHasError"
      @updateUrl="updateUrl" />

    <!-- SSL加密方式 -->
    <div class="info-container">
      <div class="title-container">
        <h4 class="title">{{$t('SSL加密方式')}}</h4>
      </div>
      <bk-select
        v-model="defaultConnection.ssl_encryption"
        :clearable="false"
        style="width: 360px;"
        @toggle="toggleSelect">
        <bk-option v-for="option in sslEncryptionChoices" :key="option" :id="option" :name="option"></bk-option>
      </bk-select>
      <p v-show="sslError" class="error-text">{{$t('请选择正确的加密方式')}}</p>
    </div>

    <!-- 超时设置 -->
    <CommonInput
      keyword="timeout_setting"
      input-type="number"
      :info="defaultConnection"
      :input-bus="inputBus"
      :title="$t('超时设置')"
      :append="$t('秒')"
      :is-need="true"
      :input-width="240"
      @hasError="handleHasError" />

    <!-- 拉取周期 -->
    <CommonInput
      keyword="pull_cycle"
      input-type="number"
      :info="defaultConnection"
      :input-bus="inputBus"
      :title="$t('拉取周期')"
      :description="$t('最小拉取周期为')"
      :error-text="$t('请输入正确的拉取周期')"
      :append="$t('秒')"
      :is-need="true"
      :input-width="240"
      @hasError="handleHasError" />

    <!-- 根目录 -->
    <CommonInput
      keyword="base_dn"
      :info="defaultConnection"
      :input-bus="inputBus"
      :title="$t('根目录（Base DN）')"
      :is-need="true"
      @hasError="handleHasError" />

    <!-- 用户名 -->
    <CommonInput
      keyword="user"
      :info="defaultConnection"
      :input-bus="inputBus"
      :title="$t('用户名（Username）')"
      :is-need="true"
      @hasError="handleHasError" />

    <!-- 密码 -->
    <input type="text" class="hidden-password-input">
    <input type="password" class="hidden-password-input">
    <CommonInput
      keyword="password"
      input-type="password"
      :info="defaultConnection"
      :input-bus="inputBus"
      :title="$t('密码（Password）')"
      :is-need="true"
      @hasError="handleHasError" />

    <!-- 测试连接 -->
    <TestConnection :test-info="testInfo" />

    <!-- 新增用户目录 -->
    <div class="save-setting-buttons" v-if="type === 'add'">
      <bk-button @click="$emit('cancel')">
        {{$t('返回列表')}}
      </bk-button>
      <bk-button @click="$emit('previous')" class="king-button">
        {{$t('上一步')}}
      </bk-button>
      <bk-button theme="primary" @click="handleNext" class="king-button">
        {{$t('下一步')}}
      </bk-button>
    </div>

    <!-- 编辑用户目录设置 -->
    <div class="save-setting-buttons" v-if="type === 'set'">
      <bk-button theme="primary" @click="handleSave">
        {{$t('保存')}}
      </bk-button>
      <bk-button @click="$emit('cancel')" class="king-button">
        {{$t('取消')}}
      </bk-button>
    </div>
  </div>
</template>

<script>
import Vue from 'vue';
import CommonInput from '@/components/catalog/operation/CommonInput';
import TestConnection from '@/components/catalog/operation/TestConnection';

export default {
  components: {
    CommonInput,
    TestConnection,
  },
  props: {
    // add 增加目录 set 修改目录设置
    type: {
      type: String,
      required: true,
    },
    connectionInfo: {
      type: Object,
      default: null,
    },
    catalogId: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      // 表单验证是否有错误
      hasError: false,
      inputBus: new Vue(),
      sslError: false,
    };
  },
  computed: {
    // default region
    defaultConnection() {
      return this.connectionInfo ? this.connectionInfo.default : null;
    },
    // ssl_encryption choices
    sslEncryptionChoices() {
      return this.$store.state.catalog.choices.ssl_encryption;
    },
    testInfo() {
      return {
        action: 'catalog/ajaxTestConnection',
        id: this.catalogId,
        data: this.connectionInfo,
      };
    },
  },
  methods: {
    handleNext() {
      this.validate() && this.$emit('next');
    },
    handleSave() {
      this.validate() && this.$emit('saveConnection');
    },
    handleHasError() {
      this.hasError = true;
    },
    validate() {
      // 表单验证
      this.hasError = false;
      // 在 CommonInput 组件里面验证必填的值是否有值
      this.inputBus.$emit('validateCatalogInfo');
      if (this.hasError === false) {
        return true;
      }
      this.$nextTick(() => {
        const els = this.$el.getElementsByClassName('error');
        if (els.length) {
          els[0].scrollIntoView();
        }
      });
      return false;
    },
    updateUrl(val) {
      if (val === 'ldaps' && this.defaultConnection.ssl_encryption === '无') {
        this.sslError = true;
        this.hasError = true;
      } else if (val === 'ldap' && this.defaultConnection.ssl_encryption === 'SSL') {
        this.sslError = true;
        this.hasError = true;
      } else {
        this.sslError = false;
      }
    },
    toggleSelect() {
      this.sslError = false;
    },
  },
};
</script>

<style lang="scss" scoped>
#catalog .catalog-setting-step.set-connection {
  .group-text {
    padding: 8px 10px;
    line-height: 14px;
    background: #fafbfd;
  }
}
</style>
