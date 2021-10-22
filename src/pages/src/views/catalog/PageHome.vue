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
  <div class="index-page">
    <div class="button-container">
      <!-- 新增目录 -->
      <bk-button theme="primary" :disabled="!catalogMetas.length" @click="addCatalog">{{$t('新增目录')}}</bk-button>
      <p class="reDataupdate" @click="dataUpdate">{{$t('数据更新记录')}}</p>
    </div>
    <div class="catalog-table">
      <div class="thead-container table-container" data-test-id="list_titelHeaderInfo">
        <table>
          <thead>
            <tr>
              <th class="table-item">{{$t('目录名')}}</th>
              <th class="table-item">{{$t('类型')}}</th>
              <th class="table-item">{{$t('更新时间')}}</th>
              <th class="table-item">{{$t('启/停')}}</th>
              <th class="table-item">{{$t('操作')}}</th>
            </tr>
          </thead>
        </table>
      </div>
      <div class="tbody-container table-container" v-show="tableLoading">
        <div class="table-loading" v-bkloading="{ isLoading: tableLoading }"></div>
      </div>
      <div class="table-empty" v-if="catalogList.length === 0 && applyUrl">
        <img class="lock-icon" src="../../images/svg/lock-radius.svg" alt="403">
        <div class="title">{{authNames + $t('无权限访问')}}</div>
        <div class="detail">{{$t('你没有相应资源的访问权限')}}</div>
        <bk-button class="king-button" theme="primary" @click="confirmPageApply">{{$t('去申请')}}</bk-button>
      </div>
      <div class="tbody-container table-container" :class="catalogList.length >= 4 && 'overflow-auto'"
           data-test-id="list_catalogData" v-else>
        <table>
          <tbody>
            <tr v-for="(item, index) in catalogList" :key="item.id">
              <!-- 目录名 -->
              <td>
                <div class="td-container">
                  <div class="catalog-name">
                    <span class="text-overflow-hidden" v-bk-overflow-tips
                          @click="goToSettingPage(item)">{{item.display_name}}
                    </span>
                    <span v-if="item.unfilled_namespaces.length" class="unfinished">{{$t('未完成')}}</span>
                  </div>
                </div>
                <transition name="fade">
                  <div v-if="loadingIdList.indexOf(item.id) !== -1" class="tr-loading" @click.stop>
                    <img src="../../images/svg/loading.svg" width="20" alt="loading">
                    <span class="loading-text">{{loadingTextList[loadingIdList.indexOf(item.id)]}}</span>
                  </div>
                </transition>
              </td>
              <!-- 类型 -->
              <td>
                <div class="td-container">
                  <span>{{$t(item.type)}}</span>
                </div>
              </td>
              <!-- 更新时间 -->
              <td>
                <div class="td-container">
                  <span>{{item.update_time | convertIsoTime}}</span>
                </div>
              </td>
              <!-- 启/停 -->
              <td>
                <div class="td-container">
                  <!-- warning 这里使用了 switcher 组件的样式，因为组件不能根据 value 控制状态 -->
                  <!-- 默认目录禁用 switch -->
                  <label v-if="item.default"
                         class="primary bk-switcher bk-switcher-small is-checked is-disabled"
                         v-bk-tooltips="$t('默认目录不能被禁用')">
                    <input type="checkbox" :value="true">
                  </label>
                  <label v-else class="primary bk-switcher bk-switcher-small"
                         :class="item.activated ? 'is-checked' : 'is-unchecked'"
                         @click="switchStatus(item)">
                    <input type="checkbox" :value="item.activated">
                  </label>
                </div>
              </td>
              <!-- 同步时间 -->
              <!-- <td>
                <div class="td-container">
                  <span>{{item.last_synced_time | convertIsoTime}}</span>
                </div>
              </td> -->
              <!-- 操作 -->
              <td v-if="item.type === 'local'">
                <div class="td-container operation-container">
                  <template v-if="item.unfilled_namespaces.length">
                    <span class="is-disabled" v-bk-tooltips="$t('目录未完成配置，无法操作')">{{$t('导出')}}</span>
                    <span class="is-disabled" v-bk-tooltips="$t('目录未完成配置，无法操作')">{{$t('导入')}}</span>
                  </template>
                  <template v-else>
                    <span v-if="computeExport(item.id)" @click="exportUser(item.id)">{{$t('导出')}}</span>
                    <span v-else class="is-disabled" v-bk-tooltips="$t('空目录无需导出')">{{$t('导出')}}</span>
                    <span @click="importUser(item.id)">{{$t('导入')}}</span>
                  </template>
                  <span v-if="item.default" class="is-disabled" v-bk-tooltips="$t('默认目录不能被删除')">{{$t('删除')}}</span>
                  <span v-else @click="deleteCatalog(item, index)">{{$t('删除')}}</span>
                </div>
              </td>
              <td v-else>
                <div class="td-container operation-container">
                  <span v-if="item.unfilled_namespaces.length"
                        v-bk-tooltips="$t('目录未完成配置，无法操作')"
                        class="is-disabled">{{$t('同步')}}
                  </span>
                  <span v-if="syncing"
                        v-bk-tooltips="$t('已有数据同步任务正在进行，请在数据更新记录中查看详情')"
                        class="is-disabled">
                    {{$t('同步')}}
                  </span>
                  <span v-else @click="syncCatalog(item)">{{$t('同步')}}</span>
                  <span @click="deleteCatalog(item, index)">{{$t('删除')}}</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 导入用户 -->
    <bk-dialog
      width="440"
      header-position="left"
      :title="$t('导入用户')"
      :ok-text="$t('提交')"
      :auto-close="false"
      v-model="showImport"
      @confirm="confirmImportUser"
      @cancel="showImport = false">
      <div>
        <ImportUser v-if="showImport" ref="importUserRef" :id="importId" />
      </div>
    </bk-dialog>
    <!-- 导出用户 -->
    <ExportUser v-if="showExport" :showing.sync="showExport" :departments="departments" :id="exportId" />

    <div v-show="tableLoading" class="loading-cover" @click.stop></div>
  </div>
