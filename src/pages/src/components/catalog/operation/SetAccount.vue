<template>
  <div v-if="accountInfo" class="catalog-setting-step set-account">
    <!-- 账号有效期 -->
    <div class="info-container">
      <div class="title-container">
        <h4 class="title">{{$t('账号有效期')}}</h4>
        <span class="star">*</span>
      </div>
      <div class="bk-button-group">
        <bk-button
          v-for="(item, index) in accountValidDaysList"
          :key="index"
          :class="{ 'is-selected': defaultAccount.expired_after_days === item.days }"
          @click="defaultAccount.expired_after_days = item.days">
          {{item.text}}
        </bk-button>
      </div>
    </div>

    <!-- 账号到期提醒时间 -->
    <div class="info-container">
      <div class="title-container">
        <h4 class="title">{{$t('账号到期提醒时间')}}</h4>
        <span class="star">*</span>
        <div class="tips">
          <span class="icon-user--l" v-bk-tooltips="$t('账号快到期前提醒_如选择_7天__则在账号到期七天前提醒一次')"></span>
        </div>
      </div>
      <bk-checkbox-group v-model="defaultAccount.account_expiration_notice_interval">
        <bk-checkbox :value="1" style="margin-right: 40px;">{{$t('1天')}}</bk-checkbox>
        <bk-checkbox :value="7" style="margin-right: 40px;">{{$t('7天')}}</bk-checkbox>
        <bk-checkbox :value="15">{{$t('15天')}}</bk-checkbox>
      </bk-checkbox-group>
      <p class="error-text" v-if="accountDateError">{{$t('账号到期提醒时间不得为空')}}</p>
    </div>

    <!-- 账号到期提醒通知方式 -->
    <div class="info-container">
      <div class="title-container">
        <h4 class="title">{{$t('账号到期提醒通知方式')}}</h4>
      </div>
      <div :class="['account-box', isAccountTemplate ? 'show-tab-color' : '']">
        <div class="account-header">
          <bk-checkbox-group v-model="defaultAccount.account_expiration_notice_methods">
            <div :class="['account-tab', showEmail ? 'active-tab' : '']" style="margin-left: 5px;">
              <bk-checkbox value="send_email" />
              <span class="checkbox-item" @click="clickEmail">{{$t('邮箱')}}</span>
            </div>
            <div :class="['account-tab', showSms ? 'active-tab' : '']">
              <bk-checkbox value="send_sms" />
              <span class="checkbox-item" @click="clickSms">{{$t('短信')}}</span>
            </div>
          </bk-checkbox-group>
          <div class="edit-info" @click="toggleAccountTemplate">
            <span style="font-size:14px">{{$t('编辑通知模板')}}</span>
            <i :class="['bk-icon', isDropdownInfo ? 'icon-angle-up' : 'icon-angle-down']"></i>
          </div>
        </div>
        <div class="account-content">
          <div
            class="template-config-container"
            v-show="showEmail && isAccountTemplate"
            data-test-id="list_emailInfo">
            <ul class="template-config clearfix">
              <li class="email-block">
                <h3 class="email-block-name">{{$t('即将到期提醒')}}</h3>
                <div class="email-info clearfix">
                  <p class="title">{{$t('标题')}}<span class="star">*</span></p>
                  <bk-input
                    type="text" class="input-style"
                    v-model="expiringEmail.title" />
                </div>
                <div class="email-info clearfix">
                  <p class="title">{{$t('发件人')}}<span class="star">*</span></p>
                  <bk-input
                    type="text" class="input-style"
                    v-model="expiringEmail.sender" />
                </div>
                <div class="email-info clearfix">
                  <p class="title" style="height: 260px">{{$t('正文')}}<span class="star">*</span></p>
                  <edtiorTemplate
                    :toolbar-config="emailConfig"
                    :html-text="expiringEmail.content_html"
                    @updateContent="(html, text) => handleEditorText(html, text, 'expiring_account_email_config')" />
                </div>
              </li>
              <li class="email-block">
                <h3 class="email-block-name">{{$t('已过期提醒')}}</h3>
                <div class="email-info clearfix">
                  <p class="title">{{$t('标题')}}<span class="star">*</span></p>
                  <bk-input
                    type="text" class="input-style"
                    v-model="expiredEmail.title" />
                </div>
                <div class="email-info clearfix">
                  <p class="title">{{$t('发件人')}}<span class="star">*</span></p>
                  <bk-input
                    type="text" class="input-style"
                    v-model="expiredEmail.sender" />
                </div>
                <div class="email-info clearfix">
                  <p class="title" style="height: 260px">{{$t('正文')}}<span class="star">*</span></p>
                  <edtiorTemplate
                    :toolbar-config="emailConfig"
                    :html-text="expiredEmail.content_html"
                    @updateContent="(html, text) => handleEditorText(html, text, 'expired_account_email_config')" />
                </div>
              </li>
            </ul>
          </div>
          <div
            class="template-config-container"
            v-show="showSms && isAccountTemplate"
            data-test-id="list_emailInfo">
            <ul class="template-config clearfix">
              <li class="email-block">
                <h3 class="email-block-name">{{$t('即将到期提醒')}}</h3>
                <div class="email-info clearfix">
                  <p class="title" style="height: 260px">{{$t('正文')}}<span class="star">*</span></p>
                  <edtiorTemplate
                    :toolbar-config="infoConfig"
                    :html-text="expiringSms.content_html"
                    @updateContent="(html, text) => handleEditorText(html, text, 'expiring_account_sms_config')" />
                </div>
              </li>
              <li class="email-block">
                <h3 class="email-block-name">{{$t('已过期提醒')}}</h3>
                <div class="email-info clearfix">
                  <p class="title" style="height: 260px">{{$t('正文')}}<span class="star">*</span></p>
                  <edtiorTemplate
                    :toolbar-config="infoConfig"
                    :html-text="expiredSms.content_html"
                    @updateContent="(html, text) => handleEditorText(html, text, 'expired_account_sms_config')" />
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增账号设置 -->
    <div v-if="type === 'add'" class="save-setting-buttons">
      <bk-button @click="$emit('cancel')" class="king-button">
        {{$t('返回列表')}}
      </bk-button>
      <bk-button @click="$emit('previous')" class="king-button">
        {{$t('上一步')}}
      </bk-button>
      <bk-button theme="primary" :disabled="isDisabledSubmit" @click="handleNext" class="king-button">
        {{$t('下一步')}}
      </bk-button>
    </div>

    <!-- 编辑账号设置 -->
    <div v-if="type === 'set'" class="save-setting-buttons">
      <bk-button theme="primary" :disabled="isDisabledSubmit" @click="saveInfo" class="king-button">
        {{$t('保存')}}
      </bk-button>
      <bk-button @click="$emit('cancel')" class="king-button">
        {{$t('取消')}}
      </bk-button>
    </div>
  </div>
