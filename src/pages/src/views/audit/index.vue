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
  <div class="audit-wrapper">
    <div class="audit-heard-wrapper">
      <div class="date-input-container">
        <span class="desc">{{$t('时间')}}</span>
        <bk-date-picker
          v-model="searchCondition.dateRange"
          class="king-date-picker"
          font-size="14"
          type="datetimerange"
          :clearable="false"
          :shortcuts="shortcuts"
          @pick-success="initUserList(panelActive)"
        ></bk-date-picker>
      </div>
      <bk-input
        v-model="searchCondition.keyword"
        v-if="panelActive === 'operate'"
        class="king-input-search"
        style="width: 400px;"
        :placeholder="$t('搜索操作用户、操作对象、操作类型')"
        :clearable="true"
        :left-icon="'bk-icon icon-search'"
        @clear="handleClear"
        @left-icon-click="getSearchInfo"
        @enter="getSearchInfo">
      </bk-input>
      <bk-search-select
        v-else
        v-model="tableSearchKey"
        class="king-input-search"
        style="width: 400px;"
        :data="searchFilterList"
        :show-condition="false"
        :placeholder="$t('搜索登录用户、登录状态')"
        :clearable="true"
        @change="getSearchInfo"
        @search="getSearchInfo"
        @clear="handleClear" />
    </div>
    <bk-tab :active.sync="panelActive" type="card" ext-cls="audit-panel-class">
      <bk-tab-panel
        v-for="(panel, index) in panels"
        v-bind="panel"
        :key="index">
      </bk-tab-panel>
      <div class="derive" v-if="panelActive === 'login'" @click="Auditderive">{{$t('审计导出')}}</div>
      <bk-table
        v-bkloading="{ isLoading: basicLoading }"
        :data="auditList"
        :pagination="paginationConfig"
        @page-change="changeCurrentPage"
        @page-limit-change="changeLimitPage">
        <template slot="empty">
          <EmptyComponent
            :is-data-empty="isDataEmpty"
            :is-search-empty="isSearchEmpty"
            :is-data-error="isDataError"
            @handleEmpty="handleEmpty"
            @handleUpdate="getSearchInfo"></EmptyComponent>
        </template>
        <template v-for="(field, index) in headTitle">
          <bk-table-column
            :key="index"
            v-if="field.key === 'is_success'"
            :label="field.name"
            :prop="field.key"
            show-overflow-tooltip>
            <template slot-scope="props">
              <span v-bk-tooltips="errorTips(props.row)">
                <i :class="['status', { 'status-fail': !props.row.is_success }]" />
                <label>{{props.row.is_success ? $t('成功') : $t('失败')}}</label>
              </span>
            </template>
          </bk-table-column>
          <bk-table-column
            v-else
            :label="field.name"
            :prop="field.key"
            :key="field.key"
            show-overflow-tooltip>
            <template slot-scope="props">
              <p>{{ props.row[field.key] || '--' }}</p>
            </template>
          </bk-table-column>
        </template>
      </bk-table>
    </bk-tab>
  </div>
</template>

