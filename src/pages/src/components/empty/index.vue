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
  <div class="no-data-wrapper">
    <bk-exception v-if="isDataEmpty" type="empty" scene="part">{{$t('暂无数据')}}</bk-exception>
    <bk-exception v-if="isSearchEmpty" type="search-empty" scene="part">
      {{$t('搜索结果为空')}}
      <p>
        {{ $t('可以尝试_调整关键词_或') }}&nbsp;
        <bk-link
          theme="primary"
          @click="$emit('handleEmpty')">{{ $t('清空筛选条件') }}
        </bk-link>
      </p>
    </bk-exception>
    <bk-exception v-if="isDataError" type="500" scene="part">
      {{$t('数据获取异常')}}
      <bk-link
        theme="primary" class="empty-search-text"
        @click="$emit('handleUpdate')">{{ $t('刷新') }}</bk-link>
    </bk-exception>
  </div>
</template>

<script>
export default {
  name: 'EmptyIndex',
  props: {
    isDataEmpty: {
      type: Boolean,
      default: false,
    },
    isSearchEmpty: {
      type: Boolean,
      default: false,
    },
    isDataError: {
      type: Boolean,
      default: false,
    },
  },
};
</script>

<style lang="scss" scoped>
.no-data-wrapper {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;

  .empty-search-text {
    display: block;
    font-size: 12px;
    line-height: 20px;
  }

  ::v-deep .bk-exception-text.part-text {
    line-height: 25px;
    p {
      display: flex;
      font-size: 12px;
      color: #979BA5;
    }
  }
  ::v-deep .bk-link-text {
    font-size: 12px;
  }
}
</style>
