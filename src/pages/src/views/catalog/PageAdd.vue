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
  <div class="add-page" data-test-id="list_catalogMetasData">
    <h1 class="page-title">{{$t('新增用户目录')}}</h1>
    <p class="description">{{$t('选择目录类型')}}</p>
    <ul class="catalog-list">
      <li
        v-for="(item, index) in catalogMetas" :key="index" v-cursor="{ active: Boolean(!item.authorized) }"
        :class="['catalog-item', !item.authorized && 'has-not-authority']" @click="handleSelectItem(item)">
        <bk-radio :checked="selectedItem === item" :disabled="!item.authorized"></bk-radio>
        <span class="label">{{item.name}}</span>
        <span class="detail">{{item.description}}</span>
        <bk-button
          v-if="!item.authorized" text style="margin-left: 8px;"
          @click="applyAuth(item)">{{$t('前往申请权限')}}
        </bk-button>
      </li>
    </ul>
    <div class="button-container">
      <bk-button @click="handleCancel">{{$t('取消')}}</bk-button>
      <bk-button
        class="king-button" theme="primary"
        :disabled="!selectedItem" @click="handleContinue">{{$t('继续')}}
      </bk-button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    catalogMetas: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      selectedItem: null,
    };
  },
  created() {
    this.catalogMetas.map((item) => {
      if (item.authorized) {
        this.selectedItem = item;
      }
    });
  },
  methods: {
    handleSelectItem(item) {
      if (item.authorized) {
        this.selectedItem = item;
      }
    },
    applyAuth(item) {
      window.open(item.extra_info.callback_url);
    },
    handleCancel() {
      this.$emit('changePage', 'showPageHome');
    },
    handleContinue() {
      switch (this.selectedItem.type) {
        case 'local':
          this.$emit('changePage', 'showLocalAdd');
          break;
        case 'mad':
          this.$emit('changePage', 'showRemoteAddMad');
          break;
        case 'ldap':
          this.$emit('changePage', 'showRemoteAddLdap');
          break;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../../scss/variable';

.add-page {
  color: $fontGray;
  padding: 40px;
  width: 100%;

  > h1.page-title {
    font-size: 24px;
    font-weight: 400;
    text-align: center;
    line-height: 33px;
    color: $fontPrimary;
  }

  > p.description {
    margin-top: 30px;
    font-size: 14px;
    font-weight: 600;
    line-height: 20px;
  }

  > .catalog-list {
    .catalog-item {
      display: flex;
      align-items: center;
      height: 60px;
      margin-top: 10px;
      padding: 20px;
      border-radius: 2px;
      border: 1px solid #dcdee5;
      font-size: 14px;
      line-height: 20px;
      cursor: pointer;

      &:hover {
        box-shadow: 0 2px 4px 0 rgba(58, 132, 255, .1);
        border: 1px solid #a3c5fd;
      }

      &.has-not-authority {
        border-color: #f0f1f5;
        background-color: #fafbfd;

        &:hover {
          box-shadow: none;
          border: 1px solid #dcdee5;
        }
      }

      > .label {
        flex-shrink: 0;
      }

      > .detail {
        color: $fontLight;
        margin-left: 40px;
        overflow: hidden;
        display: flex;
        -webkit-line-clamp: 2;
        box-orient: vertical;
      }
    }
  }

  > .button-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
    align-items: center;

    > .king-button {
      margin-left: 10px;
    }
  }
}
</style>
