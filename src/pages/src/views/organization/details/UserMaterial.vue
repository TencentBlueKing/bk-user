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
  <div :class="['look-user-info-wrapper',{ 'forbid-operate': isForbid }]">
    <div class="action-btn-wrapper" v-if="currentCategoryType === 'local'">
      <bk-button :disabled="isStatus" theme="primary" class="editor-btn" @click="editProfile">
        {{$t('编辑')}}
      </bk-button>
      <template v-if="!isStatus">
        <bk-button theme="default" :class="['editor-btn',{ 'forbidMark': isForbid }]" @click="changeStatus">
          {{!isForbid ? $t('禁用') : $t('启用')}}
        </bk-button>
        <template v-if="isAdmin">
          <bk-button theme="default" class="editor-btn" disabled>
            {{$t('删除')}}
          </bk-button>
        </template>
        <template v-else>
          <bk-button theme="default" :class="['editor-btn',{ 'forbidMark': isForbid }]" @click="deleteProfile">
            {{$t('删除')}}
          </bk-button>
        </template>
      </template>
      <template v-else>
        <bk-button theme="default" @click="restoreProfile">
          {{$t('恢复')}}
        </bk-button>
      </template>
      <div class="reset">
        <bk-button :disabled="isStatus" theme="default" @click="showResetDialog">
          {{$t('重置密码')}}
        </bk-button>
        <div class="reset-dialog" v-if="isShowReset" v-click-outside="closeResetDialog">
          <i class="arrow"></i>
          <template v-if="isAdmin">
            <h4 class="title">{{$t('原密码')}}</h4>
            <p class="pw-input-text">
              <input
                autocomplete="old-password"
                :type="passwordInputType['oldPassword']"
                :placeholder="$t('请输入原密码')"
                :class="['editor-password',{ 'input-error': isCorrectOldPw }]"
                :maxlength="32"
                v-model="oldPassword"
                v-focus
                @focus="isCorrectOldPw = false" />
              <i :class="['bk-icon', oldPasswordIconClass]" @click="changePasswordInputType('oldPassword')"></i>
            </p>
          </template>
          <h4 class="title">{{$t('重置密码')}}</h4>
          <p class="pw-input-text">
            <input type="text" class="hidden-password-input">
            <input type="password" class="hidden-password-input">
            <input
              autocomplete="new-password"
              :type="passwordInputType['newPassword']"
              :placeholder="$t('请输入新密码')"
              :class="['editor-password',{ 'input-error': isCorrectPw }]"
              :maxlength="32"
              v-model="newPassword"
              v-focus
              @focus="isCorrectPw = false" />
            <i :class="['bk-icon', passwordIconClass]" @click="changePasswordInputType('newPassword')"></i>
          </p>
          <div class="reset-btn">
            <bk-button theme="primary" class="editor-btn" @click="confirmReset">{{$t('确认')}}</bk-button>
            <bk-button theme="default" class="editor-btn" @click="isShowReset = false">{{$t('取消')}}</bk-button>
          </div>
        </div>
      </div>
    </div>
    <div class="user-detail" data-test-id="activeFieldsData">
      <div class="user-avatar-wrapper">
        <img :src="localAvatar || currentProfile.logo" width="68" height="68" @error="handleLoadAvatarError" />
        <p v-if="isForbid" class="forbid-text">{{currentProfile.status === 'DISABLED' ? $t('已禁用') : $t('已锁定')}}</p>
      </div>
      <ul v-if="fieldsList.length">
        <li class="infor-content-list">
          <h4 class="title">{{$t('用户信息')}}</h4>
          <div class="specific-text" v-for="(fieldInfo, index) in activeFieldsList" :key="index">
            <span class="name" v-bk-overflow-tips>{{fieldInfo.name}}</span>
            <span class="gap">：</span>
            <div class="desc" v-if="fieldInfo.key === 'telephone'" @click="viewTelephone">
              <p :class="['text', { 'phone': phoneNumber === $t('点击查看') }]">{{phoneNumber}}</p>
            </div>
            <div class="desc" v-else>
              <p class="text">{{fieldInfo.value || '--'}}</p>
            </div>
          </div>
        </li>
        <li class="infor-content-list">
          <h4 class="title">{{$t('用户设置')}}</h4>
          <div class="specific-text">
            <span class="name">{{$t('所在组织')}}</span>
            <span class="gap">：</span>
            <p class="desc">
              <template v-for="(item, index) in currentProfile.department_name">
                <span :key="index" class="text" v-bk-overflow-tips>{{item}}</span>
              </template>
            </p>
          </div>
          <div class="specific-text">
            <span class="name">{{$t('直接上级')}}</span>
            <span class="gap">：</span>
            <p class="desc">
              <span class="text tag-text" v-if="currentProfile.leader && currentProfile.leader.length">
                {{switchTag(currentProfile.leader)}}
              </span>
              <span class="text" v-else>--</span>
            </p>
          </div>
          <div class="specific-text">
            <span class="name">{{$t('密码有效期')}}</span>
            <span class="gap">：</span>
            <p class="desc">
              <span class="text">{{passwordValidDays}}</span>
            </p>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { dateConvert } from '@/common/util';
