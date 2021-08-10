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
  <div class="user-head-portrait" :class="{ 'chang-en': $i18n.locale === 'en' }">
    <span class="head">{{$t('头像')}}</span>
    <div class="avatar-wrapper">
      <img :src="images.avatarImg || imgSrc" alt=""
           class="avatar-img" width="68" height="68" @error="handleLoadAvatarError" />
      <input type="file" name="avatar" value="" accept="image/*"
             class="avatar-input" @change="imgOnChange($event, 'avatar')" />
    </div>
    <!-- 选择头像的弹窗 -->
    <div class="personal-pops" v-if="images.isShowImageEditor">
      <div class="pops-content">
        <h4>
          {{$t('头像剪裁')}}
          <a class="fr pops-close" href="javascript:;" @click="closeImageEditor">
            <i class="icon icon-user-close"></i>
          </a>
        </h4>
        <div class="editor">
          <img :src="images.imageWaitingForCrop" alt="" id="editor">
        </div>
        <div class="btn-row">
          <bk-button theme="primary" class="btn-list" @click="confirmCrop">{{$t('保存')}}</bk-button>
          <bk-button theme="default" class="btn-list" @click="closeImageEditor">{{$t('取消')}}</bk-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Cropper from 'cropperjs';

export default {
  props: {
    imgSrc: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      images: {
        coverImg: '',
        coverObj: null,
        coverBtn: null,
        coverUploading: false,
        avatarImg: '',
        avatarObj: null,
        avatarBtn: null,
        avatarUploading: false,
        isShowImageEditor: false,
        editImageType: '',
        imageWaitingForCrop: '',
        cropper: null,
      },
    };
  },
  methods: {
    handleLoadAvatarError() {
      this.images.avatarImg = this.$store.state.localAvatar;
    },
    imgOnChange(e, type) {
      const images = this.images;
      const target = e.target;
      const btnType = `${type}Btn`;
      const objType = `${type}Obj`;
      images.editImageType = type;
      images.isShowImageEditor = true;
      images[btnType] = target;
      if (target.files) {
        images[objType] = target.files[0];
        images.imageWaitingForCrop = this.createLocalURL(images[objType]);
      } else {
        target.select();
        images.imageWaitingForCrop = document.selection.createRange().text;
      }
      this.$nextTick(() => {
        this.initCropper();
      });
    },
    initCropper() {
      const options = {
        cropBoxResizable: false,
      };
      options.aspectRatio = 1;
      options.minCropBoxWidth = 128;
      options.minCropBoxHeight = 128;

      this.images.cropper = new Cropper(document.querySelector('#editor'), options);
    },
    // 裁剪图片确定函数
    confirmCrop() {
      const options = {
        width: 0,
        height: 0,
      };
      const type = this.images.editImageType;
      const loading = `${type}Uploading`;

      if (type === 'cover') {
        options.width = 750;
        options.height = 750;
      } else {
        options.width = 128;
        options.height = 128;
      }

      this.images[loading] = true;
      const base64 = this.images.cropper.getCroppedCanvas(options).toDataURL('image/png');
      this.images.avatarImg = base64;
      this.$emit('getBase64', base64);
      this.closeImageEditor();
    },
    closeImageEditor() {
      const images = this.images;
      this.destroyLocalURL(this.imageWaitingForCrop);
      images.isShowImageEditor = !images.isShowImageEditor;
      images[`${images.editImageType}Btn`].value = '';
      images.cropper.destroy();
    },
    createLocalURL(file) {
      if (window.createObjectURL) {
        return window.createObjectURL(file);
      } if (window.URL) {
        return window.URL.createObjectURL(file);
      } if (window.webkitURL.createObjectURL) {
        return window.webkitURL.createObjectURL(file);
      }
    },
    destroyLocalURL(url) {
      if (window.revokeObjectURL) {
        return window.revokeObjectURL(url);
      } if (window.URL) {
        return window.URL.revokeObjectURL(url);
      } if (window.webkitURL.revokeObjectURL) {
        return window.webkitURL.revokeObjectURL(url);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.user-head-portrait {
  position: absolute;
  top: 17px;
  right: 0;

  &.chang-en {
    right: -20px;
  }

  .head {
    display: block;
    margin-bottom: 7px;
    font-size: 14px;
    font-weight: 400;
    color: rgba(99, 101, 110, 1);
    line-height: 20px;
  }

  .avatar-wrapper {
    position: relative;
    width: 68px;
    height: 68px;

    .avatar-img {
      display: block;
    }

    .avatar-input {
      position: absolute;
      top: 0;
      left: 0;
      width: 68px;
      height: 68px;
      opacity: 0;
      cursor: pointer;
      z-index: 10
    }
  }
}

.personal-pops {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  right: 0;
  background: rgba(0, 0, 0, .6);
  z-index: 10000;

  .pops-content {
    width: 488px;
    height: 340px;
    padding: 20px 24px;
    background: #fff;
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);

    h4 {
      font-size: 20px;
      color: rgba(49, 50, 56, 1);
      line-height: 26px;
      font-weight: 400;
    }

    .icon-user-close {
      font-size: 13px;
    }
  }
}

.editor {
  height: 70%;
  margin: 15px 0;

  img {
    width: 100%;
    height: 100%;
  }
}

.btn-row {
  text-align: right;

  .btn-list {
    margin-right: 10px;
    width: 76px !important;

    &:last-child {
      margin-right: 0;
    }
  }
}
</style>
