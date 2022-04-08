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
  <div class="input-text">
    <!-- eslint-disable vue/no-mutating-props -->
    <input
      type="text"
      ref="intlTelInput"
      :disabled="editStatus && !item.editable"
      :class="['select-text', { 'input-error': item.isError }]"
      v-model="item.value"
      :placeholder="$t('请输入手机号')"
      @blur="verifyInput(item)"
      @focus="hiddenVerify(item)" />
    <i class="icon icon-user-exclamation-circle-shape" v-if="item.isError"></i>
    <p class="hint" v-show="item.isError">
      <i class="arrow"></i>
      <i class="icon-user-exclamation-circle-shape"></i>
      <span class="text">{{$t('请填写正确')}}{{item.name}}</span>
    </p>
  </div>
</template>
<script>
import intlTelInput from 'intl-tel-input/build/js/intlTelInput.min';
import utils from 'intl-tel-input/build/js/utils';

export default {
  props: {
    item: {
      type: Object,
      required: true,
    },
    editStatus: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      iti: null,
    };
  },
  mounted() {
    if (!this.item.iso_code) {
      // eslint-disable-next-line vue/no-mutating-props
      this.item.iso_code = 'cn';
    }
    this.initIntlTel();
  },
  beforeDestroy() {
    this.iti && this.iti.destroy();
  },
  methods: {
    initIntlTel() {
      const input = this.$refs.intlTelInput;
      try {
        this.iti = intlTelInput(input, {
          allowDropdown: true,
          separateDialCode: true, // 国旗右边显示区号
          formatOnDisplay: false, // 不自动加空格或横线
          placeholderNumberType: 'MOBILE', // 手机号码
          initialCountry: this.item.iso_code, // 初始国家
          preferredCountries: ['cn', 'us', 'gb'], // 偏好国家 中美英
          utilsScript: utils,
        });
        // iti.setCountry("gb")
        // iti.setNumber("+447733123456")
        // iti.getNumber() 带 country code 的号码
      } catch (e) {
        console.warn('手机号国际化初始化失败，默认改为中国', e);
        this.handleInitError();
      }
      input.addEventListener('countrychange', () => {
        const countryData = this.iti.getSelectedCountryData(); // iso2(eg: cn) dialCode(eg: 86)
        // eslint-disable-next-line vue/no-mutating-props
        this.item.iso_code = countryData.iso2;
      });
    },
    handleInitError() {
      const input = this.$refs.intlTelInput;
      // eslint-disable-next-line vue/no-mutating-props
      this.item.iso_code = 'cn';
      this.iti = intlTelInput(input, {
        allowDropdown: true,
        separateDialCode: true, // 国旗右边显示区号
        formatOnDisplay: false, // 不自动加空格或横线
        placeholderNumberType: 'MOBILE', // 手机号码
        initialCountry: 'cn', // 初始国家
        preferredCountries: ['cn', 'us', 'gb'], // 偏好国家 中美英
        utilsScript: utils,
      });
    },
    // 失焦验证
    verifyInput(item) {
      const validation = item.iso_code === 'cn'
        ? /^1[3-9]\d{9}$/.test(item.value)
        : this.iti.isValidNumber();
      !validation && (item.isError = true);
    },
    // 获焦去掉标红
    hiddenVerify(item) {
      item.isError = false;
    },
  },
};
</script>

<style lang="scss">
    @import '../../../../node_modules/intl-tel-input/build/css/intlTelInput.min.css';

    .iti__flag {
      background-image: url('../../../../node_modules/intl-tel-input/build/img/flags.png');
    }

    @media (min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
      .iti__flag {
        background-image: url('../../../../node_modules/intl-tel-input/build/img/flags@2x.png');
      }
    }

    .iti.iti--allow-dropdown {
      width: 100%;
    }
</style>

<style lang="scss" scoped>
.input-text {
  position: relative;
}

.select-text {
  display: block;
  padding: 0 30px 0 12px;

  &.active {
    color: #63656e !important;
  }

  &.disable {
    background-color: #fafbfd;
    cursor: not-allowed;
  }
}

.icon-user-exclamation-circle-shape {
  position: absolute;
  right: 10px;
  top: 8px;
  font-size: 16px;
  color: #ea3636;
}

.hint {
  padding: 10px;
  position: absolute;
  top: -42px;
  right: 0;
  color: #fff;
  font-size: 0;
  border-radius: 4px;
  background: #000;

  &.hint-top {
    top: -56px;
  }

  &.chang-en {
    width: 108%;
    right: -8px;

    .arrow {
      right: 20px;
    }
  }

  .arrow {
    position: absolute;
    bottom: -2px;
    right: 14px;
    width: 6px;
    height: 6px;
    border-top: 1px solid #000;
    border-left: 1px solid #000;
    transform: rotate(45deg);
    z-index: 10;
    background: #000;
  }

  .text,
  .icon-user-exclamation-circle-shape {
    display: inline-block;
    vertical-align: middle;
    font-size: 12px;
  }

  .icon-user-exclamation-circle-shape {
    font-size: 16px;
    margin-right: 10px;
    position: relative;
    right: 0;
    top: 0;
    color: #fff;
  }
}
</style>
