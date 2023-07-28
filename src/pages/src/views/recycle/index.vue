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
  <div class="recycle-wrapper" v-bkloading="{ isLoading, zIndex: 0 }">
    <header>
      <div class="header-title">{{ $t('回收站') }}</div>
      <p class="header-subtitle">
        {{ $t('回收站将自动保存') }}
        <span v-bk-tooltips.bottom="$t('由 admin 在 [回收策略设置] 中统一配置')">
          <a>{{ retentionDays }}</a>
          {{ $t('天') }}
        </span>{{ $t('内删除的数据，数据过期后将无法找回。') }}
      </p>
    </header>
    <div class="recycle-content">
      <bk-tab
        ext-cls="recycle-content-tab"
        :active.sync="active">
        <bk-tab-panel
          v-for="panel in panels"
          v-bind="panel"
          :key="panel.name">
          <template slot="label">
            <span class="panel-name">{{panel.label}}</span>
            <i class="panel-count">{{panel.count}}</i>
          </template>
          <!-- <ProfileTab
            ref="profile"
            v-if="panel.name === 'profile'"
            :data-list="profileData.results"
            :count="profileData.count"
            :is-data-empty="isDataEmpty"
            :is-search-empty="isSearchEmpty"
            :is-data-error="isDataError"
            @searchList="searchProfile" />
          <DepartmentTab
            ref="department"
            v-else-if="panel.name === 'department'"
            :data-list="departmentData.results"
            :count="departmentData.count"
            :is-data-empty="isDataEmpty"
            :is-search-empty="isSearchEmpty"
            :is-data-error="isDataError"
            @searchList="searchDepartment" /> -->
          <CategoryTab
            ref="category"
            :data-list="categoryData.results"
            :count="categoryData.count"
            :is-data-empty="isDataEmpty"
            :is-search-empty="isSearchEmpty"
            :is-data-error="isDataError"
            @searchList="searchCategory"
            @updateList="initCategoryList" />
        </bk-tab-panel>
      </bk-tab>
    </div>
  </div>
</template>

<script>
// import ProfileTab from './tab/ProfileTab.vue';
// import DepartmentTab from './tab/DepartmentTab.vue';
import CategoryTab from './tab/CategoryTab.vue';
export default {
  name: 'RecycleIndex',
  components: {
    // ProfileTab,
    // DepartmentTab,
    CategoryTab,
  },
  data() {
    return {
      panels: [],
      active: 'profile',
      // 保存天数
      retentionDays: null,
      // 数据列表
      dataList: [],
      categoryData: {},
      departmentData: {},
      profileData: {},
      isLoading: false,
      params: {
        pageSize: 10,
        page: 1,
      },
      // 暂无数据
      isDataEmpty: false,
      // 搜索结果为空
      isSearchEmpty: false,
      // 数据异常
      isDataError: false,
    };
  },
  async mounted() {
    try {
      this.isLoading = true;
      this.$store.commit('updateInitLoading', false);
      Promise.all([
        await this.initRecoverySetting(),
        // await this.initProfileList(),
        // await this.initDepartmentList(),
        await this.initCategoryList(),
      ]);
      this.panels = [
        // {
        //   name: 'profile',
        //   label: this.$t('最近删除用户'),
        //   count: this.profileData.count,
        // },
        // {
        //   name: 'department',
        //   label: this.$t('最近删除组织'),
        //   count: this.departmentData.count,
        // },
        {
          name: 'category',
          label: this.$t('最近删除目录'),
          count: this.categoryData.count,
        },
      ];
      this.isLoading = false;
    } catch (e) {
      console.warn(e);
      this.isLoading = false;
    }
  },
  methods: {
    async initRecoverySetting() {
      try {
        const res = await this.$store.dispatch('setting/getGlobalSettings');
        this.retentionDays = res.data[0].value;
      } catch (e) {
        console.warn(e);
      }
    },
    // 最近删除用户列表
    async initProfileList(keyword, limit, current) {
      try {
        this.isLoading = true;
        this.isDataEmpty = false;
        this.isSearchEmpty = false;
        this.isDataError = false;
        this.updatedParams(keyword, limit, current);
        const res = await this.$store.dispatch('setting/getProfileList', this.params);
        if (res.data.count === 0) {
          keyword === '' ? this.isDataEmpty = true : this.isSearchEmpty = true;
        }
        this.profileData = res.data;
        this.isLoading = false;
      } catch (e) {
        console.warn(e);
        this.isDataError = true;
        this.isLoading = false;
      }
    },
    // 最近删除组织列表
    async initDepartmentList(keyword, limit, current) {
      try {
        this.isLoading = true;
        this.isDataEmpty = false;
        this.isSearchEmpty = false;
        this.isDataError = false;
        this.updatedParams(keyword, limit, current);
        const res = await this.$store.dispatch('setting/getDepartmentList', this.params);
        if (res.data.count === 0) {
          keyword === '' ? this.isDataEmpty = true : this.isSearchEmpty = true;
        }
        this.departmentData = res.data;
        this.isLoading = false;
      } catch (e) {
        console.warn(e);
        this.isDataError = true;
        this.isLoading = false;
      }
    },
    // 最近删除目录列表
    async initCategoryList(keyword, limit, current) {
      try {
        this.isLoading = true;
        this.isDataEmpty = false;
        this.isSearchEmpty = false;
        this.isDataError = false;
        this.updatedParams(keyword, limit, current);
        const res = await this.$store.dispatch('setting/getCategoryList', this.params);
        if (res.data.count === 0) {
          !keyword ? this.isDataEmpty = true : this.isSearchEmpty = true;
        }
        this.categoryData = res.data;
        this.isLoading = false;
      } catch (e) {
        console.warn(e);
        this.isDataError = true;
        this.isLoading = false;
      }
    },
    updatedParams(keyword, limit, current) {
      this.params = {
        pageSize: limit ? limit : 10,
        page: current ? current : 1,
        keyword,
      };
    },
    searchProfile(key, limit, current) {
      this.initProfileList(key, limit, current);
    },
    searchDepartment(key, limit, current) {
      this.initDepartmentList(key, limit, current);
    },
    searchCategory(key, limit, current) {
      this.initCategoryList(key, limit, current);
    },
    tabChange(name) {
      switch (name) {
        case 'profile':
          this.$refs.profile[0].tableSearchKey = '';
          return this.initProfileList();
        case 'department':
          this.$refs.department[0].tableSearchKey = '';
          return this.initDepartmentList();
        case 'category':
          this.$refs.category[0].tableSearchKey = '';
          return this.initCategoryList();
      };
    },
  },
};
</script>

