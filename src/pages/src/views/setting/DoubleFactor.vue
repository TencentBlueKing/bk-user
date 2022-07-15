<template>
  <div class="double-factor-wrapper">
    <p class="info-title">{{ $t('双因子认证')}}</p>
    <div class="info-header-container">
      <div class="info-left">
        {{ $t('启用双因子认证后_登录时还需要通过短信或邮件验证码进行验证_再次确认登录者身份_进一步提高帐号安全性') }}
      </div>
      <div class="info-right">
        <i :class="['user-icon icon-duihao-i', { 'is-open': open }]"></i>
        <span>{{ $t('已开启') }}</span>
        <bk-switcher class="info-switcher" v-model="open" theme="primary"></bk-switcher>
      </div>
    </div>
    <div class="info-content-container" v-show="open">
      <bk-radio-group v-model="activeRadio">
        <span>{{ $t('认证方式') }}</span>
        <bk-radio style="margin-left: 80px" :value="'email'">{{ $t('邮件') }}</bk-radio>
        <bk-radio style="margin-left: 80px" :value="'sms'">{{ $t('短信') }}</bk-radio>
      </bk-radio-group>
      <render-member
        :users="users"
        :departments="departments"
        :is-all="isAll"
        @on-add="handleAddMember"
        @on-delete="handleMemberDelete"
        @on-delete-all="handleDeleteAll" />
      <p class="action-empty-error" v-if="isShowMemberEmptyError">{{ $t('可授权人员范围不可为空') }}</p>
      <bk-button
        theme="primary" type="button" @click="handleSubmit"
        data-test-id="grading_btn_createSubmit"
        :loading="submitLoading">
        {{ $t('提交') }}
      </bk-button>
      <dialog-index
        :show.sync="isShowAddMemberDialog"
        :users="users"
        :departments="departments"
        :title="addMemberTitle"
        :all-checked="isAll"
        show-limit
        @on-cancel="handleCancelAdd"
        @on-sumbit="handleSumbitAdd" />
    </div>
  </div>
</template>

<script>
import DialogIndex from '../../components/dialog-tree/dialogIndex.vue';
import renderMember from '../../components/dialog-tree/renderMember.vue';
export default {
  components: { DialogIndex, renderMember },
  data() {
    return {
      open: true,
      activeRadio: 'email',
      panels: [
        { name: 'organization', label: this.$t('组织架构') },
        { name: 'manual', label: this.$t('手动输入') },
      ],
      isAll: true,
      username: '',
      isShowAddMemberDialog: false,
      users: [],
      departments: [],
      addMemberTitle: this.$t('选择范围'),
      isShowMemberAdd: true,
      isShowMemberEmptyError: false,
      submitLoading: false,
    };
  },
  created() {
    this.getUser();
  },
  methods: {
    async fetchPageData() {
      if (Number(this.id) > 0) {
        await this.fetchDetail();
      }
    },
    async fetchDetail() {
      try {
        const res = await this.$store.dispatch('role/getRatingManagerDetail', { id: this.id });
        this.formData.members = res.data.members;
        this.users = res.data.subject_scopes.filter(item => item.type === 'user').map((item) => {
          return {
            name: item.name,
            username: item.id,
            type: item.type,
          };
        });
        this.departments = res.data.subject_scopes.filter(item => item.type === 'department').map((item) => {
          return {
            name: item.name,
            count: item.member_count,
            type: item.type,
            id: item.id,
          };
        });
        this.isShowMemberAdd = false;
        // const list = [];
        // res.data.authorization_scopes.forEach((item) => {
        //   item.actions.forEach((act) => {
        //     const tempResource = _.cloneDeep(act.resource_groups);
        //     tempResource.forEach((groupItem) => {
        //       groupItem.related_resource_types.forEach((subItem) => {
        //         subItem.condition = null;
        //       });
        //     });
        //     list.push({
        //       description: act.description,
        //       expired_at: act.expired_at,
        //       id: act.id,
        //       name: act.name,
        //       system_id: item.system.id,
        //       system_name: item.system.name,
        //       $id: `${item.system.id}&${act.id}`,
        //       tag: act.tag,
        //       type: act.type,
        //       resource_groups: tempResource,
        //     });
        //   });
        // });
        // this.originalList = _.cloneDeep(list);
      } catch (e) {
        console.error(e);
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'error',
          message: e.message || e.data.msg || e.statusText,
          ellipsisLine: 2,
          ellipsisCopy: true,
        });
      }
    },
    async getUser() {
      const res = await this.$store.dispatch('getUserInfo');
      this.username = res.data.username;
    },
    handleAddMember() {
      this.isShowAddMemberDialog = true;
    },
    handleCancelAdd() {
      this.isShowAddMemberDialog = false;
    },
    handleMemberDelete(type, payload) {
      window.changeDialog = true;
      if (type === 'user') {
        this.users.splice(payload, 1);
      } else {
        this.departments.splice(payload, 1);
      }
      this.isShowMemberAdd = this.users.length < 1 && this.departments.length < 1;
    },
    handleSumbitAdd(payload) {
      window.changeDialog = true;
      // const { users, departments } = payload;
      this.isAll = payload.isAll;
      // this.users = _.cloneDeep(users);
      // this.departments = _.cloneDeep(departments);
      this.isShowMemberAdd = false;
      this.isShowAddMemberDialog = false;
      this.isShowMemberEmptyError = false;
    },
    handleDeleteAll() {
      this.isAll = false;
      this.isShowMemberAdd = true;
    },
  },
};
</script>

<style lang="scss" scoped>
.double-factor-wrapper {
  height: 100%;
  padding: 20px;
  font-size: 14px;
  color: #63656e;
  .info-title {
    margin-bottom: 20px;
  }
  .info-header-container {
    display: flex;
    margin-bottom: 20px;
    .info-left {
      width: 800px;
      color: #aaa;
    }
    .info-right {
      width: 200px;
      .user-icon {
        background-color: #737987;
        border-radius: 50%;
        color: #fff;
      }
      .is-open {
        background-color: #2dcb56;
        border-radius: 50%;
        color: #fff;
      }
      span {
        display: inline-block;
        padding-right: 20px;
        position: relative;
        &::after {
          content: '|';
          position: absolute;
          top: 0;
          right: 0;
          color: #737987;
        }
      }
      .bk-switcher {
        &.info-switcher {
          display: inline-block;
          margin-left: 20px;
        }
      }
    }
  }
  .info-content-container {
    .content-item {
      margin-top: 20px;
      display: flex;
      .add-scope-contet {
        margin-left: 80px;
        .add-scope {
          color: #3a84ff;
          &:hover {
            cursor: pointer;
          }
        }
        .all-item {
          font-size: 14px;
          margin-left: 10px;
          color: #979ba5;
        }
        .member-info {
          margin-left: 10px;
          margin-bottom: 9px;
          font-size: 14px;
          color: #979ba5;
          .count {
            font-weight: 600;
          }
        }
      }
    }
  }
}
.scope-dialog {
  .scope-dialog-content {
    display: flex;
    .content-left {
      width: 50%;
      border-right: 1px solid #dcdee5;
      .member-tree-wrapper {
        min-height: 309px;
      }
      .tree {
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
    }
    .content-right {
      width: 50%;
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
  .limit-wrapper {
    float: left;
    margin-top: 5px;
  }
}
</style>
