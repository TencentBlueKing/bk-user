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
    <div class="steps">
      <bk-steps
        :steps="steps" :cur-step.sync="current"
        direction="vertical" class="king-steps add-local-step">
      </bk-steps>
    </div>
    <div class="detail" v-bkloading="{ isLoading: isLoading }">
      <div class="scroll-container">
        <!--  步骤一 -->
        <SetBasic
          v-show="current === 1"
          type="add"
          :basic-info="basicInfo"
          @cancel="$emit('cancel')"
          @next="handleNext" />
        <!--  步骤二 -->
        <SetAccount
          v-show="current === 2"
          type="add"
          :account-info="accountInfo"
          @cancel="$emit('cancel')"
          @previous="handlePrevious"
          @next="handleNext" />
        <!--  步骤三 -->
        <SetPassword
          v-show="current === 3"
          type="add"
          :passport-info="passportInfo"
          @cancel="$emit('cancel')"
          @previous="handlePrevious"
          @pushPassword="handlePush" />
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
  data() {
    return {
      isLoading: false,
      current: 1,
      steps: [
        { title: this.$t('基本设置'), icon: 1 },
        { title: this.$t('账号设置'), icon: 2 },
        { title: this.$t('密码设置'), icon: 3 },
      ],
      catalogId: null,
      basicInfo: {
        // 目录名
        display_name: '',
        // 登录域
        domain: '',
        // 是否启用
        activated: true,
      },
      passportInfo: null,
      accountInfo: {},
    };
  },
  created() {
    this.passportInfo = this.$convertPassportInfoObject(this.$store.state.catalog.defaults.password);
  },
  methods: {
    // 上一步
    handlePrevious() {
      this.current -= 1;
    },
    // 下一步，创建目录或修改目录
    async handleNext() {
      try {
        this.isLoading = true;
        if (this.catalogId === null) {
          // 创建目录
          const res = await this.$store.dispatch('catalog/ajaxPostCatalog', {
            type: 'local',
            data: this.basicInfo,
          });
          this.$bus.$emit('updateCatalogList');
          this.catalogId = res.data.id;
          this.current += 1;
          this.getAccountInfo();
        } else {
          // 配置基本信息
          await this.$store.dispatch('catalog/ajaxPatchCatalog', {
            id: this.catalogId,
            data: this.basicInfo,
          });
          this.$bus.$emit('updateCatalogList');
          this.current += 1;
        }
        if (this.current === 3) {
          await this.$store.dispatch('catalog/ajaxPutAccount', {
            id: this.catalogId,
            data: this.$convertAccountInfo(this.accountInfo),
          });
          this.$bus.$emit('updateCatalogList');
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
    async handlePush() {
      try {
        this.isLoading = true;
        await this.$store.dispatch('catalog/ajaxPostPassport', {
          id: this.catalogId,
          data: this.$convertPassportInfoArray(this.passportInfo, this.passportInfo),
        });
        this.$bus.$emit('updateCatalogList');
        this.messageSuccess(this.$t('保存成功'));
        this.$emit('changePage', 'showPageHome', 'update');
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
    async getAccountInfo() {
      try {
        this.isLoading = true;
        const accountRes = await this.$store.dispatch('catalog/ajaxGetAccount', { id: this.catalogId });
        this.accountInfo = this.$convertAccountRes(accountRes.data);
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>
