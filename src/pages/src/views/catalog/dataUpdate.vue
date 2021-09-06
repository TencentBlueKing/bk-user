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
      <span @click="showPageHome" class="userCatalog ">
        {{$t('用户目录')}} >
      </span>
      <span class="updateRecord">{{$t('数据更新记录')}}</span>
    </div>
    <div class="catalog-table">
      <bk-table
        :data="updateList"
        :size="'small'"
        v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
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
            <span :title="row.name">{{row.required_time}}h</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('操作人')">
          <template slot-scope="{ row }">
            <span :title="row.name">{{row.operator}}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('触发类型')">
          <template slot-scope="{ row }">
            <span :title="row.name">{{row.type}}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('目标目录')">
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
              <img src="../../images/svg/loading.svg" width="20" alt="loading" class="syncingImg">
              <span class="syncing">{{$t('同步中')}}</span>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('操作')">
          <template slot-scope="{ row }">
            <span class="logDetail" @click.stop="isShowDiary(row)">
              {{$t('日志详细')}}
            </span>
          </template>
        </bk-table-column>
      </bk-table>
    </div>
    <bk-sideslider :is-show.sync="showDiary" :quick-close="true" :width="696">
      <div slot="header" class="logLevel">{{$t('日志详细')}}</div>
      <div class="content" slot="content">
        <div class="userDataUpdate marginBottom" v-for="(item , index) in UpdateDetailList" :key="item.id">
          <p class="title-wrapper" @click.stop="handleExpanded(item)">
            <section class="action-group-name">
              <span :class="`bk-icon icon-angle-${item.expanded ? 'down' : 'right'}`"></span>
              <span class="name">{{stepList[index].name}}</span>
              <span class="successful" v-if="item.successful_count > 0">
                <span class="bk-icon icon-check-circle" />
                <span>{{$t('成功')}}</span>
                <span>{{item.successful_count}}</span>
              </span>
              <span class="failed" v-if="item.failed_count > 0">
                <span class="bk-icon icon-close-circle" />
                <bk-popover placement="bottom">
                  <span>{{$t('失败')}}</span>
                  <div slot="content">
                    <div v-for="(failItem) in item.failed_records" :key="failItem.id">
                      {{failItem.detail.username}};
                    </div>
                  </div>
                </bk-popover>
                <span>{{item.failed_count}}</span>
              </span>
              <span v-if="item.status === 'running'">
                <img src="../../images/svg/loading.svg" width="20" alt="loading" class="syncingImg">
                <span class="syncing">{{$t('同步中')}}</span>
              </span>
            </section>
          </p>
          <div class="action-content" v-if="item.expanded">
            <pre class="logs">{{item.logs}}</pre>
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
      UpdateDetailList: [],
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
      },
      stepList: [
        { name: '' },
        { name: '' },
        { name: '' },
        { name: '' },
      ],
    };
  },
  created() {
    // 数据更新记录
    this.getUpdateList();
  },
  methods: {
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
        const expandedList = [];
        res.data.map((item) => {
          expandedList.push(Object.assign(item, { expanded: false }));
        });
        this.UpdateDetailList = expandedList;
        for (let index = 0; index < this.UpdateDetailList.length; index++) {
          const element = this.UpdateDetailList[index];
          const Map = {
            users: '用户数据更新',
            departments: '组织数据更新',
            users_relationship: '用户间关系数据更新',
            dept_user_relationship: '用户和组织关系数据更新',
          };
          this.stepList[index].name = Map[element.step];
        }
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
      .userCatalog {
        font-size: 14px;
        color: #979ba5;
        cursor: pointer;
    }
      .updateRecord{
        font-size: 14px;
        color: #313238;
    }
  }
> .catalog-table {
    margin-top: 25px;
    padding-bottom: 25px;
    .logDetail{
      color: #3a84ff;
      cursor: pointer;
    }
   }
   .logLevel {
      color: #313238;
      font-weight: 400;
   }
  .content {
    margin-left: 32px;
    margin-top: 24px;
    .marginBottom {
      margin-bottom: 16px;
    }
    .title-wrapper {
      cursor: pointer;
    }
    .name {
      font-size: 14px;
      font-family: PingFangSC, PingFangSC-Regular;
      color: #666770;
      margin-right: 15px;
    }
    .action-content {
      font-size: 12px;
      font-family: PingFangSC, PingFangSC-Regular;
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
    opacity: 1;
    background: #94f5a4;
    border: 1px solid #2dcb56;
    border-radius: 50%;
  }
  .fail {
    display: inline-block;
    width: 8px;
    height: 8px;
    opacity: 1;
    background: #fd9c9c;
    border: 1px solid #ea3636;
    border-radius: 50%;
  }
  .syncingImg {
      vertical-align:middle;
      margin-left:-11px;
    }
  .syncing {
      vertical-align:middle;
    }
}
</style>
