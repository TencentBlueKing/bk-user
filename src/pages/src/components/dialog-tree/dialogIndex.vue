<template>
  <bk-dialog
    v-model="isShowDialog"
    width="700"
    :title="title"
    :mask-close="false"
    draggable
    header-position="left"
    ext-cls="iam-add-member-dialog"
    @after-leave="handleAfterLeave">
    <div class="add-member-content-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
      <div v-show="!isLoading">
        <div class="left">
          <div class="tab-wrapper">
            <section
              v-for="(item, index) in panels"
              :key="item.name"
              :class="['tab-item', { 'has-margin-left': index !== 0 }]"
              data-test-id="group_addGroupMemberDialog_tab_switch"
              @click.stop="handleTabChange(item)">
              {{ item.label }}
              <span class="active-line" v-if="tabActive === item.name"></span>
            </section>
          </div>
          <div
            class="member-tree-wrapper"
            v-bkloading="{ isLoading: treeLoading, opacity: 1 }"
            v-if="isOrganization">
            <bk-input
              v-model="keyword"
              :placeholder="$t('用户或组织')"
              maxlength="64"
              clearable
              :disabled="(isRatingManager || isAll) && !isAllFlag"
              :left-icon="'bk-icon icon-search'"
              ext-cls="iam-add-member-search-input-cls"
              @focus="handleSearchInput"
              @blur="handleSearchBlur"
              @keyup.enter.native="handleSearch"
              @keyup.up.native="handleKeyup"
              @keyup.down.native="handleKeydown">
            </bk-input>
            <template v-if="isShowMemberTree">
              <div class="tree">
                <infinite-tree
                  ref="memberTreeRef"
                  data-test-id="group_addGroupMemberDialog_tree_member"
                  :all-data="treeList"
                  style="height: 309px;"
                  :is-rating-manager="curIsRatingManager"
                  :key="infiniteTreeKey"
                  :is-disabled="isAll"
                  @async-load-nodes="handleRemoteLoadNode"
                  @expand-node="handleExpanded"
                  @on-select="handleOnSelected">
                </infinite-tree>
              </div>
            </template>
            <template v-if="isShowSearchResult">
              <div class="search-content">
                <template v-if="isHasSeachResult">
                  <dialog-infinite-list
                    ref="searchedResultsRef"
                    data-test-id="group_addGroupMemberDialog_list_searchResult"
                    :all-data="searchedResult"
                    :focus-index.sync="focusItemIndex"
                    :is-disabled="isAll"
                    style="height: 309px;"
                    @on-checked="handleSearchResultSelected">
                  </dialog-infinite-list>
                </template>
                <template v-if="isSeachResultTooMuch">
                  <div class="too-much-wrapper">
                    <Icon type="warning" class="much-tips-icon" />
                    <p class="text">{{ $t('搜索结果') }}</p>
                  </div>
                </template>
                <template v-if="isSeachResultEmpty">
                  <div class="search-empty-wrapper">
                    <iam-svg />
                    <p class="empty-tips">{{ $t('搜索无结果') }}</p>
                  </div>
                </template>
              </div>
            </template>
          </div>
          <div class="manual-wrapper" v-if="!isOrganization">
            <bk-input
              :placeholder="$t('请输入用户名，以回车/分号/空格分割')"
              data-test-id="group_addGroupMemberDialog_input_manualUser"
              type="textarea"
              :rows="14"
              v-model="manualValue"
              :disabled="isAll"
              @input="handleManualInput">
            </bk-input>
            <p class="manual-error-text" v-if="isManualInputOverLimit">{{ $t('手动输入提示1') }}</p>
            <p class="manual-error-text" v-if="manualInputError">{{ $t('手动输入提示2') }}</p>
            <bk-button
              theme="primary"
              style="width: 100%; margin-top: 35px;"
              :loading="manualAddLoading"
              :disabled="isManualDisabled || isAll"
              data-test-id="group_addGroupMemberDialog_btn_addManualUser"
              @click="handleAddManualUser">
              {{ $t('添加到已选列表') }}
            </bk-button>
          </div>
        </div>
        <div class="right">
          <div class="header">
            <div class="has-selected">
              {{ $t('已选择') }}
              <template v-if="isShowSelectedText">
                <span class="organization-count">{{ hasSelectedDepartments.length }}</span>
                {{ $t('个') }} {{ $t('组织') }}，
                <span class="user-count">{{ hasSelectedUsers.length }}</span>{{ $t('个') }} {{ $t('用户') }}
              </template>
              <template v-else>
                <span class="user-count">0</span>
              </template>
            </div>
            <bk-button theme="primary" text :disabled="!isShowSelectedText || isAll" @click="handleDeleteAll">
              {{ $t('清空') }}
            </bk-button>
          </div>
          <div class="content">
            <div class="organization-content" v-if="isDepartSelectedEmpty">
              <div class="organization-item" v-for="item in hasSelectedDepartments" :key="item.id">
                <Icon bk type="folder-shape" class="folder-icon" />
                <span class="organization-name" :title="item.fullName">{{ item.name }}</span>
                <span class="user-count" v-if="item.showCount">{{ '(' + item.count + `)` }}</span>
                <Icon
                  bk type="close-circle-shape" class="delete-depart-icon"
                  @click="handleDelete(item, 'organization')" />
              </div>
            </div>
            <div class="user-content" v-if="isUserSelectedEmpty">
              <div class="user-item" v-for="item in hasSelectedUsers" :key="item.id">
                <Icon bk type="user-shape" class="user-icon" />
                <span class="user-name" :title="item.name !== '' ? `${item.username}(${item.name})` : item.username">
                  {{ item.username }}
                  <template v-if="item.display_name !== ''">({{ item.display_name }})</template>
                </span>
                <Icon bk type="close-circle-shape" class="delete-icon" @click="handleDelete(item, 'user')" />
              </div>
            </div>
            <div class="selected-empty-wrapper" v-if="isSelectedEmpty">
              <iam-svg />
            </div>
          </div>
        </div>
      </div>
    </div>
    <div slot="footer">
      <div v-if="showLimit" class="limit-wrapper">
        <bk-checkbox
          :true-value="true"
          :false-value="false"
          v-model="isAll">
          {{ $t('全员') }}
        </bk-checkbox>
      </div>
      <bk-button
        theme="primary" :disabled="isDisabled && !isAll" @click="handleSave"
        data-test-id="group_btn_addMemberConfirm">{{ $t('确定') }}</bk-button>
      <bk-button style="margin-left: 10px;" :disabled="loading" @click="handleCancel">{{ $t('取消') }}</bk-button>
    </div>
  </bk-dialog>