<style lang="scss" scoped>
.recycle-wrapper {
  height: 100%;
  background: #f5f7fa;
  header {
    height: 52px;
    line-height: 52px;
    padding: 0 24px;
    background: #FFFFFF;
    box-shadow: 0 1px 1px 0 #00000014;
    display: flex;
    .header-title {
      font-size: 16px;
      color: #313238;
      &::after {
        content: '|';
        width: 1px;
        height: 16px;
        color: #EAEBF0;
        margin: 0 10px;
      }
    }
    .header-subtitle {
      font-size: 12px;
      color: #979BA5;
      span {
        border-bottom: 1px dashed;
        cursor: pointer;
        a {
          color: #EA3636;
          font-weight: 700;
        }
      }
    }
  }
  .recycle-content {
    padding: 24px;
    background: #F5F7FA;
    height: calc(100% - 52px);
    ::v-deep .recycle-content-tab {
      height: 100%;
      .bk-tab-header {
        border: none !important;
        background-image: none !important;
        height: 40px !important;
        background: #F5F7FA;
      }
      .bk-tab-section {
        height: calc(100% - 50px);
        border: none !important;
        background: #fff;
      }
      .bk-tab-label-wrapper {
        .bk-tab-label-list {
          height: 40px !important;
          .bk-tab-label-item {
            border: none !important;
            background: #EAEBF0;
            line-height: 40px !important;
            border-radius: 4px 4px 0 0;
            margin-right: 8px;
            &.active {
              background: #fff;
              .panel-count {
                background: #E1ECFF;
                color: #3A84FF;
              }
            }
          }
        }
      }
      .panel-count {
        min-width: 16px;
        height: 16px;
        padding: 0 8px ;
        line-height: 16px;
        border-radius: 8px;
        text-align: center;
        font-style: normal;
        font-size: 12px;
        color: #979BA5;
        background: #FAFBFD;
      }
      .recycle-content-header {
        display: flex;
        justify-content: right;
        .header-right {
          width: 400px;
        }
      }
      .recycle-content-table {
        margin-top: 20px;
      }
    }
  }
}
</style>
