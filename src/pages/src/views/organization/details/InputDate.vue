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
  <div :class="['input-text', { 'mark-red': item.isError }]">
    <bk-date-picker
      font-size="14"
      class="king-date-picker"
      :placeholder="$t('请选择日期')"
      :value="item.value"
      :disabled="editStatus && !item.editable"
      @change="changeDate">
    </bk-date-picker>
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
  methods: {
    changeDate(date) {
      // eslint-disable-next-line vue/no-mutating-props
      this.item.value = date;
      // eslint-disable-next-line vue/no-mutating-props
      this.item.isError = false;
    },
  },
};
</script>

<style lang="scss">
.input-text .king-date-picker {
  width: 100%;
}

.mark-red .king-date-picker input {
  border: 1px solid #ea3636;
}
</style>

<style lang="scss" scoped>
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
