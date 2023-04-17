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
    <p class="error-text" v-show="item.isError && item.value">
      {{$t('请填写正确的')}}{{item.name}}
    </p>
    <p class="error-text" v-show="item.isError && !item.value">
      {{$t('必填项')}}
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
      if (item === '') {
        return this.$emit('phone', true);
      }
      const validation = item.iso_code === 'cn'
        ? /^1[3-9]\d{9}$/.test(item.value)
        : this.iti.isValidNumber();
      !validation && (item.isError = true);
    },
    // 获焦去掉标红
    hiddenVerify(item) {
      item.isError = false;
      window.changeInput = true;
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

input::-webkit-input-placeholder {
  color : #c4c6cc;
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

.error-text {
  font-size: 12px;
  color: #ea3636;
  line-height: 18px;
  margin: 2px 0 0;
}

.input-error {
  color: #ff5656;
}
</style>
