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
      <div :class="{ 'setting-text': true, active: current === 1 }" @click="current = 1">
        <span>{{$t('基本设置')}}</span>
      </div>
      <div :class="{ 'setting-text': true, active: current === 2 }" @click="current = 2">
        <span>{{$t('连接设置')}}</span>
        <span v-if="connectionHasCreated === false" class="unfinished">{{$t('待完善')}}</span>
      </div>
      <div :class="{ 'setting-text': true, active: current === 3 }" @click="current = 3">
        <span>{{$t('字段配置')}}</span>
        <span v-if="fieldsHasCreated === false" class="unfinished">{{$t('待完善')}}</span>
      </div>
    </div>
    <div class="detail" v-bkloading="{ isLoading: isLoading }">
      <div class="scroll-container">
        <!--  步骤一 -->
        <SetBasic
          v-show="current === 1"
          type="set"
          :basic-info="basicInfo"
          @cancel="$emit('changePage', 'showPageHome')"
          @saveBasic="handleSaveBasic" />
        <!--  步骤二 -->
        <SetConnection
          v-show="current === 2"
          type="set"
          :catalog-id="catalogInfo.id"
          :connection-info="connectionInfo"
          @cancel="$emit('changePage', 'showPageHome')"
          @saveConnection="handleSaveConnection" />
        <!--  步骤三 -->
        <SetField
          v-show="current === 3"
          type="set"
          :catalog-id="catalogInfo.id"
          :catalog-name="catalogInfo.display_name"
          :fields-info="fieldsInfo"
          :custom-field="customField"
          :catalog-type="catalogInfo.type"
          :current="current"
          @cancel="$emit('changePage', 'showPageHome')"
          @saveField="handleSaveField" />
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
    catalogInfo: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      isLoading: false,
      steps: [
        { title: this.$t('基本设置'), icon: 1 },
        { title: this.$t('连接设置'), icon: 2 },
        { title: this.$t('字段配置'), icon: 3 },
      ],
      current: 1,
      // 第一步 基本设置
      basicInfo: null,
      // 第二布 连接设置
      connectionInfo: null,
      connectionHasCreated: true,
      // 第三步 字段配置：用户基础字段
      fieldsInfo: null,
      fieldsHasCreated: true,
      // 自定义字段
      customField: [],
    };
  },
  created() {
    this.getBasicInfo();
    this.getNamespaceInfo();
  },
  mounted() {
    this.$store.dispatch('setting/getFields').then((res) => {
      this.customField = this.$convertCustomField(res.data);
    });
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
        const id = this.catalogInfo.id;
        const [connectionRes, fieldsRes] = await Promise.all([
          this.$store.dispatch('catalog/ajaxGetConnection', { id }),
          this.$store.dispatch('catalog/ajaxGetFields', { id }),
        ]);

        if (fieldsRes.data.length === 0 || this.catalogInfo.unfilled_namespaces.includes('fields')) {
          // fields 信息未创建
          if (this.catalogInfo.type === 'mad') {
            this.fieldsInfo = JSON.parse(JSON.stringify(this.$store.state.catalog.defaults.fieldsMad));
          } else if (this.catalogInfo.type === 'ldap') {
            this.fieldsInfo = JSON.parse(JSON.stringify(this.$store.state.catalog.defaults.fieldsLdap));
          } else {
            console.warn('目录类型有误');
          }
          this.fieldsHasCreated = false;
          this.current = 3;
        } else {
          this.fieldsInfo = this.$convertArrayToObject(fieldsRes.data);
        }

        if (connectionRes.data.length === 0 || this.catalogInfo.unfilled_namespaces.includes('connection')) {
          // connection 信息未创建
          this.connectionInfo = JSON.parse(JSON.stringify(this.$store.state.catalog.defaults.connection));
          this.connectionHasCreated = false;
          this.current = 2;
        } else {
          this.connectionInfo = this.$convertArrayToObject(connectionRes.data);
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
    async handleSaveConnection() {
      try {
        this.isLoading = true;
        const action = this.connectionHasCreated ? 'catalog/ajaxPutConnection' : 'catalog/ajaxPostConnection';
        await this.$store.dispatch(action, {
          id: this.catalogInfo.id,
          data: this.$convertObjectToArray(this.connectionInfo),
        });
        this.handleSaveSuccess();
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
    async handleSaveField(data) {
      try {
        this.isLoading = true;
        this.handleSaveSuccess();
        this.fieldsInfo.extend.dynamic_fields_mapping = data;
        const action = this.fieldsHasCreated ? 'catalog/ajaxPutFields' : 'catalog/ajaxPostFields';
        await this.$store.dispatch(action, {
          id: this.catalogInfo.id,
          data: this.$convertObjectToArray(this.fieldsInfo),
        });
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
