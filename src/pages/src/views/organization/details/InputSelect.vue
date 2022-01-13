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
    <bk-select
      v-model="item.value"
      font-size="14"
      class="member-infor-king-select"
      :clearable="!item.require"
      :multiple="item.type === 'multi_enum'"
      :disabled="editStatus && !item.editable"
      :ext-cls="item.isError ? 'input-error' : ''"
      @change="verifyInput(item)">
      <bk-option
        v-for="(option, index) in item.options"
        :key="index"
        :id="option.id"
        :name="option.value">
      </bk-option>
    </bk-select>
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
  methods: {
    verifyInput(item) {
      if (item.type === 'one_enum') {
        item.isError = !!(item.require && (!item.value && item.value !== 0));
      } else {
        item.isError = !!(item.require && !item.value.length);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.input-text {
  position: relative;

  .input-error {
    border: 1px solid #ea3636;
  }
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
  top: 10px;
  font-size: 16px;
  color: #ea3636;
}
</style>
