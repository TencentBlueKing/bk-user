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
  <div class="test-connection">
    <div :class="{ button: true, loading: testLoading }"
         @click="testConnection">
      <span v-if="!testLoading">{{$t('测试连接')}}</span>
      <div v-if="testLoading" class="bk-loading" style="background: rgba(0, 0, 0, 0);transform: scale(.5)" @click.stop>
        <div class="bk-loading-wrapper">
          <div class="bk-loading1">
            <div class="point point1" style="background: #63656e;"></div>
            <div class="point point2" style="background: #63656e;"></div>
            <div class="point point3" style="background: #63656e;"></div>
            <div class="point point4" style="background: #63656e;"></div>
          </div>
        </div>
      </div>
    </div>
    <template v-if="testResult === 'success'">
      <div class="icon-container test-success">
        <i class="test-icon bk-icon icon-check-1"></i>
      </div>
      <span class="test-text">{{$t('连接测试成功')}}</span>
    </template>
    <template v-if="testResult === 'fail'">
      <div class="icon-container test-fail">
        <i class="test-icon bk-icon icon-close"></i>
      </div>
      <span class="test-text">{{testFailText}}</span>
    </template>
    <template v-if="testResult === 'invalid'">
      <div class="icon-container test-fail">
        <i class="test-icon bk-icon icon-close"></i>
      </div>
      <span class="test-text">{{$t('请先完善表单内容')}}</span>
    </template>
  </div>
</template>

<script>
export default {
  props: {
    testInfo: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      // 测试结果： '' 'success' 'fail'
      testResult: '',
      testFailText: '',
      testLoading: false,
    };
  },
  methods: {
    async testConnection() {
      if (this.$parent.validate() === true) {
        try {
          const { action, id, data } = this.testInfo;
          this.testLoading = true;
          this.testResult = '';
          await this.$store.dispatch(action, { id, data }, { globalError: false });
          this.testResult = 'success';
        } catch (e) {
          console.warn(e);
          this.testResult = 'fail';
          this.testFailText = e.message || this.$t('连接测试失败，请重试');
        } finally {
          this.testLoading = false;
        }
      } else {
        this.testResult = 'invalid';
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../../../scss/variable';

.test-connection {
  display: flex;
  align-items: center;
  margin-top: 20px;
  margin-bottom: 17px;
  font-size: 12px;
  line-height: 16px;

  > .button {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 110px;
    height: 32px;
    cursor: pointer;
    border-radius: 2px;
    background: #f0f1f5;
    transition: all .3s;

    &:hover:not(.loading) {
      color: $primaryColor;
      background: #e1ecff;
      transition: all .3s;
    }

    &.loading {
      cursor: not-allowed;
    }
  }

  > .icon-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 14px;
    height: 14px;
    margin: 0 7px 0 13px;
    border-radius: 7px;

    &.test-success {
      background: #2dcb56;
    }

    &.test-fail {
      background: #ea3636;
    }

    > .bk-icon {
      color: #fff;
      font-size: 12px;
      font-weight: bold;
    }
  }
}
</style>