</template>

<script>
import ImportUser from '@/components/catalog/home/ImportUser';
import ExportUser from '@/components/catalog/home/ExportUser';

export default {
  components: {
    ImportUser,
    ExportUser,
  },
  filters: {
    convertIsoTime(iso) {
      if (!iso) {
        return '';
      }
      const arr = iso.split('T');
      const year = arr[0];
      const time = arr[1].split('.')[0];
      return `${year} ${time}`;
    },
  },
  props: {
    catalogMetas: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      tableLoading: true,
      catalogList: [],
      applyUrl: '',
      authNames: [],
      departments: [],
      // 正在 loading 的目录
      loadingIdList: [],
      loadingTextList: [],
      showExport: false,
      exportId: '',
      showImport: false,
      importId: '',
      syncing: false,
    };
  },
  created() {
    this.getCatalogList();
    this.getDepartments();
    // 当目录创建、修改配置时都有可能会引起目录列表数据变化，因此需要刷新数据
    this.$bus.$on('updateCatalogList', () => {
      this.getCatalogList();
    });
  },
  methods: {
    // 新增目录
    addCatalog() {
      this.$emit('changePage', 'showPageAdd');
    },
    // 数据更新记录
    dataUpdate() {
      this.$emit('changePage', 'showReDataupdate');
    },
    // 去目录的设置页面
    goToSettingPage(item) {
      this.$emit('changePage', item);
    },
    // 获取目录列表
    async getCatalogList() {
      try {
        this.tableLoading = true;
        const res = await this.$store.dispatch('catalog/ajaxGetCatalogList');
        this.catalogList = res.data;
      } catch (e) {
        console.warn(e);
        if (e.response.status === 403) {
          const { auth_infos: authInfos, callback_url: applyUrl } = e.response.data.detail;
          this.applyUrl = applyUrl;
          this.authNames = `【${authInfos.map(authInfo => authInfo.display_name).join('，')}】`;
        }
      } finally {
        this.tableLoading = false;
        this.$store.commit('updateInitLoading', false);
      }
    },
    confirmPageApply() {
      window.open(this.applyUrl);
    },
    async getDepartments() {
      try {
        const res = await this.$store.dispatch('organization/getOrganizationTree', { onlyEnabled: false });
        this.departments = res.data;
      } catch (e) {
        console.warn(e);
      }
    },
    // 同步目录
    async syncCatalog(item) {
      try {
        this.syncing = true;
        this.loadingIdList.push(item.id);
        this.loadingTextList.push(this.$t('正在发起同步任务,') + this.$t('请在数据更新记录中查看具体详细'));
        await this.$store.dispatch('catalog/ajaxSyncCatalog', { id: item.id });
        this.messageSuccess(this.$t('同步成功'));
      } catch (e) {
        console.warn(e);
      } finally {
        this.closeLoading(item.id);
        this.syncing = false;
      }
    },
    // 切换开启或关闭状态
    switchStatus(item) {
      if (item.activated) {
        // 停用目录前需要确认
        this.$bkInfo({
          title: this.$t('确定停用该用户目录'),
          subTitle: this.$t('停用目录1') + item.display_name + this.$t('停用目录2'),
          confirmFn: this.confirmSwitchStatusSync.bind(this, item, false),
        });
      } else {
        // 激活目录
        this.confirmSwitchStatus(item, true);
      }
    },
    // 这里多一个步骤是为了避免 confirmFn 是 async 函数
    confirmSwitchStatusSync(item, activated) {
      this.confirmSwitchStatus(item, activated);
    },
    // 改变状态 启/停
    async confirmSwitchStatus(item, activated) {
      try {
        this.loadingIdList.push(item.id);
        this.loadingTextList.push('');
        const res = await this.$store.dispatch('catalog/ajaxPatchCatalog', {
          id: item.id,
          data: { activated },
        });
        item.activated = res.data.activated;
        const msg = item.activated ? this.$t('启用成功') : this.$t('停用成功');
        this.messageSuccess(msg);
      } catch (e) {
        console.warn(e);
      } finally {
        this.closeLoading(item.id);
      }
    },
    // 删除目录
    deleteCatalog(item, index) {
      this.$bkInfo({
        title: this.$t('确定删除该用户目录'),
        subTitle: this.$t('删除目录1') + item.display_name + this.$t('删除目录2'),
        confirmFn: this.confirmDeleteCatalogSync.bind(this, item, index),
      });
    },
    confirmDeleteCatalogSync(item, index) {
      this.confirmDeleteCatalog(item, index);
    },
    async confirmDeleteCatalog(item, index) {
      try {
        this.loadingIdList.push(item.id);
        this.loadingTextList.push(this.$t('正在') + this.$t('删除'));

        const res = await this.$store.dispatch('catalog/ajaxDeleteCatalog', { id: item.id });
        if (res.result === true) {
          this.catalogList.splice(index, 1);
          this.messageSuccess(this.$t('删除成功'));
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.closeLoading(item.id);
      }
    },
    // 通过判断该目录下有无组织信息决定是否激活导出按钮
    computeExport(id) {
      for (let i = 0; i < this.departments.length; i++) {
        if (this.departments[i].id === id) {
          const list = this.departments[i].departments;
          return Boolean(list.length);
        }
      }
    },
    exportUser(id) {
      this.exportId = id;
      this.showExport = true;
    },
    importUser(id) {
      this.importId = id;
      this.showImport = true;
    },
    async confirmImportUser() {
      if (!this.$refs.importUserRef.uploadInfo.name) {
        this.messageWarn(this.$t('请选择文件再上传'));
        return;
      }
      if (!this.$refs.importUserRef.uploadInfo.type) {
        this.messageWarn(this.$t('请选择正确格式的文件上传'));
        return;
      }
      const formData = new FormData();
      formData.append('file', this.$refs.importUserRef.uploadInfo.fileInfo);
      formData.append('file_name', this.$refs.importUserRef.uploadInfo.name);
      formData.append('department_id', this.$refs.importUserRef.id);

      // 如果同时有两个目录正在导入，this.importId 会变化，影响 splice loading，所以必须加个变量
      const importId = this.importId;
      this.loadingIdList.push(importId);
      this.loadingTextList.push(this.$t('正在上传'));
      this.showImport = false;
      try {
        await this.$store.dispatch('catalog/ajaxImportUser', {
          id: this.importId,
          data: formData,
        });
        await this.getDepartments();
        this.messageSuccess(this.$t('同步成功'));
      } catch (e) {
        console.warn(e);
      } finally {
        this.closeLoading(importId);
      }
    },
    closeLoading(id) {
      const index = this.loadingIdList.indexOf(id);
      this.loadingIdList.splice(index, 1);
      this.loadingTextList.splice(index, 1);
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../../scss/variable';
@import '../../scss/mixins/scroller';

.index-page {
  height: 100%;
  color: $fontGray;

  > .button-container {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
    .reDataupdate {
      font-family: MicrosoftYaHei, MicrosoftYaHei-Regular;
      height: 32px;
      font-size: 14px;
      color: #3a84ff;
      line-height: 32px;
      cursor: pointer;
    }
  }
  > .catalog-table {
    max-height: calc(100% - 52px);
    border: 1px solid $borderColor;
    overflow: hidden;

    > .table-container {
      //table 公用样式
      > table {
        width: 100%;
        table-layout: fixed;
        border: none;
        border-collapse: collapse;
        font-size: 12px;

        tr {
          height: 42px;
          border-bottom: 1px solid $borderColor;

          td,
          th {
            padding: 0 20px;
            border: none;
            font-weight: normal;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
        }
      }
    }

    > .thead-container {
      > table {
        background: #fafbfd;

        th {
          text-align: left;
          color: $fontPrimary;
        }
      }
    }

    > .table-empty {
      position: relative;
      display: flex;
      flex-flow: column;
      align-items: center;
      height: calc(100vh - 194px);
      font-size: 20px;
      font-weight: 500;
      color: #313238;

      .lock-icon {
        margin-top: 128px;
      }

      .title {
        margin-top: 26px;
        line-height: 28px;
        font-size: 20px;
        font-weight: 500;
        color: #313238;
      }

      .detail {
        margin-top: 30px;
        line-height: 20px;
        font-size: 14px;
        color: #979ba5;
      }

      .king-button {
        margin-top: 30px;
      }
    }

    > .tbody-container {
      max-height: calc(100vh - 194px);

      @include scroller($backgroundColor: #e6e9ea, $width: 4px);

      &.overflow-auto {
        overflow-y: auto;
      }

      > .table-loading {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        height: calc(100vh - 194px);
      }

      > table > tbody > tr {
        position: relative;
        transform: scale(1);
        transition: background .2s ease;

        &:hover {
          transition: background .2s ease;
          background: #e1ecff;
        }

        &:last-child {
          border-bottom: none;
        }

        > td {
          &:first-child span {
            color: $primaryColor;
            cursor: pointer;
          }

          > .td-container > .catalog-name {
            display: flex;
            align-items: center;
            line-height: 16px;

            .unfinished {
              padding: 2px 4px;
              height: 16px;
              line-height: 12px;
              color: #fff;
              font-weight: 600;
              background: #c4c6cc;
              transform: scale(.8);
              border-radius: 2px;
            }
          }

          > .operation-container {
            color: $primaryColor;
            display: flex;

            > span {
              cursor: pointer;
              outline: none;

              &:not(:last-child) {
                margin-right: 14px;
              }

              &.is-disabled {
                cursor: not-allowed;
                color: #d9d9d9;
              }
            }
          }
        }

        .tr-loading {
          position: absolute;
          top: 1px;
          left: 0;
          width: 100%;
          height: 41px;
          display: flex;
          justify-content: center;
          align-items: center;
          background: #fff;
          opacity: .9;
          z-index: 100;
          cursor: not-allowed;

          > .loading-text {
            cursor: not-allowed;
            color: $primaryColor;
            padding-left: 12px;
            font-size: 12px;
          }
        }
      }
    }
  }
}
</style>
