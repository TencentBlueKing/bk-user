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
      <notifyEditorTemplate
        :checkbox-info="checkboxInfo"
        :data-list="accountInfo"
        :is-template="isAccountTemplate"
        :expiring-email-key="'expiring_account_email_config'"
        :expired-email-key="'expired_account_email_config'"
        :expiring-sms-key="'expiring_account_sms_config'"
        :expired-sms-key="'expired_account_sms_config'"
        @handleEditorText="handleEditorText">
        <template slot="label">
          <div class="password-header">
            <bk-checkbox-group
              :class="$i18n.locale === 'en' ? 'checkbox-en' : 'checkbox-zh'"
              v-model="defaultAccount.account_expiration_notice_methods">
              <div
                v-for="(item, index) in checkboxInfo" :key="index"
                :class="['password-tab', item.status ? 'active-tab' : '']"
                style="margin-left: 5px;">
                <bk-checkbox :value="item.value" />
                <span class="checkbox-item" @click="handleClickLabel(item)">{{item.label}}</span>
              </div>
            </bk-checkbox-group>
            <div class="edit-info" @click="toggleAccountTemplate">
              <span style="font-size:14px">{{$t('编辑通知模板')}}</span>
              <i :class="['bk-icon', isDropdownInfo ? 'icon-angle-up' : 'icon-angle-down']"></i>
            </div>
          </div>
        </template>
      </notifyEditorTemplate>
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
import notifyEditorTemplate from './NotifyEditorTemplate.vue';
export default {
  components: { notifyEditorTemplate },
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
      // 显示编辑通知模板
      isAccountTemplate: false,
      checkboxInfo: [
        { value: 'send_email', label: this.$t('邮箱'), status: true },
        { value: 'send_sms', label: this.$t('短信'), status: false },
      ],
    };
  },
  computed: {
    defaultAccount() {
      return this.accountInfo;
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
    handleEditorText(html, text, key) {
      this.defaultAccount[key].content_html = html;
      this.defaultAccount[key].content = text;
    },
    handleClickLabel(item) {
      this.checkboxInfo.map((element) => {
        if (element.value === item.value) {
          element.status = true;
        } else {
          element.status = false;
        }
      });
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
    .tab-box {
      .password-header {
        display: flex;
        line-height: 50px;
        .bk-form-control {
          display: flex;
          line-height: 50px;
          font-size: 14px;
          .password-tab {
            padding-left: 20px;
            .checkbox-item {
              font-size: 14px;
              display: inline-block;
              padding: 0 20px 0 5px;
            }
          }
        }
        .checkbox-zh {
          width: 85% !important;
        }
        .checkbox-en {
          width: 75% !important;
        }
        .edit-info {
          color: #3A84FF;
          :hover {
            cursor: pointer;
          }
        }
      }
    }
    ::v-deep .show-tab-color {
      .password-header {
        display: flex;
        border-bottom: 1px solid #dcdee5;
        .active-tab {
          border-bottom: 2px solid #3A84FF;
        }
        .password-tab span:hover {
          cursor: pointer;
          color: #3a84ff;
        }
      }
      .bk-tab-label-list .bk-tab-label-item.active:after {
        height: 2px;
      }
      .bk-tab-header {
        background-image: linear-gradient(transparent 41px, #dcdee5 0);
      }
    }
  }
}
</style>
