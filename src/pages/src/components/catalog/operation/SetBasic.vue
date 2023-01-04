<!--
  - TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
  - Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
  - Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at http://opensource.org/licenses/MIT
  - Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
  - an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
  - specific language governing permissions and limitations under the License.
  -->
<template>
  <div v-if="basicInfo" class="catalog-setting-step set-basic">
    <!-- 目录名 -->
    <!-- eslint-disable vue/no-mutating-props -->
    <div class="name-container">
      <CommonInput
        keyword="display_name"
        :info="basicInfo"
        :input-bus="inputBus"
        :title="$t('目录名')"
        :is-need="true"
        @hasError="handleHasError" />
      <div class="check-container">
        <bk-checkbox v-model="basicInfo.activated" class="king-checkbox">
          {{$t('开启账号登录')}}
        </bk-checkbox>
        <i class="hint-message icon-user--l" v-bk-tooltips="$t('启用目录提示')"></i>
      </div>
    </div>

    <!-- 登录域 -->
    <input type="text" class="hidden-password-input">
    <input type="password" class="hidden-password-input">
    <CommonInput
      keyword="domain"
      :info="basicInfo"
      :input-bus="inputBus"
      :title="$t('登录域')"
      :is-need="true"
      :error-text="$t('登录域错误')"
      :disabled="type === 'set'"
      :description="$t('登录域描述')"
      @hasError="handleHasError" />

    <!-- 新增用户目录 -->
    <div class="save-setting-buttons" v-if="type === 'add'">
      <bk-button @click="$emit('cancel')">
        {{$t('取消')}}
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

export default {
  components: {
    CommonInput,
  },
  props: {
    // add 增加目录 set 修改目录设置
    type: {
      type: String,
      required: true,
    },
    basicInfo: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      hasError: false,
      inputBus: new Vue(),
    };
  },
  methods: {
    handleNext() {
      this.validate() && this.$emit('next');
    },
    handleSave() {
      this.validate() && this.$emit('saveBasic');
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
    },
  },
};
</script>

<style lang="scss" scoped>
#catalog .catalog-setting-step.set-basic {
  > .name-container {
    display: flex;

    > .check-container {
      display: flex;
      align-items: center;
      height: 32px;
      margin-top: 27px;
      margin-bottom: 17px;

      > .king-checkbox {
        height: 16px;
        line-height: 16px;
        vertical-align: center;
        margin-left: 23px;
      }

      > .hint-message {
        font-size: 14px;
        margin-left: 3px;
        outline: none;
      }
    }
  }
}
</style>
