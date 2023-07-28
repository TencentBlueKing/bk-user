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
  <div class="member-infor-wrapper" v-bkloading="{ isLoading: detailsBarInfo.basicLoading }">
    <!-- view -->
    <UserMaterial
      v-if="detailsBarInfo.type === 'view'"
      :current-profile="currentProfile"
      :current-category-id="currentCategoryId"
      :current-category-type="currentCategoryType"
      :fields-list="fieldsList"
      :status-map="statusMap"
      :timer-map="timerMap"
      @editProfile="editProfile"
      @deleteProfile="$emit('deleteProfile', currentProfile)"
      @restoreProfile="$emit('restoreProfile')"
      @showBarLoading="$emit('showBarLoading')"
      @closeBarLoading="$emit('closeBarLoading')" />
    <!-- add/edit -->
    <div class="add-user-infor" v-else>
      <div class="user-infor-wrapper" ref="userInforWrapper">
        <div class="information-box" data-test-id="superiorData">
          <h4 class="infor-title" @click="isUserInfo">
            <i :class="['bk-icon', showUserInfo ? 'icon-down-shape' : 'icon-up-shape']" />
            {{$t('用户信息')}}
          </h4>
          <div :class="showUserInfo ? 'fill-infor-wrapper' : 'isHide'">
            <InputComponents
              :edit-status="detailsBarInfo.type === 'edit'"
              :profile-info-list="profileInfoList"
              :status-map="statusMap"
              :rules="rules"
              :expire-date="currentProfile"
              ref="userInfoData" />
            <UploadAvatar
              @getBase64="getBase64"
              :img-src="currentProfile === null ? $store.state.localAvatar : currentProfile.logo" />
          </div>
          <h4 class="infor-title" style="margin-top: 30px" @click="isUserSetting">
            <i :class="['bk-icon', showUserSetting ? 'icon-down-shape' : 'icon-up-shape']" />
            {{$t('用户设置')}}
          </h4>
          <div :class="showUserSetting ? 'mark-width' : 'isHide'">
            <bk-form
              ref="userSetting"
              :model="userSettingData"
              form-type="vertical"
              :rules="userSettingRules">
              <bk-form-item
                class="leader-input"
                :label="$t('直接上级')"
                :required="false"
                :property="'leader'"
                :error-display-type="'normal'">
                <bk-select
                  v-if="showselectData || detailsBarInfo.type === 'add'"
                  searchable
                  multiple
                  display-tag
                  v-model="userSettingData.leader"
                  :list="rtxList"
                  ext-popover-cls="scrollview"
                  @toggle="handleBranchToggle"
                  :scroll-height="188"
                  @change="changSelect">
                  <bk-option
                    v-for="option in rtxList"
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
                  v-model="userSettingData.leader"
                  @toggle="handleBranchToggle"
                  @change="changSelect">
                  <bk-option
                    v-for="option in currentProfile.leader"
                    :key="option.id"
                    :id="option.id"
                    :name="option.username">
                  </bk-option>
                </bk-select>
                <div class="input-loading" @click.stop v-show="showLeaderLoading">
                  <img src="../../../images/svg/loading.svg" alt="">
                </div>
              </bk-form-item>
              <bk-form-item
                :label="$t('所在公司')"
                :required="true"
                :property="'department_name'"
                :error-display-type="'normal'">
                <bk-input
                  class="input-text"
                  :value="formatDepartments(initialDepartments)"
                  @focus="showSetDepartments" />
              </bk-form-item>
              <bk-form-item
                :label="$t('密码有效期')"
                :required="true"
                :property="'password_valid_days'"
                :error-display-type="'normal'">
                <bk-select v-model="userSettingData.password_valid_days" :clearable="false" @change="changSelect">
                  <bk-option
                    v-for="option in passwordValidDaysList"
                    :key="option.days"
                    :id="option.days"
                    :name="option.text">
                  </bk-option>
                </bk-select>
              </bk-form-item>
            </bk-form>
          </div>
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
    statusMap: {
      type: Object,
      default: {},
    },
    timerMap: {
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
      showLeaderLoading: false,
      isShowSetDepartments: false,
      initialDepartments: [],
      // 选择的组织
      getSelectedDepartments: [],
      rtxListUpdated: false,
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
      // 不展示的字段
      hiddenFields: ['department_name', 'leader', 'last_login_time', 'create_time'],
      showUserInfo: true,
      showUserSetting: true,
      // 用户设置字段
      userSettingData: {
        leader: [],
        department_name: [],
        password_valid_days: null,
      },
      rules: {
        username: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur',
          },
          {
            max: 32,
            message: this.$t('不能多于32个字符'),
            trigger: 'blur',
          },
          {
            regex: /^[a-zA-Z0-9][0-9a-zA-Z_.-]{0,31}$/,
            message: this.$t('由1-32位字母、数字、下划线(_)、点(.)、减号(-)字符组成，以字母或数字开头'),
            trigger: 'blur',
          },
        ],
        display_name: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur',
          },
          {
            max: 32,
            message: this.$t('不能多于32个字符'),
            trigger: 'blur',
          },
        ],
        email: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur',
          },
          {
            regex: /^([A-Za-z0-9_\-.])+@([A-Za-z0-9_\-.])+\.[A-Za-z]+$/,
            message: this.$t('请输入正确的邮箱地址'),
            trigger: 'blur',
          },
        ],
        status: [
          {
            required: true,
            message: this.$t('请选择账户状态'),
            trigger: 'blur',
          },
        ],
        staff_status: [
          {
            required: true,
            message: this.$t('请选择在职状态'),
            trigger: 'blur',
          },
        ],
      },
      userSettingRules: {
        department_name: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'change',
          },
        ],
      },
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
      const list = JSON.parse(JSON.stringify(this.fieldsList));
      const fieldsList = [];
      list.forEach((item) => {
        fieldsList.push(item);
      });
      this.profileInfoList = fieldsList.filter((fieldInfo) => {
        if (this.hiddenFields.includes(fieldInfo.key)) {
          return false;
        }
        fieldInfo.holder = this.$t('请输入');
        fieldInfo.value = fieldInfo.type === 'multi_enum' ? JSON.parse(fieldInfo.default) : fieldInfo.default;
        fieldInfo.isError = false;
        return true;
      });
      this.initialDepartments = this.detailsBarInfo.departments;
      this.userSettingData.department_name = this.formatDepartments(this.initialDepartments);
      this.getSelectedDepartments = this.initialDepartments;
      this.$store.dispatch('catalog/ajaxGetPassport', { id: this.currentCategoryId }).then((res) => {
        this.userSettingData.password_valid_days = res.data.find(item => item.key === 'password_valid_days').value;
      });
    }
    // 进入页面获取数据
    this.searchValue = '';
    this.paginationConfig.current = 1;
    this.initRtxList(this.searchValue, this.paginationConfig.current);
  },
  methods: {
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
        if (this.hiddenFields.includes(fieldInfo.key)) {
          return false;
        }
        if (fieldInfo.key === 'telephone') {
          fieldInfo.iso_code = this.currentProfile.iso_code || 'cn';
        }
        if (fieldInfo.editable) {
          fieldInfo.holder = this.$t('请输入');
        }
        if (fieldInfo.value === '--') {
          fieldInfo.value = '';
        } else {
          fieldInfo.value = this.currentProfile[fieldInfo.key];
        }
        fieldInfo.isError = false;
        return true;
      });
      const { leader, leaders } = this.currentProfile;
      this.userSettingData.leader = (leader || leaders).map(item => item.id);
      this.initialDepartments = this.currentProfile.departments;
      this.userSettingData.department_name = this.formatDepartments(this.initialDepartments);
      this.getSelectedDepartments = this.initialDepartments;
      this.userSettingData.password_valid_days = this.currentProfile.password_valid_days;

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
        this.copyList.push(...res.data.results);
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
      this.userSettingData.department_name = this.formatDepartments(this.initialDepartments);
      this.isShowSetDepartments = false;
      window.changeInput = true;
    },
    handleCancelSet() {
      this.isShowSetDepartments = false;
    },
    handleSubmit() {
      let phoneValue = '';
      this.profileInfoList.map((item) => {
        if (item.key === 'telephone') {
          phoneValue = this.$refs.userInfoData.$refs.phone[0].verifyInput(item.value);
        }
        if (item.key === 'position' && item.value === '') {
          item.value = null;
        }
        if (item.type === 'number' && item.key !== 'telephone') {
          item.value = item.value.toString();
        }
      });
      Promise.all([
        this.$refs.userInfoData.$refs.validateForm.validate(),
        this.$refs.userSetting.validate(),
      ]).then(() => {
        // 编辑
        if (this.detailsBarInfo.type === 'edit') {
          // 点击保存时，只在样式上隐藏侧边栏，打开loading

          const data = {
            leader: this.userSettingData.leader,
            departments: this.getSelectedDepartments.map(item => item.id),
            password_valid_days: this.userSettingData.password_valid_days,
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

          !phoneValue && this.$store.dispatch('organization/patchProfile', {
            id: this.currentProfile.id,
            data,
          }).then((res) => {
            if (res.result) {
              this.$emit('updateUserInfor');
              this.$emit('hideBar');
            }
          })
            .catch((e) => {
              console.warn(e);
              this.$emit('showBar');
            });
        } else if (this.detailsBarInfo.type === 'add') {
          // 点击保存时，只在样式上隐藏侧边栏，打开loading

          const params = {
            category_id: this.currentCategoryId,
            leader: this.userSettingData.leader,
            departments: this.getSelectedDepartments.map(item => item.id),
            password_valid_days: this.userSettingData.password_valid_days,
          };
          this.profileInfoList.forEach((info) => {
            if (info.key !== 'last_login_time' && info.key !== 'create_time') {
              params[info.key] = info.value;
            }
            if (info.key === 'telephone') {
              params.iso_code = info.iso_code;
            }
          });
          if (this.AvatarBase64) {
            params.logo = this.AvatarBase64;
          }

          !phoneValue && this.$store.dispatch('organization/postProfile', params).then((res) => {
            if (res.result) {
              this.$emit('updateUserInfor');
              this.$emit('hideBar');
            }
          })
            .catch((e) => {
              console.warn(e);
            })
            .finally(() => {
              this.$emit('showBar');
            });
        }
      });
    },
    isUserInfo() {
      this.showUserInfo = !this.showUserInfo;
    },
    isUserSetting() {
      this.showUserSetting = !this.showUserSetting;
    },
    changSelect(val, oldVal) {
      if (oldVal === null) return;
      window.changeInput = true;
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
  padding: 24px 24px 75px;
  height: calc(100% - 51px);
  overflow: hidden;
  overflow-y: auto;

  @include scroller($backgroundColor: #e6e9ea, $width: 4px);

  > .information-box {
    width: 100%;
  }
}

.fill-infor-wrapper {
  width: 100%;
  position: relative;
  display: block;
  margin-top: 8px;
}
.isHide {
  display: none;
}

.infor-title {
  font-size: 12px;
  color: #313238;
  line-height: 30px;
  background-color: #F0F1F5;
  i {
    margin-left: 5px;
    color: #979BA5;
  }
  &:hover {
    cursor: pointer;
  }
}

.infor-list {
  padding-top: 17px;
  color: rgba(99, 101, 110, 1);

  &.no-verifica {
    .select-text {
      padding-right: 12px;
    }
  }

  &:nth-child(1),
  &:nth-child(2) {
    .input-text {
      width: 475px;
      font-size: 12px;

      .select-text {
        width: 475px;
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
  display: block;
  margin-top: 8px;
  .bk-form-item {
    .input-text {
      cursor: pointer;

      .select-text {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        display: inline-block;
        padding: 0 30px 0 12px;
        font-size: 14px;
        color: #63656e;
        background: #fff;
      }
    }
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
  }
}

.action-btn {
  position: fixed;
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

::v-deep .bk-form  {
  .bk-label-text {
    font-size: 12px !important;
  }
  .bk-select-dropdown {
    background: #fff;
  }
}
</style>
