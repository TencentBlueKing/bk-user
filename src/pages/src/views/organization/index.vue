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
  <div class="organization-wrapper" @click="hiddenMenu($event)" v-bkloading="{ isLoading: initLoading }">
    <bk-resize-layout
      :min="260" :max="420" v-show="showingPage === 'showPageHome'">
      <div slot="aside" class="organization-left" v-show="!initLoading">
        <TreeSearch ref="searchChild" @searchTree="handleSearchTree" @addDirectory="addDirectory" />
        <div class="tree-loading-wrapper" v-bkloading="{ isLoading: treeLoading }">
          <div class="tree-content-wrapper" ref="treePanel">
            <OrganizationTree
              :tree-data-list="treeDataList"
              :tree-search-result="treeSearchResult"
              :current-category-id="currentCategoryId"
              @handleClickTreeNode="handleClickTreeNode"
              @handleClickToggle="handleClickToggle"
              @handleRename="handleRename"
              @handleClickOption="handleClickOption"
              @deleteDepartment="deleteDepartment"
              @switchNodeOrder="switchNodeOrder"
              @handleConfigDirectory="handleClickConfig"
              @addOrganization="addOrganization"
              @updateScroll="updateScroll"
              @updateAcitveNode="updateAcitveNode" />
          </div>
        </div>
      </div>
      <div slot="main" class="organization-right" v-show="!initLoading">
        <!-- 组织名称和人数 -->
        <div class="department-title">
          <div class="title-left">
            <div class="title-left-name">
              <i
                :class="[currentParam.item.display_name
                  ? 'icon user-icon icon-root-node-i'
                  : 'icon icon-user-file-close-01']"></i>
              <span class="profile-name text-overflow">
                {{ currentParam.item.display_name || currentParam.item.name}}
              </span>
              <span class="profile-count">
                {{ handleTabData.totalNumber }}
              </span>
            </div>
            <ul class="title-left-ul" v-if="currentParam.item.type">
              <li>
                {{ $t('目录类型：') + (currentCategoryType === 'local' ? $t('本地目录') : currentCategoryType) }}
              </li>
              <li>
                {{ $t('登录域：') + currentParam.item.domain }}
              </li>
              <li>
                {{ $t('目录状态：') }}
                <span
                  :class="[{ 'incomplete': !currentParam.item.configured },
                           { 'deactivate': currentParam.item.configured && !currentParam.item.activated }]">
                  {{ itemActivated }}
                </span>
              </li>
              <li>
                {{ $t('更新时间：') + itemUpdateTime }}
              </li>
            </ul>
          </div>
          <div class="title-right">
            <bk-button
              v-if="currentParam.item.type"
              :theme="'primary'" class="mr10" size="small"
              @click="handleClickConfig">
              {{ $t('目录配置') }}
            </bk-button>
            <OperationConfig
              :node="currentParam.item"
              :current-category-id="currentCategoryId"
              @handleRename="handleRename"
              @deleteDepartment="deleteDepartment" />
          </div>
        </div>
        <!-- 目录配置未完成 -->
        <template v-if="!showSyncDetails">
          <bk-exception
            v-if="!currentParam.item.configured && !currentParam.item.parent"
            type="empty" scene="page">
            <p style="font-size: 20px">{{$t('目录配置未完成')}}</p>
            <bk-link
              theme="primary"
              class="empty-subtitle"
              @click="handleClickConfig">{{ $t('继续配置') }}</bk-link>
          </bk-exception>
          <!-- 正常分页查询有数据，或者筛选筛选、搜索无数据 -->
          <div class="staff-info-wrapper" v-else>
            <!-- 表格上方的操作栏，组织树搜索结果为非组织时不渲染 -->
            <div class="table-actions" v-if="noSearchOrSearchDepartment">
              <!-- 本地用户目录 -->
              <template v-if="currentCategoryType === 'local'">
                <div class="table-actions-left-container local-type" data-test-id="list_operationUser">
                  <!-- 添加成员 -->
                  <bk-dropdown-menu
                    ref="dropdownAdd" class="king-dropdown-menu"
                    :disabled="basicLoading" @show="isDropdownShowAdd = true"
                    @hide="isDropdownShowAdd = false">
                    <bk-button slot="dropdown-trigger" class="king-button">
                      <span class="more-action">{{$t('添加用户')}}</span>
                      <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShowAdd }]"></i>
                    </bk-button>
                    <ul class="bk-dropdown-list" slot="dropdown-content">
                      <li><a href="javascript:;" @click="addUserFn">{{$t('新增用户1')}}</a></li>
                      <li><a href="javascript:;" @click="pullUserFn">{{$t('拉取已有用户')}}</a></li>
                    </ul>
                  </bk-dropdown-menu>
                  <!-- 更多操作 -->
                  <bk-dropdown-menu
                    ref="dropdownMore" class="king-dropdown-menu"
                    :disabled="basicLoading" @show="isDropdownShowMore = true"
                    @hide="isDropdownShowMore = false">
                    <bk-button slot="dropdown-trigger" class="king-button">
                      <span class="more-action">{{$t('更多操作')}}</span>
                      <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShowMore }]"></i>
                    </bk-button>
                    <ul class="bk-dropdown-list" slot="dropdown-content">
                      <li>
                        <a
                          href="javascript:;" :class="{ 'disabled': !isClick }"
                          @click="handleSetDepartment">{{$t('设置所在组织')}}
                        </a>
                      </li>
                      <li>
                        <a
                          href="javascript:;" :class="{ 'disabled': !isClick }"
                          @click="deleteProfiles">{{$t('批量删除')}}
                        </a>
                      </li>
                    </ul>
                  </bk-dropdown-menu>
                  <!-- 仅显示本级组织成员 -->
                  <p class="filter-current">
                    <bk-checkbox
                      class="king-checkbox" :checked="isSearchCurrentDepartment"
                      @change="changeSearchLevel">
                    </bk-checkbox>
                    <span class="text text-overflow-hidden" v-bk-overflow-tips @click="changeSearchLevel">
                      {{$t('仅显示本级组织成员') + `(${handleTabData.currentNumber})`}}
                    </span>
                  </p>
                </div>
                <div class="table-actions-right-container">
                  <!-- 用户搜索框 -->
                  <bk-search-select
                    class="king-input-search"
                    style="width: 400px;"
                    :placeholder="$t('输入用户名/全名，按Enter搜索')"
                    :data="searchFilterList"
                    :show-condition="false"
                    v-model="tableSearchKey"
                    @change="handleTableSearch"
                    @input-click.once="handleSearchList" />
                </div>
              </template>
              <!-- 非本地用户目录 -->
              <template v-else>
                <div class="table-actions-left-container">
                  <!-- 用户搜索框 -->
                  <bk-search-select
                    class="king-input-search"
                    style="width: 400px;margin-right: 20px;"
                    :placeholder="$t('输入用户名/全名，按Enter搜索')"
                    :data="searchFilterList"
                    :show-condition="false"
                    v-model="tableSearchKey"
                    @change="handleTableSearch"
                    @input-click.once="handleSearchList" />
                  <!-- 仅显示本级组织成员 -->
                  <p class="filter-current">
                    <bk-checkbox
                      class="king-checkbox" :checked="isSearchCurrentDepartment"
                      @change="changeSearchLevel"></bk-checkbox>
                    <span class="text" @click="changeSearchLevel">
                      {{$t('仅显示本级组织成员') + `(${handleTabData.currentNumber})`}}
                    </span>
                  </p>
                </div>
                <div class="table-actions-right-container">
                  <bk-button
                    class="sync-details"
                    v-if="currentParam.item.type "
                    :text="true"
                    title="primary"
                    @click="handleClickUpdate">
                    <i class="bk-sq-icon icon-lishijilu"></i>
                    {{ $t('数据更新记录') }}
                  </bk-button>
                </div>
              </template>
            </div>
            <div
              :class="['department-staff-info',{ 'set-height': !userMessage.userInforList.length && !basicLoading,
                                                 'search-user': !noSearchOrSearchDepartment }]">
              <!-- table表格 用户信息 -->
              <UserTable
                v-bkloading="{ isLoading: basicLoading, zIndex: 0 }"
                :user-message="userMessage"
                :is-empty-search="isEmptySearch"
                :is-table-data-error="isTableDataError"
                :is-table-data-empty="isTableDataEmpty"
                :fields-list="fieldsList"
                :pagination="paginationConfig"
                :timer-map="timerMap"
                :status-map="statusMap"
                :is-click.sync="isClick"
                @handlePageChange="handlePageChange"
                @handlePageLimitChange="handlePageLimitChange"
                @handleSetFieldList="handleSetFieldList"
                @viewDetails="viewDetails"
                @updateTableData="updateTableData"
                @updateHeardList="updateHeardList"
                @isClickList="isClickList"
                @deleteProfile="deleteProfile"
                @handleRefresh="getTableData"
                @handleClickEmpty="handleClickEmpty" />
            </div>
          </div>
        </template>
        <div class="staff-info-wrapper" v-else>
          <bk-button
            class="sync-details"
            v-if="currentParam.item.type"
            :text="true"
            title="primary"
            @click="showSyncDetails = false">
            <i class="bk-sq-icon icon-arrow-left"></i>
            {{ $t('返回上一页') }}
          </bk-button>
          <DataUpdate
            :update-list="dataUpdateList"
            :pagination="dataUpdatePagination"
            :table-loading="dataUpdateLoading"
            @dataUpdatePageChange="dataUpdatePageChange"
            @dateUpdatePageLimit="dateUpdatePageLimit" />
        </div>
        <!-- 弹窗操作 -->
        <div class="operation-wrapper">
          <!-- 新增用户 侧边栏 -->
          <bk-sideslider
            class="king-sideslider"
            :width="630"
            :show-mask="false"
            :is-show.sync="detailsBarInfo.isShow"
            :quick-close="true"
            :title="detailsBarInfo.title"
            :style="{ visibility: isHideBar ? 'hidden' : 'visible' }"
            :before-close="beforeClose">
            <div slot="content" class="member-content" v-if="detailsBarInfo.isShow">
              <DetailsBar
                :details-bar-info="detailsBarInfo"
                :current-profile="currentProfile"
                :current-category-id="currentCategoryId"
                :current-category-type="currentCategoryType"
                :fields-list="fieldsList"
                :status-map="statusMap"
                :timer-map="timerMap"
                @hideBar="hideBar"
                @showBar="showBar"
                @showBarLoading="showBarLoading"
                @closeBarLoading="closeBarLoading"
                @updateUserInfor="updateUserInfor"
                @editProfile="editProfile"
                @handleCancelEdit="handleCancelEdit"
                @deleteProfile="deleteProfile"
                @restoreProfile="restoreProfile" />
            </div>
          </bk-sideslider>
          <!-- 重命名、添加下级组织 -->
          <bk-dialog
            width="648"
            header-position="left"
            :auto-close="false"
            :title="handleTabData.title"
            v-model="handleTabData.isShow"
            @confirm="actionConfirmFn"
            @cancel="actionCancelFn">
            <DialogContent
              v-if="handleTabData.isShow"
              ref="dialogContentRef"
              :rename-data="renameData"
              :handle-tab-data="handleTabData"
              :set-table-fields="setTableFields"
              @onEnter="actionConfirmFn" />
          </bk-dialog>
          <!-- 设置所在组织的弹窗 -->
          <bk-dialog
            width="721"
            class="king-dialog department-dialog"
            header-position="left"
            :position="{ top: setDepartmentTop }"
            :auto-close="false"
            :title="$t('设置所在组织')"
            v-model="isShowSetDepartments"
            @confirm="selectDeConfirmFn"
            @cancel="isShowSetDepartments = false">
            <div class="select-department-wrapper clearfix">
              <SetDepartment
                v-if="isShowSetDepartments"
                :current-category-id="currentCategoryId"
                :initial-departments="initialDepartments"
                @getDepartments="getDepartments" />
            </div>
          </bk-dialog>
          <!-- 批量拉取用户 -->
          <bk-dialog
            width="440"
            header-position="left"
            v-model="batchUserInfo.isShow"
            :auto-close="false"
            :title="$t('拉取已有用户')"
            :ok-text="$t('提交')"
            @confirm="submitBatch"
            @cancel="BatchCancelFn">
            <div class="batch-content-wrapper">
              <PullUser v-if="batchUserInfo.isShow" ref="pullUser" :id="currentCategoryId" @getPullUser="getPullUser" />
            </div>
          </bk-dialog>
          <!-- 添加组织 -->
          <div class="new-department" style="display: none;">
            <div class="folder-icon">
              <span class="icon icon-user-file-close-01"></span>
            </div>
            <bk-input
              v-model="addOrganizationName"
              type="text"
              font-size="medium"
              class="adding-input"
              :placeholder="$t('按Enter键确认添加')"
              @enter="confirmAdd"
              @blur="cancelAdd"
              @keydown="handleKeydown"
            ></bk-input>
          </div>
        </div>
      </div>
    </bk-resize-layout>
    <div id="catalog" v-show="showingPage !== 'showPageHome'">
      <!-- 新增目录 -->
      <PageAdd v-if="showingPage === 'showPageAdd'" :catalog-metas="catalogMetas" @changePage="changePage" />
      <!-- 本地用户 -->
      <LocalAdd v-if="showingPage === 'showLocalAdd'" @changePage="changePage" @cancel="handleCancel" />
      <LocalSet v-if="showingPage === 'showLocalSet'" @changePage="changePage" :catalog-info="catalogInfo" />
      <!-- MAD 用户 -->
      <RemoteAdd
        v-if="showingPage === 'showRemoteAddMad'"
        @changePage="changePage"
        @cancel="handleCancel" catalog-type="mad" />
      <RemoteSet v-if="showingPage === 'showRemoteSetMad'" @changePage="changePage" :catalog-info="catalogInfo" />
      <!-- LDAP 用户 -->
      <RemoteAdd
        v-if="showingPage === 'showRemoteAddLdap'"
        @changePage="changePage"
        @cancel="handleCancel" catalog-type="ldap" />
      <RemoteSet v-if="showingPage === 'showRemoteSetLdap'" @changePage="changePage" :catalog-info="catalogInfo" />
    </div>
    <!-- table basic loading 时的遮罩层 -->
    <div v-show="basicLoading || initLoading" class="loading-cover" @click.stop></div>
  </div>
