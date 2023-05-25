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
  <div class="guide-into-wrapper">
    <div class="upload-xsl-wrapper">
      <template v-if="!uploadInfo.name">
        <div class="bk-upload-content">
          <img src="../../../images/svg/upload.svg">
          <span>{{ $t('将文件拖到此处或') }}</span>
          <span class="bk-click-upload">{{ $t('点击上传') }}</span>
        </div>
      </template>
      <template v-else>
        <div class="bk-upload-content bk-upload-success">
          <img src="../../../images/xsl.png">
          <div class="bk-upload-info">
            <div class="bk-info-word">
              <span class="bk-word-name">{{uploadInfo.name}}</span>
              <span class="bk-word-size">{{uploadInfo.size}}</span>
              <i class="bk-icon icon-close close-upload" @click="closeFile"></i>
            </div>
            <div class="bk-info-line" :class="{ 'bk-line-error': !uploadInfo.type }"></div>
          </div>
        </div>
      </template>
      <input type="file" accept=".xls,.xlsx" name="" class="bk-upload-file" @change="handleFile">
    </div>
    <p :class="['expalin-wrapper', { 'chang-en': $i18n.locale === 'en' }]">
      <span class="text">{{$t('仅支持xls、xlsx格式文件')}}</span>
      <span class="template" @click="downloadTemplate"><i class="icon-user-download"></i>{{$t('下载模板')}}</span>
    </p>
    <p class="tip-wrapper">
      <bk-checkbox
        v-model="uploadInfo.isOverwrite">
        {{ $t('允许对同名用户覆盖更新') }}
      </bk-checkbox>
      <i class="tip-icon icon-user--l" v-bk-tooltips="{ width: 310, content: $t('导入覆盖提升') }"></i>
    </p>
  </div>
</template>

<script>
export default {
  props: {
    id: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      isDisableUpload: true,
      fileList: null,
      // 上传文件内容
      uploadInfo: {
        fileInfo: {},
        name: '',
        size: '',
        type: false,
        isOverwrite: false,
      },
    };
  },
  watch: {
    fileList(val) {
      this.$nextTick(() => {
        const el = document.querySelector('.file-wrapper');
        const imgCover = document.querySelector('.file-item .file-icon img');
        if (!val.length) {
          el.style.display = 'block';
          return;
        }
        imgCover.style.display = 'none';
        el.style.display = 'none';
      });
    },
  },
  methods: {
    // eslint-disable-next-line no-unused-vars
    guideSuccess(file, fileList) {
      this.isDisableUpload = false;
    },
    downloadTemplate() {
      const newA = document.createElement('a');
      let url = window.AJAX_URL;
      if (url.endsWith('/')) {
        // 去掉末尾的斜杠
        url = url.slice(0, url.length - 1);
      }
      if (!url.startsWith('http')) {
        // tips: 后端提供的 SITE_URL 需以 / 开头
        url = window.location.origin + url;
      }
      newA.href = `${url}/api/v1/web/categories/1/operations/export_template/`;
      newA.download = 'example.xlsx';
      newA.click();
    },
    // eslint-disable-next-line no-unused-vars
    testErr(file, fileList) {
      this.isDisableUpload = true;
    },
    closeFile() {
      this.uploadInfo = {
        fileInfo: {},
        name: '',
        size: '',
        type: false,
        isOverwrite: false,
      };
    },
    // 上传
    handleFile(e) {
      this.uploadInfo.fileInfo = e.target.files[0];
      this.uploadInfo.name = this.uploadInfo.fileInfo.name;
      this.uploadInfo.size = `${(this.uploadInfo.fileInfo.size / 1024).toFixed(2)}KB`;
      // 判断上传文件的格式
      const fileReg = /[.xls|.xlsx]$/;
      this.uploadInfo.type = fileReg.test(this.uploadInfo.name);
    },
  },
};
</script>

<style>
  .bk-upload .all-file .file-item {
    border: 1px solid #dcdee5 !important;
    background: #fff !important;
  }

  .bk-upload .all-file .file-item .file-icon {
    background: url('../../../images/xsl.png')
  }

  .bk-selector .bk-selector-node .text {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

</style>

<style lang="scss" scoped>
@import '../../../scss/mixins/clearfix';

.guide-into-wrapper {
  .head-department {
    position: relative;
    margin: 15px 0;
    color: #63656e;
    line-height: 20px;
    font-size: 14px;

    .title {
      position: absolute;
      left: 0;
    }

    .text {
      display: block;
      margin-left: 50px;
      font-weight: bold;
    }
  }
}

.upload-xsl-wrapper {
  margin: 0 0 12px 0;
  position: relative;
  overflow: hidden;

  .bk-upload-content {
    width: 100%;
    height: 68px;
    line-height: 66px;
    border: 1px dashed #c3cdd7;
    border-radius: 2px;
    text-align: center;
    color: #c3cdd7;

    img {
      width: 24px;
      vertical-align: middle;
      margin-bottom: 5px;
    }

    .bk-click-upload {
      color: #3c96ff;
      margin-left: 5px;
    }
  }

  .bk-upload-success {
    cursor: pointer;

    @include clearfix;

    img {
      width: 45px;
      float: left;
      margin-top: 12px;
      margin-left: 12px;
    }

    .bk-upload-info {
      float: left;
      margin-top: 12px;
      width: calc(100% - 95px);
      margin-left: 10px;
      position: relative;
      height: 45px;

      .bk-info-word {
        display: inline-block;
        font-size: 12px;
        width: 100%;
        line-height: 24px;
        float: left;
        position: relative;

        .bk-word-name {
          float: left;
          max-width: 250px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .bk-word-size {
          float: right;
        }

        .close-upload {
          position: absolute;
          top: -10px;
          right: -24px;
          z-index: 2;
          padding: 5px;
          border-radius: 50%;
          color: #979ba5;
          font-size: 20px;

          &:hover {
            background-color: #f0f1f5;
          }
        }
      }

      .bk-info-line {
        width: 100%;
        height: 6px;
        border-radius: 2px;
        background: #30d878;
        float: left;
      }

      .bk-line-error {
        background: #ff5656;
      }
    }
  }

  .bk-upload-file {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    cursor: pointer;
    opacity: 0;
  }
}

.expalin-wrapper {
  position: relative;
  margin: 12px 0 0 0;
  font-size: 14px;
  color: rgba(151, 155, 165, 1);
  line-height: 19px;

  &.chang-en {
    .template {
      position: relative;
      right: auto;
      display: block;
      margin-top: 10px;
    }

    .icon-user-download {
      margin-right: 10px;
    }
  }

  .template {
    position: absolute;
    right: 0;
    color: rgba(99, 101, 110, 1);
    cursor: pointer;
  }
}

.tip-wrapper {
  margin-top: 10px;
  .tip-icon {
    display: inline-block;
    transform: translateY(4px);
  }
}
</style>