export default {
  directives: {
    focus: {
      // 输入框自动获焦
      inserted(el) {
        el.focus();
      },
    },
  },
  props: {
    currentProfile: {
      type: Object,
      default() {
        return {};
      },
    },
    // 当前用户目录 ID
    currentCategoryId: {
      type: Number,
      default: null,
    },
    currentCategoryType: {
      type: String,
      default: '',
    },
    fieldsList: {
      type: Array,
      default() {
        return [];
      },
    },
    statusMap: {
      type: Object,
      default: {},
    },
    timerMap: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      // 如果 logo url 加载出错显示本地头像
      localAvatar: '',
      isForbid: false,
      phoneNumber: this.$t('点击查看'),
      isCorrectOldPw: false,
      isCorrectPw: false,
      // 是否显示重置密码的弹窗
      isShowReset: false,
      oldPassword: '',
      newPassword: '',
      passwordInputType: {
        oldPassword: 'password',
        newPassword: 'password',
      },
      passwordRules: null,
    };
  },
  computed: {
    activeFieldsList() {
      return this.fieldsList.filter((fieldInfo) => {
        return fieldInfo.key !== 'department_name' && fieldInfo.key !== 'leader';
      });
    },
    oldPasswordIconClass() {
      return this.passwordInputType.oldPassword === 'password' ? 'icon-hide' : 'icon-eye';
    },
    passwordIconClass() {
      return this.passwordInputType.newPassword === 'password' ? 'icon-hide' : 'icon-eye';
    },
    passwordValidDays() {
      return this.$store.state.passwordValidDaysList.find(item => (
        item.days === this.currentProfile.password_valid_days
      )).text;
    },
    isAdmin() {
      // 这里先根据唯一字段 username 判断是否是 admin 用户
      return this.currentProfile.username === 'admin';
    },
    isStatus() {
      return this.currentProfile.status === 'DELETED';
    },
  },
  created() {
    this.getUserInfo();
  },
  mounted() {
    this.$nextTick(() => {
      this.isForbid = (this.currentProfile.status === 'DISABLED' || this.currentProfile.status === 'LOCKED');
    });
  },
  methods: {
    // 上级显示
    switchTag(tagList) {
      const getUserList = tagList.map(item => item.username);
      return getUserList.join(' , ');
    },
    // 获取用户信息
    getUserInfo() {
      this.activeFieldsList.forEach((item) => {
        if (item.options.length > 0) {
          item.options.map((key) => {
            if (key.id === this.currentProfile[item.key]) {
              item.value = key.value;
            }
          });
        } else if (this.timerMap.includes(item.key)) {
          item.value = dateConvert(this.currentProfile[item.key]);
        } else if (item.key !== 'telephone') {
          item.value = this.currentProfile[item.key];
        }
      });
    },
    // 编辑
    editProfile() {
      if (this.isForbid) {
        return;
      }
      this.$emit('editProfile');
    },
    // 删除
    deleteProfile() {
      this.$emit('deleteProfile');
    },
    // 恢复已删除用户
    restoreProfile() {
      this.$emit('restoreProfile');
    },
    // 禁用/启用
    async changeStatus() {
      try {
        this.$emit('showBarLoading');
        const status = this.isForbid ? 'NORMAL' : 'DISABLED';
        const res = await this.$store.dispatch('organization/patchProfile', {
          id: this.currentProfile.id,
          data: { status },
        });
        if (res.result === true) {
          this.isForbid = !this.isForbid;
          // eslint-disable-next-line vue/no-mutating-props
          this.currentProfile.status = status;
          const message = this.isForbid ? this.$t('禁用') : this.$t('启用');
          this.messageSuccess(message + this.$t('成功'));
          this.$emit('getTableData');
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.$emit('closeBarLoading');
      }
    },
    // 查看手机号
    // eslint-disable-next-line no-unused-vars
    viewTelephone(item) {
      if (this.isForbid) {
        return;
      }
      this.phoneNumber = this.currentProfile.telephone;
    },
    // 重置密码
    showResetDialog() {
      if (this.isForbid) {
        return;
      }
      this.isShowReset = true;
      // 清空上次输入
      this.oldPassword = '';
      this.newPassword = '';
    },
    // 验证密码的格式
    async confirmReset() {
      if (!this.passwordRules) {
        const currentPasswordInfo = this.$store.state.organization.currentPasswordInfo;
        if (currentPasswordInfo.id === this.currentCategoryId && currentPasswordInfo.data) {
          this.passwordRules = {
            passwordMinLength: currentPasswordInfo.data.password_min_length,
            passwordMustIncludes: currentPasswordInfo.data.password_must_includes,
          };
        } else {
          try {
            this.$emit('showBarLoading');
            const res = await this.$store.dispatch('catalog/ajaxGetPassport', {
              id: this.currentCategoryId,
            });
            const passwordInfo = this.$convertArrayToObject(res.data).default;
            this.passwordRules = {
              passwordMinLength: passwordInfo.password_min_length,
              passwordMustIncludes: passwordInfo.password_must_includes,
            };
            this.$store.commit('organization/updatePasswordInfo', {
              id: this.currentCategoryId,
              data: passwordInfo,
            });
          } catch (e) {
            // 如果获取规则失败，就给后端校验
            console.warn(e);
          } finally {
            this.$emit('closeBarLoading');
          }
        }
      }
      if (this.passwordRules) {
        // 如果上面拿到了规则就进行前端校验
        // 原密码校验, 任何人在重置admin密码时，需要先输入原密码
        if (this.isAdmin) {
          this.isCorrectOldPw = !this.$validatePassportByRules(this.oldPassword, this.passwordRules);
          if (this.isCorrectOldPw) {
            this.$bkMessage({
              message: this.$getMessageByRules(this, this.passwordRules),
              theme: 'error',
            });
            return;
          }
        }
        // 新密码校验
        this.isCorrectPw = !this.$validatePassportByRules(this.newPassword, this.passwordRules);
        if (this.isCorrectPw) {
          this.$bkMessage({
            message: this.$getMessageByRules(this, this.passwordRules),
            theme: 'error',
          });
          return;
        }
      }
      if (this.clickSecond) {
        return;
      }
      this.clickSecond = true;
      try {
        this.$emit('showBarLoading');
        const passwordData = {
          password: this.newPassword.trim(),
        };
        // 任何人在重置admin密码时，需要先输入原密码
        if (this.isAdmin) {
          passwordData.old_password = this.oldPassword.trim();
        };
        await this.$store.dispatch('organization/patchProfile', {
          id: this.currentProfile.id,
          data: passwordData,
        });
        this.$bkMessage({
          message: this.$t('重置密码成功'),
          theme: 'success',
        });
        this.isShowReset = false;
      } catch (e) {
        console.warn(e);
      } finally {
        this.clickSecond = false;
        this.$emit('closeBarLoading');
      }
    },
    closeResetDialog(e) {
      if (e.target.innerText === '重置密码') return;
      this.isShowReset = false;
      // 清空
      this.oldPassword = '';
      this.newPassword = '';
    },
    // 查看密码
    changePasswordInputType(type = 'newPassword') {
      this.passwordInputType[type] = this.passwordInputType[type] === 'password' ? 'text' : 'password';
    },
    handleLoadAvatarError() {
      this.localAvatar = this.$store.state.localAvatar;
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../../../scss/mixins/scroller';

.look-user-info-wrapper {
  height: 100%;
  padding: 30px 0;

  &.forbid-operate {
    .bk-button {
      color: #c8cacf;
      cursor: not-allowed;
    }

    .bk-button.bk-primary {
      background: #dcdee5;
      border: none;
      color: #fefefe;
    }

    .forbidMark {
      color: #737987;
      cursor: pointer;
    }

    .infor-content-list {
      .title,
      .specific-text .name,
      .specific-text .desc {
        color: #c4c6cc;
      }

      .desc {
        .text {
          display: block;

          &.phone {
            color: #c4c6cc;
          }
        }
      }
    }
  }
}

.action-btn-wrapper {
  font-size: 0;
  position: relative;
  margin: 0 30px;

  .editor-btn {
    /*width: 76px !important;*/
    margin-right: 10px;
  }

  .reset {
    position: absolute;
    right: 0;
    top: 0;
    transition: all .3s ease;

    .editor-btn {
      margin-right: 0;
    }

    .reset-dialog {
      position: absolute;
      top: 38px;
      right: 0;
      padding: 12px 20px 20px 20px;
      width: 302px;
      border-radius: 2px;
      background: rgba(255, 255, 255, 1);
      border: 1px solid rgba(221, 228, 235, 1);
      box-shadow: 0px 5px 10px 0px rgba(0, 0, 0, .1);
      z-index: 10;
      transition: all .3s ease;

      .pw-input-text {
        position: relative;

        .bk-icon {
          position: absolute;
          top: 10px;
          right: 10px;
          font-size: 16px;
          cursor: pointer;
        }
      }

      .arrow {
        position: absolute;
        top: -5px;
        right: 39px;
        width: 8px;
        height: 8px;
        border-top: 1px solid #dde4eb;
        border-left: 1px solid #dde4eb;
        transform: rotate(45deg);
        z-index: 10;
        background: rgba(255, 255, 255, 1);
      }

      .title {
        font-size: 14px;
        line-height: 33px;
        color: #808692;
        font-weight: normal;
      }

      .editor-password {
        padding: 0 12px;
        margin-bottom: 14px;
        width: 260px;
        height: 36px;
        font-size: 14px;
        color: #63656e;
        line-height: 36px;
        border: 1px solid #c3cdd7;
        resize: none;
        outline: none;

        &::input-placeholder {
          color: rgba(195, 205, 215, 1);
        }

        &:focus {
          border-color: #3c96ff !important;
        }

        &.input-error {
          border: 1px solid #ea3636;
        }
      }

      .reset-btn {
        .bk-button {
          margin-right: 10px;
          width: auto !important;
        }
      }
    }
  }
}

.user-detail {
  position: relative;
  height: calc(100% - 36px);
  padding: 0 30px;
  overflow: hidden;
  overflow-y: auto;

  @include scroller($backgroundColor: #e6e9ea, $width: 4px);
}

.user-avatar-wrapper {
  position: absolute;
  top: 61px;
  right: 30px;
  width: 68px;
  height: 68px;
  border-radius: 2px;

  .forbid-text {
    position: absolute;
    top: 0;
    left: 0;
    height: 68px;
    width: 68px;
    line-height: 68px;
    font-size: 14px;
    text-align: center;
    color: rgba(255, 255, 255, 1);
    background: rgba(0, 0, 0, .6);
  }
}

.infor-content-list {
  margin-bottom: 28px;

  &:last-child {
    margin-bottom: 0;
  }

  .title {
    padding: 17px 0 8px 0;
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: bold;
    color: rgba(51, 60, 72, 1);
    line-height: 19px;
    border-bottom: 1px solid #dde4eb;
  }

  .specific-text {
    display: flex;
    line-height: 26px;
    font-size: 12px;
    color: #313238;

    .name {
      width: 100px;
      text-align: right;
      font-weight: 500;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .gap {
      width: 20px;
      font-weight: bold;
    }

    .desc {
      width: calc(100% - 120px);
      color: #63656e;

      .text {
        display: block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        outline: none;

        &.tag-text {
          overflow: inherit;
          text-emphasis: none;
          word-break: break-all;
          white-space: normal;
        }

        &.phone {
          color: #468bfe;
          cursor: pointer;
        }
      }
    }
  }
}
</style>
