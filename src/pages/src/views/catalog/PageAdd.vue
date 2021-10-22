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
  <div class="add-page" data-test-id="list_catalogMetasData">
    <h1 class="page-title">{{$t('新增用户目录')}}</h1>
    <p class="description">{{$t('选择目录类型')}}</p>
    <ul class="catalog-list">
      <li v-for="(item, index) in catalogMetas" :key="index" v-cursor="{ active: Boolean(!item.authorized) }"
          :class="['catalog-item', !item.authorized && 'has-not-authority']" @click="handleSelectItem(item)">
        <bk-radio :checked="selectedItem === item" :disabled="!item.authorized"></bk-radio>
        <span class="label">{{item.name}}</span>
        <span class="detail">{{item.description}}</span>
        <bk-button v-if="!item.authorized" text style="margin-left: 8px;"
                   @click="applyAuth(item)">{{$t('前往申请权限')}}
        </bk-button>
      </li>
    </ul>
    <div class="button-container">
      <bk-button @click="handleCancel">{{$t('取消')}}</bk-button>
      <bk-button class="king-button" theme="primary"
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
    for (const item of this.catalogMetas) {
      if (item.authorized) {
        this.selectedItem = item;
        break;
      }
    }
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
