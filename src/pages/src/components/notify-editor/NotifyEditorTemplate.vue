<template>
  <div :class="['tab-box', isTemplate ? 'show-tab-color' : '']">
    <slot name="label" />
    <div class="password-content">
      <div
        class="template-config-container"
        v-show="checkboxInfo[0].status && isTemplate"
        data-test-id="list_emailInfo">
        <ul class="template-config clearfix">
          <li class="email-block">
            <h3 class="email-block-name">{{createAccountEmail ? createAccountEmail : '即将到期提醒'}}</h3>
            <div class="email-info clearfix">
              <p class="title">标题<span class="star">*</span></p>
              <bk-input
                type="text" class="input-style"
                v-model="expiringEmail.title" />
            </div>
            <div class="email-info clearfix">
              <p class="title">发件人<span class="star">*</span></p>
              <bk-input
                type="text" class="input-style"
                v-model="expiringEmail.sender" />
            </div>
            <div class="email-info clearfix">
              <p class="title" style="height: 260px">正文<span class="star">*</span></p>
              <edtiorTemplate
                :toolbar-config="emailConfig"
                :html-text="expiringEmail.content_html"
                @updateContent="(html, text) => emit('handleEditorText', html, text, expiringEmailKey, 'email')" />
            </div>
          </li>
          <li class="email-block">
            <h3 class="email-block-name">{{resetPasswordEmail ? resetPasswordEmail : '已过期提醒'}}</h3>
            <div class="email-info clearfix">
              <p class="title">标题<span class="star">*</span></p>
              <bk-input
                type="text" class="input-style"
                v-model="expiredEmail.title" />
            </div>
            <div class="email-info clearfix">
              <p class="title">发件人<span class="star">*</span></p>
              <bk-input
                type="text" class="input-style"
                v-model="expiredEmail.sender" />
            </div>
            <div class="email-info clearfix">
              <p class="title" style="height: 260px">正文<span class="star">*</span></p>
              <edtiorTemplate
                :toolbar-config="emailConfig"
                :html-text="expiredEmail.content_html"
                @updateContent="(html, text) => emit('handleEditorText', html, text, expiredEmailKey, 'email')" />
            </div>
          </li>
        </ul>
      </div>
      <div
        class="template-config-container"
        v-show="checkboxInfo[1] && checkboxInfo[1].status && isTemplate"
        data-test-id="list_emailInfo">
        <ul class="template-config clearfix">
          <li class="email-block">
            <h3 class="email-block-name">{{createAccountSms ? createAccountSms : '即将到期提醒'}}</h3>
            <div class="email-info clearfix">
              <p class="title" style="height: 260px">正文<span class="star">*</span></p>
              <edtiorTemplate
                :toolbar-config="infoConfig"
                :html-text="expiringSms.content_html"
                @updateContent="(html, text) => emit('handleEditorText', html, text, expiringSmsKey, 'sms')" />
            </div>
          </li>
          <li class="email-block">
            <h3 class="email-block-name">{{resetPasswordSms ? resetPasswordSms : '已过期提醒'}}</h3>
            <div class="email-info clearfix">
              <p class="title" style="height: 260px">正文<span class="star">*</span></p>
              <edtiorTemplate
                :toolbar-config="infoConfig"
                :html-text="expiredSms.content_html"
                @updateContent="(html, text) => emit('handleEditorText', html, text, expiredSmsKey, 'sms')" />
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineEmits, defineProps, reactive } from 'vue';

import edtiorTemplate from './editorTemplate.vue';

const props = defineProps({
  activeMethods: {
    type: String,
    default: '',
  },
  checkboxInfo: {
    type: Array,
    default: () => ([]),
  },
  dataList: {
    type: Object,
    default: () => ({}),
  },
  isTemplate: {
    type: Boolean,
    default: false,
  },
  expiringEmailKey: {
    type: String,
    default: '',
  },
  expiredEmailKey: {
    type: String,
    default: '',
  },
  expiringSmsKey: {
    type: String,
    default: '',
  },
  expiredSmsKey: {
    type: String,
    default: '',
  },
  createAccountEmail: {
    type: String,
    default: '',
  },
  resetPasswordEmail: {
    type: String,
    default: '',
  },
  createAccountSms: {
    type: String,
    default: '',
  },
  resetPasswordSms: {
    type: String,
    default: '',
  },
});

