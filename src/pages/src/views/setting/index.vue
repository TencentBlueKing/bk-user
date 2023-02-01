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
  <div class="setting-wrapper clearfix">
    <div class="setting-left">
      <a
        href="javascript:void(0);"
        :class="['nav-item', { 'active': index === curIndex }]"
        v-for="(item, index) in settingList" :key="index"
        @click="changTab(index)">
        {{item}}
      </a>
    </div>
    <div class="setting-right">
      <FieldsSetting v-if="curIndex === 0" />
    </div>
  </div>
</template>

<script>
import FieldsSetting from './FieldsSetting';

export default {
  name: 'SettingIndex',
  components: {
    FieldsSetting,
  },
  data() {
    return {
      isNav: false,
      settingList: [this.$t('用户字段设置')],
      curIndex: 0,
    };
  },
  methods: {
    changTab(index) {
      this.curIndex = index;
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../scss/mixins/clearfix.scss';

  .setting-wrapper {
    height: 100%;
    border: 1px solid #dcdee5;
    padding: 40px;
  }

  .setting-left {
    padding-top: 14px;
    float: left;
    width: 220px;
    height: 100%;
    background: #fafbfd;
    border: 1px solid #dcdee5;

    .nav-item {
      padding: 11px 0 11px 30px;
      display: block;
      font-size: 14px;
      font-weight: 400;
      color: rgba(99, 101, 110, 1);
      line-height: 20px;

      &.active {
        color: rgba(58, 132, 255, 1);
        background: #e1ecff;
      }
    }
  }

  .setting-right {
    float: left;
    width: calc(100% - 220px);
    min-width: 958px;
    height: 100%;
    border: 1px solid #dcdee5;
    border-left: none;
  }
</style>
