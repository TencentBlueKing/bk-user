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
      <bk-steps :steps="steps" :cur-step.sync="current" direction="vertical" class="king-steps"></bk-steps>
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
        <SetConnection
          v-show="current === 2"
          type="add"
          :catalog-id="catalogId"
          :connection-info="connectionInfo"
          @cancel="$emit('cancel')"
          @previous="handlePrevious"
          @next="handleNext" />
        <!--  步骤三 -->
        <SetField
          v-show="current === 3"
          type="add"
          :catalog-id="catalogId"
          :catalog-name="catalogName"
          :fields-info="fieldsInfo"
          :custom-field="customField"
          :catalog-type="catalogType"
          @cancel="$emit('cancel')"
          @previous="handlePrevious"
          @push="handlePush" />
      </div>
    </div>
    <!-- loading 时的遮罩层 -->
    <div v-show="isLoading" class="loading-cover" @click.stop></div>
  </div>
</template>

<script>
import SetBasic from '@/components/catalog/operation/SetBasic';
import SetConnection from '@/components/catalog/operation/SetConnection';
import SetField from '@/components/catalog/operation/SetField';

export default {
  components: {
    SetBasic,
    SetConnection,
    SetField,
  },
  props: {
    catalogType: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      isLoading: false,
      current: 1,
      steps: [
        { title: this.$t('基本设置'), icon: 1 },
        { title: this.$t('连接设置'), icon: 2 },
        { title: this.$t('字段配置'), icon: 3 },
      ],
      catalogId: null,
      catalogName: '',
      connectionHasCreated: false,
      // 第一步 基本设置
      basicInfo: {
        // 目录名
        display_name: '',
        // 登录域
        domain: '',
        // 是否启用
        activated: true,
      },
      connectionInfo: null,
      fieldsInfo: null,
      // 自定义字段
      customField: [],
    };
  },
  created() {
    this.connectionInfo = JSON.parse(JSON.stringify(this.$store.state.catalog.defaults.connection));
    if (this.catalogType === 'mad') {
      this.fieldsInfo = JSON.parse(JSON.stringify(this.$store.state.catalog.defaults.fieldsMad));
    } else if (this.catalogType === 'ldap') {
      this.fieldsInfo = JSON.parse(JSON.stringify(this.$store.state.catalog.defaults.fieldsLdap));
    }
  },
  mounted() {
    this.$store.dispatch('setting/getFields').then((res) => {
      this.customField = this.$convertCustomField(res.data);
    });
  },
  methods: {
    // 上一步
    handlePrevious() {
      this.current -= 1;
    },
    // 下一步
    async handleNext() {
      try {
        this.isLoading = true;
        if (this.current === 1) {
          // 第一步基本设置的下一步
          if (this.catalogId === null) {
            // 创建 mad 目录
            const res = await this.$store.dispatch('catalog/ajaxPostCatalog', {
              type: this.catalogType,
              data: this.basicInfo,
            });
            this.$bus.$emit('updateCatalogList');
            this.catalogId = res.data.id;
            this.catalogName = res.data.display_name;
            this.current += 1;
          } else {
            // 目录已经创建，修改基本信息
            const res = await this.$store.dispatch('catalog/ajaxPatchCatalog', {
              id: this.catalogId,
              data: this.basicInfo,
            });
            this.$bus.$emit('updateCatalogList');
            this.catalogName = res.data.display_name;
            this.current += 1;
          }
        } else if (this.current === 2) {
          // 第二步连接设置的下一步
          const action = this.connectionHasCreated ? 'catalog/ajaxPutConnection' : 'catalog/ajaxPostConnection';
          await this.$store.dispatch(action, {
            id: this.catalogId,
            data: this.$convertObjectToArray(this.connectionInfo),
          });
          this.$bus.$emit('updateCatalogList');
          this.connectionHasCreated = true;
          this.current += 1;
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
    async handlePush(data) {
      try {
        this.isLoading = true;
        this.fieldsInfo.extend.dynamic_fields_mapping = data;
        await this.$store.dispatch('catalog/ajaxPostFields', {
          id: this.catalogId,
          data: this.$convertObjectToArray(this.fieldsInfo),
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
  },
};
</script>
