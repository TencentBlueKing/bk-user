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
import intlTelInput from 'intl-tel-input';
import 'intl-tel-input/build/js/utils';

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
          showFlags: true, // 显示国旗
          separateDialCode: true, // 国旗右边显示区号
          nationalMode: false, // 不显示本地号码格式
          formatOnDisplay: false, // 不自动加空格或横线
          autoPlaceholder: 'aggressive', // 自动显示占位符
          placeholderNumberType: 'MOBILE', // 手机号码
          initialCountry: this.item.iso_code,
          preferredCountries: ['cn', 'us', 'gb'], // 优先显示的国家 中美英
          onlyCountries: [], // 空数组表示显示所有国家
          i18n: {
            searchPlaceholder: '搜索', // 修改搜索框为中文
          },
        });
        // iti.setCountry("gb")
        // iti.setNumber("+447733123456")
        // iti.getNumber() 带 country code 的号码
        // 手动将三个国家置顶
        this.$nextTick(() => {
          this.reorderCountryList();
        });
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
    reorderCountryList() {
      // 获取国家列表容器
      const countryList = this.$refs.intlTelInput?.parentElement?.querySelector('.iti__country-list');
      if (!countryList) return;
      // 优先显示的国家代码
      const priorityCountries = ['cn', 'us', 'gb'];
      // 获取所有国家项
      const countryItems = Array.from(countryList.querySelectorAll('.iti__country'));
      // 分离优先国家和其他国家
      const priorityItems = [];
      const otherItems = [];
      countryItems.forEach((item) => {
        const countryCode = item.getAttribute('data-country-code');
        if (priorityCountries.includes(countryCode)) {
          priorityItems.push(item);
        } else {
          otherItems.push(item);
        }
      });
      // 按优先级排序优先国家
      priorityItems.sort((a, b) => {
        const codeA = a.getAttribute('data-country-code');
        const codeB = b.getAttribute('data-country-code');
        return priorityCountries.indexOf(codeA) - priorityCountries.indexOf(codeB);
      });
      // 创建分隔线
      const divider = document.createElement('li');
      divider.className = 'iti__divider';
      divider.setAttribute('role', 'separator');
      // 清空列表
      countryList.innerHTML = '';
      // 重新添加：优先国家 + 分隔线 + 其他国家
      priorityItems.forEach(item => countryList.appendChild(item));
      countryList.appendChild(divider);
      otherItems.forEach(item => countryList.appendChild(item));
    },
    handleInitError() {
      const input = this.$refs.intlTelInput;
      // eslint-disable-next-line vue/no-mutating-props
      this.item.iso_code = 'cn';
      this.iti = intlTelInput(input, {
        allowDropdown: true,
        showFlags: true, // 显示国旗
        separateDialCode: true, // 国旗右边显示区号
        nationalMode: false, // 不显示本地号码格式
        formatOnDisplay: false, // 不自动加空格或横线
        autoPlaceholder: 'aggressive', // 自动显示占位符
        placeholderNumberType: 'MOBILE', // 手机号码
        initialCountry: 'cn', // 初始国家
        preferredCountries: ['cn', 'us', 'gb'], // 优先显示的国家 中美英
        onlyCountries: [], // 空数组表示显示所有国家
        i18n: {
          searchPlaceholder: '搜索', // 修改搜索框为中文
        },
      });
      // 手动将三个国家置顶
      this.$nextTick(() => {
        this.reorderCountryList();
      });
    },
    // 失焦验证
    verifyInput(item) {
      if (item.value === '') {
        return this.$emit('phone', true);
      }
      if (item.value.includes('****')) {
        return true;
      }
      let validation = false;
      const currentIsoCode = this.iti && this.iti.getSelectedCountryData()
        ? this.iti.getSelectedCountryData().iso2
        : item.iso_code;
      if (currentIsoCode && currentIsoCode.toLowerCase() === 'cn') {
        validation = /^1[3-9]\d{9}$/.test(item.value.replace(/\s+/g, ''));
      } else {
        validation = this.iti && typeof this.iti.isValidNumber === 'function'
          ? this.iti.isValidNumber()
          : false;
      }
      !validation && (item.isError = true);
      return !validation;
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

    .iti__divider {
      padding-bottom: 5px;
      margin-bottom: 5px;
      border-bottom: 1px solid #ccc;
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
  padding: 0 30px 0 52px;

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
