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
  <div class="member-infor-wrapper" v-bkloading="{ isLoading: detailsBarInfo.basicLoading }">
    <!-- view -->
    <UserMaterial
      v-if="detailsBarInfo.type === 'view'"
      :current-profile="currentProfile"
      :current-category-id="currentCategoryId"
      :current-category-type="currentCategoryType"
      :fields-list="fieldsList"
      @editProfile="editProfile"
      @deleteProfile="$emit('deleteProfile')"
      @getTableData="$emit('getTableData')"
      @showBarLoading="$emit('showBarLoading')"
      @closeBarLoading="$emit('closeBarLoading')" />
    <!-- add/edit -->
    <div class="add-user-infor" v-else>
      <div class="user-infor-wrapper" ref="userInforWrapper">
        <div class="information-box" data-test-id="superiorData">
          <h4 class="infor-title">{{$t('用户信息')}}</h4>
          <div class="fill-infor-wrapper">
            <InputComponents :edit-status="detailsBarInfo.type === 'edit'" :profile-info-list="profileInfoList" />
            <UploadAvatar @getBase64="getBase64"
                          :img-src="currentProfile === null ? $store.state.localAvatar : currentProfile.logo" />
          </div>
          <h4 class="infor-title" style="margin-top: 37px">{{$t('用户设置')}}</h4>
          <ul class="mark-width">
            <li class="infor-list">
              <p class="desc">{{$t('直接上级')}}</p>
              <div class="input-text leader-input" ref="leaderInput">
                <bk-select
                  v-if="showselectData || detailsBarInfo.type === 'add'"
                  searchable
                  multiple
                  display-tag
                  v-model="leaderIdList"
                  :remote-method="selectData"
                  :list="rtxList"
                  ext-popover-cls="scrollview"
                  @toggle="handleBranchToggle"
                  :scroll-height="188">
                  <bk-option v-for="option in rtxList"
                             :key="option.id"
                             :id="option.id"
                             :name="option.username">
                  </bk-option>
                </bk-select>
                <bk-select
                  v-else
                  searchable
                  multiple
                  display-tag
                  v-model="leaderIdList"
                  @toggle="handleBranchToggle">
                  <bk-option v-for="option in currentProfile.leader"
                             :key="option.id"
                             :id="option.id"
                             :name="option.username">
                  </bk-option>
                </bk-select>
                <div class="input-loading" @click.stop v-show="showLeaderLoading">
                  <img src="../../../images/svg/loading.svg" alt="">
                </div>
              </div>
            </li>
            <li class="infor-list">
              <p class="desc">{{$t('所在组织')}}<span class="star">*</span></p>
              <div class="input-text" @click="showSetDepartments">
                <span class="select-text">
                  {{formatDepartments(initialDepartments)}}
                </span>
              </div>
            </li>
            <li class="infor-list">
              <p class="desc">{{$t('密码有效期')}}<span class="star">*</span></p>
              <div class="input-text">
                <bk-select v-model="passwordValidDays" :clearable="false">
                  <bk-option v-for="option in passwordValidDaysList"
                             :key="option.days"
                             :id="option.days"
                             :name="option.text">
                  </bk-option>
                </bk-select>
              </div>
            </li>
          </ul>
        </div>
      </div>
      <div class="action-btn">
        <bk-button theme="primary" class="btn" @click="handleSubmit">{{$t('保存')}}</bk-button>
        <bk-button theme="default" class="btn" @click="$emit('handleCancelEdit')">{{$t('取消')}}</bk-button>
      </div>
    </div>
    <!-- 所在组织的弹窗 -->
    <div class="operation-wrapper">
      <bk-dialog
        width="721"
        class="king-dialog department-dialog"
        :auto-close="false"
        header-position="left"
        v-model="isShowSetDepartments"
        :title="$t('设置所在组织')"
        @confirm="handleConfirmSet"
        @cancel="handleCancelSet">
        <div class="select-department-wrapper clearfix">
          <SetDepartment
            v-if="isShowSetDepartments"
            :current-category-id="currentCategoryId"
            :initial-departments="initialDepartments"
            @getDepartments="getDepartments" />
        </div>
      </bk-dialog>
    </div>
  </div>
</template>

<script>
import UserMaterial from './UserMaterial';
import InputComponents from './InputComponents';
import UploadAvatar from './UploadAvatar';

import SetDepartment from '@/components/organization/SetDepartment';