const emit = defineEmits(['handleEditorText']);

/* 邮箱工具栏配置 */
const emailConfig = reactive({
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
});

/* 短信工具栏配置 */
const infoConfig = reactive({
  toolbarKeys: ['insertLink'],
});

const findMethodScene = (method, sceneKey) => computed(() => props.dataList
  .find(item => item.method === method && item.scene === sceneKey) || {});

const expiredEmail = findMethodScene('email', props.expiredEmailKey);
const expiringEmail = findMethodScene('email', props.expiringEmailKey);
const expiringSms = findMethodScene('sms', props.expiringSmsKey);
const expiredSms = findMethodScene('sms', props.expiredSmsKey);
</script>

<style lang="less" scoped>
.tab-box {
  width: 800px;
  border: 1px solid #3A84FF;
}

.show-tab-color {
  .password-content {
    padding: 20px;

    .template-config-container {
      border: 1px solid #dcdee5;
    }
  }

  .bk-tab-label-list .bk-tab-label-item.active::after {
    height: 2px;
  }

  .bk-tab-header {
    background-image: linear-gradient(transparent 41px, #dcdee5 0);
  }
}

.template-config-container {
  position: relative;
  width: 100%;

  > ul.template-config > li.email-block {
    float: left;
    width: 50%;

    &:first-child {
      border-right: 1px solid #dcdee5;
    }

    > .email-block-name {
      height: 42px;
      font-size: 14px;
      font-weight: bold;
      line-height: 42px;
      text-align: center;
      background: #fafbfd;
    }

    > .email-info {
      display: flex;
      font-size: 0;
      border-top: 1px solid #dcdee5;

      input,
      textarea {
        border: none;
        outline: none;
        resize: none;
      }

      .title,
      .input-text,
      .textarea-text {
        font-size: 14px;
      }

      .title {
        width: 20%;
        padding: 13px 0 10px;
        text-align: center;
        border-right: 1px solid #dcdee5;

        .star {
          display: inline-block;
          margin: 0 0 0 3px;
          line-height: 19px;
          color: #ff5e5e;
          vertical-align: middle;
        }
      }

      .input-text {
        width: 80%;
        padding: 13px 0 10px 19px;
      }

      .input-style {
        width: 80%;
        height: 55px;
        border: 1px solid transparent;
      }

      .is-focused {
        border: 1px solid #3c96ff;
      }

      .focus-editor {
        border: 1px solid #3c96ff;
      }

      ::v-deep .textarea-text {
        width: 80%;
        height: 260px;
        overflow: hidden;
        overflow-y: auto;
        font-size: 14px;
        font-weight: 400;
        line-height: 20px;
        word-break: break-all;
        background: #fff;

        &::-webkit-scrollbar {
          width: 4px;
          background-color: transparent;
        }

        &::-webkit-scrollbar-thumb {
          background-color: #dcdee5;
          border-radius: 4px;
        }

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
              background-color: #dcdee5;
              border-radius: 4px;
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
        overflow: hidden;
        font-size: 14px;
        font-weight: 400;
        line-height: 20px;
        word-break: break-all;
        background: #fff;

        .toolbar-content {
          height: 40px;

          .w-e-toolbar {
            padding-left: 15px;
            background-color: #F0F2F5;
          }
        }

        .editor-content {
          width: 100%;
          height: calc(100% - 40px);
          overflow-y: auto;

          &::-webkit-scrollbar {
            width: 4px;
            background-color: transparent;
          }

          &::-webkit-scrollbar-thumb {
            background-color: #dcdee5;
            border-radius: 4px;
          }

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
</style>
