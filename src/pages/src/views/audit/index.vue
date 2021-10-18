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
  <div class="audit-wrapper">
    <div class="audit-heard-wrapper">
      <div class="date-input-container">
        <span class="desc">{{$t('时间')}}</span>
        <bk-date-picker v-model="searchCondition.dateRange"
                        class="king-date-picker"
                        font-size="14"
                        type="datetimerange"
                        :clearable="false"
                        :shortcuts="shortcuts"
                        @pick-success="initUserList(panelActive)"
        ></bk-date-picker>
      </div>
      <bk-input v-model="searchCondition.keyword"
                v-if="panelActive === 'operate'"
                class="king-input-search"
                style="width: 400px;"
                :placeholder="$t('搜索操作人员、操作对象、操作类型')"
                :clearable="true"
                :left-icon="'bk-icon icon-search'"
                @clear="handleClear"
                @left-icon-click="getSearchInfo"
                @enter="getSearchInfo">
      </bk-input>
    </div>
    <bk-tab :active.sync="panelActive" type="card" ext-cls="audit-panel-class">
      <bk-tab-panel
        v-for="(panel, index) in panels"
        v-bind="panel"
        :key="index">
      </bk-tab-panel>
      <div class="derive" v-if="panelActive === 'login'" @click="Auditderive">{{$t('审计导出')}}</div>
      <div class="audit-content-wrapper">
        <div class="thead-container table-container" data-test-id="list_headTitleData">
          <table>
            <thead>
              <tr>
                <th v-for="item in headTitle" :key="item.key">{{item.name}}</th>
              </tr>
            </thead>
          </table>
        </div>
        <div class="tbody-container table-container" v-bkloading="{ isLoading: basicLoading }">
          <div class="scroll-container" ref="auditScroller" data-test-id="list_auditData">
            <table>
              <tbody v-if="auditList.length">
                <tr v-for="(item, index) in auditList" :key="index">
                  <template v-if="isOperate">
                    <td><div class="text-overflow-hidden" v-bk-overflow-tips>{{item.operator}}</div></td>
                    <td><div class="text-overflow-hidden">{{item.datetime | convertIsoTime}}</div></td>
                    <td><div class="text-overflow-hidden" v-bk-overflow-tips>{{item.client_ip}}</div></td>
                    <td><div class="text-overflow-hidden">{{item.operation}}</div></td>
                    <td><div class="text-overflow-hidden" v-bk-overflow-tips>{{item.category_display_name}}</div></td>
                    <td><div class="text-overflow-hidden" v-bk-overflow-tips>{{item.target_obj}}</div></td>
                  </template>
                  <template v-else>
                    <td><div class="text-overflow-hidden">{{item.username}}</div></td>
                    <td><div class="text-overflow-hidden">{{item.datetime | convertIsoTime}}</div></td>
                    <td><div class="text-overflow-hidden">{{item.client_ip}}</div></td>
                    <td><div class="text-overflow-hidden" v-bk-tooltips="errorTips(item)">
                      <i :class="['status', { 'status-fail': !item.is_success }]" />
                      <label>{{item.is_success ? $t('成功') : $t('失败')}}</label>
                    </div></td>
                  </template>
                </tr>
              </tbody>
            </table>
            <div class="no-data-wrapper" v-if="!basicLoading && !auditList.length">
              <p class="no-data-text">{{$t('暂无数据')}}</p>
            </div>
          </div>
        </div>
        <div class="table-pagination" v-if="auditList.length && paginationConfig.count > 0">
          <div class="table-pagination-left">{{$t('共计')}}
            {{Math.ceil(paginationConfig.count / paginationConfig.limit)}} {{$t('页')}}，
          </div>
          <div class="table-pagination-right">
            <bk-pagination
              size="small"
              align="right"
              :current.sync="paginationConfig.current"
              :count="paginationConfig.count"
              :limit="paginationConfig.limit"
              :limit-list="limitList"
              @change="changeCurrentPage"
              @limit-change="changeLimitPage"></bk-pagination>
          </div>
        </div>
      </div>
    </bk-tab>
    <div v-show="basicLoading" class="loading-cover" @click.stop></div>
  </div>
</template>

