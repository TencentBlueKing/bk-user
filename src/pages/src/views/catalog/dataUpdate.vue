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
  <div class="update-page">
    <div class="header">
      <span @click="showPageHome" class="user-catalog ">
        {{$t('用户目录')}} >
      </span>
      <span class="update-decord">{{$t('数据更新记录')}}</span>
    </div>
    <div class="catalog-table" data-test-id="list_dataUpdateInfo">
      <bk-table
        :data="updateList"
        :size="'small'"
        v-bkloading="{ isLoading: tableLoading }"
        :pagination="pagination"
        @page-change="handlePageChange"
        @page-limit-change="pageLimitChange">
        <bk-table-column :label="$t('开始时间')">
          <template slot-scope="{ row }">
            <span :title="row.name">{{row.create_time | convertIsoTime}}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('耗时')">
          <template slot-scope="{ row }">
            <span>{{ timeText(row) }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('操作人')">
          <template slot-scope="{ row }">
            <span :title="row.name">{{row.operator}}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('触发类型')">
          <template slot-scope="{ row }">
            <span :title="row.name">{{triggeMode[row.type]}}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('用户目录')">
          <template slot-scope="{ row }">
            <span :title="row.name">{{row.category.display_name}}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('状态')">
          <template slot-scope="{ row }">
            <div class="td-container" v-if="row.status === 'successful'">
              <span class="success"></span>
              <span>{{$t('成功')}}</span>
            </div>
            <div class="td-container" v-else-if="row.status === 'failed'">
              <span class="fail"></span>
              <span v-bk-tooltips="$t('同步操作失败，请在用户管理后台 API 日志中查询详情')">{{$t('失败')}}</span>
            </div>
            <div class="td-container" v-else-if="row.status === 'running'">
              <img src="../../images/svg/loading.svg" width="20" alt="loading" class="syncing-img">
              <span class="syncing">{{$t('同步中')}}</span>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('操作')">
          <template slot-scope="{ row }">
            <span class="log-detail" @click.stop="isShowDiary(row)">
              {{$t('日志详细')}}
            </span>
          </template>
        </bk-table-column>
      </bk-table>
    </div>
    <bk-sideslider :is-show.sync="showDiary" :quick-close="true" :width="696">
      <div slot="header" class="log-level">{{$t('日志详细')}}</div>
      <div class="content" slot="content">
        <div class="user-data-update margin-bottom" v-for="(item) in updateDetailList" :key="item.id">
          <p class="title-wrapper" @click.stop="handleExpanded(item)">
            <section class="action-group-name">
              <span :class="`bk-icon icon-angle-${item.expanded ? 'down' : 'right'}`"></span>
              <span class="name">{{mapList[item.step]}}</span>
              <span class="successful" v-if="item.successful_count > 0">
                <img src="../../images/svg/right.svg" width="20" alt="loading" class="status-img">
                <span class="status-text">{{$t('成功')}}</span>
                <span class="status-img">({{item.successful_count}})</span>
              </span>
              <span class="failed" v-if="item.failed_count > 0">
                <img src="../../images/svg/fail.svg" width="20" alt="loading" class="status-img">
                <bk-popover placement="bottom">
                  <span class="status-text">{{$t('失败')}}</span>
                  <div slot="content">
                    <div v-for="(failItem) in item.failed_records" :key="failItem.id">
                      {{failItem.detail.username}};
                    </div>
                  </div>
                </bk-popover>
                <span class="status-img">({{item.failed_count}})</span>
              </span>
              <span v-if="item.status === 'running'">
                <img src="../../images/svg/loading.svg" width="20" alt="loading" class="statusg-img">
                <span class="status-text">{{$t('同步中')}}</span>
              </span>
            </section>
          </p>
          <div class="action-content" v-if="item.expanded">
            <pre v-if="item.logs.length > 0" class="logs">{{item.logs}}</pre>
            <p v-else class="logs">{{$t('暂无数据')}}</p>
          </div>
        </div>
      </div>
    </bk-sideslider>
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
      tableLoading: false,
      showDiary: false,
      updateList: [],
      updateDetailList: [],
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
      },
      mapList: {
        users: this.$t('用户数据更新'),
        departments: this.$t('组织数据更新'),
        users_relationship: this.$t('用户间关系数据更新'),
        dept_user_relationship: this.$t('用户和组织关系数据更新'),
      },
      triggeMode: {
        manual: this.$t('手动触发'),
        auto: this.$t('定时触发'),
      },
    };
  },
  created() {
    // 数据更新记录
    this.getUpdateList();
  },
  methods: {
    timeText(row) {
      if (row.required_time < 60) {
        return `<1${this.$t('分钟')}`;
      }
      if (60 <= row.required_time && row.required_time < 3600) {
        const time = row.required_time / 60;
        const min = time.toString().split('.')[0];
        const sec = parseInt(time.toString().split('.')[1][0]) * 6;
        return `${min}${this.$t('分钟')}${sec}${this.$t('秒')}`;
      }
      if (3600 <= row.required_time) {
        const time = row.required_time / 3600;
        const hour = time.toString().split('.')[0];
        const min = parseInt(time.toString().split('.')[1][0]) * 6;
        return `${hour}${this.$t('小时')}${min}${this.$t('分钟')}`;
      }
    },
    showPageHome() {
      this.$emit('changePage', 'showPageHome');
    },
    isShowDiary(item) {
      this.showDiary = true;
      this.getUpdateDetailList(item);
    },
    handleExpanded(item) {
      item.expanded = !item.expanded;
    },
    handlePageChange(page) {
      this.pagination.current = page;
      this.getUpdateList(true);
    },
    pageLimitChange(currentLimit) {
      this.pagination.limit = currentLimit;
      this.pagination.current = 1;
      this.getUpdateList(true);
    },
    // 获取数据更新记录
    async getUpdateList() {
      try {
        this.tableLoading = true;
        const params = {
          page: this.pagination.current,
          page_size: this.pagination.limit,
        };
        const res = await this.$store.dispatch('catalog/ajaxGetUpdateRecord', params);
        this.updateList = res.data.results;
        this.pagination.count = res.data.count;
      } catch (e) {
        console.warn(e);
      } finally {
        this.tableLoading = false;
      }
    },
    // 获取日志更新详细数据
    async getUpdateDetailList(item) {
      try {
        const res = await this.$store.dispatch('catalog/ajaxGetUpdateDetailRecord', { id: item.id });
        res.data.map((item) => {
          return Object.assign(item, { expanded: false });
        });
        this.updateDetailList = res.data;
      } catch (e) {
        console.warn(e);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../../scss/variable';
@import '../../scss/mixins/scroller';
.update-page {
      height: 100%;
      color: $fontGray;
 > .header {
      .user-catalog {
        font-size: 14px;
        color: #979ba5;
        cursor: pointer;
    }
      .update-decord{
        font-size: 14px;
        color: #313238;
    }
  }
> .catalog-table {
    margin-top: 25px;
    padding-bottom: 25px;
    .log-detail{
      color: #3a84ff;
      cursor: pointer;
    }
   }
   .log-level {
      color: #313238;
      font-weight: 400;
   }
  .content {
    margin-left: 32px;
    margin-top: 24px;
    .margin-bottom {
      margin-bottom: 16px;
    }
    .title-wrapper {
      cursor: pointer;
    }
    .name {
      font-size: 14px;
      color: #666770;
      margin-right: 15px;
    }
    .action-content {
      font-size: 12px;
      color: #666770;
      margin-top: 8px;
      margin-left: 20px;
    }
    .successful {
      font-size:12px;
      color: #2dcb56;
    }
    .failed {
      font-size:12px;
      color: #ed5555;
    }
    .icon-check-circle,
    .icon-close-circle {
      font-size: 18px;
    }
    .logs {
      font-size:12px;
      color:#666770;
      font-family: PingFangSC, PingFangSC-Regular;
      }
  }
  .success {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #94f5a4;
    border: 1px solid #2dcb56;
    border-radius: 50%;
    margin-right: 8px;
  }
  .fail {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #fd9c9c;
    border: 1px solid #ea3636;
    border-radius: 50%;
    margin-right: 8px;
  }
  .status-img {
      vertical-align:middle;
    }
  .status-text {
      vertical-align:middle;
      margin: 0 5px;
    }
}
</style>
