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
    <div class="steps">
      <bk-steps :steps="steps" :cur-step.sync="current"
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
        <SetPassword
          v-show="current === 2"
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
import SetPassword from '@/components/catalog/operation/SetPassword';

export default {
  components: {
    SetBasic,
    SetPassword,
  },
  data() {
    return {
      isLoading: false,
      current: 1,
      steps: [
        { title: this.$t('基本设置'), icon: 1 },
        { title: this.$t('密码设置'), icon: 2 },
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
        } else {
          // 配置基本信息
          await this.$store.dispatch('catalog/ajaxPutCatalog', {
            id: this.catalogId,
            data: this.basicInfo,
          });
          this.$bus.$emit('updateCatalogList');
          this.current += 1;
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
          data: this.$convertPassportInfoArray(this.passportInfo),
        });
        this.$bus.$emit('updateCatalogList');
        this.messageSuccess(this.$t('保存成功'));
        this.$emit('changePage', 'showPageHome');
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>
