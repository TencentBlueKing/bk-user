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
