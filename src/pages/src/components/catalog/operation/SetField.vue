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
  <div v-if="fieldsInfo" class="set-field">
    <!-- 用户基础字段 -->
    <div class="collapse">
      <div class="collapse-item">
        <div class="header-container" @click="expandBasic = !expandBasic">
          <div class="header">
            <span class="title">{{$t('用户基础字段')}}</span>
            <div :class="{ 'collapse-group': true, expanded: expandBasic }">
              <i class="collapse-icon bk-icon icon-angle-double-down"></i>
              <span class="collapse-text">{{expandBasic ? $t('收起') : $t('展开')}}</span>
            </div>
          </div>
        </div>
        <!-- todo 动画 -->
        <div class="content catalog-setting-step" v-show="expandBasic">
          <!-- 选择拉取节点 -->
          <div class="info-container">
            <div class="title-container">
              <h4 class="title">{{$t('选择拉取节点')}}</h4>
              <span class="star">*</span>
            </div>
            <bk-input v-model="basicFields.basic_pull_node" style="width: 360px; "></bk-input>
            <!--<bk-select v-model="basicFields.basic_pull_node" multiple style="width: 360px;"
                           :clearable="false"
                           :placeholder="$t('请选择')">-->
            <!--<bk-option v-for="option in basicPullNodeChoices"
                           :key="option"
                           :id="option"
                           :name="option"></bk-option>-->
            <!--</bk-select>-->
            <p class="description">{{$t('选择拉取节点描述')}}</p>
          </div>

          <!-- 用户对象类 -->
          <CommonInput
            keyword="user_class"
            :info="basicFields"
            :input-bus="inputBus"
            :title="$t('用户对象类')"
            :is-need="true"
            @hasError="handleHasError" />

          <!-- 用户对象过滤 -->
          <CommonInput
            keyword="user_filter"
            :info="basicFields"
            :input-bus="inputBus"
            :title="$t('用户对象过滤')"
            :is-need="true"
            @hasError="handleHasError" />

          <!-- 组织架构类 -->
          <CommonInput
            keyword="organization_class"
            :info="basicFields"
            :input-bus="inputBus"
            :title="$t('组织架构类')"
            :is-need="true"
            @hasError="handleHasError" />
        </div>
      </div>
    </div>

    <!-- 用户基础字段 -->
    <div class="collapse">
      <div class="collapse-item">
        <div class="header-container" @click="expandUser = !expandUser">
          <div class="header">
            <span class="title">{{$t('用户基础字段')}}</span>
            <div :class="{ 'collapse-group': true, expanded: expandUser }">
              <i class="collapse-icon bk-icon icon-angle-double-down"></i>
              <span class="collapse-text">{{expandUser ? $t('收起') : $t('展开')}}</span>
            </div>
          </div>
        </div>
        <div class="content catalog-setting-step" v-show="expandUser">
          <div class="user-directory">
            <p>{{$t('蓝鲸用户管理字段')}}</p>
            <p>{{$t('对应')}} {{catalogType}} {{$t('目录字段')}}</p>
          </div>
          <div class="user-content">
            <div class="user-item">
              <bk-input class="user-key" :value="$t('用户名')" :readonly="true" />
              <bk-input class="user-value" v-model="basicFields.username" />
            </div>
            <div class="user-item">
              <bk-input class="user-key" :value="$t('全名')" :readonly="true" />
              <bk-input class="user-value" v-model="basicFields.display_name" />
            </div>
            <div class="user-item">
              <bk-input class="user-key" :value="$t('邮箱')" :readonly="true" />
              <bk-input class="user-value" v-model="basicFields.email" />
            </div>
            <div class="user-item">
              <bk-input class="user-key" :value="$t('手机号')" :readonly="true" />
              <bk-input class="user-value" v-model="basicFields.telephone" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 自定义字段 -->
    <div class="collapse">
      <div class="collapse-item">
        <div class="header-container" @click="expandCustom = !expandCustom">
          <div class="header">
            <span class="title">{{$t('自定义字段')}}
            </span>
            <div :class="{ 'collapse-group': true, expanded: expandCustom }">
              <i class="collapse-icon bk-icon icon-angle-double-down"></i>
              <span class="collapse-text">{{expandCustom ? $t('收起') : $t('展开')}}</span>
            </div>
          </div>
        </div>
        <div class="content catalog-setting-step" v-show="expandCustom">
          <div class="user-directory">
            <p>{{$t('蓝鲸用户管理字段')}}</p>
            <p>{{$t('对应')}} {{catalogType}} {{$t('目录字段')}}</p>
          </div>
          <addCustomField :type="type" :custom-field="customField" @upAddFieldList="getAddFieldList" />
          <setCustomField
            :type="type" :extend-fields="extendFields" :custom-field="customField"
            :current="current" @upSetFieldList="getSetFieldList" />
        </div>
      </div>
    </div>

    <!-- 用户组字段 -->
    <div class="collapse">
      <div class="collapse-item">
        <div class="header-container" @click="expandGroup = !expandGroup">
          <div class="header">
            <span class="title">{{$t('用户组字段')}}
              <span class="namespace-description">({{$t('用户组配置描述')}})</span>
            </span>
            <div :class="{ 'collapse-group': true, expanded: expandGroup }">
              <i class="collapse-icon bk-icon icon-angle-double-down"></i>
              <span class="collapse-text">{{expandGroup ? $t('收起') : $t('展开')}}</span>
            </div>
          </div>
        </div>
        <!-- todo 动画 -->
        <div class="content catalog-setting-step" v-show="expandGroup">
          <!-- 用户组对象类 -->
          <CommonInput
            keyword="user_group_class"
            :info="groupFields"
            :input-bus="inputBus"
            :title="$t('用户组对象类')"
            :is-need="false"
            @hasError="handleHasError" />

          <!-- 用户组对象过滤 -->
          <CommonInput
            keyword="user_group_filter"
            :info="groupFields"
            :input-bus="inputBus"
            :title="$t('用户组对象过滤')"
            :is-need="false"
            @hasError="handleHasError" />

          <!-- 用户组名字段 -->
          <CommonInput
            keyword="user_group_name"
            :info="groupFields"
            :input-bus="inputBus"
            :title="$t('用户组名字段')"
            :is-need="false"
            @hasError="handleHasError" />


          <!-- 用户组描述字段 -->
          <CommonInput
            keyword="user_group_description"
            :info="groupFields"
            :input-bus="inputBus"
            :title="$t('用户组描述字段')"
            :is-need="false"
            @hasError="handleHasError" />


          <!-- 用户组关联字段 -->
          <CommonInput
            keyword="user_member_of"
            :info="groupFields"
            :input-bus="inputBus"
            :title="$t('用户组关联字段')"
            :description="$t('用户组关联字段描述')"
            :is-need="false"
            @hasError="handleHasError" />

        </div>
      </div>
    </div>

    <!-- 测试连接 -->
    <TestConnection :test-info="testInfo" />

    <!-- 新增用户目录 -->
    <div class="save-setting-buttons" v-if="type === 'add'">
      <bk-button @click="$emit('cancel')">
        {{$t('返回列表')}}
      </bk-button>
      <bk-button @click="$emit('previous')" class="king-button">
        {{$t('上一步')}}
      </bk-button>
      <bk-button theme="primary" @click="handlePush" class="king-button">
        {{$t('提交')}}
      </bk-button>
    </div>

    <!-- 编辑用户目录设置 -->
    <div class="save-setting-buttons" v-if="type === 'set'">
      <bk-button theme="primary" @click="handleSave">
        {{$t('保存')}}
      </bk-button>
      <bk-button @click="$emit('cancel')" class="king-button">
        {{$t('取消')}}
      </bk-button>
    </div>
  </div>
