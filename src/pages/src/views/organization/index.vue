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
  <div class="organization-wrapper" @click="hiddenMenu" v-bkloading="{ isLoading: initLoading }">
    <div class="organization-left" :style="{ width: treeBoxWidth + 'px' }" v-show="!initLoading">
      <TreeSearch ref="searchChild" @searchTree="handleSearchTree" />
      <div class="tree-loading-wrapper" v-bkloading="{ isLoading: treeLoading }">
        <div class="tree-content-wrapper" ref="treePanel">
          <OrganizationTree
            v-show="!isShowingSearchTree"
            :tree-data-list="treeDataList"
            :tree-search-result="treeSearchResult"
            @handleClickToggle="handleClickToggle"
            @handleClickTreeNode="handleClickTreeNode"
            @handleClickOption="handleClickOption"
            @addChildDepartment="addChildDepartment"
            @handleRename="handleRename"
            @switchNodeOrder="switchNodeOrder"
            @deleteDepartment="deleteDepartment"
            @showTreeLoading="treeLoading = true"
            @closeTreeLoading="treeLoading = false" />
          <OrganizationTree
            v-if="isShowingSearchTree"
            :tree-data-list="searchTreeList"
            :tree-search-result="treeSearchResult"
            @handleClickOption="handleClickOption"
            @handleRename="handleRename"
            @deleteDepartment="deleteDepartment" />
        </div>
      </div>
    </div>
    <div class="organization-right" :style="{ width: 'calc(100% - ' + treeBoxWidth + 'px)' }" v-show="!initLoading">
      <!-- 用户目录节点 -->
      <div class="catalog-info" v-if="isShowCatalogPage">
        <h1 class="catalog-name">
          {{currentParam.item.display_name}}
        </h1>
        <p class="catalog-detail">
          {{$t('含') + currentParam.item.departments.length +
            $t('个组织') +
            (currentParam.item.profile_count || '0') + $t('人')}}
        </p>
      </div>
      <!-- 组织节点 -->
      <template v-else>
        <!-- 组织名称和人数 -->
        <div class="department-title">
          <div class="title-content">
            <span class="department-name" v-bk-overflow-tips>{{handleTabData.departName}}</span>
            <span class="total-number" v-if="handleTabData.totalNumber !== null && noSearchOrSearchDepartment">
              ({{handleTabData.totalNumber}})
            </span>
          </div>
        </div>
        <!-- 组织下无成员 -->
        <div class="empty-department" v-show="isEmptyDepartment" v-bkloading="{ isLoading: basicLoading }">
          <div class="empty-search">
            <img src="../../images/svg/info.svg" alt="info">
            <p>{{$t('暂无组织成员')}}</p>
            <template v-if="currentCategoryType === 'local' && isTableDataError === false">
              <p class="tips">{{$t('如需添加组织成员，可通过以下两种方式进行')}}</p>
              <div class="button-container">
                <bk-button theme="primary" style="min-width: 120px;margin-right: 10px;" @click="addUserFn">
                  {{$t('新增用户')}}
                </bk-button>
                <!-- 从其他组织拉取 -->
                <bk-button style="min-width: 120px;" @click="pullUserFn">
                  {{$t('从其他组织拉取')}}
                </bk-button>
              </div>
            </template>
          </div>
        </div>
        <!-- 正常分页查询有数据，或者筛选筛选、搜索无数据 -->
        <div class="staff-info-wrapper" v-show="!isEmptyDepartment">
          <!-- 表格上方的操作栏，组织树搜索结果为非组织时不渲染 -->
          <div class="table-actions" v-if="noSearchOrSearchDepartment">
            <!-- 本地用户目录 -->
            <template v-if="currentCategoryType === 'local'">
              <div class="table-actions-left-container local-type" data-test-id="list_operationUser">
                <!-- 添加成员 -->
                <bk-dropdown-menu ref="dropdownAdd" class="king-dropdown-menu"
                                  :disabled="basicLoading" @show="isDropdownShowAdd = true"
                                  @hide="isDropdownShowAdd = false">
                  <bk-button slot="dropdown-trigger" class="king-button">
                    <span class="more-action">{{$t('添加用户')}}</span>
                    <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShowAdd }]"></i>
                  </bk-button>
                  <ul class="bk-dropdown-list" slot="dropdown-content">
                    <li><a href="javascript:;" @click="addUserFn">{{$t('新增用户')}}</a></li>
                    <li><a href="javascript:;" @click="pullUserFn">{{$t('从其他组织拉取')}}</a></li>
                  </ul>
                </bk-dropdown-menu>
                <!-- 更多操作 -->
                <bk-dropdown-menu ref="dropdownMore" class="king-dropdown-menu"
                                  :disabled="basicLoading" @show="isDropdownShowMore = true"
                                  @hide="isDropdownShowMore = false">
                  <bk-button slot="dropdown-trigger" class="king-button">
                    <span class="more-action">{{$t('更多操作')}}</span>
                    <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShowMore }]"></i>
                  </bk-button>
                  <ul class="bk-dropdown-list" slot="dropdown-content">
                    <li>
                      <a href="javascript:;" :class="{ 'disabled': !isClick }"
                         @click="handleSetDepartment">{{$t('设置所在组织')}}
                      </a>
                    </li>
                    <li>
                      <a href="javascript:;" :class="{ 'disabled': !isClick }"
                         @click="deleteProfiles">{{$t('批量删除')}}
                      </a>
                    </li>
                  </ul>
                </bk-dropdown-menu>
                <!-- 仅显示本级组织成员 -->
                <p class="filter-current">
                  <bk-checkbox class="king-checkbox" :checked="isSearchCurrentDepartment"
                               @change="changeSearchLevel">
                  </bk-checkbox>
                  <span class="text text-overflow-hidden" v-bk-overflow-tips @click="changeSearchLevel">
                    {{$t('仅显示本级组织成员') + (handleTabData.currentNumber === null ? ''
                      : `(${handleTabData.currentNumber})`)}}
                  </span>
                </p>
              </div>
              <div class="table-actions-right-container">
                <!-- 用户搜索框 -->
                <bk-input v-model="tableSearchKey"
                          class="king-input-search"
                          style="width: 280px;margin-right: 20px;"
                          :placeholder="$t('输入用户名/中文名，按Enter搜索')"
                          :clearable="true"
                          :left-icon="'bk-icon icon-search'"
                          @clear="handleClear"
                          @left-icon-click="handleTableSearch"
                          @enter="handleTableSearch">
                </bk-input>
                <!-- 设置列表字段 -->
                <div class="set-table-field" v-bk-tooltips.top="$t('设置列表字段')" @click="setFieldList">
                  <i class="icon icon-user-cog"></i>
                </div>
              </div>
            </template>
            <!-- 非本地用户目录 -->
            <template v-else>
              <div class="table-actions-left-container">
                <!-- 用户搜索框 -->
                <bk-input v-model="tableSearchKey"
                          class="king-input-search"
                          style="width: 360px;margin-right: 20px;"
                          :placeholder="$t('输入用户名/中文名，按Enter搜索')"
                          :clearable="true"
                          :left-icon="'bk-icon icon-search'"
                          @clear="handleClear"
                          @left-icon-click="handleTableSearch"
                          @enter="handleTableSearch">
                </bk-input>
                <!-- 仅显示本级组织成员 -->
                <p class="filter-current">
                  <bk-checkbox class="king-checkbox" :checked="isSearchCurrentDepartment"
                               @change="changeSearchLevel"></bk-checkbox>
                  <span class="text" @click="changeSearchLevel">
                    {{$t('仅显示本级组织成员') + (handleTabData.currentNumber === null ? ''
                      : `(${handleTabData.currentNumber})`)}}
                  </span>
                </p>
              </div>
              <div class="table-actions-right-container">
                <!-- 设置列表字段 -->
                <div class="set-table-field" v-bk-tooltips.top="$t('设置列表字段')" @click="setFieldList">
                  <i class="icon icon-user-cog"></i>
                </div>
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
              :is-click.sync="isClick"
              :loading="basicLoading"
              :fields-list="fieldsList"
              :current-category-type="currentCategoryType"
              :no-search-or-search-department="noSearchOrSearchDepartment"
              @viewDetails="viewDetails"
              @showTableLoading="showTableLoading"
              @closeTableLoading="closeTableLoading" />
            <div class="table-pagination" v-if="noSearchOrSearchDepartment && paginationConfig.count > 0">
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
        </div>
      </template>
    </div>
    <!-- 新增用户 侧边栏 -->
    <bk-sideslider class="king-sideslider"
                   :width="520"
                   :show-mask="false"
                   :is-show.sync="detailsBarInfo.isShow"
                   :quick-close="detailsBarInfo.quickClose"
                   :title="detailsBarInfo.title"
                   :style="{ visibility: isHideBar ? 'hidden' : 'visible' }">
      <div slot="content" class="member-content" v-if="detailsBarInfo.isShow">
        <DetailsBar
          :details-bar-info="detailsBarInfo"
          :current-profile="currentProfile"
          :current-category-id="currentCategoryId"
          :current-category-type="currentCategoryType"
          :fields-list="fieldsList"
          @hideBar="hideBar"
          @showBar="showBar"
          @showBarLoading="showBarLoading"
          @closeBarLoading="closeBarLoading"
          @getTableData="getTableData"
          @updateUserInfor="updateUserInfor"
          @editProfile="editProfile"
          @handleCancelEdit="handleCancelEdit"
          @deleteProfile="deleteProfile" />
      </div>
    </bk-sideslider>
    <!-- 弹窗操作 -->
    <div class="operation-wrapper">
      <!-- 重命名、添加下级组织、设置列表字段 -->
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
      <bk-dialog width="721"
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
        :title="$t('从其他组织拉取')"
        :ok-text="$t('提交')"
        @confirm="submitBatch"
        @cancel="BatchCancelFn">
        <div class="batch-content-wrapper">
          <PullUser v-if="batchUserInfo.isShow" ref="pullUser" :id="currentCategoryId" @getPullUser="getPullUser" />
        </div>
      </bk-dialog>
    </div>
    <!-- table basic loading 时的遮罩层 -->
    <div v-show="basicLoading || initLoading || isChangingWidth" class="loading-cover" @click.stop></div>
    <!-- 可拖拽页面布局宽度 -->
    <div ref="dragBar" :class="['drag-bar', isChangingWidth && 'dragging']" :style="{ left: treeBoxWidth - 1 + 'px' }">
      <img src="../../images/svg/drag-icon.svg" alt="drag"
           draggable="false" class="drag-icon" @mousedown.left="dragBegin">
    </div>
  </div>