</template>

<script>
import moment from 'moment';
import TreeSearch from './tree/TreeSearch';
import DialogContent from './tree/DialogContent';
import PullUser from './table/PullUser';
import DetailsBar from './details/DetailsBar';
import OrganizationTree from './tree/OrganizationTree.vue';
import UserTable from './table/UserTable.vue';

import SetDepartment from '@/components/organization/SetDepartment';
import mixin from './mixin';
import PageAdd from '../catalog/PageAdd.vue';
import LocalAdd from '../catalog/operation/LocalAdd';
import LocalSet from '../catalog/operation/LocalSet';
import RemoteAdd from '../catalog/operation/RemoteAdd';
import RemoteSet from '../catalog/operation/RemoteSet';
import OperationConfig from '@/components/organization/OperationConfig';
import DataUpdate from '../catalog/dataUpdate.vue';

export default {
  name: 'OrganizationIndex',
  components: {
    DetailsBar,
    DialogContent,
    SetDepartment,
    TreeSearch,
    PullUser,
    OrganizationTree,
    UserTable,
    PageAdd,
    LocalAdd,
    LocalSet,
    RemoteAdd,
    RemoteSet,
    OperationConfig,
    DataUpdate,
  },
  mixins: [mixin],
  data() {
    return {
      initLoading: true,
      // 增加组织请求接口时给树组织一个loading
      treeLoading: false,
      paginationConfig: {
        current: 1,
        count: 1,
        limit: 10,
      },
      clickSecond: false,
      // 保存的字段信息列表
      fieldsList: [],
      // 侧边栏信息
      detailsBarInfo: {
        isShow: false,
        // add edit view
        type: '',
        basicLoading: false,
        title: '',
        quickClose: true,
      },
      // 点击保存时打开 loading，临时在样式上隐藏侧边栏
      isHideBar: false,
      handleTabData: {
        isShow: false,
        departName: '',
        title: this.$t('添加下级组织'),
        isMark: false,
        totalNumber: 0,
        currentNumber: 0,
      },
      // 重命名的目录或组织
      renameData: {},
      // 渲染用户信息
      userMessage: {
        tableHeardList: [],
        userInforList: [],
      },
      // 搜索结果为空
      isEmptySearch: false,
      // 表格请求出错
      isTableDataError: false,
      // 表格请求结果为空
      isTableDataEmpty: false,
      // 是否勾选了表格数据
      isClick: false,
      isShowSetDepartments: false,
      treeDataList: [],
      isShowingSearchTree: false,
      // 在搜索的结果里重命名或删除了组织，需要重新初始化数据
      hasTreeDataModified: false,
      // 当前 focus 的组织，通过是否有 type 字段判断是否为用户目录节点，这里设置为布尔值是为了初始页面显示为用户目录
      currentParam: {
        item: {
          type: true,
          display_name: '',
          departments: [],
        },
      },
      currentCategoryId: '',
      currentCategoryType: '',
      // 当前成员的信息
      currentProfile: {},
      isSearchCurrentDepartment: false,
      getSelectedDepartments: [],
      // 表格 loading
      basicLoading: false,
      setTableFields: [],
      treeSearchResult: null,
      isAddChild: false,
      initialDepartments: [],
      batchUserInfo: {
        isShow: false,
        tags: [],
      },
      tableSearchKey: [],
      // 记录搜索过的关键字，blur 的时候如果和当前关键字不一样就刷新表格
      tableSearchedKey: [],
      isDropdownShowAdd: false,
      isDropdownShowMore: false,
      setDepartmentTop: (window.document.body.offsetHeight - 519) / 2,
      tableData: [],
      searchDataList: [],
      searchFilterList: [],
      heardList: [],
      enumList: {
        username: 'username',
        display_name: 'display_name',
        email: 'email',
        telephone: 'telephone',
        status: 'status',
        staff_status: 'staff_status',
        leader: 'leaders',
        position: 'position',
        wx_userid: 'wx_userid',
        qq: 'qq',
      },
      statusMap: {},
      timerMap: ['account_expiration_date', 'last_login_time', 'create_time', 'update_time'],
      checkSearchKey: '',
      departmentsId: null,
      // 选中列表
      isCheckList: [],
      showingPage: 'showPageHome',
      catalogMetas: [],
      catalogInfo: '',
      catalogList: [],
      // 添加组织名称
      addOrganizationName: '',
      currentParentNode: null,
      currentNode: null,
      // 回收保留天数
      retentionDays: null,
      // 数据更新记录配置
      showSyncDetails: false,
      dataUpdateLoading: false,
      dataUpdateList: [],
      dataUpdatePagination: {
        current: 1,
        count: 1,
        limit: 10,
      },
    };
  },
  computed: {
    noSearchOrSearchDepartment() {
      return Boolean(!this.treeSearchResult || (this.treeSearchResult && this.treeSearchResult.groupType === 'department'));
    },
    isShowCatalogPage() {
      return Boolean(this.currentParam.item.type && !this.treeSearchResult);
    },
    isRootDirectory() {
      return this.currentParam.item.parent === null;
    },
    itemActivated() {
      let text = '';
      if (this.currentParam.item.configured && !this.currentParam.item.activated) {
        text = this.$t('停用');
      } else if (!this.currentParam.item.configured) {
        text = this.$t('未完成');
      } else {
        text = this.$t('启用');
      }
      return text;
    },
    itemUpdateTime() {
      return moment.utc(this.currentParam.item.update_time).format('YYYY-MM-DD HH:mm:ss');
    },
  },
  watch: {
    'currentParam.item'(val, oldVal) {
      this.departmentsId = val.id;
      // 搜索结果为 profile 时切换节点不刷新表格数据
      if (this.treeSearchResult && this.treeSearchResult.groupType !== 'department') {
        return;
      }
      // 当变更选中节点（组织节点），更新用户信息列表
      if (val !== oldVal) {
        this.initTableData();
      }
      this.currentCategoryId = val.type ? val.id : this.findCategoryId(val);
      this.currentCategoryType = val.type ? val.type : this.findCategoryType(val);
    },
    searchDataList(val) {
      this.heardList = [];
      val.forEach((item) => {
        const { name, options } = item;
        const id = item.key;
        const children = [];
        const multiable = true;
        if (options.length > 0) {
          options.forEach((k) => {
            if (this.$i18n.locale === 'en') {
              children.push({ id: k.id, name: k.id });
            } else {
              children.push({ id: k.id, name: k.value });
            }
          });
          this.heardList.push({ name, id, multiable, children });
        } else if (!this.timerMap.includes(id)) {
          this.heardList.push({ name, id });
        }
      });
      this.searchFilterList = this.heardList;
    },
    'tableSearchKey'(val) {
      this.searchFilterList = this.heardList;
      if (val.length) {
        val.filter((item) => {
          if (item.id === 'username' || item.id === 'display_name') {
            this.checkSearchKey = item.values[0].name;
          }
          this.searchFilterList = this.searchFilterList.filter((k) => {
            if (!item.id.includes(k.id)) {
              return k;
            }
          });
        });
      } else {
        this.checkSearchKey = '';
      }
    },
    // 当前节点添加className
    currentNode(val, oldVal) {
      if (val !== oldVal) {
        val.classList.add('node-li');
        if (oldVal) {
          oldVal.classList.remove('node-li');
        }
      }
    },
  },
  created() {
    this.initCatalogMetas();
    this.getCatalogList();
    if (this.$store.state.catalog.defaults.password === null) {
      this.getDefaultInfo();
    }
  },
  async mounted() {
    try {
      await Promise.all([this.initData(), this.getTableTitle(), this.initRecoverySetting()]);
      this.getNodeColor();
    } catch (e) {
      console.warn(e);
    } finally {
      this.initLoading = false;
      this.$store.commit('updateInitLoading', false);
    }
  },
  methods: {
    async initData() {
      try {
        this.treeLoading = true;
        const res = await this.$store.dispatch('organization/getOrganizationTree');
        if (!res.data || !res.data.length) return;
        this.treeDataList = res.data;
        this.treeDataList.forEach((catalog, index) => {
          if (index === 0) {
            this.initRtxList(catalog.id);
          }
          this.filterTreeData(catalog, this.treeDataList);
          catalog.children = catalog.departments;
          catalog.level = 1;
          catalog.children.forEach((department) => {
            this.$set(department, 'async', department.has_children);
            this.$set(department, 'category_id', catalog.id);
            this.$set(department, 'level', catalog.level + 1);
            this.filterTreeData(department, catalog, catalog.type === 'local');
          });
        });
        this.treeDataList[0] && (this.treeDataList[0].showChildren = true);
        // 初始化添加下级组织
        this.currentParam = {
          item: this.treeDataList[0],
        };
        this.treeDataList[0].showBackground = true;
        this.treeDataList[0].expanded = true;
      } catch (e) {
        console.warn(e);
        const { response } = e;
        if (response.status === 403) {
          setTimeout(() => {
            this.$store.commit('updateNoAuthData', {
              requestId: 'has_not_path_auth',
              data: response.data,
            });
          });
        }
      } finally {
        this.treeLoading = false;
      }
    },

    // 初始化用户信息的title
    async getTableTitle() {
      try {
        this.userMessage.tableHeardList = [];
        const res = await this.$store.dispatch('setting/getFields');
        const fieldsList = res.data;
        if (!fieldsList) return;
        this.fieldsList = JSON.parse(JSON.stringify(fieldsList));
        this.setTableFields = JSON.parse(JSON.stringify(fieldsList));
        this.setTableFields.forEach((item) => {
          if (item.options && item.options.length) {
            this.$set(this.statusMap, [item.key], {});
            item.options.forEach((key) => {
              Object.entries(this.statusMap).map((k) => {
                if (k[0] === item.key) {
                  this.$set(k[1], key.id, key.value);
                }
              });
            });
          }
        });
        const tableHeardList = fieldsList.filter(field => field.visible);
        tableHeardList.push(
          {
            key: 'id',
            name: 'id',
          },
          {
            key: 'isCheck',
            name: 'isCheck',
          },
          {
            key: 'departments',
            name: 'departments',
          },
        );
        tableHeardList.forEach((item) => {
          this.userMessage.tableHeardList.push(item);
        });
      } catch (e) {
        console.warn(e);
      }
    },
    async initRecoverySetting() {
      try {
        const res = await this.$store.dispatch('setting/getGlobalSettings');
        this.retentionDays = res.data[0].value;
      } catch (e) {
        console.warn(e);
      }
    },
    // 初始化直接上级列表
    async initRtxList(id) {
      try {
        this.basicLoading = true;
        this.showSyncDetails = false;
        const params = {
          id,
          pageSize: this.paginationConfig.limit,
          page: this.paginationConfig.current,
          keyword: this.checkSearchKey,
          hasNotDepartment: !this.isSearchCurrentDepartment,
        };
        const res = await this.$store.dispatch('organization/getSupOrganization', params);
        this.handleTabData.totalNumber = res.data.count;
        this.handleTabData.currentNumber = res.data.count;
        this.isTableDataEmpty = false;
        this.isEmptySearch = false;
        this.isTableDataError = false;

        if (!!this.tableSearchKey.length) return;
        this.paginationConfig.count = res.data.count;
        this.filterUserData(res.data.results);
        if (this.paginationConfig.count === 0) {
          this.isTableDataEmpty = true;
        }
      } catch (e) {
        console.warn(e);
        this.isTableDataError = true;
      } finally {
        this.basicLoading = false;
        this.isClick = false;
        this.tableSearchedKey = this.tableSearchKey;
      }
    },
    getNodeColor() {
      this.currentNode = document.getElementsByClassName('tree-drag-node')[0];
    },
    updateAcitveNode() {
      this.$nextTick(() => {
        const activeNode = document.getElementsByClassName('show-background')[0];
        if (!activeNode) return;
        this.currentNode = activeNode.parentNode.parentNode;
      });
    },
    // 激活节点变化、清空组织搜索刷新表格数据
    initTableData() {
      this.handleTabData.totalNumber = 0;
      this.handleTabData.departName = this.currentParam.item.full_name || this.currentParam.item.display_name;
      this.handleTableData();
    },
    async getTableData() {
      if (this.currentParam.item.isNewDeparment === true) {
        this.handleTabData.totalNumber = 0;
        this.currentParam.item.isNewDeparment = false;
        return;
      }

      try {
        this.basicLoading = true;
        this.showSyncDetails = false;
        let id = '';
        if (this.treeSearchResult && this.treeSearchResult.groupType === 'department') {
          id = this.treeSearchResult.id;
        }
        const params = {
          id: id || this.currentParam.item.id,
          pageSize: this.paginationConfig.limit,
          page: this.paginationConfig.current,
          keyword: this.checkSearchKey,
          recursive: !this.isSearchCurrentDepartment,
        };
        const res = await this.$store.dispatch('organization/getProfiles', params);
        this.handleTabData.totalNumber = res.data.count;
        this.handleTabData.currentNumber = res.data.count;
        this.isTableDataEmpty = false;
        this.isEmptySearch = false;
        this.isTableDataError = false;

        if (!!this.tableSearchKey.length) return;
        this.$set(this.currentParam.item, 'profile_count', res.data.count);
        this.filterUserData(res.data.results);
        this.paginationConfig.count = res.data.count;
        if (this.paginationConfig.count === 0) {
          this.isTableDataEmpty = true;
        }
      } catch (e) {
        console.warn(e);
        this.isTableDataError = true;
      } finally {
        this.basicLoading = false;
        this.isClick = false;
        this.tableSearchedKey = this.tableSearchKey;
      }
    },
    // 过滤用户信息列表
    filterUserData(list) {
      if (!list.length) {
        this.userMessage.userInforList = [];
        return;
      }
      const userInforList = [];
      list.forEach((item) => {
        const filterTitle = Object.keys(item);
        if (item.leaders) {
          this.$set(item, 'leader', item.leaders);
        }
        if (!item.department_name) {
          // 兼容旧代码，因为后端不再返回 display_name
          item.department_name = item.departments.map(department => department.full_name);
        }
        const originItem = JSON.parse(JSON.stringify(item));

        item.isCheck = false;
        const obj = {};
        const tempObj = {};
        Object.keys(item).forEach((key) => {
          filterTitle.forEach((element) => {
            if (element === key) {
              obj[key] = item[key];
            }
          });
        });
        // title与内容一一对应
        for (let i = 0; i < filterTitle.length; i++) {
          tempObj[filterTitle[i]] = (obj[filterTitle[i]]);
        }
        tempObj.originItem = originItem;
        userInforList.push(tempObj);
      });
      this.userMessage.userInforList = list;
    },
    // 切换是否仅显示本级成员
    changeSearchLevel() {
      this.isSearchCurrentDepartment = !this.isSearchCurrentDepartment;
      this.handleTableData();
    },

    // 分页查询
    handlePageChange(page) {
      this.paginationConfig.current = page;
      this.tableSearchKey.length ? this.handleTableSearch(this.tableSearchKey) : this.handleTableData();
    },
    handlePageLimitChange(limit) {
      this.paginationConfig.limit = limit;
      this.tableSearchKey.length ? this.handleTableSearch(this.tableSearchKey) : this.handleTableData();
    },
    // 选中的用户列表
    isClickList(selection) {
      this.isCheckList = selection;
    },
    updateHeardList(value) {
      this.searchDataList = [];
      value.forEach((item) => {
        if (item.builtin && item.key !== 'department_name') {
          this.searchDataList.push(item);
        }
      });
    },
    // 清空筛选条件
    handleClickEmpty() {
      this.tableSearchKey = [];
      this.checkSearchKey = '';
      this.handleTableData();
    },
    // 搜索table
    handleTableSearch(list) {
      this.isTableDataEmpty = false;
      this.basicLoading = true;
      if (!list.length) return this.handleClickEmpty();
      const valueList = [`category_id=${this.currentCategoryId}&page=${this.paginationConfig.current}&page_size=${this.paginationConfig.limit}`];
      let key = '';
      list.forEach((item) => {
        const value = [];
        if (Object.keys(this.enumList).includes(item.id)) {
          key = this.enumList[item.id];
        }
        if (!item.values) return;
        item.values.forEach((v) => {
          value.push(v.id);
        });
        valueList.push(`${key}=${value}`);
      });
      const params = valueList.join('&');
      this.$store.dispatch('organization/getMultiConditionQuery', params).then((res) => {
        if (res.result) {
          this.basicLoading = false;
          this.isEmptySearch = res.data.count === 0;
          this.paginationConfig.count = res.data.count;
          this.filterUserData(res.data.results);
        }
      })
        .catch((e) => {
          console.warn(e);
          this.isTableDataError = true;
          this.basicLoading = false;
        });
    },
    // 搜索文件配置列表
    handleSearchList() {
      this.getLeadersList();
    },
    // 获取上级列表
    async getLeadersList() {
      try {
        const params = this.isSearchCurrentDepartment ? [`category_id=${this.currentCategoryId}&departments=${this.departmentsId}`] : [`category_id=${this.currentCategoryId}`];
        const list = [];
        const res = await this.$store.dispatch('organization/getMultiConditionQuery', params);
        res.data.results.forEach((item) => {
          list.push({
            id: item.id,
            name: `${item.username}（${item.display_name}）`,
          });
        });
        this.getChildrenList(list, 'leader');
      } catch (e) {
        console.warn(e);
      }
    },
    // 获取组织和上级的子列表
    getChildrenList(list, value) {
      this.heardList.filter((item) => {
        if (item.id === value) {
          this.$set(item, 'children', list);
          this.$set(item, 'multiable', true);
        }
      });
    },
    // 搜索结果： 1.展开tree 找到对应的node 加载用户信息列表
    async handleSearchTree(searchResult) {
      // 消除之前空组织对搜索结果的影响
      this.treeSearchResult = searchResult;
      if (searchResult === null) {
        // 关闭搜索
        const currentItem = this.currentParam.item;
        this.isShowingSearchTree = false;
        this.treeLoading = true;
        if (this.hasTreeDataModified) {
          // 在搜索的结果里重命名或删除了组织，需要重新初始化数据
          this.initLoading = true;
          await this.initData();
          this.getNodeColor();
          this.initLoading = false;
        } else {
          // 恢复组织显示
          await this.initData();
          this.getNodeColor();
        }
        this.hasTreeDataModified = false;
        this.treeLoading = false;
        // 恢复当前目录/组织类型
        this.currentCategoryId = currentItem.type ? currentItem.id : this.findCategoryId(currentItem);
        this.currentCategoryType = currentItem.type ? currentItem.type : this.findCategoryType(currentItem);
      } else if (searchResult.groupType === 'department') {
        // 搜索结果为组织
        this.handleTabData.totalNumber = 0;
        // 搜索的结果就是展示的组织
        this.setTreeDataFromSearchResult(searchResult, searchResult.category_id);
        // 获取该组织下的人员
        this.handleTableData();
      } else {
        // 搜索结果为人员，只展示所在的第一个组织
        this.setTreeDataFromSearchResult(searchResult, searchResult.category_id);
        // 直接将搜索的单个人员信息展示在表格中
        this.filterUserData([searchResult]);
        this.$nextTick(() => {
          // 搜索用户后展开详情
          this.viewDetails(searchResult);
        });
      }
    },
    // 生成搜索结果的组织树（单条）
    setTreeDataFromSearchResult(department, catalogId) {
      this.isShowingSearchTree = true;
      if (!department) {
        this.handleTabData.departName = '';
        return;
      }
      this.handleTabData.departName = department.full_name;
      this.$set(department, 'showBackground', true);
      this.$set(department, 'showOption', false);
      // 判断是不是本地目录下的组织
      this.treeDataList = this.treeDataList.filter((catalog) => {
        if (catalog.id === catalogId) {
          department.isLocalDepartment = catalog.type === 'local';
          this.currentCategoryId = catalogId;
          this.currentCategoryType = catalog.type;
          return catalog.children = catalog.children.filter((child) => {
            if (child.id === department.id) {
              this.currentParam.item = child;
              this.handleClickTreeNode(child);
              return child;
            }
          });
        }
      });
      this.updateAcitveNode();
    },

    // 重命名，添加下级组织，设置表字段弹窗操作
    handleRename(item, event) {
      if (event) {
        event.stopPropagation();
      }
      item.showOption = false;
      const type = item.parent === null ? 'catalog' : 'department';
      this.renameData = { item, type };
      this.handleTabData.title = this.$t('重命名');
      this.handleTabData.isShow = true;
    },
    actionConfirmFn() {
      if (this.handleTabData.isNameError) {
        return;
      }
      if (this.handleTabData.title === this.$t('重命名')) {
        // 重命名
        this.treeLoading = true;
        this.renameData.type === 'catalog' ? this.confirmRenameCatalog() : this.confirmRenameDepartment();
      }
      this.handleTabData.isShow = false;
    },
    actionCancelFn() {
      this.handleTabData.isShow = false;
    },
    // 目录重命名
    async confirmRenameCatalog() {
      try {
        const res = await this.$store.dispatch('catalog/ajaxPatchCatalog', {
          id: this.renameData.item.id,
          data: {
            display_name: this.$refs.dialogContentRef.departmentName,
          },
        });
        const { display_name: name } = res.data;
        this.renameData.item.display_name = name;
        this.messageSuccess(this.$t('重命名成功'));
      } catch (e) {
        console.warn(e);
      } finally {
        this.treeLoading = false;
      }
    },
    // 组织重命名
    async confirmRenameDepartment() {
      try {
        const res = await this.$store.dispatch('organization/modifyDepartmentName', {
          id: this.renameData.item.id,
          name: this.$refs.dialogContentRef.departmentName,
        });
        const { name, full_name: fullName } = res.data;
        this.renameData.item.name = name;
        this.renameData.item.full_name = fullName;
        this.handleTabData.departName = fullName;
        this.messageSuccess(this.$t('重命名成功'));
        this.hasTreeDataModified = true;
        this.handleTableData();
      } catch (e) {
        console.warn(e);
      } finally {
        this.treeLoading = false;
      }
    },
    // 设置列表字段
    async handleSetFieldList(idList) {
      try {
        this.basicLoading = true;
        await this.$store.dispatch('setting/updateFieldsVisible', { idList });
        // 更新头部title + 用户信息列表
        await this.getTableTitle();
        await this.handleTableData();
      } catch (e) {
        console.warn(e);
        this.basicLoading = false;
      }
    },
    // 查看当前用户的信息
    viewDetails(item) {
      this.currentProfile = item;
      this.detailsBarInfo.type = 'view';
      this.detailsBarInfo.title = item.username;
      this.detailsBarInfo.isShow = true;
      this.detailsBarInfo.basicLoading = false;
    },
    // 侧边栏 点击保存 更新列表 userMessage.userInforList
    async updateUserInfor() {
      if (this.treeSearchResult && this.treeSearchResult.groupType !== 'department') {
        // 搜索个人信息下保存 profile
        this.getProfileById();
        this.cancelHideBar();
      } else {
        this.handleTableData();
      }
      this.detailsBarInfo.isShow = false;
      setTimeout(() => {
        this.isHideBar = false;
      }, 300);

      let tipMessage;
      if (this.detailsBarInfo.title === this.$t('新增用户')) {
        const res = await this.$store.dispatch('catalog/ajaxGetPassport', {
          id: this.currentCategoryId,
        });
        const method = this.$convertArrayToObject(res.data).default.init_password_method;
        if (method === 'fixed_preset') {
          tipMessage = this.$t('账户创建成功');
        } else if (method === 'random_via_mail') {
          tipMessage = this.$t('账户创建成功，登录方式已发送至用户邮箱');
        }
      } else {
        tipMessage = this.$t('编辑成功');
      }
      this.$bkMessage({
        message: tipMessage,
        theme: 'success',
      });
    },
    // 搜索个人信息
    async getProfileById() {
      try {
        this.basicLoading = true;
        this.showSyncDetails = false;
        const res = await this.$store.dispatch('organization/getProfileById', { id: this.treeSearchResult.id });
        const searchList = [res.data];
        this.filterUserData(searchList);
      } catch (e) {
        console.warn(e);
      } finally {
        this.basicLoading = false;
      }
    },
    // 控制侧边栏 loading
    showBarLoading() {
      this.detailsBarInfo.basicLoading = true;
    },
    closeBarLoading() {
      this.detailsBarInfo.basicLoading = false;
    },

    // 控制表格 loading
    showTableLoading() {
      this.basicLoading = true;
    },
    closeTableLoading() {
      this.basicLoading = false;
    },
    // 点击保存时打开 loading，临时在样式上隐藏侧边栏
    hideBar() {
      this.isHideBar = true;
      this.basicLoading = true;
    },
    showBar() {
      this.isHideBar = false;
      this.basicLoading = false;
    },
    // 因为 updateUserInfor 里面有个逻辑不会关闭 loading
    cancelHideBar() {
      this.basicLoading = false;
      setTimeout(() => {
        this.isHideBar = false;
      }, 300);
    },

    // 编辑成员信息
    editProfile() {
      this.detailsBarInfo.type = 'edit';
      this.detailsBarInfo.title = this.$t('编辑用户');
    },
    handleCancelEdit() {
      if (this.detailsBarInfo.type === 'add') {
        this.detailsBarInfo.isShow = false;
      } else {
        this.detailsBarInfo.type = 'view';
        this.detailsBarInfo.title = this.$t('用户详情');
      }
    },
    // 新增用户 调用接口，拿到数据传给子组件
    async addUserFn() {
      this.currentProfile = null;
      this.detailsBarInfo.title = this.$t('新增用户');
      this.detailsBarInfo.type = 'add';
      this.detailsBarInfo.isShow = true;
      // 设置所在的组织
      const department = this.treeSearchResult ? this.treeSearchResult : this.currentParam.item;
      this.detailsBarInfo.departments = [{
        id: department.id,
        name: department.name,
      }];
      this.$refs.dropdownAdd.hide();
    },
    // 设置所在的组织
    handleSetDepartment() {
      if (!this.isClick) {
        return;
      }
      this.$refs.dropdownMore.hide();
      // 1.只勾选一条 则回显所设置的组织  2.勾选多条则不用，只用展开第一层
      if (this.isCheckList.length === 1) {
        // 因为这里必有组织，所以子组件定会 emit selectedDepartments 因此不用对 selectedDepartments 初始化
        this.initialDepartments = this.isCheckList[0].departments;
      } else {
        this.initialDepartments = [];
      }
      this.isShowSetDepartments = true;
    },
    // 设置所在组织拿到的组织列表
    getDepartments(val) {
      this.getSelectedDepartments = val;
    },
    // 确定 设置所在组织
    async selectDeConfirmFn() {
      if (!this.getSelectedDepartments.length) {
        this.$bkMessage({
          message: this.$t('请选择组织'),
          theme: 'warning',
        });
        return;
      }

      // 获取到勾选的用户id
      const userSelected = this.isCheckList.filter(item => item.id);
      // 获取到设置组织的id
      const departmentIds = this.getSelectedDepartments.map(item => item.id);

      const params = userSelected.map((item) => {
        return {
          id: item.id,
        };
      });
      params.forEach((item) => {
        item.departments = departmentIds;
      });

      if (this.clickSecond) {
        return;
      }
      this.clickSecond = true;
      this.basicLoading = true;
      this.isShowSetDepartments = false;
      try {
        await this.$store.dispatch('organization/batchAddDepart', params);
        this.handleTableData();
        this.$bkMessage({
          message: this.$t('设置成功'),
          theme: 'success',
        });
      } catch (e) {
        console.warn(e);
        this.basicLoading = false;
        this.isShowSetDepartments = true;
      } finally {
        this.clickSecond = false;
      }
    },
    // 批量删除用户信息
    deleteProfiles() {
      if (!this.isClick) {
        return;
      }
      this.$refs.dropdownMore.hide();
      this.$bkInfo({
        title: this.$t('确认要删除当前用户？'),
        extCls: 'king-info long-title',
        confirmFn: async () => {
          if (this.clickSecond) {
            return;
          }
          this.clickSecond = true;
          this.basicLoading = true;
          try {
            const checkIds = [];
            this.isCheckList.forEach((element) => {
              checkIds.push({
                id: element.id,
              });
            });
            const res = await this.$store.dispatch('organization/deleteProfiles', checkIds);
            if (res.result === true) {
              this.$bkMessage({
                message: this.$t('删除成功'),
                theme: 'success',
              });
            }
            this.handleTableData();
          } catch (e) {
            console.warn(e);
            this.basicLoading = false;
          } finally {
            this.clickSecond = false;
          }
        },
      });
    },
    // 删除某一条用户信息，更新用户信息列表
    deleteProfile({ id, username }) {
      this.$bkInfo({
        title: this.$t('delete-user', { name: username }),
        extCls: 'king-info long-title',
        confirmFn: () => {
          if (this.clickSecond) {
            return;
          }
          this.clickSecond = true;
          this.hideBar();
          this.$store.dispatch('organization/deleteProfiles', [{ id: id ? id : this.currentProfile.id }]).then(async (res) => {
            if (res.result === true) {
              this.$bkMessage({
                message: this.$t('删除成功'),
                theme: 'success',
              });
              this.currentProfile.status = 'DELETED';
            }
            this.detailsBarInfo.isShow = false;
            setTimeout(() => {
              this.isHideBar = false;
            }, 500);
            if (this.treeSearchResult && this.treeSearchResult.groupType !== 'department') {
              // 搜索个人信息下删除 profile 关闭搜索
              this.basicLoading = false;
              this.$refs.searchChild.closeSearch();
            } else {
              this.handleTableData();
            }
          })
            .catch((e) => {
              console.warn(e);
              this.showBar();
            })
            .finally(() => {
              this.clickSecond = false;
            });
        },
      });
    },
    // 恢复某一条用户信息
    restoreProfile() {
      this.clickSecond = true;
      this.hideBar();
      this.$store.dispatch('organization/postProfilesRestoration', {
        id: this.currentProfile.id,
      }).then((res) => {
        if (res.result === true) {
          this.$bkMessage({
            message: this.$t('恢复成功'),
            theme: 'success',
          });
          this.currentProfile.status = 'NORMAL';
        }
        this.detailsBarInfo.isShow = false;
        setTimeout(() => {
          this.isHideBar = false;
        }, 500);
        if (this.treeSearchResult && this.treeSearchResult.groupType !== 'department') {
          // 搜索个人信息下删除 profile 关闭搜索
          this.basicLoading = false;
          this.$refs.searchChild.closeSearch();
        } else {
          this.handleTableData();
        }
      })
        .catch((e) => {
          console.warn(e);
          this.showBar();
        })
        .finally(() => {
          this.clickSecond = false;
        });
    },
    beforeClose() {
      if (this.detailsBarInfo.type === 'view') {
        this.detailsBarInfo.isShow = false;
      } else {
        if (window.changeInput) {
          this.$bkInfo({
            title: this.$t('确认离开当前页？'),
            subTitle: this.$t('离开将会导致未保存信息丢失'),
            okText: this.$t('离开'),
            confirmFn: () => {
              this.detailsBarInfo.isShow = false;
              window.changeInput = false;
            },
          });
        } else {
          this.detailsBarInfo.isShow = false;
        }
      }
    },
    // 移入某个树节点
    handleMouseenter(event) {
      const targetNode = event.target.parentNode.parentNode;
      if (!targetNode.style.background || targetNode.style.background === 'none') {
        targetNode.style.background = '#f0f1f5';
      }
    },
    // 移出某个树节点
    handleMouseleave(event) {
      const targetNode = event.target.parentNode.parentNode;
      if (targetNode.style.background === 'rgb(240, 241, 245)') {
        targetNode.style.background = 'none';
      }
    },
    // 点击某个树节点
    handleClickTreeNode(item, event) {
      this.paginationConfig.current = 1;
      this.checkSearchKey = '';
      if (event) {
        this.currentNode = event.target.offsetParent.parentNode.parentNode;
      }
      if (this.treeSearchResult && this.treeSearchResult.groupType !== 'department') {
        item.showBackground = true;
        this.handleTabData.totalNumber = 0;
        this.handleTabData.departName = item.full_name;
        return;
      }
      this.treeDataList.forEach((item) => {
        this.closeMenu(item);
      });
      if (this.tableSearchKey) {
        this.tableSearchKey = [];
      }
      this.currentParam.item = item;
      this.$set(item, 'showBackground', true);
      this.handleClickToggle(item);
    },
    // 展开/收起 子级
    async handleClickToggle(item) {
      // 没有子节点，控制文件夹的开关样式
      if (item.has_children === false || (item.children && item.children.length)) {
        item.showChildren = !item.showChildren;
        return;
      }
      // 有子节点，但是还没加载 children 数据
      try {
        item.showLoading = true;
        const res = await this.$store.dispatch('organization/getDataById', { id: item.id });
        this.$set(item, 'children', res.data.children);
        item.children.forEach((element) => {
          this.filterTreeData(element, item, item.isLocalDepartment);
        });
        this.$set(item, 'showChildren', true);
      } catch (e) {
        console.warn(e);
      } finally {
        item.showLoading = false;
      }
    },
    // 隐藏所有节点的功能菜单
    closeMenu(tree) {
      this.$set(tree, 'showOption', false);
      this.$set(tree, 'showBackground', false);
      if (tree.children && tree.children.length) {
        tree.children.forEach((item) => {
          this.closeMenu(item);
        });
      }
    },
    // 显示对应的子菜单
    handleClickOption(item, event) {
      event.stopPropagation();
      this.currentParentNode = event.target.offsetParent.offsetParent.parentNode.parentNode;
      this.currentNode = event.target.offsetParent.offsetParent.parentNode.parentNode;
      if (!this.treeSearchResult) {
        // 展示当前节点
        this.currentParam.item = item;
        // 遍历 只激活当前节点样式和功能菜单
        this.treeDataList.forEach((item) => {
          this.closeMenu(item);
        });
      }
      this.$set(item, 'showOption', true);
      this.$set(item, 'showBackground', true);
      this.$nextTick(() => {
        const next = ((item.activated && item.configured) || item.parent)
          ? event.target.nextElementSibling : event.target.nextElementSibling.nextElementSibling;
        const dom = event.target;
        const { top } = dom.getBoundingClientRect();
        const bottomHeight = window.innerHeight - top - 20;
        if (bottomHeight < next.clientHeight) {
          next.style.top = `${top - next.clientHeight - 12}px`;
        } else  {
          next.style.top = `${top + 26}px`;
        }
      });
    },
    // 点击空白处 ，关闭子菜单
    hiddenMenu(e) {
      if (e.target.classList.contains('show-more')) {
        return;
      }
      this.treeDataList.forEach((item) => {
        this.closeTreeMenu(item);
      });
    },
    closeTreeMenu(tree) {
      tree.showOption = false;
      if (tree.children && tree.children.length) {
        tree.children.forEach((item) => {
          this.closeTreeMenu(item);
        });
      }
    },
    // 拖拽node
    async switchNodeOrder(param) {
      try {
        this.treeLoading = true;
        const { dragNode, targetNode } = param;
        if (dragNode.category_id !== targetNode.category_id || dragNode.parent.id !== targetNode.parent.id) {
          return;
        }
        await this.$store.dispatch('organization/switchNodeOrder', {
          id: dragNode.id,
          upId: targetNode.id,
          nodeType: dragNode.type ? 'categories' : 'departments',
        });
      } catch (e) {
        console.warn(e);
      } finally {
        this.treeLoading = false;
      }
    },
    // 删除组织节点
    deleteDepartment(deleteItem, event) {
      if (event) {
        event.stopPropagation();
      }
      deleteItem.showOption = false;
      if (deleteItem.default || deleteItem.activated || (!deleteItem.type && deleteItem.has_children)) {
        deleteItem.showDeleteTips = false;
        return;
      }
      const h = this.$createElement;
      let instance1 = null;
      let instance2 = null;
      deleteItem.display_name
        ? this.$bkInfo({
          title: this.$t('delete-directory', { name: deleteItem.display_name }),
          subHeader: h(
            'div',
            {
              style: { color: '#63656E', fontSize: '14px', lineHeight: '24px' },
            }, [
              h('p', [this.$t('删除后，该目录下的数据将为你保存'),
                h('span', {
                  style: { color: '#EA3636', fontWeight: '700', cursor: 'pointer', borderBottom: '1px dashed #C4C6CC', padding: '0 5px' },
                  on: {
                    mouseleave: () => {
                      instance1 && instance1.hide(100);
                    },
                    mouseenter: (e) => {
                      instance1 = instance1 || this.$bkPopover(e.target, { content: this.$t('由 admin 在 [回收策略设置] 中统一配置'), arrow: true, placement: 'top' });
                      instance1.show(1000);
                    },
                  },
                }, this.retentionDays), this.$t('天。'),
              ]),
              h('p', [this.$t('你可以在'),
                h('i', {
                  class: 'bk-sq-icon icon-huishouxiang',
                  style: { color: '#699DF4', fontSize: '16px', cursor: 'pointer', borderBottom: '1px dashed #C4C6CC', padding: '0 5px' },
                  on: {
                    mouseleave: () => {
                      instance2 && instance2.hide(100);
                    },
                    mouseenter: (e) => {
                      instance2 = instance2 || this.$bkPopover(e.target, { content: this.$t('在顶部导航栏的右侧'), arrow: true, placement: 'top' });
                      instance2.show(1000);
                    },
                  },
                }), this.$t('回收站中查看已删除的目录数据，并进行还原、彻底删除的操作。'),
              ]),
            ],
          ),
          extCls: 'king-info long-title',
          confirmFn: this.syncConfirmDeleteDepartment.bind(this, deleteItem),
        })
        : this.$bkInfo({
          title: this.$t('delete-organization', { name: deleteItem.name }),
          extCls: 'king-info long-title',
          confirmFn: this.syncConfirmDeleteDepartment.bind(this, deleteItem),
        });
    },
    // 这里使用同步是为了点击确认后立即关闭info
    syncConfirmDeleteDepartment(deleteItem) {
      this.confirmDeleteDepartment(deleteItem);
    },
    async confirmDeleteDepartment(deleteItem) {
      try {
        this.treeLoading = true;
        if (deleteItem.display_name) {
          await this.$store.dispatch('catalog/ajaxDeleteCatalog', { id: deleteItem.id });
          this.messageSuccess(this.$t('目录删除成功'));
          this.treeDataList = this.treeDataList.filter(item => item.id !== deleteItem.id);
          if (this.treeSearchResult) {
            // 搜索里面删除组织后回到正常页面
            this.hasTreeDataModified = true;
            this.$refs.searchChild.closeSearch();
          } else {
            // 本地处理数据
            this.treeDataList[0].showBackground = true;
            this.currentParam.item = this.treeDataList[0];
          }
          this.updateAcitveNode();
        } else {
          await this.$store.dispatch('organization/deleteDepartment', { id: deleteItem.id });
          this.messageSuccess(this.$t('组织删除成功'));
          deleteItem.directParent.children = deleteItem.directParent.children.filter(item => item.id !== deleteItem.id);
          if (this.treeSearchResult) {
            // 搜索里面删除组织后回到正常页面
            this.hasTreeDataModified = true;
            this.$refs.searchChild.closeSearch();
          } else {
            // 本地处理数据
            if (!deleteItem.directParent.children.length) {
              deleteItem.directParent.has_children = false;
              deleteItem.directParent.async = false;
            }
            deleteItem.directParent.showBackground = true;
            this.currentParam.item = deleteItem.directParent;
          }
          this.updateAcitveNode();
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.treeLoading = false;
      }
    },

    // 批量拉取用户
    pullUserFn() {
      this.batchUserInfo.isShow = true;
      this.$refs.dropdownAdd.hide();
    },
    getPullUser(item) {
      this.batchUserInfo.tags = item;
    },
    // 确认：批量拉取用户
    async submitBatch() {
      if (!this.batchUserInfo.tags.length) {
        this.$bkMessage({
          message: this.$t('请输入账户'),
          theme: 'warning',
        });
        return;
      }
      try {
        this.batchUserInfo.isShow = false;
        this.basicLoading = true;
        const selectIds = this.batchUserInfo.tags;
        await this.$store.dispatch('organization/postUserToDepartments', {
          id: this.treeSearchResult ? this.treeSearchResult.id : this.currentParam.item.id,
          idList: selectIds,
        });
        this.handleTableData();
      } catch (e) {
        console.warn(e);
        this.basicLoading = false;
      } finally {
        this.batchUserInfo.tags = [];
      }
    },
    // 取消：批量拉取用户
    BatchCancelFn() {
      this.batchUserInfo.isShow = false;
      this.batchUserInfo.tags = [];
    },
    findCategoryId(item) {
      if (item.category_id) {
        return item.category_id;
      }
      return this.findCategoryId(item.directParent);
    },
    findCategoryType(item) {
      if (item.type) {
        return item.type;
      }
      return this.findCategoryType(item.directParent);
    },
    handleTableData() {
      this.isRootDirectory
        ? this.initRtxList(this.currentParam.item.id)
        : this.getTableData();
    },
    // 配置目录
    addDirectory() {
      this.showingPage = 'showPageAdd';
    },
    // 获取目录列表
    async getCatalogList() {
      try {
        const res = await this.$store.dispatch('catalog/ajaxGetCatalogList');
        this.catalogList = res.data;
      } catch (e) {
        console.warn(e);
      } finally {
        this.$store.commit('updateInitLoading', false);
      }
    },
    async initCatalogMetas() {
      try {
        const res = await this.$store.dispatch('catalog/ajaxGetCatalogMetas');
        this.catalogMetas = res.data;
      } catch (e) {
        console.warn(e);
      }
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
          password: this.$convertDefault(password.data),
          connection: this.$convertDefault(connection.data),
          fieldsMad: this.$convertDefault(fieldsMad.data),
          fieldsLdap: this.$convertDefault(fieldsLdap.data),
        };
        this.$store.commit('catalog/updateDefaults', defaults);
      } catch (e) {
        console.warn(e);
      }
    },
    changePage(param, update) {
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
        if (update) {
          Promise.all([this.initData(), this.getCatalogList(), this.getNodeColor()]);
        }
      }
    },
    handleCancel() {
      this.$bkInfo({
        title: this.$t('您尚未完成所有设置，确定离开页面？'),
        width: 560,
        confirmFn: () => {
          this.showingPage = 'showPageHome';
          this.getCatalogList();
          this.initData();
        },
      });
    },
    // 配置未完成目录
    handleClickConfig(event) {
      event.stopPropagation();
      this.catalogList.map((item) => {
        if (item.id === this.currentCategoryId) {
          this.changePage(item);
        }
      });
    },
    // 添加组织
    addOrganization(node, event) {
      if (node.level > 9) return;
      if (node.expanded) {
        event.stopPropagation();
      }
      node.showOption = false;
      node.showChildren = true;
      const inputNode = document.getElementsByClassName('new-department')[0];
      inputNode.style.display = 'flex';
      if (node.type === 'local') {
        const ulNode = this.currentParentNode.parentNode.lastChild;
        ulNode.appendChild(inputNode);
        ulNode.lastChild.getElementsByClassName('bk-form-input')[0].focus();
      }
      if (node.isLocalDepartment) {
        const liNode = this.currentParentNode.parentNode;
        liNode.after(inputNode);
        liNode.nextElementSibling.getElementsByClassName('bk-form-input')[0].focus();
      }
    },
    cancelAdd() {
      const inputNode = document.getElementsByClassName('new-department')[0];
      inputNode.style.display = 'none';
      this.addOrganizationName = '';
    },
    handleKeydown(value, event) {
      if (event.code === 'Escape') {
        this.cancelAdd();
      }
    },
    async confirmAdd() {
      const name = this.addOrganizationName.trim();
      if (!name) {
        this.cancelAdd();
        return;
      }
      try {
        this.treeLoading = true;
        if (this.currentParam.item.type) {
          const params = {
            name: this.addOrganizationName,
            category_id: this.currentCategoryId,
          };
          const res = await this.$store.dispatch('organization/addDepartment', params);
          const newDepartment = res.data;
          newDepartment.isNewDeparment = false;
          this.filterTreeData(newDepartment, this.currentParam.item, this.currentParam.item.type === 'local');
          this.currentParam.item.children.push(newDepartment);
          this.handleClickTreeNode(newDepartment);
          this.updateAcitveNode();
        } else {
          const params = {
            name: this.addOrganizationName,
            category_id: this.currentCategoryId,
            parent: this.currentParam.item.id,
          };
          const res = await this.$store.dispatch('organization/addDepartment', params);
          if (res.result === true) {
            this.messageSuccess(`${this.$t('成功添加下级组织')} ${params.name}`);
            if (this.currentParam.item.showChildren) {
              this.isAddChild = true;
            }
            this.currentParam.item.has_children = true;
            this.currentParam.item.async = true;
            this.updateChildren(this.currentParam.item);
          }
        }
        this.cancelAdd();
      } catch (e) {
        console.warn(e);
      } finally {
        this.treeLoading = false;
      }
    },
    updateScroll() {
      this.currentParam.item.showOption = false;
    },
    // 更新数据记录
    async handleClickUpdate() {
      try {
        this.showSyncDetails = true;
        this.dataUpdateLoading = true;
        const params = {
          categoryId: this.currentCategoryId,
          page: this.dataUpdatePagination.current,
          pageSize: this.dataUpdatePagination.limit,
        };
        const res = await this.$store.dispatch('catalog/ajaxGetUpdateRecord', params);
        this.dataUpdateList = res.data.results;
        this.dataUpdatePagination.count = res.data.count;
      } catch (e) {
        console.warn(e);
      } finally {
        this.dataUpdateLoading = false;
      }
    },
    dataUpdatePageChange(page) {
      this.dataUpdatePagination.current = page;
      this.handleClickUpdate();
    },
    dateUpdatePageLimit(limit) {
      this.dataUpdatePagination.limit = limit;
      this.handleClickUpdate();
    },
  },
};
</script>

<style lang="scss" scoped>
@import './index.scss';

.king-sideslider {
  background-color: rgba(0, 0, 0, .6);
}
</style>

<style lang="scss">
@import './index.scss';
@import '../../scss/variable.scss';
#catalog {
  width: 100%;
  // 新增、设置目录页面公共样式
  .catalog-operation-container {
    display: flex;
    width: 100%;
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