export default {
  components: {
    SetDepartment,
    InputComponents,
    UploadAvatar,
    UserMaterial,
  },
  props: {
    // 侧边栏信息
    detailsBarInfo: {
      type: Object,
      required: true,
    },
    // 当前用户的信息
    currentProfile: {
      type: Object,
      default: null,
    },
    // 当前用户目录 ID
    currentCategoryId: {
      type: Number,
      default: null,
    },
    // 当前用户所属目录类型 只有 local 可以编辑信息
    currentCategoryType: {
      type: String,
      default: '',
    },
    // 字段信息
    fieldsList: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      // 新增或编辑时赋值
      profileInfoList: [],
      // 修改头像后从后台获取的 id，保存时上传
      AvatarBase64: '',
      // 直接上级，[1, 2, 3]
      leaderIdList: [],
      showLeaderLoading: false,
      isShowSetDepartments: false,
      initialDepartments: [],
      // 选择的组织
      getSelectedDepartments: [],
      rtxListUpdated: false,
      // 密码有效期
      passwordValidDays: null,
      paginationConfig: {
        current: 1,
        count: 1,
        limit: 10,
      },
      searchValue: '',
      // 人员选择器的数据，初始化调用接口
      rtxList: [],
      copyList: [],
      timer: null,
      showselectData: false,
    };
  },
  computed: {
    passwordValidDaysList() {
      return this.$store.state.passwordValidDaysList;
    },
  },
  created() {
    // 新增用户
    if (this.detailsBarInfo.type === 'add') {
      const fieldsList = JSON.parse(JSON.stringify(this.fieldsList));
      this.profileInfoList = fieldsList.filter((fieldInfo) => {
        if (fieldInfo.key === 'department_name' || fieldInfo.key === 'leader') {
          return false;
        }
        fieldInfo.holder = this.$t('请输入');
        fieldInfo.value = fieldInfo.default;
        fieldInfo.isError = false;
        return true;
      });
      this.initialDepartments = this.detailsBarInfo.departments;
      this.getSelectedDepartments = this.initialDepartments;
      this.$store.dispatch('catalog/ajaxGetPassport', { id: this.currentCategoryId }).then((res) => {
        this.passwordValidDays = res.data.find(item => item.key === 'password_valid_days').value;
      });
    }
    // 进入页面获取数据
    this.searchValue = '';
    this.paginationConfig.current = 1;
    this.initRtxList(this.searchValue, this.paginationConfig.current);
  },
  methods: {
    // 上级组织搜索
    selectData(val) {
      this.searchValue = val;
      this.paginationConfig.current = 1;
      this.copyList = [];
      clearTimeout(this.timer);
      this.timer = setTimeout(async () => {
        await this.initRtxList(val, this.paginationConfig.current);
      }, 500);
    },
    // 点击select
    async handleBranchToggle(value) {
      this.showselectData = value;
      if (value) {
        this.$nextTick(() => {
          this.paginationConfig.current = 1;
          this.copyList = [];
          this.initRtxList(this.searchValue, this.paginationConfig.current);
          const selectorList = document.querySelector('.scrollview').querySelector('.bk-options');
          if (selectorList) {
            selectorList.scrollTop = 0;
            selectorList.addEventListener('scroll', this.scrollHandler);
          }
        });
      }
    },
    // 滚动回调
    scrollHandler() {
      const scrollContainer = document.querySelector('.scrollview').querySelector('.bk-options');
      if (scrollContainer.scrollTop === 0) {
        return;
      }
      if (scrollContainer.scrollTop + scrollContainer.offsetHeight >= scrollContainer.scrollHeight) {
        this.paginationConfig.current = this.paginationConfig.current + 1;
        if (this.paginationConfig.current
        <= Math.floor((this.paginationConfig.count / this.paginationConfig.limit) + 1)) {
          setTimeout(async () => {
            await this.initRtxList(this.searchValue, this.paginationConfig.current);
          }, 200);
        }
      }
    },
    // 编辑成员信息
    editProfile() {
      const fieldsList = JSON.parse(JSON.stringify(this.fieldsList));
      this.profileInfoList = fieldsList.filter((fieldInfo) => {
        if (fieldInfo.key === 'department_name' || fieldInfo.key === 'leader') {
          return false;
        } if (fieldInfo.key === 'telephone') {
          fieldInfo.iso_code = this.currentProfile.iso_code || 'cn';
        }
        if (fieldInfo.editable) {
          fieldInfo.holder = this.$t('请输入');
        }
        fieldInfo.value = this.currentProfile[fieldInfo.key];
        fieldInfo.isError = false;
        return true;
      });
      this.leaderIdList = this.currentProfile.leader.map(item => item.id);
      this.initialDepartments = this.currentProfile.departments;
      this.getSelectedDepartments = this.initialDepartments;
      this.passwordValidDays = this.currentProfile.password_valid_days;

      // 让父组件去修改 detailsBarInfo.type = 'edit'
      this.$emit('editProfile');
    },
    // 展示所在的组织
    formatDepartments(departments) {
      return departments.map(item => item.name).join(';');
    },
    // 更换头像
    getBase64(AvatarBase64) {
      this.AvatarBase64 = AvatarBase64;
    },
    // 初始化直接上级列表
    // eslint-disable-next-line no-unused-vars
    async initRtxList(searchValue, curPage) {
      try {
        const params = {
          id: this.currentCategoryId,
          pageSize: this.paginationConfig.limit,
          page: curPage,
          keyword: searchValue,
        };
        this.showLeaderLoading = true;
        const res = await this.$store.dispatch('organization/getSupOrganization', params);
        this.paginationConfig.count = res.data.count;
        this.copyList.push(...res.data.data);
        if (this.detailsBarInfo.type === 'add') {
          // 新增 profile
          this.rtxList = this.copyList;
        } else {
          // 编辑 profile
          this.rtxList = this.copyList.filter((item) => {
            return item.username !== this.currentProfile.username;
          });
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.showLeaderLoading = false;
      }
    },
    tpl(node, ctx, highlightKeyword) {
      const innerHtml = highlightKeyword(`${node.username}(${node.display_name})`);
      return (
        <div class="bk-selector-node">
            <span class="text" domPropsInnerHTML={innerHtml}></span>
        </div>
      );
    },
    // 显示 所在组织 弹窗
    showSetDepartments() {
      this.isShowSetDepartments = true;
    },
    // 得到子组件已选择的组织
    getDepartments(val) {
      this.getSelectedDepartments = val;
    },
    // 点击确定 设置所在组织
    handleConfirmSet() {
      if (!this.getSelectedDepartments.length) {
        this.$bkMessage({
          message: this.$t('请选择组织'),
          theme: 'warning',
        });
        return;
      }
      // 这里确定之后需要缓存
      this.initialDepartments = this.getSelectedDepartments;
      this.isShowSetDepartments = false;
    },
    handleCancelSet() {
      this.isShowSetDepartments = false;
    },
    handleSubmit() {
      // 验证是否必填
      if (!this.submitVerify()) {
        return;
      }
      // 编辑
      if (this.detailsBarInfo.type === 'edit') {
        // 点击保存时，只在样式上隐藏侧边栏，打开loading
        this.$emit('hideBar');

        const data = {
          leader: this.leaderIdList,
          departments: this.getSelectedDepartments.map(item => item.id),
          password_valid_days: this.passwordValidDays,
        };
        this.profileInfoList.forEach((info) => {
          // 不保存内置不可编辑字段
          if (!(info.editable === false && info.builtin === true)) {
            data[info.key] = info.value;
            if (info.key === 'telephone') {
              data.iso_code = info.iso_code;
            }
          }
        });
        if (this.AvatarBase64) {
          data.logo = this.AvatarBase64;
        }

        this.$store.dispatch('organization/patchProfile', {
          id: this.currentProfile.id,
          data,
        }).then((res) => {
          if (res.result) {
            this.$emit('updateUserInfor');
          }
        })
          .catch((e) => {
            console.warn(e);
            this.$emit('showBar');
          });
      } else if (this.detailsBarInfo.type === 'add') {
        // 点击保存时，只在样式上隐藏侧边栏，打开loading
        this.$emit('hideBar');

        const leader = this.leaderIdList;
        const params = {
          category_id: this.currentCategoryId,
          leader,
          departments: this.getSelectedDepartments.map(item => item.id),
          password_valid_days: this.passwordValidDays,
        };
        this.profileInfoList.forEach((info) => {
          params[info.key] = info.value;
          if (info.key === 'telephone') {
            params.iso_code = info.iso_code;
          }
        });
        if (this.AvatarBase64) {
          params.logo = this.AvatarBase64;
        }

        this.$store.dispatch('organization/postProfile', params).then((res) => {
          if (res.result) {
            this.$emit('updateUserInfor');
          }
        })
          .catch((e) => {
            console.warn(e);
          })
          .finally(() => {
            this.$emit('showBar');
          });
      }
    },
    submitVerify() {
      let markError = false;
      this.profileInfoList.forEach((item) => {
        if (item.isError) {
          markError = true;
        }
        if (this.detailsBarInfo.type === 'edit') {
          if (item.editable && item.require && !this.isValidValue(item.value)) {
            item.isError = true;
            markError = true;
          }
        } else if (this.detailsBarInfo.type === 'add') {
          if (item.require && !this.isValidValue(item.value)) {
            item.isError = true;
            markError = true;
          }
        }
      });
      this.$nextTick(() => {
        const els = this.$el.getElementsByClassName('input-error');
        if (els.length) {
          els[0].scrollIntoView();
        }
      });
      return !markError;
    },
    isValidValue(value) {
      if (value === null || value === undefined) {
        return false;
      } if (typeof value === 'number') {
        return Boolean(value) || value === 0;
      } if (typeof value === 'string') {
        return value !== '';
      }
      return value.length !== 0;
    },
  },
};
</script>

