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
  <div class="setting-wrapper clearfix">
    <div class="setting-left">
      <a
        href="javascript:void(0);"
        :class="['nav-item', { 'active': index === curIndex }]"
        v-for="(item, index) in settingList" :key="index"
        @click="changTab(index)">
        {{item}}
      </a>
    </div>
    <div class="setting-right">
      <FieldsSetting v-show="curIndex === 0" />
      <DoubleFactor v-show="curIndex === 1" />
    </div>
  </div>
</template>

<script>
import FieldsSetting from './FieldsSetting';
import DoubleFactor from './DoubleFactor.vue';

export default {
  name: 'SettingIndex',
  components: {
    FieldsSetting,
    DoubleFactor,
  },
  data() {
    return {
      isNav: false,
      settingList: [this.$t('用户字段设置'), this.$t('双因子认证')],
      curIndex: 0,
    };
  },
  methods: {
    changTab(index) {
      this.curIndex = index;
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../scss/mixins/clearfix.scss';

  .setting-wrapper {
    height: 100%;
    border: 1px solid #dcdee5;
  }

  .setting-left {
    padding-top: 14px;
    float: left;
    width: 220px;
    height: 100%;
    background: #fafbfd;
    border-right: 1px solid #dcdee5;

    .nav-item {
      padding: 11px 0 11px 30px;
      display: block;
      font-size: 14px;
      font-weight: 400;
      color: rgba(99, 101, 110, 1);
      line-height: 20px;

      &.active {
        color: rgba(58, 132, 255, 1);
        background: #e1ecff;
      }
    }
  }

  .setting-right {
    float: left;
    width: calc(100% - 220px);
    min-width: 958px;
    height: 100%;
  }
</style>