<script>
import EmptyComponent from '@/components/empty';
export default {
  name: 'AuditIndex',
  components: { EmptyComponent },
  data() {
    return {
      basicLoading: true,
      errorMessage: this.$t('审计日志为空, 无法导出'),
      paginationConfig: {
        current: 1,
        count: 1,
        limit: 10,
      },
      searchCondition: {
        dateRange: [
          new Date(Date.now() - 86400000),
          new Date(),
        ],
        keyword: '',
        username: '',
        is_success: '',
      },
      // 记录搜索过的关键字，blur 的时候如果和当前关键字不一样就刷新表格
      searchedKey: '',
      auditList: [],
      shortcuts: [
        {
          text: this.$t('昨天'),
          value() {
            const start = new Date();
            start.setTime(start.getTime() - 86400000);
            const end = new Date();
            return [start, end];
          },
        },
        {
          text: this.$t('最近一周'),
          value() {
            const start = new Date();
            start.setTime(start.getTime() - 86400000 * 7);
            const end = new Date();
            return [start, end];
          },
        },
        {
          text: this.$t('最近一个月'),
          value() {
            const start = new Date();
            start.setTime(start.getTime() - 86400000 * 30);
            const end = new Date();
            return [start, end];
          },
        },
        {
          text: this.$t('最近三个月'),
          value() {
            const start = new Date();
            start.setTime(start.getTime() - 86400000 * 90);
            const end = new Date();
            return [start, end];
          },
        },
      ],
      panels: [
        { name: 'operate', label: this.$t('操作审计') },
        { name: 'login', label: this.$t('登录审计') },
      ],
      panelActive: 'operate',
      auditHead: [
        { key: 'operator', name: this.$t('操作用户') },
        { key: 'display_name', name: this.$t('用户全名') },
        { key: 'datetime', name: this.$t('时间') },
        { key: 'client_ip', name: this.$t('来源 IP') },
        { key: 'operation', name: this.$t('操作类型') },
        { key: 'category_display_name', name: this.$t('用户目录') },
        { key: 'target_obj', name: this.$t('操作对象') },
      ],
      /** 登录审计表头 */
      loginHead: [
        { key: 'username', name: this.$t('登录用户') },
        { key: 'display_name', name: this.$t('用户全名') },
        { key: 'datetime', name: this.$t('登录时间') },
        { key: 'client_ip', name: this.$t('登录来源IP') },
        { key: 'is_success', name: this.$t('登录状态') },
      ],
      // 暂无数据
      isDataEmpty: false,
      // 搜索结果为空
      isSearchEmpty: false,
      // 数据异常
      isDataError: false,
      tableSearchKey: '',
      searchSelectList: [
        { id: 'username', name: this.$t('登录用户') },
        { id: 'is_success', name: this.$t('登录状态'),
          children: [{ id: 1, name: this.$t('成功') }, { id: 0, name: this.$t('失败') }],
        },
      ],
      searchFilterList: [],
    };
  },
  computed: {
    /** 表头展示字段 */
    headTitle() {
      return this.isOperate ? this.auditHead : this.loginHead;
    },
    /** 是否为操作审计 */
    isOperate() {
      return this.panelActive === 'operate';
    },
  },
  watch: {
    'panelActive'(val) {
      this.searchCondition.keyword = '';
      this.tableSearchKey = '';
      this.auditList = [];
      this.paginationConfig.current = 1;
      this.initUserList(val);
    },
    tableSearchKey: {
      immediate: true,
      handler(val) {
        this.searchFilterList = this.searchSelectList;
        this.searchCondition.username = '';
        this.searchCondition.is_success = '';
        if (val.length) {
          val.forEach((item) => {
            this.searchFilterList = this.searchFilterList.filter(key => key.id !== item.id);
          });
        }
      },
    },
  },
  mounted() {
    this.initUserList(this.panelActive);
  },
  methods: {
    handleWarning(config) {
      config.message = this.errorMessage;
      config.offsetY = 80;
      this.$bkMessage(config);
    },
    async Auditderive() {
      const startTime = this.getMyDate(this.searchCondition.dateRange[0]);
      const endTime = this.getMyDate(this.searchCondition.dateRange[1]);
      let userName = '';
      let isSuccess = '';
      this.tableSearchKey.length && this.tableSearchKey.forEach((item) => {
        item.id === 'username' ? userName = item.values[0].id : isSuccess = item.values[0].id;
      });
      let url = window.AJAX_URL;
      if (url.endsWith('/')) {
        // 去掉末尾的斜杠
        url = url.slice(0, url.length - 1);
      }
      if (!url.startsWith('http')) {
        // tips: 后端提供的 SITE_URL 需以 / 开头
        url = window.location.origin + url;
      }
      if (this.panelActive === 'login' && this.auditList.length === 0) {
        this.handleWarning({ theme: 'error' });
      } else {
        url = `${url}/api/v1/web/audits/logs/types/login/operations/export/?start_time=${startTime}&end_time=${endTime}&username=${userName}&is_success=${isSuccess}`;
        window.open(url);
      }
    },
    getMyDate(date) {
      // return date.getFullYear() + '-' + (date.getMonth() + 1)
      // `${+ '-' + date.getDate()}-${date.toString().match(/\d\d:\d\d:\d\d/)[0]}`;
      return date.toISOString();
    },
    async initUserList(panelActive) {
      try {
        this.basicLoading = true;
        this.isDataEmpty = false;
        this.isSearchEmpty = false;
        this.isDataError = false;
        const currentStatus = panelActive === 'operate';
        const startTime = this.getMyDate(this.searchCondition.dateRange[0]);
        const endTime = this.getMyDate(this.searchCondition.dateRange[1]);
        if (this.tableSearchKey.length) {
          this.tableSearchKey.forEach((item) => {
            this.searchCondition[item.id] = item.values[0].id;
          });
        }
        const auditParam = {
          startTime,
          endTime,
          pageSize: this.paginationConfig.limit,
          page: this.paginationConfig.current,
        };
        const param = currentStatus
          ? Object.assign(auditParam, { keyword: this.searchCondition.keyword })
          : Object.assign(auditParam, {
            userName: this.searchCondition.username,
            isSuccess: this.searchCondition.is_success,
          });
        const url = currentStatus ? 'audit/getList' : 'audit/getLoginList';
        const res = await this.$store.dispatch(url, param);
        this.auditList = res.data.results;
        // 计算页码数
        this.paginationConfig.count = res.data.count;
        if (res.data.count === 0 && currentStatus) {
          this.searchCondition.keyword === '' ? this.isDataEmpty = true : this.isSearchEmpty = true;
        } else if (res.data.count === 0 && !currentStatus) {
          this.tableSearchKey === '' ? this.isDataEmpty = true : this.isSearchEmpty = true;
        }
      } catch (e) {
        console.warn(e);
        this.isDataError = true;
      } finally {
        this.basicLoading = false;
        this.searchedKey = this.searchCondition.keyword;
        this.$store.commit('updateInitLoading', false);
      }
    },
    // eslint-disable-next-line no-unused-vars
    changeCurrentPage(current) {
      this.paginationConfig.current = current;
      this.initUserList(this.panelActive);
    },
    changeLimitPage(limit) {
      this.paginationConfig.current = 1;
      this.paginationConfig.limit = limit;
      this.initUserList(this.panelActive);
    },
    async getSearchInfo() {
      this.paginationConfig.current = 1;
      this.initUserList(this.panelActive);
    },
    handleClear() {
      if (this.searchedKey !== '' || this.tableSearchKey !== '') {
        this.getSearchInfo();
      }
    },
    handleEmpty() {
      this.searchCondition.keyword = '';
      this.tableSearchKey = '';
      this.getSearchInfo();
    },
    /** 登录审计记录失败原因tips */
    errorTips(item) {
      return {
        disabled: item.is_success,
        placement: 'right-start',
        content: `${item.reason}`,
      };
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../../scss/mixins/scroller.scss';

.audit-wrapper {
  height: 100%;
  color: #63656e;
  padding: 40px;
  // 时间选择器和查询框
  .audit-heard-wrapper {
    display: flex;
    justify-content: space-between;

    .date-input-container {
      display: flex;
      align-items: center;
      font-size: 14px;

      .desc {
        margin-right: 15px;
      }
    }
  }
  .derive {
    position: absolute;
    font-size: 14px;
    cursor: pointer;
    color: #3a84ff;
    right: 40px;
    top: 110px;
    z-index: 999;
  }
  // 表格
  ::v-deep .bk-table-body-wrapper {
    color: #888;
    max-height: calc(100vh - 400px);
    overflow-y: auto;
    @include scroller($backgroundColor: #e6e9ea, $width: 4px);
  }

  .status {
    display: inline-block;
    width: 8px;
    height: 8px;
    border: 1px solid #3fc06d;
    background: #e5f6ea;
    border-radius: 100%;
    margin-right: 5px;
  }

  .status-fail {
    background: #fdd;
    border: 1px solid #ea3636;
  }

  ::v-deep .audit-panel-class {
    margin-top: 20px;

    .bk-tab-section {
      padding: 20px 20px 30px 20px;
    }
  }
}
  .confirmExport{
    text-align: center;
    font-weight: normal;
  }
</style>
