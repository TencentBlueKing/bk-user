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
  <!-- eslint-disable vue/no-mutating-props -->
  <div class="info-container">
    <div class="title-container">
      <h4 class="title">{{title}}</h4>
      <span v-if="isNeed" class="star">*</span>
      <div v-if="tips" class="tips">
        <span class="icon-user--l" v-bk-tooltips="tips"></span>
      </div>
    </div>
    <bk-input
      v-model="info[keyword]"
      :type="inputType"
      :style="{ width: inputWidth + 'px' }"
      :class="{ 'king-input': true, error: error }"
      :disabled="disabled"
      :placeholder="placeholder"
      @input="handleInput">
      <template v-if="append" slot="append">
        <div class="group-text">{{append}}</div>
      </template>
    </bk-input>
    <p v-show="error" class="error-text">{{errorText || $t('请输入') + title}}</p>
    <p v-show="!regError" class="error-text">{{$t('请输入合法的ldap地址')}}</p>
    <p v-if="description" class="description">{{description}}</p>
  </div>
</template>

<script>
export default {
  props: {
    info: {
      type: Object,
      required: true,
    },
    keyword: {
      type: String,
      required: true,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    inputBus: {
      type: Object,
      required: true,
    },
    // 输入框类型
    inputType: {
      type: String,
      default: 'text',
    },
    tips: {
      type: String,
      default: '',
    },
    // input 框 append slot
    append: {
      type: String,
      default: '',
    },
    // 标题
    title: {
      type: String,
      required: true,
    },
    // 输入框宽度
    inputWidth: {
      type: [String, Number],
      default: '360',
    },
    // 是否必填
    isNeed: {
      type: Boolean,
      default: false,
    },
    // 错误提示文本
    errorText: {
      type: String,
      default: '',
    },
    description: {
      type: String,
      default: '',
    },
    placeholder: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      error: false,
      regError: true,
    };
  },
  watch: {
    'info.connection_url'() {
      this.regError = true;
    },
  },
  mounted() {
    this.inputBus.$on('validateCatalogInfo', () => {
      // 提交时 trim
      const value = this.info[this.keyword];
      if (typeof value === 'string') {
        // eslint-disable-next-line vue/no-mutating-props
        this.info[this.keyword] = value.trim();
      }
      this.validate();
      this.regUrl();
    });
  },
  methods: {
    handleInput(value) {
      // 避免数值变成字符串
      if (this.inputType === 'number' && typeof value !== 'number') {
        // eslint-disable-next-line vue/no-mutating-props
        this.info[this.keyword] = value === '' ? null : Number(value);
      }
      this.validate();
      this.$emit('input', value);
    },
    validate() {
      if (this.isNeed) {
        const key = this.keyword;
        let value = this.info[this.keyword];
        if (typeof value === 'string') {
          value = value.trim();
        }
        let result;
        // 校验过程
        if (key === 'domain') {
          // 登录域校验规则
          const reg = /^[a-zA-Z0-9]/;
          // eslint-disable-next-line no-useless-escape
          const notReg = /[^a-zA-Z0-9.\-]/;
          result = value.match(reg) && !value.match(notReg) && value.length >= 1 && value.length <= 16;
        } else if (key === 'pull_cycle') {
          result = value >= 60 || value === 0;
        } else {
          // 简单校验是否存在值
          result = Boolean(value) || value === 0;
        }
        // 处理校验结果
        if (result) {
          this.error = false;
        } else {
          this.error = true;
          this.$emit('hasError');
        }
      }
    },
    regUrl() {
      const key = this.keyword;
      const value = this.info[this.keyword];
      if (key === 'connection_url') {
        const url = value.split('://')[0];
        this.$emit('updateUrl', url);
        // IP | IP + 端口号
        const ipReg = new RegExp(/^ldap(s)?:\/\/(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5]):([0-9]|[1-9]\d{1,3})$/);
        // 域名 | 域名 + 端口号
        const reg = new RegExp(/^ldap(s)?:\/\/(([a-zA-Z0-9]([-a-zA-Z0-9])*){1,62}\.)+[a-zA-Z]{2,62}(:([0-9]|[1-9]\d{1,3}))?$/);
        this.regError = reg.test(value) || ipReg.test(value);
        if (this.regError === false) {
          this.$emit('hasError');
        }
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../../../scss/variable';

.info-container {
  margin-bottom: 17px;

  > .title-container {
    display: flex;

    > .title {
      font-size: 14px;
      line-height: 19px;
      font-weight: normal;
      margin-bottom: 8px;
    }

    > .star {
      height: 19px;
      margin-left: 3px;
      font-size: 14px;
      vertical-align: middle;
      color: #fe5c5c;
    }

    > .tips {
      display: flex;
      align-items: center;
      height: 19px;
      margin-left: 2px;

      > .icon-user--l {
        font-size: 16px;
        outline: none;
      }
    }
  }

  > p.description {
    margin-top: 8px;
    font-size: 12px;
    line-height: 16px;
    color: $fontLight;
  }

  > p.error-text {
    font-size: 12px;
    color: #fe5c5c;
  }
}
</style>
