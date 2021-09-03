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
  <div id="catalog">
    <!-- 首页 -->
    <PageHome v-show="showingPage === 'showPageHome'" :catalog-metas="catalogMetas" @changePage="changePage" />
    <!-- 新增目录 -->
    <PageAdd v-if="showingPage === 'showPageAdd'" :catalog-metas="catalogMetas" @changePage="changePage" />
    <!-- 数据更新记录 -->
    <ReDataupdate v-if="showingPage === 'showReDataupdate'" :catalog-metas="catalogMetas"
                  @changePage="changePage">
    </ReDataupdate>
    <!-- 本地用户 -->
    <LocalAdd v-if="showingPage === 'showLocalAdd'" @changePage="changePage" @cancel="handleCancel" />
    <LocalSet v-if="showingPage === 'showLocalSet'" @changePage="changePage" :catalog-info="catalogInfo" />
    <!-- MAD 用户 -->
    <RemoteAdd v-if="showingPage === 'showRemoteAddMad'"
               @changePage="changePage"
               @cancel="handleCancel" catalog-type="mad" />
    <RemoteSet v-if="showingPage === 'showRemoteSetMad'" @changePage="changePage" :catalog-info="catalogInfo" />
    <!-- LDAP 用户 -->
    <RemoteAdd v-if="showingPage === 'showRemoteAddLdap'"
               @changePage="changePage"
               @cancel="handleCancel" catalog-type="ldap" />
    <RemoteSet v-if="showingPage === 'showRemoteSetLdap'" @changePage="changePage" :catalog-info="catalogInfo" />
  </div>
</template>

<script>
import PageHome from './PageHome';
import PageAdd from './PageAdd';
import ReDataupdate from './dataUpdate.vue';
import LocalAdd from './operation/LocalAdd';
import LocalSet from './operation/LocalSet';
import RemoteAdd from './operation/RemoteAdd';
import RemoteSet from './operation/RemoteSet';

export default {
  name: 'Catalog',
  components: {
    PageHome,
    PageAdd,
    LocalAdd,
    LocalSet,
    RemoteAdd,
    RemoteSet,
    ReDataupdate,
  },
  data() {
    return {
      showingPage: 'showPageHome',
      catalogInfo: '',
      catalogMetas: [],
    };
  },
  created() {
    this.initCatalogMetas();

    if (this.$store.state.catalog.defaults.password === null) {
      this.getDefaultInfo();
    }
  },
  methods: {
    async initCatalogMetas() {
      try {
        const res = await this.$store.dispatch('catalog/ajaxGetCatalogMetas');
        this.catalogMetas = res.data;
      } catch (e) {
        console.warn(e);
      }
    },
    changePage(param) {
      if (typeof param === 'object') { // 点击目录名跳转到设置页面
        this.catalogInfo = { ...param };
        switch (param.type) {
          case 'local':
            this.showingPage = 'showLocalSet';
            break;
          case 'mad':
            this.showingPage = 'showRemoteSetMad';
            break;
          case 'ldap':
            this.showingPage = 'showRemoteSetLdap';
            break;
        }
      } else {
        this.showingPage = param;
      }
    },
    handleCancel() {
      this.$bkInfo({
        title: this.$t('您尚未完成所有设置，确定离开页面？'),
        width: 560,
        confirmFn: () => {
          this.changePage('showPageHome');
        },
      });
    },
    async getDefaultInfo() {
      try {
        const [password, connection, fieldsMad, fieldsLdap] = await Promise.all([
          this.$store.dispatch('catalog/ajaxGetDefaultPassport'),
          this.$store.dispatch('catalog/ajaxGetDefaultConnection'),
          this.$store.dispatch('catalog/ajaxGetDefaultFields', { type: 'mad' }),
          this.$store.dispatch('catalog/ajaxGetDefaultFields', { type: 'ldap' }),
        ]);
        const defaults = {
          password: this.convertDefault(password.data),
          connection: this.convertDefault(connection.data),
          fieldsMad: this.convertDefault(fieldsMad.data),
          fieldsLdap: this.convertDefault(fieldsLdap.data),
        };
        try {
          if (defaults.fieldsMad.extend.mad_fields.length === 0) {
            defaults.fieldsMad.extend.mad_fields = new Array(defaults.fieldsMad.extend.bk_fields.length);
          }
          if (defaults.fieldsLdap.extend.mad_fields.length === 0) {
            defaults.fieldsLdap.extend.mad_fields = new Array(defaults.fieldsLdap.extend.bk_fields.length);
          }
        } catch (e) {
          console.warn('fields 默认值缺少 mad_fields 字段', e);
        }
        this.$store.commit('catalog/updateDefaults', defaults);
      } catch (e) {
        console.warn(e);
      }
    },
    convertDefault(arr) {
      try {
        const objectData = {};
        arr.forEach((regionObject) => {
          const { region, key, choices } = regionObject;
          if (!objectData[region]) {
            // 创建 region
            objectData[region] = {};
          }
          // 字段默认值
          objectData[region][key] = regionObject.default;

          const choicesArray = ['ssl_encryption', 'basic_pull_node', 'group_pull_node', 'bk_fields', 'mad_fields'];
          if (choicesArray.includes(key)) {
            this.$store.commit('catalog/updateChoices', {
              ...this.$store.state.catalog.choices,
              [key]: choices,
            });
          }
        });
        return objectData;
      } catch (e) {
        console.warn('参数错误', e);
      }
    },
  },
};
</script>