</template>

<script>
import TreeSearch from './tree/TreeSearch';
import OrganizationTree from './tree/OrganizationTree';
import DialogContent from './tree/DialogContent';
import UserTable from './table/UserTable';
import PullUser from './table/PullUser';
import DetailsBar from './details/DetailsBar';

import SetDepartment from '@/components/organization/SetDepartment';

export default {
  components: {
    DetailsBar,
    DialogContent,
    SetDepartment,
    OrganizationTree,
    UserTable,
    TreeSearch,
    PullUser,
  },
  data() {
    return {
      initLoading: true,
      // 增加组织请求接口时给树组织一个loading
      treeLoading: false,
      // 左边树组织内容宽度
      treeBoxWidth: 260,
      treeBoxMinWidth: 260,
      treeBoxMaxWidth: 420,
      // 是否正在拖拽宽度
      isChangingWidth: false,
      paginationConfig: {
        current: 1,
        count: 1,
        limit: 10,
      },
      limitList: [10, 20, 50, 100],
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
        totalNumber: null,
        currentNumber: 0,
      },
      // 重命名的目录或组织
      renameData: {},
      // 渲染用户信息
      userMessage: {
        tableHeardList: [],
        userInforList: [],
      },
      // 组织为空
      isEmptyDepartment: false,
      // 搜索结果为空
      isEmptySearch: false,
      // 表格请求出错
      isTableDataError: false,
      // 是否勾选了表格数据
      isClick: false,
      isShowSetDepartments: false,
      treeDataList: [],
      searchTreeList: [],
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
      tableSearchKey: '',
      // 记录搜索过的关键字，blur 的时候如果和当前关键字不一样就刷新表格
      tableSearchedKey: '',
      isDropdownShowAdd: false,
      isDropdownShowMore: false,
      setDepartmentTop: (window.document.body.offsetHeight - 519) / 2,
    };
  },
  computed: {
    noSearchOrSearchDepartment() {
      return Boolean(!this.treeSearchResult || (this.treeSearchResult && this.treeSearchResult.groupType === 'department'));
    },
    isShowCatalogPage() {
      return Boolean(this.currentParam.item.type && !this.treeSearchResult);
    },
  },
  watch: {
    'currentParam.item'(val, oldVal) {
      // 搜索结果为 profile 时切换节点不刷新表格数据
      if (this.treeSearchResult && this.treeSearchResult.groupType !== 'department') {
        return;
      }
      // 当变更选中节点（组织节点），更新用户信息列表
      if (!val.type && (val.id !== oldVal.id || oldVal.type)) {
        this.initTableData();
      }
      this.currentCategoryId = val.type ? val.id : this.findCategoryId(val);
      this.currentCategoryType = val.type ? val.type : this.findCategoryType(val);
    },
  },
  async mounted() {
    // 初始化tree、用户信息title
    const limit = Math.floor((this.$el.offsetHeight - 240) / 42);
    this.paginationConfig.limit = limit;
    const limitList = [10, 20, 50, 100];
    if (!limitList.includes(limit)) {
      limitList.push(limit);
      limitList.sort((a, b) => a - b);
    }
    this.limitList = limitList;
    try {
      await Promise.all([this.initData(), this.getTableTitle()]);
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
        const res = await this.$store.dispatch('organization/getOrganizationTree');
        if (!res.data || !res.data.length) return;
        this.treeDataList = res.data;
        this.treeDataList.forEach((catalog) => {
          this.filterTreeData(catalog, this.treeDataList);
          catalog.children = catalog.departments;
          catalog.children.forEach((department) => {
            this.filterTreeData(department, catalog, catalog.type === 'local');
          });
        });
        this.treeDataList[0] && (this.treeDataList[0].showChildren = true);
        // 初始化添加下级组织
        this.currentParam = {
          item: this.treeDataList[0],
        };
        this.treeDataList[0].showBackground = true;
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
      }
    },
    // 递归处理后台返回的数据
    filterTreeData(tree, directParent, isLocalDepartment = null) {
      // 通过判断存在 type 确定用户目录，手动添加 has_children
      if (tree.type) {
        this.$set(tree, 'has_children', !!tree.departments.length);
      }
      // 组织节点添加一个类型标记
      if (isLocalDepartment !== null) {
        tree.isLocalDepartment = isLocalDepartment;
      }
      tree.directParent = directParent;
      this.$set(tree, 'showOption', false);
      // 激活背景蓝色
      this.$set(tree, 'showBackground', false);
      // 展示子级组织
      this.$set(tree, 'showChildren', false);
      this.$set(tree, 'showLoading', false);

      if (tree.children && tree.children.length) {
        tree.children.forEach((item) => {
          this.filterTreeData(item, tree, isLocalDepartment);
        });
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
          }
        );
        this.userMessage.tableHeardList = tableHeardList;
      } catch (e) {
        console.warn(e);
      }
    },
    // 激活节点变化、清空组织搜索刷新表格数据
    initTableData() {
      this.paginationConfig.count = 1;
      this.paginationConfig.current = 1;
      this.handleTabData.totalNumber = null;
      this.handleTabData.currentNumber = null;
      this.handleTabData.departName = this.currentParam.item.full_name || this.currentParam.item.display_name;
      this.getTableData();
    },
    async getTableData() {
      if (this.currentParam.item.isNewDeparment === true) {
        this.handleTabData.totalNumber = 0;
        this.isEmptyDepartment = true;
        this.currentParam.item.isNewDeparment = false;
        return;
      }

      try {
        this.basicLoading = true;
        let id = '';
        if (this.treeSearchResult && this.treeSearchResult.groupType === 'department') {
          id = this.treeSearchResult.id;
        }
        const params = {
          id: id || this.currentParam.item.id,
          pageSize: this.paginationConfig.limit,
          page: this.paginationConfig.current,
          keyword: this.tableSearchKey,
          recursive: true,
        };
        if (this.isSearchCurrentDepartment) {
          params.recursive = false;
        }
        const res = await this.$store.dispatch('organization/getProfiles', params);

        this.filterUserData(res.data.data);
        this.paginationConfig.count = res.data.count;
        if (!this.tableSearchKey) {
          if (this.isSearchCurrentDepartment) {
            // 当前组织下成员
            this.handleTabData.totalNumber = res.data.total_count;
            this.handleTabData.currentNumber = res.data.count;
          } else {
            // 默认查询
            this.handleTabData.totalNumber = res.data.count;
            this.handleTabData.currentNumber = res.data.current_count;
          }
        }

        this.isEmptyDepartment = false;
        this.isEmptySearch = false;
        if (this.handleTabData.totalNumber === 0) {
          this.isEmptyDepartment = true;
        } else if (this.paginationConfig.count === 0) {
          this.isEmptySearch = true;
        }

        this.isTableDataError = false;
      } catch (e) {
        console.warn(e);
        this.isTableDataError = true;
        this.isEmptyDepartment = true;
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
      const filterTitle = this.userMessage.tableHeardList.map(item => item.key);
      list.forEach((item) => {
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
      this.userMessage.userInforList = userInforList;
    },
    // 切换是否仅显示本级成员
    changeSearchLevel() {
      this.paginationConfig.current = 1;
      this.isSearchCurrentDepartment = !this.isSearchCurrentDepartment;
      this.getTableData();
    },

    // 分页查询
    changeCurrentPage() {
      this.getTableData();
    },
    changeLimitPage(limit) {
      this.paginationConfig.current = 1;
      this.paginationConfig.limit = limit;
      this.getTableData();
    },

    handleClear() {
      if (this.tableSearchedKey !== '') {
        this.handleTableSearch();
      }
    },
    handleTableSearch() {
      if (!this.basicLoading) {
        this.paginationConfig.current = 1;
        this.getTableData();
      }
    },
    // 搜索结果： 1.展开tree 找到对应的node 加载用户信息列表
    async handleSearchTree(searchResult) {
      // 消除之前空组织对搜索结果的影响
      this.isEmptyDepartment = false;
      this.treeSearchResult = searchResult;
      if (searchResult === null) {
        // 关闭搜索
        const currentItem = this.currentParam.item;
        this.searchTreeList = [];
        this.isShowingSearchTree = false;
        if (this.hasTreeDataModified) {
          // 在搜索的结果里重命名或删除了组织，需要重新初始化数据
          this.initLoading = true;
          await this.initData();
          this.initLoading = false;
        } else if (currentItem.type) {
          // 恢复用户目录显示
          this.userMessage.userInforList = [];
        } else {
          // 恢复组织显示
          this.initTableData();
        }
        this.hasTreeDataModified = false;
        // 恢复当前目录/组织类型
        this.currentCategoryId = currentItem.type ? currentItem.id : this.findCategoryId(currentItem);
        this.currentCategoryType = currentItem.type ? currentItem.type : this.findCategoryType(currentItem);
      } else if (searchResult.groupType === 'department') {
        // 搜索结果为组织
        this.paginationConfig.count = 1;
        this.paginationConfig.current = 1;
        this.handleTabData.totalNumber = null;
        this.handleTabData.currentNumber = null;
        // 搜索的结果就是展示的组织
        this.setTreeDataFromSearchResult(searchResult, searchResult.category_id);
        // 获取该组织下的人员
        this.getTableData();
      } else {
        // 搜索结果为人员，只展示所在的第一个组织
        this.setTreeDataFromSearchResult(searchResult.departments[0], searchResult.category_id);
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
        this.searchTreeList = [];
        return;
      }
      this.handleTabData.departName = department.full_name;
      this.$set(department, 'showBackground', true);
      this.$set(department, 'showOption', false);
      // 判断是不是本地目录下的组织
      this.treeDataList.forEach((catalog) => {
        if (catalog.id === catalogId) {
          department.isLocalDepartment = catalog.type === 'local';
          this.currentCategoryId = catalogId;
          this.currentCategoryType = catalog.type;
        }
      });
      this.searchTreeList = [department];
    },

    // 重命名，添加下级组织，设置表字段弹窗操作
    handleRename(item, type) {
      this.renameData = { item, type };
      this.handleTabData.title = this.$t('重命名');
      this.handleTabData.isShow = true;
    },
    addChildDepartment(item) {
      this.currentParam = { item };
      this.handleTabData.title = this.$t('添加下级组织');
      this.handleTabData.isShow = true;
    },
    setFieldList() {
      this.handleTabData.title = this.$t('设置列表字段');
      this.handleTabData.isShow = true;
    },
    actionConfirmFn() {
      if (this.handleTabData.isNameError) {
        return;
      }
      if (this.handleTabData.title === this.$t('设置列表字段')) {
        // 设置列表字段
        this.setTableFields = this.$refs.dialogContentRef.localSetTableFields;
        this.confirmSetFieldList();
      } else if (this.handleTabData.title === this.$t('重命名')) {
        // 重命名
        this.treeLoading = true;
        this.renameData.type === 'catalog' ? this.confirmRenameCatalog() : this.confirmRenameDepartment();
      } else if (this.handleTabData.title === this.$t('添加下级组织')) {
        // 添加下级组织
        this.confirmAddChildDepartment(this.currentParam.item);
      }
      this.handleTabData.isShow = false;
    },
    actionCancelFn() {
      this.handleTabData.isShow = false;
    },
    // 目录重命名
    async confirmRenameCatalog() {
      try {
        const res = await this.$store.dispatch('catalog/ajaxPutCatalog', {
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
        this.getTableData();
      } catch (e) {
        console.warn(e);
      } finally {
        this.treeLoading = false;
      }
    },
    // 设置列表字段
    async confirmSetFieldList() {
      try {
        const selected = this.setTableFields.filter(item => item.visible);
        const idList = selected.map((item) => {
          return item.id;
        });
        this.basicLoading = true;
        // idList.unshift('username', 'display_name', 'email', 'department_name')
        await this.$store.dispatch('setting/updateFieldsVisible', { idList });
        // 更新头部title + 用户信息列表
        await this.getTableTitle();
        await this.getTableData();
      } catch (e) {
        console.warn(e);
        this.basicLoading = false;
      }
    },
    // 添加下级组织
    async confirmAddChildDepartment(item) {
      try {
        this.treeLoading = true;
        const params = {
          name: this.$refs.dialogContentRef.childDepartment,
          parent: item.id,
          category_id: this.currentCategoryId,
        };
        const res = await this.$store.dispatch('organization/addDepartment', params);
        if (res.result === true) {
          this.messageSuccess(`${this.$t('成功添加下级组织')} ${params.name}`);
          if (item.showChildren) {
            this.isAddChild = true;
          }
          item.has_children = true;
          this.updateData(item);
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.treeLoading = false;
      }
    },

    // 查看当前用户的信息
    viewDetails(item) {
      this.currentProfile = item;
      this.detailsBarInfo.type = 'view';
      this.detailsBarInfo.title = this.currentProfile.display_name;
      this.detailsBarInfo.isShow = true;
      this.detailsBarInfo.basicLoading = false;
      this.detailsBarInfo.quickClose = true;
    },
    // 侧边栏 点击保存 更新列表 userMessage.userInforList
    async updateUserInfor() {
      if (this.treeSearchResult && this.treeSearchResult.groupType !== 'department') {
        // 搜索个人信息下保存 profile
        this.getProfileById();
        this.cancelHideBar();
      } else {
        this.getTableData();
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
      this.detailsBarInfo.quickClose = false;
    },
    handleCancelEdit() {
      if (this.detailsBarInfo.type === 'add') {
        this.detailsBarInfo.isShow = false;
      } else {
        this.detailsBarInfo.type = 'view';
        this.detailsBarInfo.quickClose = true;
      }
    },
    // 新增用户 调用接口，拿到数据传给子组件
    async addUserFn() {
      this.currentProfile = null;
      this.detailsBarInfo.title = this.$t('新增用户');
      this.detailsBarInfo.type = 'add';
      this.detailsBarInfo.isShow = true;
      this.detailsBarInfo.quickClose = false;
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
      const userSelected = this.userMessage.userInforList.filter(item => item.isCheck);
      if (userSelected.length === 1) {
        // 因为这里必有组织，所以子组件定会 emit selectedDepartments 因此不用对 selectedDepartments 初始化
        this.initialDepartments = userSelected[0].departments;
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
      const userSelected = this.userMessage.userInforList.filter(item => item.isCheck);
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
        this.getTableData();
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
        title: this.$t('删除后会保留用户的数据，以便需要时审查'),
        extCls: 'king-info long-title',
        confirmFn: async () => {
          if (this.clickSecond) {
            return;
          }
          this.clickSecond = true;
          this.basicLoading = true;
          try {
            const checkIds = [];
            this.userMessage.userInforList.forEach((element) => {
              if (element.isCheck) {
                checkIds.push({
                  id: element.id,
                });
              }
            });
            const res = await this.$store.dispatch('organization/deleteProfiles', checkIds);
            if (res.result === true) {
              this.$bkMessage({
                message: this.$t('删除成功'),
                theme: 'success',
              });
            }
            this.getTableData();
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
    deleteProfile() {
      this.$bkInfo({
        title: this.$t('删除后会保留用户的数据，以便需要时审查'),
        extCls: 'king-info long-title',
        confirmFn: () => {
          if (this.clickSecond) {
            return;
          }
          this.clickSecond = true;
          this.hideBar();
          this.$store.dispatch('organization/deleteProfiles', [{ id: this.currentProfile.id }]).then(async (res) => {
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
              this.getTableData();
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
    // 点击某个树节点
    handleClickTreeNode(item, isSearchProfile = false) {
      if (isSearchProfile) {
        this.searchTreeList.forEach((item) => {
          this.$set(item, 'showBackground', false);
        });
        item.showBackground = true;
        this.handleTabData.totalNumber = null;
        this.handleTabData.currentNumber = null;
        this.handleTabData.departName = item.full_name;
        return;
      }
      this.treeDataList.forEach((item) => {
        this.closeMenu(item);
      });
      if (this.tableSearchKey) {
        this.tableSearchKey = '';
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
    // 展开子级并添加上背景 改变右侧的title
    updateData(item) {
      this.$store.dispatch('organization/getDataById', {
        id: item.id,
      }).then((res) => {
        if (!res.result) {
          return;
        }
        if (this.isAddChild) {
          item.showChildren = true;
        } else {
          item.showChildren = !item.showChildren;
        }
        this.isAddChild = false;
        if (item.children === null) {
          this.$set(item, 'children', []);
        }
        item.children = res.data.children;
        item.children.forEach((element) => {
          this.filterTreeData(element, item, item.isLocalDepartment);
        });
      })
        .catch((e) => {
          console.warn(e);
        });
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
        const calculateDistance = this.calculate(event.target);
        const differ = document.querySelector('body').offsetHeight - calculateDistance.getOffsetTop;
        const next = event.target.nextElementSibling;
        next.style.left = `${calculateDistance.getOffsetLeft + 20}px`;
        next.style.top = `${calculateDistance.getOffsetTop + 30}px`;
        if (differ <= 198) {
          next.style.top = 'auto';
          next.style.bottom = `${differ}px`;
        }
      });
    },
    // 计算treeNode面板的位置
    calculate(currentDom) {
      const calculateDistance = {
        getOffsetLeft: 0,
        getOffsetTop: 0,
      };
      calculateDistance.getOffsetLeft = currentDom.offsetLeft;
      calculateDistance.getOffsetTop = currentDom.offsetTop - this.$refs.treePanel.scrollTop;
      let currentParent = currentDom.offsetParent;
      while (currentParent !== null) {
        calculateDistance.getOffsetLeft += currentParent.offsetLeft;
        calculateDistance.getOffsetTop += currentParent.offsetTop;
        currentParent = currentParent.offsetParent;
      }
      return calculateDistance;
    },
    // 点击空白处 ，关闭子菜单
    hiddenMenu() {
      this.treeDataList.forEach((item) => {
        this.closeTreeMenu(item);
      });
      this.searchTreeList.forEach((item) => {
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
    async switchNodeOrder(param) {
      try {
        this.treeLoading = true;
        const { item, index, type } = param;
        const orderList = item.type ? item.directParent : item.directParent.children;
        const targetIndex = type === 'up' ? index - 1 : index + 1;
        await this.$store.dispatch('organization/switchNodeOrder', {
          id: item.id,
          upId: orderList[targetIndex].id,
          nodeType: item.type ? 'categories' : 'departments',
        });
        // 本地更新
        this.$set(orderList, index, orderList[targetIndex]);
        this.$set(orderList, targetIndex, item);
      } catch (e) {
        console.warn(e);
      } finally {
        this.treeLoading = false;
      }
    },
    // 删除组织节点
    deleteDepartment(deleteItem, deleteIndex) {
      this.$bkInfo({
        title: this.$t('删除后会保留该组织的数据'),
        extCls: 'king-info long-title',
        confirmFn: this.syncConfirmDeleteDepartment.bind(this, deleteItem, deleteIndex),
      });
    },
    // 这里使用同步是为了点击确认后立即关闭info
    syncConfirmDeleteDepartment(deleteItem, deleteIndex) {
      this.confirmDeleteDepartment(deleteItem, deleteIndex);
    },
    async confirmDeleteDepartment(deleteItem, deleteIndex) {
      try {
        this.treeLoading = true;
        await this.$store.dispatch('organization/deleteDepartment', { id: deleteItem.id });
        this.messageSuccess(this.$t('删除成功'));
        if (this.treeSearchResult) {
          // 搜索里面删除组织后回到正常页面
          this.hasTreeDataModified = true;
          this.$refs.searchChild.closeSearch();
        } else {
          // 本地处理数据
          deleteItem.directParent.children.splice(deleteIndex, 1);
          if (!deleteItem.directParent.children.length) {
            deleteItem.directParent.has_children = false;
          }
          deleteItem.directParent.showBackground = true;
          this.currentParam.item = deleteItem.directParent;
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
        this.getTableData();
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

    // 控制页面布局宽度
    dragBegin(e) {
      this.isChangingWidth = true;
      this.currentTreeBoxWidth = this.treeBoxWidth;
      this.currentScreenX = e.screenX;
      window.addEventListener('mousemove', this.dragMoving, { passive: true });
      window.addEventListener('mouseup', this.dragStop, { passive: true });
    },
    dragMoving(e) {
      const newTreeBoxWidth = this.currentTreeBoxWidth + e.screenX - this.currentScreenX;
      if (newTreeBoxWidth <= this.treeBoxMinWidth) {
        this.treeBoxWidth = this.treeBoxMinWidth;
      } else if (newTreeBoxWidth >= this.treeBoxMaxWidth) {
        this.treeBoxWidth = this.treeBoxMaxWidth;
      } else {
        this.treeBoxWidth = newTreeBoxWidth;
      }
    },
    dragStop() {
      this.isChangingWidth = false;
      this.currentTreeBoxWidth = null;
      this.currentScreenX = null;
      window.removeEventListener('mousemove', this.dragMoving);
      window.removeEventListener('mouseup', this.dragStop);
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

<style>
    /*@import '../../scss/mixins/scroller.scss';*/

    /*.bk-table>thead>tr>th, .bk-table>thead>tr>td, .bk-table>tbody>tr>th, .bk-table>tbody>tr>td {*/

    /*    padding: 10px;*/

    /*    overflow: hidden;*/

    /*    text-overflow: ellipsis;*/

    /*    white-space: nowrap;*/

    /*}*/

    /*.bk-table>tbody>tr>td {*/

    /*    font-size: 14px;*/

    /*}*/

    /*.bk-sideslider-wrapper {*/

    /*    padding-bottom: 0 !important;*/

    /*    overflow-y: hidden;*/

    /*}*/

    /*.batch-content-wrapper .bk-tag-selector .bk-tag-input {*/

    /*    max-height: 240px;*/

    /*    overflow: hidden;*/

    /*    overflow-y: auto;*/

    /*}*/

    /*.batch-content-wrapper .bk-tag-selector .bk-tag-input::-webkit-scrollbar {*/

    /*    width: 4px;*/

    /*    background-color: lighten(#e6e9ea, 80%);*/

    /*}*/

    /*.batch-content-wrapper .bk-tag-selector .bk-tag-input::-webkit-scrollbar {*/

    /*    height: 5px;*/

    /*    border-radius: 2px;*/

    /*    background-color: #e6e9ea;*/

    /*}*/

    /*.bk-dropdown-menu .bk-button.bk-primary {*/

    /*    background-color: #fff;*/

    /*    color: #63656E;*/

    /*    border-color: #C4C6CC;*/

    /*    width: 106px;*/

    /*    padding: 0 13px;*/

    /*}*/

    /*.bk-dropdown-menu .bk-dropdown-trigger .bk-icon {*/

    /*    font-size: 12px;*/

    /*    width: 14px;*/

    /*    height: 14px;*/

    /*}*/
</style>
