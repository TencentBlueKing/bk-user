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
  <div class="reset-wrapper">
    <div class="reset-box-content" :class="{ 'before-set': hasSet === false, 'has-set': hasSet === true }">
      <div class="login-heard">
        <img src="../../images/svg/logo_cn.svg" alt="蓝鲸智云" width="160">
      </div>
      <div class="login-content">
        <div class="reset-pw">
          <div class="reset-content" v-if="hasSet === false">
            <h4 class="common-title">{{$t('设置新密码')}}</h4>
            <p :class="['text', isError && 'show-error-info']">{{$t('请输入新密码进行密码重设')}}</p>
            <p class="error-text" v-if="isError">
              <i class="icon icon-user-exclamation-circle-shape"></i>
              <span class="text">{{errorText}}</span>
            </p>
            <input type="password"
                   :class="['select-text', { 'input-error': isError }]"
                   :placeholder="$t('请输入新密码')"
                   v-model="password"
                   @focus="isError = false" />
            <input type="password"
                   :class="['select-text', { 'input-error': isError }]"
                   :placeholder="$t('请再次确认新密码')"
                   v-model="confirmPassword"
                   @focus="isError = false" />
            <bk-button theme="primary" class="submit"
                       :disabled="!password || !confirmPassword" @click="handlePush">{{$t('提交')}}</bk-button>
          </div>
          <div class="reset-content" v-if="hasSet === true">
            <h4 class="common-title">{{$t('密码修改成功')}}</h4>
            <p class="text" style="margin: 0 0 18px 0">{{$t('您现在可以用新密码登录了')}}</p>
            <bk-button theme="primary" class="submit" @click="register">{{$t('登录账户')}}</bk-button>
          </div>
        </div>
      </div>
    </div>
    <div class="bk-open-set-password">
      <bk-dialog width="440"
                 header-position="left"
                 v-model="successDialog.isShow"
                 :title="successDialog.title"
                 @confirm="register">
        <div style="min-height: 20px;">
          <p class="text" style="margin: 0 0 18px 0;">{{$t('点击确定后将跳到蓝鲸登录页面')}}</p>
        </div>
      </bk-dialog>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      // 密码是否已经设置成功
      hasSet: false,
      password: '',
      confirmPassword: '',
      isError: false,
      errorText: this.$t('两次输入的密码不一致，请重新输入'),
      successDialog: {
        isShow: false,
        title: this.$t('密码修改成功'),
      },
    };
  },
  // mounted () {
  //     this.initToken()
  // },
  methods: {
    // async initToken () {
    //     try {
    //         await this.$store.dispatch('password/getToken', this.$route.query.token)
    //     } catch (e) {
    //         this.$bkMessage({
    //             message: e.message,
    //             theme: 'warning',
    //             delay: 3000,
    //             onClose: () => {
    //                 this.$router.push({
    //                     name: 'pwReset'
    //                 })
    //             }
    //         })
    //     }
    // },
    async handlePush() {
      try {
        // 确认密码是否一致
        if (this.password !== this.confirmPassword) {
          this.isError = true;
          return;
        }
        const sureParam = {
          token: this.$route.query.token,
          password: this.password.trim(),
        };
        await this.$store.dispatch('password/setByToken', sureParam);
        this.successDialog.isShow = true;
        this.hasSet = true;
      } catch (e) {
        console.warn(e);
      }
    },
    register() {
      window.location.href = window.login_url;
    },
  },
};
</script>

<style lang="scss" scoped>
.reset-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #fafbfd;
  z-index: 1000;
}

.reset-box-content {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  margin: auto;
  width: 400px;
  background: #fff;
  border-radius: 2px;
  box-shadow: 0 0 7px 3px rgba(0, 0, 0, .1);

  &.before-set {
    max-height: 425px;
  }

  &.has-set {
    max-height: 261px;
  }
}

.login-heard {
  width: 400px;
  height: 100px;
  line-height: 100px;
  text-align: center;
  background: #192948;
  border-radius: 2px 2px 0 0;

  img {
    vertical-align: middle;
  }
}

.login-content {
  padding: 0 24px;
  font-size: 14px;
}

.common-title {
  margin: 20px 0 6px 0;
  font-size: 20px;
  font-weight: 400;
  color: rgba(49, 50, 56, 1);
  line-height: 28px;
}

.select-text {
  padding-left: 12px;

  &::input-placeholder {
    color: rgba(195, 205, 215, 1);
  }
}

.submit {
  width: 100%;
}
// 重置密码
.reset-content {
  .text {
    font-size: 14px;
    font-weight: 400;
    color: rgba(99, 101, 110, 1);
    line-height: 20px;
    margin: 10px 0 20px;

    &.show-error-info {
      margin-bottom: 10px;
    }
  }

  .select-text {
    margin-bottom: 20px;
  }
}
// 错误提示
.error-text {
  margin-bottom: 10px;
  color: #ea3636;
  font-size: 14px;

  .text {
    color: #ea3636;
  }

  .icon {
    color: #ea3636;
  }
}
</style>