</template>

<script>
import Vue from 'vue';
import CommonInput from '@/components/catalog/operation/CommonInput';
import TestConnection from '@/components/catalog/operation/TestConnection';
import addCustomField  from './addCustomField.vue';
import setCustomField from './setCustomField.vue';

export default {
  components: {
    CommonInput,
    TestConnection,
    addCustomField,
    setCustomField,
  },
  props: {
    // add 增加目录 set 修改目录设置
    type: {
      type: String,
      required: true,
    },
    fieldsInfo: {
      type: Object,
      default: null,
    },
    catalogId: {
      type: Number,
      default: null,
    },
    catalogName: {
      type: String,
      default: '',
    },
    customField: {
      type: Array,
      default: () => ([]),
    },
    catalogType: {
      type: String,
      default: '',
    },
    current: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      // 展开基础字段、扩展字段，用户组字段
      expandBasic: true,
      expandExtensional: true,
      expandGroup: true,
      expandUser: true,
      expandCustom: true,
      // 表单验证是否有错误
      hasError: false,
      inputBus: new Vue(),
      fieldsList: [],
    };
  },
  computed: {
    basicFields() {
      return this.fieldsInfo ? this.fieldsInfo.basic : null;
    },
    extendFields() {
      return this.fieldsInfo ? this.fieldsInfo.extend.dynamic_fields_mapping : null;
    },
    groupFields() {
      return this.fieldsInfo ? this.fieldsInfo.group : null;
    },
    // basicPullNodeChoices () {
    //     return this.$store.state.catalog.choices.basic_pull_node
    // },
    // groupPullNodeChoices () {
    //     return this.$store.state.catalog.choices.group_pull_node
    // },
    // madFieldsChoices () {
    //     return this.$store.state.catalog.choices.mad_fields
    // },
    bkFieldsChoices() {
      return this.$store.state.catalog.choices.bk_fields;
    },
    testInfo() {
      return {
        action: 'catalog/ajaxTestField',
        id: this.catalogId,
        data: this.fieldsInfo,
      };
    },
  },
  methods: {
    handlePush() {
      this.validate() && this.$emit('push', this.fieldsList);
    },
    handleSave() {
      this.validate() && this.$emit('saveField', this.fieldsList);
    },
    handleHasError() {
      this.hasError = true;
    },
    validate() {
      // 表单验证
      this.hasError = false;
      // 在 CommonInput 组件里面验证必填的值是否有值
      this.inputBus.$emit('validateCatalogInfo');
      if (this.hasError === false) {
        return true;
      }
      this.$nextTick(() => {
        const els = this.$el.getElementsByClassName('error');
        if (els.length) {
          els[0].scrollIntoView();
        }
      });
      return false;
    },
    getAddFieldList(data) {
      this.fieldsList = data;
    },
    getSetFieldList(data) {
      this.fieldsList = data;
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../../../scss/variable';

#catalog .set-field {
  padding: 38px 40px 54px;
  font-size: 14px;

  .catalog-setting-step {
    padding: 0 !important;
  }

  .test-connection {
    margin-top: 0 !important;
  }

  > .collapse {
    > .collapse-item {
      display: flow-root;

      > .header-container {
        margin-bottom: 10px;
        padding-bottom: 10px;
        border-bottom: 1px solid $borderColor;

        > .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          height: 22px;
          line-height: 22px;
          border-radius: 2px;
          cursor: pointer;
          transition: background-color .3s;

          &:hover {
            background: #f0f1f5;
            transition: background-color .3s;
          }

          > .title {
            font-weight: bold;

            > .namespace-description {
              margin-top: 8px;
              font-size: 12px;
              font-weight: lighter;
              color: $fontLight;
            }
          }

          > .collapse-group {
            display: flex;
            align-items: center;
            color: $fontGray;

            > .collapse-icon {
              display: flex;
              justify-content: center;
              align-items: center;
              width: 20px;
              height: 20px;
              font-size: 20px;
              transition: transform .2s;
            }

            > .collapse-text {
              font-size: 12px;
              line-height: 20px;
            }

            &.expanded {
              color: $primaryColor;

              > .collapse-icon {
                transform: rotate(-180deg);
                transition: transform .2s;
              }
            }
          }
        }
      }

      > .content {
        margin: 17px 0 20px;

        &.extend-content {
          display: flex;

          .input-container {
            display: flex;
            flex-flow: column;
            width: 435px;

            > .description {
              height: 16px;
              line-height: 19px;
            }

            > .extend-input {
              margin-top: 10px;

              &:first-child {
                margin-top: 7px;
              }

              &:last-child {
                margin-bottom: 17px;
              }
            }
          }

          > .symbol {
            display: flex;
            flex-flow: column;
            width: 28px;

            > span {
              height: 16px;
            }

            > i {
              display: flex;
              justify-content: center;
              align-items: center;
              height: 32px;
              margin-top: 10px;
              font-size: 12px;
              font-weight: bold;
              font-style: normal;
              color: #ff9c01;
            }
          }
        }

        .user-directory {
          display: flex;
          p {
            width: 400px;
            margin-left: 30px;
            line-height: 40px;
            font-size: 16px;
          }
        }
        .user-content {
          .user-item {
            display: flex;
            margin: 15px 0;
            .bk-form-control {
              width: 400px;
              margin-left: 30px;
            }
            .custom-select {
              width: 400px;
              margin-left: 30px;
            }
            .i-add, .i-del {
              font-size: 18px;
              color: #3A84FF;
              line-height: 32px;
              margin-left: 15px;
              &:hover {
                cursor: pointer;
              }
            }
            .delete {
              pointer-events: none;
              cursor: default;
            }
            .user-key {
              position: relative;
              &::before {
                content: '*';
                display: inline;
                width: 30px;
                height: 30px;
                position: absolute;
                left: -19px;
                top: 9px;
                font-size: 14px;
                color: #EA3536;
              }
            }
            .user-value {
              position: relative;
              &::before {
                content: '=';
                display: inline;
                width: 30px;
                height: 30px;
                position: absolute;
                left: -20px;
                top: 5px;
                font-size: 14px;
                color: #FE9C00;
              }
            }
          }
        }
      }
    }
  }

  > .save-setting-buttons > .king-button:not(:first-child) {
    margin-left: 10px;
  }
}
</style>