<style lang="scss">
    .member-info-king-tag-input.bk-tag-selector {
      > div {
        > .no-item {
          padding: 0;
        }

        > .placeholder {
          font-size: 14px;
        }
      }

      > .bk-tag-input {
        padding-left: 12px;
        border: 1px solid #c4c6cc !important;

        > .placeholder {
          left: 12px;
        }
      }
    }
</style>

<style lang="scss" scoped>
@import '../../../scss/mixins/scroller';

.add-user-infor,
.member-infor-wrapper {
  height: 100%;
  display: block;
}

.user-infor-wrapper {
  padding: 17px 30px;
  height: calc(100% - 51px);
  background: #fafbfd;
  overflow: hidden;
  overflow-y: auto;

  @include scroller($backgroundColor: #e6e9ea, $width: 4px);

  > .information-box {
    width: 460px;
  }
}

.fill-infor-wrapper {
  width: 460px;
  position: relative;
}

.infor-title {
  padding-bottom: 8px;
  font-size: 14px;
  font-weight: bold;
  color: rgba(51, 60, 72, 1);
  line-height: 19px;
  border-bottom: 1px solid #dde4eb;
}

.infor-list {
  padding-top: 17px;
  font-size: 14px;
  color: rgba(99, 101, 110, 1);

  &.no-verifica {
    .select-text {
      padding-right: 12px;
    }
  }

  &:nth-child(1),
  &:nth-child(2) {
    .input-text {
      width: 368px;

      .select-text {
        width: 368px;
      }
    }
  }

  .desc {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
    line-height: 19px;

    .star {
      display: inline-block;
      vertical-align: middle;
      margin-left: 4px;
      color: #fe5c5c;
    }
  }

  .input-text {
    position: relative;
    min-height: 32px;
    background: #fff;

    &.leader-input {
      .input-loading {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1500;
        cursor: not-allowed;
        background: rgba(0, 0, 0, .05);

        img {
          width: 20px;
        }
      }
    }

    .select-text {
      display: block;
      padding: 0 30px 0 12px;
      width: 460px;

      &.active {
        color: #63656e !important;
      }

      &.disable {
        background-color: #fafbfd;
        cursor: not-allowed;
      }
    }

    .icon-user-exclamation-circle-shape {
      position: absolute;
      right: 10px;
      top: 10px;
      font-size: 16px;
      color: #ea3636;
    }
  }

  .hint {
    padding: 0 10px;
    position: absolute;
    top: -42px;
    right: 0;
    height: 36px;
    line-height: 36px;
    color: #fff;
    font-size: 0;
    border-radius: 4px;
    background: #000;

    .arrow {
      position: absolute;
      bottom: -2px;
      right: 14px;
      width: 6px;
      height: 6px;
      border-top: 1px solid #000;
      border-left: 1px solid #000;
      transform: rotate(45deg);
      z-index: 10;
      background: #000;
    }

    .text,
    .icon-user-exclamation-circle-shape {
      display: inline-block;
      vertical-align: middle;
      font-size: 12px;
    }

    .icon-user-exclamation-circle-shape {
      font-size: 16px;
      margin-right: 10px;
      position: relative;
      right: 0;
      top: 0;
      color: #fff;
    }
  }
}

.mark-width {
  .infor-list {
    .input-text {
      width: 460px;
      cursor: pointer;

      .select-text {
        width: 460px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }
}

.action-btn {
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  padding: 9px 0 9px 30px;
  background: #fff;
  border-top: 1px solid #dcdee5;

  .btn {
    width: 76px !important;
    margin-right: 10px;
  }
}
</style>