</template>

<script>
import edtiorTemplate from '../operation/editorTemplate.vue';
export default {
  components: { edtiorTemplate },
  props: {
    // add 增加目录 set 修改目录设置
    type: {
      type: String,
      required: true,
    },
    accountInfo: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      accountDateError: false,
      showEmail: true,
      showSms: false,
      // 显示编辑通知模板
      isAccountTemplate: false,
      /* 邮箱工具栏配置 */
      emailConfig: {
        toolbarKeys: [
          'bold', 'italic', 'color',
          {
            key: 'group-justify',
            iconSvg: `<svg viewBox="0 0 1024 1024">
              <path d="M768 793.6v102.4H51.2v-102.4h716.8z m204.8-230.4v102.4H51.2v-102.4h921.6z
                m-204.8-230.4v102.4H51.2v-102.4h716.8zM972.8 102.4v102.4H51.2V102.4h921.6z"></path>
            </svg>`,
            menuKeys: ['justifyLeft', 'justifyRight', 'justifyCenter', 'justifyJustify'],
          },
          'insertLink',
        ],
      },
      /* 短信工具栏配置 */
      infoConfig: {
        toolbarKeys: ['insertLink'],
      },
    };
  },
  computed: {
    defaultAccount() {
      return this.accountInfo;
    },
    expiredEmail() {
      return this.accountInfo.expired_account_email_config || {};
    },
    expiringEmail() {
      return this.accountInfo.expiring_account_email_config || {};
    },
    expiringSms() {
      return this.accountInfo.expiring_account_sms_config || {};
    },
    expiredSms() {
      return this.accountInfo.expired_account_sms_config || {};
    },
    // 账号有效期
    accountValidDaysList() {
      return this.$store.state.passwordValidDaysList;
    },
    isDisabledSubmit() {
      return this.accountDateError;
    },
  },
  watch: {
    'defaultAccount.account_expiration_notice_methods'(val) {
      if (val.length && !this.defaultAccount.account_expiration_notice_interval.length) {
        this.accountDateError = true;
      } else {
        this.accountDateError = false;
      }
    },
    'defaultAccount.account_expiration_notice_interval'(val) {
      if (!val.length && this.defaultAccount.account_expiration_notice_methods.length) {
        this.accountDateError = true;
      } else {
        this.accountDateError = false;
      }
    },
  },
  methods: {
    handleNext() {
      this.$emit('next');
    },
    // 保存
    saveInfo() {
      this.$emit('saveAccount');
    },
    toggleAccountTemplate() {
      this.isAccountTemplate = !this.isAccountTemplate;
      this.isDropdownInfo = !this.isDropdownInfo;
    },
    clickEmail() {
      this.showEmail = true;
      this.showSms = false;
    },
    clickSms() {
      this.showEmail = false;
      this.showSms = true;
    },
    handleEditorText(html, text, key) {
      this.defaultAccount[key].content_html = html;
      this.defaultAccount[key].content = text;
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../../../scss/mixins/scroller';

#catalog .catalog-setting-step.set-account {
  > .info-container {
    margin-bottom: 17px;

    .template-config-container {
      position: relative;
      width: 100%;

      > ul.template-config > li.email-block {
        width: 50%;
        float: left;

        &:first-child {
          border-right: 1px solid #dcdee5;
        }

        > .email-block-name {
          height: 42px;
          line-height: 42px;
          text-align: center;
          font-size: 14px;
          font-weight: bold;
          background: #fafbfd;
        }

        > .email-info {
          font-size: 0;
          border-top: 1px solid #dcdee5;
          display: flex;

          input,
          textarea {
            resize: none;
            outline: none;
            border: none;
          }

          .title,
          .input-text,
          .textarea-text {
            font-size: 14px;
          }

          .title {
            padding: 13px 0 10px 0;
            width: 20%;
            text-align: center;
            border-right: 1px solid #dcdee5;

            .star {
              display: inline-block;
              vertical-align: middle;
              margin: 0 0 0 3px;
              line-height: 19px;
              color: #ff5e5e;
            }
          }

          .input-text {
            width: 80%;
            padding: 13px 0 10px 19px;
          }

          ::v-deep .input-style {
            width: 80%;
            .bk-input-text .bk-form-input {
              height: 44px;
              border: 1px solid #fff;
            }
          }

          .focus-editor {
            border: 1px solid #3c96ff;
          }

          ::v-deep .textarea-text {
            width: 80%;
            height: 260px;
            line-height: 20px;
            font-size: 14px;
            font-weight: 400;
            word-break: break-all;
            background: #fff;
            overflow: hidden;
            overflow-y: auto;

            @include scroller($backgroundColor: #e6e9ea, $width: 4px);

            .bk-textarea-wrapper {
              height: 100%;
              border: none;
              .bk-form-textarea {
                height: 100%;
                &::-webkit-scrollbar {
                  width: 4px;
                  background-color: transparent;
                }
                &::-webkit-scrollbar-thumb {
                  border-radius: 4px;
                  background-color: #dcdee5;
                }
              }
            }
          }
          ::v-deep .bk-form-control.control-active .bk-textarea-wrapper {
            border: 1px solid #3A84FF;
          }
          ::v-deep .markdown-box {
            width: 80%;
            height: 260px;
            line-height: 20px;
            font-size: 14px;
            font-weight: 400;
            word-break: break-all;
            background: #fff;
            overflow: hidden;
            .toolbar-content {
              height: 40px;
              .w-e-toolbar {
                background-color: #F0F2F5;
                padding-left: 15px;
              }
            }
            .editor-content {
              width: 100%;
              height: calc(100% - 40px);
              overflow-y: auto;
              @include scroller($backgroundColor: #e6e9ea, $width: 4px);
              .w-e-text-container .w-e-scroll {
                overflow: inherit !important;
              }
              .w-e-modal {
                right: 0 !important;
              }
            }
          }
        }
      }
    }
    ::v-deep .show-tab-color {
      .account-header {
        display: flex;
        border-bottom: 1px solid #dcdee5;
        .active-tab {
          border-bottom: 2px solid #3A84FF;
        }
        .account-tab span:hover {
          cursor: pointer;
          color: #3a84ff;
        }
      }
      .account-content {
        padding: 20px;
        .template-config-container {
          border: 1px solid #dcdee5;
        }
      }
      .bk-tab-label-list .bk-tab-label-item.active:after {
        height: 2px;
      }
      .bk-tab-header {
        background-image: linear-gradient(transparent 41px, #dcdee5 0);
      }
    }
    ::v-deep .account-box {
      width: 860px;
      border: 1px solid #3A84FF;
      .account-header {
        display: flex;
        line-height: 50px;
        .bk-form-control {
          display: flex;
          width: 85%;
          .account-tab {
            padding-left: 20px;
            .checkbox-item {
              font-size: 14px;
              display: inline-block;
              padding: 0 20px 0 5px;
            }
          }
        }
        .edit-info {
          color: #3A84FF;
          :hover {
            cursor: pointer;
          }
        }
      }
    }
  }
}
</style>
