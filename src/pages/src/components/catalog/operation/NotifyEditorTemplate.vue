<!--
  - TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
  - Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
  - Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at http://opensource.org/licenses/MIT
  - Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
  - an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
  - specific language governing permissions and limitations under the License.
  -->
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
            <h3 class="email-block-name">{{createAccountEmail ? createAccountEmail : $t('即将到期提醒')}}</h3>
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
                @updateContent="(html, text) => $emit('handleEditorText', html, text, expiringEmailKey)" />
            </div>
          </li>
          <li class="email-block">
            <h3 class="email-block-name">{{resetPasswordEmail ? resetPasswordEmail : $t('已过期提醒')}}</h3>
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
                @updateContent="(html, text) => $emit('handleEditorText', html, text, expiredEmailKey)" />
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
            <h3 class="email-block-name">{{$t('即将到期提醒')}}</h3>
            <div class="email-info clearfix">
              <p class="title" style="height: 260px">{{$t('正文')}}<span class="star">*</span></p>
              <edtiorTemplate
                :toolbar-config="infoConfig"
                :html-text="expiringSms.content_html"
                @updateContent="(html, text) => $emit('handleEditorText', html, text, expiringSmsKey)" />
            </div>
          </li>
          <li class="email-block">
            <h3 class="email-block-name">{{$t('已过期提醒')}}</h3>
            <div class="email-info clearfix">
              <p class="title" style="height: 260px">{{$t('正文')}}<span class="star">*</span></p>
              <edtiorTemplate
                :toolbar-config="infoConfig"
                :html-text="expiredSms.content_html"
                @updateContent="(html, text) => $emit('handleEditorText', html, text, expiredSmsKey)" />
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import edtiorTemplate from './editorTemplate.vue';
export default {
  components: { edtiorTemplate },
  props: {
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
      default: () => '',
    },
    expiredEmailKey: {
      type: String,
      default: () => '',
    },
    expiringSmsKey: {
      type: String,
      default: () => '',
    },
    expiredSmsKey: {
      type: String,
      default: () => '',
    },
    createAccountEmail: {
      type: String,
      default: () => '',
    },
    resetPasswordEmail: {
      type: String,
      default: () => '',
    },
  },
  data() {
    return {
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
    expiredEmail() {
      return this.dataList[this.expiredEmailKey] || {};
    },
    expiringEmail() {
      return this.dataList[this.expiringEmailKey] || {};
    },
    expiringSms() {
      return this.dataList[this.expiringSmsKey] || {};
    },
    expiredSms() {
      return this.dataList[this.expiredSmsKey] || {};
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../../../scss/mixins/scroller';
.tab-box {
  width: 860px;
  border: 1px solid #3A84FF;
}
.show-tab-color {
  .password-content {
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
        // float: left;
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
        }
      }
    }
  }
}
</style>
