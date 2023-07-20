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
  <div class="catalog-operation-container">
    <div class="steps set-steps">
      <div class="catalog-name-container text-overflow-hidden">
        <span class="catalog-name">{{catalogInfo.display_name}}</span>
      </div>
      <div
        v-for="(item, index) in localSetConfig"
        :key="index"
        :class="{ 'setting-text': true, active: current === item.key }"
        @click="current = item.key">
        <span>{{item.title}}</span>
        <span v-if="!item.show" class="unfinished">{{$t('待完善')}}</span>
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
        <!-- 账号设置 -->
        <SetAccount
          v-show="current === 2"
          type="set"
          :account-info="accountInfo"
          @cancel="$emit('changePage', 'showPageHome')"
          @saveAccount="handleSaveAccount" />
        <!-- 密码设置 -->
        <SetPassword
          v-show="current === 3"
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
import SetAccount from '@/components/catalog/operation/SetAccount';
import SetPassword from '@/components/catalog/operation/SetPassword';

export default {
  components: {
    SetBasic,
    SetAccount,
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
      accountInfo: {},
      localSetConfig: [
        { title: this.$t('基本设置'), icon: 1, key: 1, show: true },
        { title: this.$t('账号设置'), icon: 2, key: 2, show: true },
        { title: this.$t('密码设置'), icon: 3, key: 3, show: this.passwordHasCreated },
      ],
    };
  },
  watch: {
    passwordHasCreated: {
      immediate: true,
      handler(value) {
        this.localSetConfig[2].show = value;
      },
    },
  },
  created() {
    this.getBasicInfo();
    this.getNamespaceInfo();
    this.getAccountInfo();
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
          this.passwordInfo = JSON.parse(JSON.stringify(this.$store.state.catalog.defaults.password.default));
          this.passwordHasCreated = false;
          this.current = 3;
        } else {
          this.passwordInfo = this.$convertPassportRes(passportRes.data);
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
    async getAccountInfo() {
      try {
        this.isLoading = true;
        const accountRes = await this.$store.dispatch('catalog/ajaxGetAccount', { id: this.catalogInfo.id });
        this.accountInfo = this.$convertAccountRes(accountRes.data);
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
    async handleSaveBasic() {
      try {
        this.isLoading = true;
        await this.$store.dispatch('catalog/ajaxPatchCatalog', {
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
    async handleSaveAccount() {
      try {
        this.isLoading = true;
        await this.$store.dispatch('catalog/ajaxPutAccount', {
          id: this.catalogInfo.id,
          data: this.$convertAccountInfo(this.accountInfo),
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
          data: this.$convertPassportInfoArray(this.passwordInfo, this.passwordInfo),
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
      this.$emit('changePage', 'showPageHome', 'update');
    },
  },
};
</script>