</template>
<script>
import _ from 'lodash';
import InfiniteTree from './infiniteTree.vue';
import dialogInfiniteList from './inginiteList.vue';
import { guid } from '@/common/util';
import Icon from './iconIndex';

// 去除()以及之间的字符
const getUsername = (str) => {
  const array = str.split('');
  const index = array.findIndex(item => item === '(');
  if (index !== -1) {
    return array.splice(0, index).join('');
  }
  return str;
};

export default {
//   name: '',
  components: {
    InfiniteTree,
    dialogInfiniteList,
    Icon,
  },
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    users: {
      type: Array,
      default: () => [],
    },
    departments: {
      type: Array,
      default: () => [],
    },
    // 已选择的是否需要禁用
    disabled: {
      type: Boolean,
      default: false,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    name: {
      type: String,
      default: '',
    },
    id: {
      type: [String, Number],
      default: '',
    },
    title: {
      type: String,
      default: '',
    },
    isRatingManager: {
      type: Boolean,
      default: false,
    },
    showLimit: {
      type: Boolean,
      default: false,
    },
    allChecked: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isShowDialog: false,
      keyword: '',
      treeLoading: false,
      isBeingSearch: false,
      hasSelectedUsers: [],
      searchedUsers: [],
      searchedDepartment: [],
      hasSelectedDepartments: [],
      treeList: [],
      infiniteTreeKey: -1,
      searchedResult: [],
      // 搜索时 键盘上下键 hover 的 index
      focusItemIndex: -1,
      requestQueue: ['categories', 'memberList'],
      defaultDepartments: [],
      defaultUsers: [],
      isShowTooMuch: false,
      searchConditionValue: 'fuzzy',
      isSerachFocus: false,
      panels: [
        { name: 'organization', label: this.$t('组织架构') },
        { name: 'manual', label: this.$t('手动输入') },
      ],
      tabActive: 'organization',
      manualValue: '',
      manualAddLoading: false,
      manualInputError: false,
      manualValueBackup: [],
      isAll: false,
      isAllFlag: false,
    };
  },
  computed: {
    isLoading() {
      return this.requestQueue.length > 0;
    },
    isDisabled() {
      return this.isLoading || (this.hasSelectedUsers.length < 1 && this.hasSelectedDepartments.length < 1);
    },
    isHasSeachResult() {
      return (this.searchedDepartment.length > 0 || this.searchedUsers.length > 0) && !this.treeLoading;
    },
    isSeachResultTooMuch() {
      return !this.treeLoading && this.isShowTooMuch;
    },
    isSeachResultEmpty() {
      return this.searchedDepartment.length < 1
          && this.searchedUsers.length < 1 && !this.treeLoading && !this.isShowTooMuch;
    },
    isShowSelectedText() {
      return this.hasSelectedDepartments.length > 0 || this.hasSelectedUsers.length > 0;
    },
    isShowSearchResult() {
      return this.isBeingSearch && !this.treeLoading;
    },
    isShowMemberTree() {
      return !this.isBeingSearch && !this.treeLoading;
    },
    isDepartSelectedEmpty() {
      return this.hasSelectedDepartments.length > 0;
    },
    isUserSelectedEmpty() {
      return this.hasSelectedUsers.length > 0;
    },
    isSelectedEmpty() {
      return this.hasSelectedDepartments.length < 1 && this.hasSelectedUsers.length < 1;
    },
    isOrganization() {
      return this.tabActive === 'organization';
    },
    isManualInputOverLimit() {
      if (this.manualValue === '') {
        return false;
      }
      const MAX_LEN = 100;
      return this.manualValue.split(';').filter(item => item !== '').length > MAX_LEN;
    },
    isManualDisabled() {
      return this.manualValue === '' || this.isManualInputOverLimit;
    },
    manualValueActual() {
      return this.manualValue.replace(/\n|\s+/g, ';');
    },
    curIsRatingManager() {
      if (this.isAllFlag) {
        return false;
      }
      return this.isRatingManager;
    },
  },
  watch: {
    show: {
      handler(value) {
        this.isShowDialog = !!value;
        if (this.isShowDialog) {
          this.infiniteTreeKey = new Date().getTime();
          this.hasSelectedUsers.splice(0, this.hasSelectedUsers.length, ...this.users);
          this.hasSelectedDepartments.splice(0, this.hasSelectedDepartments.length, ...this.departments);
          this.requestQueue = ['categories'];
          if (this.isRatingManager) {
            this.fetchRoleSubjectScope(false, true);
          } else {
            this.fetchCategories(false, true);
          }
        }
      },
      immediate: true,
    },
    keyword(newVal, oldVal) {
      this.focusItemIndex = -1;
      if (!newVal && oldVal) {
        if (this.isBeingSearch) {
          this.infiniteTreeKey = new Date().getTime();
          if (this.isAllFlag) {
            this.fetchCategories(true, false);
          } else {
            if (this.isRatingManager) {
              this.fetchRoleSubjectScope(true, false);
            } else {
              this.fetchCategories(true, false);
            }
          }
          this.isBeingSearch = false;
        }
      }
    },
    allChecked: {
      handler(value) {
        this.isAll = !!value;
      },
      immediate: true,
    },
  },
  created() {
    if (this.$route.name === 'gradingAdminCreate') {
      this.handleSave();
    }
  },
  methods: {
    handleSearchInput() {
      this.isSerachFocus = true;
    },
    handleSearchBlur() {
      this.isSerachFocus = false;
    },
    handleTabChange({ name }) {
      this.tabActive = name;
      // 已选择的需要从输入框中去掉
      if (this.tabActive === 'manual'
        && this.hasSelectedUsers.length > 0
        && this.manualValue !== '') {
        const templateArr = [];
        const usernameList = this.hasSelectedUsers.map(item => item.username);
        const manualValueBackup = this.manualValueActual.split(';').filter(item => item !== '');
        manualValueBackup.forEach((item) => {
          const name = getUsername(item);
          if (!usernameList.includes(name)) {
            templateArr.push(item);
          }
        });
        this.manualValue = templateArr.join(';');
      }
    },
    handleManualInput() {
      this.manualInputError = false;
    },
    async handleAddManualUser() {
      this.manualAddLoading = true;
      try {
        // 手动输入查询
        const url = this.isRatingManager ? 'role/queryRolesUsers' : 'organization/verifyManualUser';
        const res = await this.$store.dispatch(url, {
          usernames: this.manualValueActual.split(';').filter(item => item !== '')
            .map((item) => {
              return getUsername(item);
            }),
        });
        const temps = res.data
          .filter(item => !this.hasSelectedUsers.map(subItem => subItem.username).includes(item.username));
        this.hasSelectedUsers.push(...temps);
        if (res.data.length > 0) {
          const usernameList = res.data.map(item => item.username);
          const templateArr = [];
          this.manualValueBackup = this.manualValueActual.split(';').filter(item => item !== '');
          this.manualValueBackup.forEach((item) => {
            const name = getUsername(item);
            if (!usernameList.includes(name)) {
              templateArr.push(item);
            }
          });
          this.manualValue = templateArr.join(';');
          if (this.manualValue !== '') {
            this.manualInputError = true;
          }
        } else {
          this.manualInputError = true;
        }
      } catch (e) {
        console.error(e);
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'error',
          message: this.$t('用户名输入格式错误'),
        });
      } finally {
        this.manualAddLoading = false;
      }
    },
    handleKeyup() {
      // 当搜索的结果数据小于10条时才支持键盘上下键选中
      if (!this.isBeingSearch || this.searchedResult.length > 10) {
        return;
      }
      const len = this.$refs.searchedResultsRef.renderData.length;
      this.focusItemIndex -= 1;
      this.focusItemIndex = this.focusItemIndex < 0 ? -1 : this.focusItemIndex;
      if (this.focusItemIndex === -1) {
        this.focusItemIndex = len - 1;
      }
    },
    handleKeydown() {
      // 当搜索的结果数据小于10条时才支持键盘上下键选中
      if (!this.isBeingSearch || this.searchedResult.length > 10) {
        return;
      }
      const len = this.$refs.searchedResultsRef.renderData.length;
      this.focusItemIndex += 1;
      this.focusItemIndex = this.focusItemIndex > len - 1
        ? len
        : this.focusItemIndex;
      if (this.focusItemIndex === len) {
        this.focusItemIndex = 0;
      }
    },
    async fetchMemberList() {
      try {
        const params = {
          id: this.id,
          limit: 1000,
          offset: 0,
        };
        const res = await this.$store.dispatch('userGroup/getUserGroupMemberList', params);

        this.defaultDepartments = res.data.results.filter(item => item.type === 'department');
        this.defaultUsers = res.data.results.filter(item => item.type === 'user');
        if (this.isRatingManager) {
          this.fetchRoleSubjectScope(false, true);
        } else {
          this.fetchCategories(false, true);
        }
      } catch (e) {
        console.error(e);
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'error',
          message: e.message || e.data.msg || e.statusText,
          ellipsisLine: 2,
          ellipsisCopy: true,
        });
      } finally {
        this.requestQueue.shift();
      }
    },
    async fetchRoleSubjectScope(isTreeLoading = false, isDialogLoading = false) {
      this.treeLoading = isTreeLoading;
      try {
        const res = await this.$store.dispatch('role/getRoleSubjectScope');

        const departments = [...res.data];
        this.isAllFlag = departments.some(item => item.type === '*' && item.id === '*');
        if (this.isAllFlag) {
          this.fetchCategories(false, true);
          return;
        }
        departments.forEach((child) => {
          child.visiable = true;
          child.level = 0;
          child.loading = false;
          child.showRadio = true;
          child.selected = false;
          child.expanded = false;
          child.disabled = false;
          child.type = child.type === 'user' ? 'user' : 'depart';
          // child.count = child.recursive_member_count
          child.count = child.member_count;
          child.showCount = child.type !== 'user';
          child.async = child.child_count > 0 || child.member_count > 0;
          child.isNewMember = false;
          child.parentNodeId = '';
          if (child.type === 'user') {
            child.username = child.id;
          }

          if (this.hasSelectedDepartments.length > 0) {
            child.is_selected = this.hasSelectedDepartments.map(item => item.id).includes(child.id);
          } else {
            child.is_selected = false;
          }
          if (this.hasSelectedUsers.length > 0) {
            child.is_selected = this.hasSelectedUsers.map(item => item.id).includes(child.id);
          } else {
            child.is_selected = false;
          }
          if (this.defaultDepartments.length > 0
              && this.defaultDepartments.map(item => item.id).includes(child.id.toString())
          ) {
            child.is_selected = true;
            child.disabled = true;
          }

          if (this.defaultUsers.length && this.defaultUsers.map(item => item.id).includes(child.id)) {
            child.is_selected = true;
            child.disabled = true;
          }
        });
        this.treeList = _.cloneDeep(departments);
      } catch (e) {
        console.error(e);
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'error',
          message: e.message || e.data.msg || e.statusText,
          ellipsisLine: 2,
          ellipsisCopy: true,
        });
      } finally {
        this.treeLoading = false;
        if (isDialogLoading) {
          this.requestQueue.shift();
        }
      }
    },
    async fetchCategories(isTreeLoading = false, isDialogLoading = false) {
      this.treeLoading = isTreeLoading;
      try {
        const res = await this.$store.dispatch('organization/getOrganizationTree');
        const categories = [...res.data];
        categories.forEach((item) => {
          item.visiable = true;
          item.level = 0;
          item.showRadio = false;
          item.selected = false;
          item.expanded = false;
          item.count = 0;
          item.disabled = !item.departments || item.departments.length < 1;
          item.type = 'depart';
          item.showCount = false;
          item.async = item.departments && item.departments.length > 0;
          item.isNewMember = false;
          item.loading = false;
          item.is_selected = false;
          item.parentNodeId = '';
          item.id = `${item.id}&${item.level}`;
          item.name = item.display_name;
          if (item.departments && item.departments.length > 0) {
            item.departments.forEach((child) => {
              child.visiable = false;
              child.level = 1;
              child.loading = false;
              child.showRadio = true;
              child.selected = false;
              child.expanded = false;
              child.disabled = false;
              child.type = 'depart';
              child.count = child.recursive_member_count;
              child.showCount = true;
              child.async = child.has_children;
              child.isNewMember = false;
              child.parentNodeId = item.id;
              if (this.hasSelectedDepartments.length > 0) {
                child.is_selected = this.hasSelectedDepartments.map(item => item.id).includes(child.id);
              } else {
                child.is_selected = false;
              }
              if (this.defaultDepartments.length > 0
                  && this.defaultDepartments.map(item => item.id).includes(child.id.toString())
              ) {
                child.is_selected = true;
                child.disabled = true;
              }
            });
            item.children = _.cloneDeep(item.departments);
          }
        });
        this.treeList = _.cloneDeep(categories);
      } catch (e) {
        console.error(e);
        this.bkMessageInstance = this.$bkMessage({
          theme: 'error',
          message: e.message || e.data.msg || e.statusText,
        });
      } finally {
        this.treeLoading = false;
        if (isDialogLoading) {
          this.requestQueue.shift();
        }
      }
    },
    async handleOnSelected(newVal, node) {
      if (newVal) {
        if (node.type === 'user') {
          this.hasSelectedUsers.push(node);
        } else {
          this.hasSelectedDepartments.push(node);
        }
      } else {
        if (node.type === 'user') {
          this.hasSelectedUsers = [
            ...this.hasSelectedUsers.filter(item => item.username !== node.username),
          ];
        } else {
          this.hasSelectedDepartments = [
            ...this.hasSelectedDepartments.filter(item => item.id !== node.id),
          ];
        }
      }
    },
    handleDeleteAll() {
      if (this.searchedUsers.length) {
        this.searchedUsers.forEach((search) => {
          search.is_selected = false;
        });
      }
      if (this.searchedDepartment.length) {
        this.searchedDepartment.forEach((organ) => {
          organ.is_selected = false;
        });
      }
      this.hasSelectedUsers.splice(0, this.hasSelectedUsers.length, ...[]);
      this.hasSelectedDepartments.splice(0, this.hasSelectedDepartments.length, ...[]);
      this.$refs.memberTreeRef && this.$refs.memberTreeRef.clearAllIsSelectedStatus();
    },
    handleConditionSelcted(payload) {
      this.$refs.dropdown.hide();
      this.searchConditionValue = payload.id;
      this.handleSearch();
    },

    async handleSearch() {
      if (this.keyword === '') {
        return;
      }

      // if (this.searchedResult.length === 1) {
      //   if (this.searchedDepartment.length === 1) {
      //     this.hasSelectedDepartments.push(this.searchedDepartment[0]);
      //   } else {
      //     this.hasSelectedUsers.push(this.searchedUsers[0]);
      //   }
      //   this.keyword = '';
      //   this.searchedResult.splice(0, this.searchedResult.length, ...[]);
      //   this.searchedDepartment.splice(0, this.searchedDepartment.length, ...[]);
      //   this.searchedUsers.splice(0, this.searchedUsers.length, ...[]);
      //   return;
      // }

      if (this.focusItemIndex !== -1) {
        this.$refs.searchedResultsRef.setCheckStatusByIndex();
        return;
      }

      this.treeList.splice(0, this.treeList.length, ...[]);
      this.isBeingSearch = true;
      this.treeLoading = true;

      this.searchedResult.splice(0, this.searchedResult.length, ...[]);
      this.searchedDepartment.splice(0, this.searchedDepartment.length, ...[]);
      this.searchedUsers.splice(0, this.searchedUsers.length, ...[]);

      const defaultDepartIds = [...this.defaultDepartments.map(item => item.id)];
      const defaultUserIds = [...this.defaultUsers.map(item => item.id)];
      const departIds = [...this.hasSelectedDepartments.map(item => item.id)];
      const userIds = [...this.hasSelectedUsers.map(item => item.username)];
      const params = {
        keyword: this.keyword,
        is_exact: this.searchConditionValue === 'exact',
      };
      try {
        const res = await this.$store.dispatch('organization/getSeachOrganizations', params);
        if (res.data.is_too_much) {
          this.isShowTooMuch = true;
          return;
        }
        this.isShowTooMuch = false;
        if (res.data.departments.length > 0) {
          res.data.departments.forEach((depart) => {
            depart.showRadio = true;
            depart.type = 'depart';
            if (departIds.length && departIds.includes(depart.id)) {
              this.$set(depart, 'is_selected', true);
            } else {
              this.$set(depart, 'is_selected', false);
            }
            if (defaultDepartIds.length && defaultDepartIds.includes(depart.id.toString())) {
              this.$set(depart, 'is_selected', true);
              this.$set(depart, 'disabled', true);
            }
            depart.count = depart.recursive_member_count;
            depart.showCount = true;
          });
          this.searchedDepartment.splice(0, this.searchedDepartment.length, ...res.data.departments);
        }
        if (res.data.users.length > 0) {
          res.data.users.forEach((user) => {
            user.id = guid();
            user.showRadio = true;
            user.type = 'user';
            if (userIds.length && userIds.includes(user.username)) {
              this.$set(user, 'is_selected', true);
            } else {
              this.$set(user, 'is_selected', false);
            }
            if (defaultUserIds.length && defaultUserIds.includes(user.username)) {
              this.$set(user, 'is_selected', true);
              this.$set(user, 'disabled', true);
            }
          });
          this.searchedUsers.splice(0, this.searchedUsers.length, ...res.data.users);
        }
        this.searchedResult.splice(
          0,
          this.searchedResult.length,
          ...this.searchedDepartment.concat(this.searchedUsers),
        );
      } catch (e) {
        console.error(e);
        this.bkMessageInstance = this.$bkMessage({
          theme: 'error',
          message: e.message || e.data.msg || e.statusText,
        });
      } finally {
        this.treeLoading = false;
      }
    },
    handleExpanded(payload) {
      if (this.isRatingManager && !this.isAllFlag) {
        return;
      }
      const flag = this.treeList.some(item => item.parentNodeId === payload.id);
      if (payload.level === 0 && !flag) {
        const curIndex = this.treeList.findIndex(item => item.id === payload.id);
        if (curIndex !== -1) {
          const children = _.cloneDeep(this.treeList[curIndex].children);
          if (children && children.length > 0) {
            children.forEach((item) => {
              item.visiable = true;
            });
            this.treeList.splice(curIndex + 1, 0, ...children);
          }
        }
      }
    },
    async handleRemoteLoadNode(payload) {
      if (payload.level === 0 && !this.isRatingManager) {
        return;
      }
      payload.loading = true;
      try {
        // 点击tree子节点调用
        const params = {
          id: payload.id,
          pageSize: 100,
          page: 1,
          keyword: '',
          recursive: true,
        };
        const res = await this.$store.dispatch('organization/getDataById', { id: payload.id });
        const membersList = await this.$store.dispatch('organization/getProfiles', params);
        // const { child_count, children, id, member_count, members, name, recursive_member_count } = res.data;
        const { children } = res.data;
        const members = membersList.data.data;
        if (children.length < 1 && members.length < 1) {
          payload.expanded = false;
          return;
        }

        const curIndex = this.treeList.findIndex(item => item.id === payload.id);

        if (curIndex === -1) {
          return;
        }
        const treeList = [];
        treeList.splice(0, 0, ...this.treeList);
        if (children.length > 0) {
          children.forEach((child) => {
            child.visiable = payload.expanded;
            child.level = payload.level + 1;
            child.loading = false;
            child.showRadio = true;
            child.selected = false;
            child.expanded = false;
            child.disabled = this.disabled;
            child.type = 'depart';
            child.count = child.recursive_member_count;
            child.showCount = true;
            child.async = payload.has_children;
            child.isNewMember = false;
            child.parentNodeId = payload.id;

            if (this.hasSelectedDepartments.length > 0) {
              child.is_selected = this.hasSelectedDepartments.map(item => item.id).includes(child.id);
            } else {
              child.is_selected = false;
            }

            if (this.defaultDepartments.length > 0
                && this.defaultDepartments.map(item => item.id).includes(child.id.toString())
            ) {
              child.is_selected = true;
              child.disabled = true;
            }
          });
        }

        if (members.length > 0) {
          members.forEach((child) => {
            child.visiable = payload.expanded;
            child.level = payload.level + 1;
            child.loading = false;
            child.showRadio = true;
            child.selected = false;
            child.expanded = false;
            child.disabled = this.disabled;
            child.type = 'user';
            child.count = 0;
            child.showCount = false;
            child.async = false;
            child.isNewMember = false;
            child.parentNodeId = payload.id;

            // parentNodeId + username 组合成id
            child.id = `${child.parentNodeId}${child.username}`;

            if (this.hasSelectedUsers.length > 0) {
              child.is_selected = this.hasSelectedUsers.map(item => item.id).includes(child.id);
            } else {
              child.is_selected = false;
            }
            const existSelectedNode = this.treeList.find(item => item.is_selected && item.username === child.username);
            if (existSelectedNode) {
              child.is_selected = true;
              child.disabled = true;
            }

            if (this.defaultUsers.length && this.defaultUsers.map(item => item.id).includes(child.username)) {
              child.is_selected = true;
              child.disabled = true;
            }
          });
        }

        const loadChildren = children.concat([...members]);

        treeList.splice(curIndex + 1, 0, ...loadChildren);

        this.treeList.splice(0, this.treeList.length, ...treeList);

        if (!payload.children) {
          payload.children = [];
        }

        payload.children.splice(0, payload.children.length, ...loadChildren);
      } catch (e) {
        console.error(e);
        this.bkMessageInstance = this.$bkMessage({
          theme: 'error',
          message: e.message || e.data.msg || e.statusText,
        });
      } finally {
        setTimeout(() => {
          payload.loading = false;
        }, 300);
      }
    },
    handleDelete(item, type) {
      if (this.isAll) {
        return;
      }
      if (this.isBeingSearch) {
        if (this.searchedUsers.length) {
          this.searchedUsers.forEach((search) => {
            if (search.username === item.username) {
              search.is_selected = false;
            }
          });
        }
        if (this.searchedDepartment.length) {
          this.searchedDepartment.forEach((organ) => {
            if (organ.id === item.id) {
              organ.is_selected = false;
            }
          });
        }
      } else {
        this.tabActive === 'organization' && this.$refs.memberTreeRef.setSingleSelectedStatus(item.id, false);
      }
      if (type === 'user') {
        this.hasSelectedUsers = [...this.hasSelectedUsers.filter(user => user.username !== item.username)];
      } else {
        // eslint-disable-next-line max-len
        this.hasSelectedDepartments = [...this.hasSelectedDepartments.filter(organ => organ.id !== item.id)];
      }
    },
    async handleSearchResultSelected(newVal, oldVal, localVal, item) {
      if (item.type === 'user') {
        this.handleSearchUserSelected(newVal, item);
      } else {
        if (newVal) {
          this.hasSelectedDepartments.push(item);
        } else {
          this.hasSelectedDepartments = this.hasSelectedDepartments.filter(organ => organ.id !== item.id);
        }
      }
    },
    handleSearchUserSelected(newVal, item) {
      if (newVal) {
        this.hasSelectedUsers.push(item);
      } else {
        this.hasSelectedUsers = this.hasSelectedUsers.filter(user => user.username !== item.username);
      }
    },
    handleAfterLeave() {
      this.keyword = '';
      this.treeLoading = false;
      this.isBeingSearch = false;
      this.hasSelectedUsers.splice(0, this.hasSelectedUsers.length, ...[]);
      this.hasSelectedDepartments.splice(0, this.hasSelectedDepartments.length, ...[]);
      this.searchedDepartment.splice(0, this.searchedDepartment.length, ...[]);
      this.searchedUsers.splice(0, this.searchedUsers.length, ...[]);
      this.searchedResult.splice(0, this.searchedResult.length, ...[]);
      this.treeList.splice(0, this.treeList.length, ...[]);
      this.requestQueue = ['categories', 'memberList'];
      this.focusItemIndex = -1;
      this.$refs.memberTreeRef && this.$refs.memberTreeRef.clearAllIsSelectedStatus();
      this.searchConditionValue = 'fuzzy';
      this.tabActive = 'organization';
      this.manualValue = '';
      this.manualAddLoading = false;
      this.manualInputError = false;
      this.manualValueBackup = [];
      this.$emit('update:show', false);
      this.$emit('on-after-leave');
    },
    handleCancel() {
      this.$emit('on-cancel');
    },
    handleSave() {
      const params = {
        users: this.hasSelectedUsers,
        departments: this.hasSelectedDepartments,
        // expiredAt: this.expiredAt,
        isAll: this.isAll,
      };
      this.$emit('on-sumbit', params);
    },
  },
};
</script>
<style lang='postcss'>
.iam-add-member-dialog {
  .bk-dialog-body {
    padding: 3px 24px 0px 24px;
  }
  .limit-wrapper {
    float: left;
    margin-top: 5px;
  }
  .add-member-content-wrapper {
    height: 383px;
    .left {
      display: inline-block;
      width: 320px;
      height: 383px;
      border-right: 1px solid #dcdee5;
      float: left;
      .tab-wrapper {
        position: relative;
        top: -15px;
        display: flex;
        justify-content: flex-start;
        height: 32px;
        line-height: 32px;
        border-bottom: 1px solid #d8d8d8;
        .tab-item {
          position: relative;
          cursor: pointer;
          &.has-margin-left {
            margin-left: 20px;
          }
          .active-line {
            position: absolute;
            bottom: -1px;
            left: 0;
            width: 100%;
            height: 2px;
            background: #3a84ff;
          }
        }
      }
      .member-tree-wrapper {
        min-height: 309px;
        .iam-add-member-search-input-cls {
          padding-right: 10px;
        }
      }
      .tree {
        margin-right: 10px;
        max-height: 309px;
        overflow: auto;
        &::-webkit-scrollbar {
          width: 4px;
          background-color: lighten(transparent, 80%);
        }
        &::-webkit-scrollbar-thumb {
          height: 5px;
          border-radius: 2px;
          background-color: #e6e9ea;
        }
      }
      .search-input {
        margin-bottom: 5px;
        width: 310px;
        height: 32px;
        line-height: normal;
        color: #63656e;
        background-color: #fff;
        border-radius: 2px;
        font-size: 12px;
        border: 1px solid #c4c6cc;
        padding: 0 10px;
        text-align: left;
        vertical-align: middle;
        outline: none;
        resize: none;
        transition: border .2s linear;
        &.disabled {
          background-color: #fafbfd;
        }
        &.active {
          border-color: #3a84ff;
        }
        .search-config-icon {
          font-size: 14px;
        }
        .bk-dropdown-menu {
          position: relative;
          top: 7px;
          &:hover {
            .search-icon {
              color: #3a84ff;
            }
          }
          .search-icon {
            font-size: 16px;
          }
        }
        .bk-dropdown-trigger {
          cursor: pointer;
        }
        .bk-dropdown-list {
          li {
            a {
              font-size: 14px;
              &.active {
                background-color: #eaf3ff;
                color: #3a84ff;
              }
            }
          }
        }
      }
      .search-content {
        .too-much-wrapper {
          position: absolute;
          left: 50%;
          top: 50%;
          text-align: center;
          transform: translate(-50%, -50%);
          .much-tips-icon {
            font-size: 21px;
            color: #63656e;
          }
          .text {
            margin-top: 6px;
            font-size: 12px;
            color: #dcdee5;
          }
        }
        .search-empty-wrapper {
          position: absolute;
          left: 50%;
          top: 50%;
          text-align: center;
          transform: translate(-50%, -50%);
          img {
            width: 120px;
          }
          .empty-tips {
            position: relative;
            top: -20px;
            font-size: 12px;
            color: #dcdee5;
          }
        }
      }
      .manual-wrapper {
        padding-right: 10px;
        .manual-error-text {
          position: absolute;
          width: 320px;
          line-height: 1;
          margin-top: 4px;
          font-size: 12px;
          color: #ff4d4d;
        }
      }
    }
    .right {
      display: inline-block;
      padding-left: 10px;
      width: 327px;
      height: 383px;
      .header {
        display: flex;
        justify-content: space-between;
        position: relative;
        top: 6px;
        .organization-count {
          margin-right: 3px;
          color: #2dcb56;
        }
        .user-count {
          margin-right: 3px;
          color: #2dcb56
        }
      }
      .content {
        position: relative;
        margin-top: 15px;
        padding-left: 10px;
        height: 345px;
        overflow: auto;
        &::-webkit-scrollbar {
          width: 4px;
          background-color: lighten(transparent, 80%);
        }
        &::-webkit-scrollbar-thumb {
          height: 5px;
          border-radius: 2px;
          background-color: #e6e9ea;
        }
        .organization-content {
          .organization-item {
            padding: 5px 0;
            .organization-name {
              display: inline-block;
              max-width: 200px;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
              vertical-align: top;
            }
            .delete-depart-icon {
              display: block;
              margin: 4px 6px 0 0;
              color: #c4c6cc;
              cursor: pointer;
              float: right;
              &:hover {
                color: #3a84ff;
              }
            }
            .user-count {
              color: #c4c6cc;
            }
          }
          .folder-icon {
            font-size: 17px;
            color: #a3c5fd;
          }
        }
        .user-content {
          .user-item {
            padding: 5px 0;
            .user-name {
              display: inline-block;
              max-width: 200px;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
              vertical-align: top;
            }
            .delete-icon {
              display: block;
              margin: 4px 6px 0 0;
              color: #c4c6cc;
              cursor: pointer;
              float: right;
              &:hover {
                color: #3a84ff;
              }
            }
          }
          .user-icon {
            font-size: 16px;
            color: #a3c5fd;
          }
        }
        .selected-empty-wrapper {
          position: absolute;
          left: 50%;
          top: 50%;
          transform: translate(-50%, -50%);
          img {
            width: 120px;
          }
        }
      }
    }
  }
}
</style>
