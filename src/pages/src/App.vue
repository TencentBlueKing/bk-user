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
  <div id="app">
    <Header v-if="showHeader" @reloadRouter="routerKey += 1" />
    <main class="main-content">
      <router-view :key="routerKey" />
      <KingLoading v-show="initLoading"></KingLoading>
      <NoAuthority v-if="noAuthData" :no-auth-data="noAuthData" @reloadRouter="routerKey += 1" />
    </main>
    <Login v-if="loginData" :login-data="loginData" />
    <Footer />
  </div>
</template>

<script>
import Header from './Header';
import Footer from './Footer';
import Login from '@/components/login';
import NoAuthority from '@/components/authority/NoAuthority';
import KingLoading from '@/components/KingLoading';

export default {
  name: 'App',
  components: {
    Header,
    Login,
    NoAuthority,
    KingLoading,
    Footer,
  },
  data() {
    return {
      showHeader: true,
      loginData: null,
      routerKey: 0,
    };
  },
  computed: {
    initLoading() {
      return this.$store.state.initLoading;
    },
    noAuthData() {
      return this.$store.state.noAuthData;
    },
  },
  created() {
    const platform = window.navigator.platform.toLowerCase();
    if (platform.indexOf('win') === 0) {
      document.body.style['font-family'] = 'Microsoft Yahei, pingFang-SC-Regular, Helvetica, Aria, sans-serif';
    } else {
      document.body.style['font-family'] = 'pingFang-SC-Regular, Microsoft Yahei, Helvetica, Aria, sans-serif';
    }
    // 修改、重置密码页面不渲染 NavHeader
    if (window.location.pathname.indexOf('password') !== -1) {
      this.showHeader = false;
    }
    // 401 打开登录弹窗
    window.bus.$on('show-login-modal', (loginData) => {
      this.loginData = loginData;
    });
    window.bus.$on('close-login-modal', () => {
      this.loginData = null;
      setTimeout(() => {
        window.location.reload();
      }, 0);
    });
  },
};
</script>

<style lang="scss">
@import './scss/reset.scss';
@import './scss/svg-icon/style.css';
@import './scss/bk_icon_font/style.css';

html,
body,
#app {
  height: 100%;
  color: #737987;
  background-color: #fff;
}

// body {
  /*鼠标快速滚动 tips dom 会抖动*/
//   overflow-y: hidden;
// }

/*无权限时 v-cursor 样式*/
.cursor-element {
  width: 12px;
  height: 16px;
  background: url('./images/svg/cursor-lock.svg') no-repeat;
}

.clearfix::after {
  display: block;
  clear: both;
  content: '';
  font-size: 0;
  visibility: hidden;
}

.tips-word-break {
  word-break: break-all;
}

.main-content {
  position: relative;
  min-height: 500px;
  height: calc(100% - 130px);
  width: calc(100% - 188px);
  min-width: 1180px;
  margin: 0 auto;
}

.loading-cover {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 3000;
  opacity: 0;
  cursor: not-allowed;
}

.text-overflow-hidden {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hidden-password-input {
  position: fixed;
  left: -1000px;
  top: -1000px;
  z-index: -1000;
}
// bk.css hack
.bk-dialog-wrapper .bk-info-box .bk-dialog-sub-header .bk-dialog-header-inner {
  text-align: initial !important;
}
// bk-input error 公共样式
.king-input.error input {
  border: 1px solid #fe5c5c;
}
// bk-input 密码 icon 公共样式
.king-input .control-icon > .bk-icon {
  cursor: pointer;
}
// bk-input append 背景
.king-input .group-box.group-append {
  background: #fafbfd;
}

.king-input-search .icon-search {
  &:hover {
    color: #3b84ff;
    cursor: pointer;
  }
}
// input 公共class = select-text
.select-text {
  height: 32px;
  line-height: 32px;
  width: 100%;
  resize: none;
  outline: none;
  border: 1px solid #c4c6cc;
  border-radius: 2px;

  &:focus {
    border-color: #3c96ff !important;
  }

  &.input-error {
    border: 1px solid #ea3636;
  }
}
// 设置密码的弹窗样式
.bk-open-set-password {
  .icon-close {
    display: none;
  }

  .bk-dialog-btn-cancel {
    display: none;
  }
}
// 单选框公共class=checkbox
.king-checkbox input[type=checkbox] {
  display: inline-block;
  width: 18px;
  height: 18px;
  outline: none;
  cursor: pointer;
  vertical-align: middle;
  background-image: url(./images/icon.png);
  background-position: 0 -62px;
  appearance: none;
  margin: 0 5px 0 0;
}

.king-checkbox input[type=checkbox]:checked {
  background-position: -33px -62px
}

.king-checkbox input[type=checkbox]:checked[disabled] {
  color: #ccc;
  background-position: -99px -62px
}

.king-checkbox input[type=checkbox][disabled] {
  background-position: -66px -62px;
  cursor: default
}

.king-checkbox input[type=checkbox][disabled] + .bk-checkbox-text {
  color: #ccc;
  cursor: default
}

.king-checkbox.king-checkbox-small input[type=checkbox] {
  width: 14px;
  height: 14px;
  background-position: 0 -95px
}

.king-checkbox.king-checkbox-small input[type=checkbox][disabled] {
  background-position: -66px -95px
}

.king-checkbox.king-checkbox-small input[type=checkbox]:checked {
  background-position: -33px -95px
}

.king-checkbox.king-checkbox-small input[type=checkbox]:checked[disabled] {
  background-position: -99px -95px
}
// 组织弹窗
.king-dialog.department-dialog .bk-dialog-body {
  padding: 0 !important;
}
// info 弹窗
.king-info.long-title .bk-dialog-header-inner {
  font-size: 20px;
  line-height: 28px;
  white-space: normal !important;
}
// 解决侧边栏组件样式问题
.king-sideslider .bk-sideslider-wrapper {
  > .bk-sideslider-content {
    height: calc(100vh - 60px);
  }
}
</style>
