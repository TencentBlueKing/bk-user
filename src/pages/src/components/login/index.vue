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
  <div class="bk-login-dialog">
    <div class="bk-login-wrapper">
      <iframe :src="loginData.loginUrl" :width="loginData.width || '400'" :height="loginData.height || '400'"></iframe>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AppAuth',
  props: {
    loginData: {
      type: Object,
      default() {
        return {
          loginUrl: '',
          width: '400',
          height: '400',
        };
      },
    },
  },
};
</script>

<style lang="scss" scoped>
.bk-login-dialog {
  position: fixed;
  left: 0;
  top: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  z-index: 999999999;
  background: rgba(0, 0, 0, .7);

  .bk-login-wrapper {
    display: flex;
    background-color: #fff;
    border-radius: 2%;

    iframe {
      border: none;
      border-radius: 2%;
    }
  }
}
</style>
