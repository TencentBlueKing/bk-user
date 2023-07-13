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
    <bk-input
      v-if="item.key === 'username' || item.key === 'display_name'"
      :maxlength="32"
      :disabled="editStatus && !item.editable"
      :placeholder="placeholderText"
      :show-word-limit="true"
      :class="{ 'input-error': item.isError }"
      v-model="item.value"
      @blur="verifyInput(item)"
      @focus="handleFocus">
    </bk-input>
    <bk-input
      v-else
      :type="inputType"
      :disabled="editStatus && !item.editable"
      :placeholder="inputType === 'number' ? $t('请输入数字') : item.holder"
      :class="{ 'input-error': item.isError }"
      :max="numberRule.max"
      :min="numberRule.min"
      :maxlength="numberRule.maxlength"
      v-model="item.value"
      @focus="handleFocus" />
  </div>
</template>

<script>
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
  computed: {
    inputType() {
      return this.item.type === 'string' ? 'text' : 'number';
    },
    placeholderText() {
      return this.item.key === 'username' ? this.$t('字母、数字、下划线(_)、点(.)、减号(-)字符组成，以字母或数字开头') : this.$t('请输入');
    },
    numberRule() {
      let rules = {};
      if (this.item.type === 'number') {
        rules = {
          max: 999999999999999,
          min: -999999999999999,
          maxlength: 15,
        };
      }
      return rules;
    },
  },
  methods: {
    verifyInput(item) {
      item.value = this.$xssVerification(item.value);
    },
    handleFocus() {
      window.changeInput = true;
    },
  },
};
</script>

<style lang="scss" scoped>
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  appearance: none;
}

.input-text {
  position: relative;
  .text {
    color: #ea3636;
  }
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

  &[disabled] {
    color: #c4c6cc;
    background-color: #fafbfd !important;
    cursor: not-allowed;
    border-color: #dcdee5 !important;
  }
}
</style>
