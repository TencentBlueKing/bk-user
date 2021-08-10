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
  <div class="catalog-operation-container">
    <div class="steps set-steps">
      <div class="catalog-name-container text-overflow-hidden">
        <span class="catalog-name">{{catalogInfo.display_name}}</span>
      </div>
      <div :class="{ 'setting-text': true, active: current === 1 }" @click="current = 1">
        <span>{{$t('基本设置')}}</span>
      </div>
      <div :class="{ 'setting-text': true, active: current === 2 }" @click="current = 2">
        <span>{{$t('密码设置')}}</span>
        <span v-if="passwordHasCreated === false" class="unfinished">{{$t('待完善')}}</span>
      </div>
    </div>
    <div class="detail" v-bkloading="{ isLoading: isLoading }">
      <div class="scroll-container">
        <!-- 基本设置 -->
        <SetBasic
          v-show="current === 1"
          type="set"
          :basic-info="basicInfo"
          @cancel="$emit('changePage', 'showPageHome')"
          @saveBasic="handleSaveBasic" />
        <!-- 密码设置 -->
        <SetPassword
          v-show="current === 2"
          type="set"
          :passport-info="passwordInfo"
          @cancel="$emit('changePage', 'showPageHome')"
          @savePassport="handleSavePassport" />
      </div>
    </div>
    <!-- loading 时的遮罩层 -->
    <div v-show="isLoading" class="loading-cover" @click.stop></div>
  </div>
</template>

<script>
import SetBasic from '@/components/catalog/operation/SetBasic';
import SetPassword from '@/components/catalog/operation/SetPassword';

export default {
  components: {
    SetBasic,
    SetPassword,
  },
  props: {
    catalogInfo: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      current: 1,
      isLoading: false,
      basicInfo: null,
      passwordInfo: null,
      passwordHasCreated: true,
    };
  },
  created() {
    this.getBasicInfo();
    this.getNamespaceInfo();
  },
  methods: {
    getBasicInfo() {
      this.basicInfo = {
        display_name: this.catalogInfo.display_name,
        domain: this.catalogInfo.domain,
        activated: this.catalogInfo.activated,
      };
    },
    async getNamespaceInfo() {
      try {
        this.isLoading = true;
        const passportRes = await this.$store.dispatch('catalog/ajaxGetPassport', { id: this.catalogInfo.id });
        if (passportRes.data.length === 0 && this.catalogInfo.unfilled_namespaces.includes('password')) {
          // password 信息未创建
          this.passwordInfo = JSON.parse(JSON.stringify(this.$store.state.catalog.defaults.password));
          this.passwordHasCreated = false;
          this.current = 2;
        } else {
          this.passwordInfo = this.$convertArrayToObject(passportRes.data);
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
    async handleSaveBasic() {
      try {
        this.isLoading = true;
        await this.$store.dispatch('catalog/ajaxPutCatalog', {
          id: this.catalogInfo.id,
          data: this.basicInfo,
        });
        this.handleSaveSuccess();
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
    async handleSavePassport() {
      try {
        this.isLoading = true;
        const action = this.passwordHasCreated ? 'catalog/ajaxPutPassport' : 'catalog/ajaxPostPassport';
        await this.$store.dispatch(action, {
          id: this.catalogInfo.id,
          data: this.$convertObjectToArray(this.passwordInfo),
        });
        this.handleSaveSuccess();
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
    handleSaveSuccess() {
      this.$bus.$emit('updateCatalogList');
      this.messageSuccess(this.$t('保存成功'));
      this.$emit('changePage', 'showPageHome');
    },
  },
};
</script>
