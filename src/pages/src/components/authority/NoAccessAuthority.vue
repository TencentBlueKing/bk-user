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
  <div class="exception-wrap">
    <bk-exception class="exception-wrap-item" type="403">
      <span>{{ $t('无该应用访问权限') }}</span>
      <div class="text-subtitle">{{ noAccessAuthData }}</div>
    </bk-exception>
  </div>
</template>

<script>
export default {
  props: {
    noAccessAuthData: {
      type: String,
      default: '',
    },
  },
};
</script>

<style lang="scss" scoped>
.exception-wrap {
  width: 100%;
  height: 100%;
  .exception-wrap-item {
    height: 420px;
    padding-top: 48px;
    .text-subtitle {
      color: #979BA5;
      font-size: 16px;
      text-align: center;
      margin-top: 14px;
    }
  }
}
</style>
