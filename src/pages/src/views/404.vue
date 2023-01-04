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
  <div class="exception-box">
    <img src="https://magicbox.bk.tencent.com/static_api/v3/components/exception_building/images/building.png" alt="">
    <h1>{{$t('页面找不到了')}}</h1>
  </div>
</template>

<script>
export default {
  name: 'PageNotFound',
  data() {
    return {};
  },
};
</script>

<style lang="scss" scoped>
.exception-box {
  text-align: center;
  margin: auto;

  img {
    width: 300px;
    margin-top: 100px;
  }

  h1 {
    margin-top: 32px;
    font-size: 20px;
    font-weight: 400;
  }
}
</style>