<style lang="scss">
@import '../../scss/variable';
@import '../../scss/mixins/scroller';

#catalog {
  height: 100%;
  // 新增、设置目录页面公共样式
  .catalog-operation-container {
    display: flex;
    height: 100%;
    color: $fontGray;
    border-radius: 2px 2px 0 0;
    border: 1px solid #dcdee5;

    > .steps {
      width: 201px;
      height: 100%;
      background: #fafbfd;
      border-right: 1px solid #dcdee5;
      // 新增页面左边的步骤
      > .king-steps {
        padding: 30px;
        height: 300px;
        width: 100%;

        &.add-local-step {
          height: 220px;
        }
      }
      // 设置页面左边 bar 的背景
      &.set-steps {
        background: #fafbfd;

        > .catalog-name-container {
          margin: 0 20px 6px;
          padding: 12px 10px 14px;
          border-bottom: 1px solid #dcdee5;

          > .catalog-name {
            height: 19px;
            line-height: 19px;
            font-size: 14px;
            font-weight: bold;
            color: #63656e;
          }
        }
      }
      // 设置页面左边的文字
      > .setting-text {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-left: 30px;
        height: 42px;
        line-height: 42px;
        cursor: pointer;

        > span {
          height: 21px;
          line-height: 20px;
          font-size: 14px;
        }

        > .unfinished {
          margin-right: 20px;
          padding: 2px 4px;
          height: 16px;
          line-height: 12px;
          color: #fff;
          font-weight: 600;
          background: #c4c6cc;
          transform: scale(.8);
          border-radius: 2px;
        }

        &.active {
          color: #3a84ff;
          background: #e1ecff;
        }
      }
    }

    > .detail {
      width: calc(100% - 201px);

      > .scroll-container {
        height: 100%;
        overflow-y: auto;

        @include scroller($backgroundColor: #e6e9ea, $width: 4px);
      }
    }
  }
  // 新增、设置目录各个步骤的公共样式
  .catalog-setting-step {
    padding: 38px 40px 54px;
    display: flow-root;

    .info-container {
      margin-bottom: 17px;

      > .title-container {
        display: flex;

        > .title {
          font-size: 14px;
          line-height: 19px;
          font-weight: normal;
          margin-bottom: 8px;
        }

        > .star {
          height: 19px;
          margin-left: 3px;
          font-size: 14px;
          vertical-align: middle;
          color: #fe5c5c;
        }

        > .tips {
          display: flex;
          align-items: center;
          height: 19px;
          margin-left: 2px;

          > .icon-user--l {
            font-size: 16px;
            outline: none;
          }
        }
      }

      > .input-container {
        display: flex;
        align-items: center;
        height: 32px;
      }

      > p.description {
        margin-top: 8px;
        font-size: 12px;
        line-height: 16px;
        color: $fontLight;
      }
    }

    .error-text {
      font-size: 12px;
      color: #fe5c5c;
    }
  }

  .save-setting-buttons {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    background: #fff;
    border-top: 1px solid $borderColor;
    padding: 10px 0 10px 40px;

    > .king-button:not(:first-child) {
      margin-left: 10px;
    }
  }
}
</style>
