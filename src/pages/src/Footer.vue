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
  <div class="footer-content">
    <div class="link-container">
      <template v-for="(item, index) in footerList">
        <a
          class="footer-link"
          :key="index + 'link'"
          :href="item.link"
          :target="item.is_blank ? '_blank' : '_self'">
          {{ isEnglish ? item.text_en : item.text }}
        </a>
        <span v-if="index !== footerList.length - 1" :key="index + 'gap'" class="gap"> | </span>
      </template>
    </div>
    <div>Copyright © 2012-{{ new Date().getFullYear() }} Tencent BlueKing. All Rights Reserved. V{{ version }}</div>
  </div>
</template>

<script>
import cookie from 'cookie';

export default {
  name: 'FooterBox',
  data() {
    return {
      isEnglish: cookie.parse(document.cookie).blueking_language === 'en',
      footerList: [],
      version: '',
    };
  },
  async created() {
    try {
      const res = await this.$store.dispatch('getFooter');
      this.footerList = res.data.footer || [];
      const versionList = await this.$store.dispatch('getVersionLog');
      this.version = versionList.data.versions[0].version;
    } catch (e) {
      console.warn(e);
    }
  },
};
</script>

<style scoped lang="scss">
.footer-content {
  position: fixed;
  bottom: 0;
  left: 0;
  height: 50px;
  padding-top: 5px;
  display: flex;
  flex-flow: column;
  align-items: center;
  width: 100%;
  line-height: 20px;
  font-size: 12px;

  .link-container {
    display: flex;
    align-items: center;
    height: 20px;

    .footer-link {
      color: #3a84ff;

      &:hover {
        color: #699df4;
      }

      &:active {
        color: #2761dd;
      }
    }

    .gap {
      margin: -2px 4px 0 4px;
    }
  }
}
</style>
