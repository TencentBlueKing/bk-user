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
          <CommonInput keyword="user_class"
                       :info="basicFields"
                       :input-bus="inputBus"
                       :title="$t('用户对象类')"
                       :is-need="true"
                       @hasError="handleHasError" />

          <!-- 用户对象过滤 -->
          <CommonInput keyword="user_filter"
                       :info="basicFields"
                       :input-bus="inputBus"
                       :title="$t('用户对象过滤')"
                       :is-need="true"
                       @hasError="handleHasError" />

          <!-- 组织架构类 -->
          <CommonInput keyword="organization_class"
                       :info="basicFields"
                       :input-bus="inputBus"
                       :title="$t('组织架构类')"
                       :is-need="true"
                       @hasError="handleHasError" />

          <!-- 用户名字段 -->
          <CommonInput keyword="username"
                       :info="basicFields"
                       :input-bus="inputBus"
                       :title="$t('用户名字段')"
                       :description="$t('用户名字段描述')"
                       :is-need="true"
                       @hasError="handleHasError" />

          <!-- 中文名字段 -->
          <CommonInput keyword="display_name"
                       :info="basicFields"
                       :input-bus="inputBus"
                       :title="$t('中文名字段')"
                       :is-need="true"
                       @hasError="handleHasError" />

          <!-- 邮箱字段 -->
          <CommonInput keyword="email"
                       :info="basicFields"
                       :input-bus="inputBus"
                       :title="$t('邮箱字段')"
                       :is-need="true"
                       @hasError="handleHasError" />

          <!-- 手机号字段 -->
          <CommonInput keyword="telephone"
                       :info="basicFields"
                       :input-bus="inputBus"
                       :title="$t('手机号字段')"
                       @hasError="handleHasError" />
        </div>
      </div>
    </div>

    <!--    &lt;!&ndash; 用户扩展字段 &ndash;&gt;-->
    <!--    <div class="collapse">-->
    <!--      <div class="collapse-item">-->
    <!--        <div class="header-container" @click="expandExtensional = !expandExtensional">-->
    <!--          <div class="header">-->
    <!--            <span class="title">{{$t('用户扩展字段')}}</span>-->
    <!--            <div :class="{ 'collapse-group': true, expanded: expandExtensional }">-->
    <!--              <i class="collapse-icon bk-icon icon-angle-double-down"></i>-->
    <!--              <span class="collapse-text">{{expandExtensional ? $t('收起') : $t('展开')}}</span>-->
    <!--            </div>-->
    <!--          </div>-->
    <!--        </div>-->
    <!--        &lt;!&ndash; todo 动画 &ndash;&gt;-->
    <!--        <div class="content extend-content catalog-setting-step" v-show="expandExtensional">-->
    <!--          &lt;!&ndash; 蓝鲸用户管理字段 &ndash;&gt;-->
    <!--          <div class="input-container">-->
    <!--            <span class="description">{{$t('蓝鲸用户管理字段')}}</span>-->
    <!--            <bk-input disabled class="extend-input" v-for="(item, index) in bkFieldsChoices"-->
    <!--                      :key="index"-->
    <!--                      :value="item"></bk-input>-->
    <!--          </div>-->
    <!--          &lt;!&ndash; = &ndash;&gt;-->
    <!--          <div class="symbol">-->
    <!--            <span></span><i v-for="item in bkFieldsChoices" :key="item">=</i>-->
    <!--          </div>-->
    <!--          &lt;!&ndash; 对应用户目录字段 &ndash;&gt;-->
    <!--          <div class="input-container">-->
    <!--            <span class="description">{{$t('对应字段1') + catalogName + $t('对应字段2')}}</span>-->
    <!--            <bk-input-->
    <!--              class="extend-input"-->
    <!--              v-for="(item, index) in bkFieldsChoices"-->
    <!--              v-model="extendFields.mad_fields[index]"-->
    <!--              :key="index"-->
    <!--            ></bk-input>-->
    <!--            &lt;!&ndash;                        <bk-select&ndash;&gt;-->
    <!--            &lt;!&ndash;                            class="extend-input"&ndash;&gt;-->
    <!--            &lt;!&ndash;                            v-for="(item, index) in bkFieldsChoices"&ndash;&gt;-->
    <!--            &lt;!&ndash;                            v-model="extendFields.mad_fields[index]"&ndash;&gt;-->
    <!--            &lt;!&ndash;                            :key="index"&ndash;&gt;-->
    <!--            &lt;!&ndash;                            :clearable="false"&ndash;&gt;-->
    <!--            &lt;!&ndash;                            :placeholder="$t('请选择')">&ndash;&gt;-->
    <!--            &lt;!&ndash;                            <bk-option v-for="option in madFieldsChoices"-->
    <!--                                                       :key="option" :id="option"-->
    <!--                                                       :name="option"></bk-option>&ndash;&gt;-->
    <!--            &lt;!&ndash;                        </bk-select>&ndash;&gt;-->
    <!--          </div>-->
    <!--        </div>-->
    <!--      </div>-->
    <!--    </div>-->

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
          <CommonInput keyword="user_group_class"
                       :info="groupFields"
                       :input-bus="inputBus"
                       :title="$t('用户组对象类')"
                       :is-need="false"
                       @hasError="handleHasError" />

          <!-- 用户组对象过滤 -->
          <CommonInput keyword="user_group_filter"
                       :info="groupFields"
                       :input-bus="inputBus"
                       :title="$t('用户组对象过滤')"
                       :is-need="false"
                       @hasError="handleHasError" />

          <!-- 用户组名字段 -->
          <!-- <CommonInput keyword="user_group_name"
                       :info="groupFields"
                       :input-bus="inputBus"
                       :title="$t('用户组名字段')"
                       :is-need="false"
                       @hasError="handleHasError" />
          -->

          <!-- 用户组描述字段 -->
          <!-- <CommonInput keyword="user_group_description"
                       :info="groupFields"
                       :input-bus="inputBus"
                       :title="$t('用户组描述字段')"
                       :is-need="false"
                       @hasError="handleHasError" />
          -->

          <!-- 用户组关联字段 -->
          <CommonInput keyword="user_member_of"
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

export default {
  components: {
    CommonInput,
    TestConnection,
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
  },
  data() {
    return {
      // 展开基础字段、扩展字段，用户组字段
      expandBasic: true,
      expandExtensional: true,
      expandGroup: true,
      // 表单验证是否有错误
      hasError: false,
      inputBus: new Vue(),
    };
  },
  computed: {
    basicFields() {
      return this.fieldsInfo ? this.fieldsInfo.basic : null;
    },
    extendFields() {
      return this.fieldsInfo ? this.fieldsInfo.extend : null;
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
      this.validate() && this.$emit('push');
    },
    handleSave() {
      this.validate() && this.$emit('saveField');
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
      }
    }
  }

  > .save-setting-buttons > .king-button:not(:first-child) {
    margin-left: 10px;
  }
}
</style>
