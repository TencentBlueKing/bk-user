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
      :type="inputType"
      :disabled="editStatus && !item.editable"
      :placeholder="inputType === 'number' ? $t('请输入数字') : item.holder"
      :class="['select-text', { 'input-error': item.isError }]"
      v-model="item.value"
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
  },
  methods: {
    // 失焦验证
    verifyInput(item) {
      item.value = this.$xssVerification(item.value);
      if (!item.require) {
        return;
      }
      // 验证账户： 字母、数字、下划线(_)、点(.)、减号(-)组合，长度1-32个字符，以字母或数字开头
      const usernameReg = /^[a-zA-Z0-9][0-9a-zA-Z_.-]{0,31}$/;
      // 验证姓名： 长度在1-32个字符
      const displayNameReg = /^.{1,32}$/;
      // 验证微信号
      const wxReg = /^[a-zA-Z]{1}[-_a-zA-Z0-9]{5,19}$/;
      // 验证邮箱
      // eslint-disable-next-line no-useless-escape
      const emailReg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.[A-Za-z]+$/;

      if ((item.key === 'username' && !usernameReg.test(item.value))
                    || (item.key === 'display_name' && !displayNameReg.test(item.value))
                    || (item.key === 'email' && !emailReg.test(item.value))
                    || (!item.value.length && item.key === 'wx_userid' && (!wxReg.test(item.value)))
                    || !item.value.length) {
        item.isError = true;
      }
    },
    // 获焦去掉标红
    hiddenVerify(item) {
      item.isError = false;
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
  background: rgba(0, 0, 0, .8);;

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