<script>
export default {
  filters: {
    convertIsoTime(iso) {
      const arr = iso.split('T');
      const year = arr[0];
      const time = arr[1].split('.')[0];
      return `${year} ${time}`;
    },
  },
  data() {
    return {
      basicLoading: true,
      errorMessage: this.$t('审计日志为空，无法导出'),
      paginationConfig: {
        current: 1,
        count: 1,
        limit: 10,
      },
      limitList: [10, 20, 50, 100],
      searchCondition: {
        dateRange: [
          new Date(Date.now() - 86400000),
          new Date(),
        ],
        keyword: '',
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
        { key: 'operater', name: this.$t('操作人员') },
        { key: 'time', name: this.$t('时间') },
        { key: 'IP', name: this.$t('来源 IP') },
        { key: 'type', name: this.$t('操作类型') },
        { key: 'contents', name: this.$t('用户目录') },
        { key: 'object', name: this.$t('操作对象') },
      ],
      /** 登录审计表头 */
      loginHead: [
        { key: 'user', name: this.$t('登录用户') },
        { key: 'time', name: this.$t('登录时间') },
        { key: 'IP', name: this.$t('登录来源IP') },
        { key: 'status', name: this.$t('登录状态') },
      ],
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
      this.auditList = [];
      this.paginationConfig.current = 1;
      this.initUserList(val);
    },
  },
  mounted() {
    const limit = Math.floor((this.$el.offsetHeight - 158) / 42);
    this.paginationConfig.limit = limit;
    const limitList = [10, 20, 50, 100];
    if (!limitList.includes(limit)) {
      limitList.push(limit);
      limitList.sort((a, b) => a - b);
    }
    this.limitList = limitList;
    this.initUserList(this.panelActive);
  },
  methods: {
    handleWarning(config) {
      config.message = this.errorMessage;
      config.offsetY = 80;
      this.$bkMessage(config);
    },
    async  Auditderive() {
      const startTime = this.getMyDate(this.searchCondition.dateRange[0]);
      const endTime = this.getMyDate(this.searchCondition.dateRange[1]);
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
        url = `${url}/api/v2/audit/login_log/export/?start_time=${startTime}&end_time=${endTime}`;
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
        const currentStatus = panelActive === 'operate';
        const startTime = this.getMyDate(this.searchCondition.dateRange[0]);
        const endTime = this.getMyDate(this.searchCondition.dateRange[1]);
        const auditParam = {
          startTime,
          endTime,
          pageSize: this.paginationConfig.limit,
          page: this.paginationConfig.current,
        };
        const param = currentStatus ? Object.assign(auditParam, { keyword: this.searchCondition.keyword }) : auditParam;
        const url = currentStatus ? 'audit/getList' : 'audit/getLoginList';
        const res = await this.$store.dispatch(url, param);
        this.auditList = res.data.results;
        // 计算页码数
        this.paginationConfig.count = res.data.count;
        this.$refs.auditScroller.scrollTo({ top: 0 });
      } catch (e) {
        console.warn(e);
      } finally {
        this.basicLoading = false;
        this.searchedKey = this.searchCondition.keyword;
        this.$store.commit('updateInitLoading', false);
      }
    },
    // eslint-disable-next-line no-unused-vars
    changeCurrentPage(current) {
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
      if (this.searchedKey !== '') {
        this.getSearchInfo();
      }
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
    right: 0px;
    top: 65px;
    z-index: 9999;
  }
  // 表格
  .audit-content-wrapper {
    margin: 0 0 30px 0;
    height: calc(100vh - 320px);
    border: 1px solid #e6e6e6;

    .table-container {
      // table 公用样式
      table {
        color: #888;
        width: 100%;
        table-layout: fixed;
        border: none;
        border-collapse: collapse;
        font-size: 12px;

        tr {
          height: 42px;
          border-bottom: 1px solid #dcdee5;
        }

        td {
          font-size: 12px;
        }
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
    }

    .thead-container {
      height: 42px;

      > table {
        background: #fafbfd;

        th {
          padding: 0 20px;
          text-align: left;
          border: none;
          color: #666;

          &.hidden {
            display: none;
          }
        }
      }
    }

    .tbody-container {
      height: calc(100vh - 362px);

      > .scroll-container {
        height: 100%;
        overflow: auto;

        @include scroller($backgroundColor: #e6e9ea, $width: 4px);

        > table > tbody > tr {
          transition: all .3s ease;

          &:hover {
            background: #e1ecff;
          }

          > td {
            padding: 0 20px;
            border: none;

            &.hidden {
              display: none;
            }
          }
        }

        .no-data-wrapper {
          height: 100%;
          display: flex;
          justify-content: center;
          align-items: center;

          > .no-data-text {
            font-size: 14px;
            color: rgba(99, 101, 110, 1);
            text-align: center;
          }
        }
      }
    }
  }
  // 分页
  .table-pagination {
    margin-top: 10px;
    display: flex;
    align-items: center;

    > .table-pagination-left {
      line-height: 32px;
      font-size: 12px;
    }

    > .table-pagination-right {
      flex-grow: 1;
    }
  }

  /deep/ .audit-panel-class {
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
