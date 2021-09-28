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
  <div class="no-authority">
    <div v-if="showPageAuth" class="page-authority-container">
      <img src="../../images/svg/lock-radius.svg" alt="lock" class="lock-icon">
      <div class="title">{{authNames + $t('无权限访问')}}</div>
      <div class="detail">{{$t('你没有相应资源的访问权限')}}</div>
      <bk-button v-if="applyUrl" class="king-button" theme="primary" @click="confirmPageApply">{{$t('去申请')}}</bk-button>
    </div>

    <bk-dialog v-model="showApplyDialog"
               :mask-close="false"
               :close-icon="false"
               :width="740"
               :ok-text="$t('去申请')"
               @confirm="confirmSourceApply"
               @cancel="closeAuth">
      <div class="apply-authority-dialog-container" data-test-id="list_authorityManagement">
        <img src="../../images/svg/lock-radius.svg" alt="lock" class="lock-icon">
        <div class="title">{{$t('该操作需要以下权限')}}</div>
        <bk-table class="king-table" :data="authInfos" :outer-border="false">
          <bk-table-column :label="$t('需要申请的权限')" prop="display_name"></bk-table-column>
          <bk-table-column :label="$t('关联的资源实例')">
            <div class="related-resources-container" slot-scope="{ row }">
              <span v-for="(src, index) in row.related_resources" :key="index">
                {{ src.type_name + '：' + src.name }}
              </span>
              <span v-if="!row.related_resources.length">--</span>
            </div>
          </bk-table-column>
        </bk-table>
      </div>
    </bk-dialog>

    <bk-dialog v-model="showConfirmDialog"
               :title="$t('权限申请单已提交？')"
               :ok-text="$t('刷新页面')"
               @confirm="confirmAfterApply"
               @cancel="closeAuth">
      {{$t('请在权限中心填写权限申请单')}}
    </bk-dialog>
  </div>
</template>

<script>
export default {
  props: {
    noAuthData: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      showPageAuth: false,
      showApplyDialog: false,
      showConfirmDialog: false,
      applyUrl: '',
      authInfos: [],
    };
  },
  computed: {
    authNames() {
      return `【${this.authInfos.map(authInfo => authInfo.display_name).join('，')}】`;
    },
  },
  mounted() {
    try {
      const id = this.noAuthData.requestId;

      // 以下接口由具体业务侧处理，不统一处理
      const startsExceptList = [
        'get_api/v2/departments/?only_enabled=', // 组织列表
      ];
      const equalExceptList = [
        'get_api/v2/categories/', // 目录列表
        'get_api/v2/fields/manageable/', // 字段管理权限查看
      ];
      // eslint-disable-next-line max-len
      if (startsExceptList.some(exceptId => id.startsWith(exceptId)) || equalExceptList.some(exceptId => id === exceptId)) {
        this.$store.commit('updateNoAuthData', null);
        return;
      }

      // 以下接口页面无权限；其他接口展示申请权限对话框
      const startsPageList = [
        'has_not_path_auth', // 自定义页面无权限
        'get_api/v2/audit/operation_logs/?start_time=', // 审计列表
      ];
      if (startsPageList.some(pageId => id.startsWith(pageId))) {
        this.showPageAuth = true;
      } else {
        this.showApplyDialog = true;
      }
      const { auth_infos: authInfos, callback_url: applyUrl } = this.noAuthData.data.detail;
      this.applyUrl = applyUrl;
      this.authInfos = authInfos;
    } catch (e) {
      this.showPageAuth = true;
      console.warn(e, '403 response error data');
    }
  },
  methods: {
    confirmPageApply() {
      window.open(this.applyUrl);
    },
    confirmSourceApply() {
      this.showApplyDialog = false;

      setTimeout(() => {
        this.showConfirmDialog = true;
        window.open(this.applyUrl);
      }, 340);
    },
    confirmAfterApply() {
      this.closeAuth();
      this.$emit('reloadRouter');
    },
    closeAuth() {
      this.$nextTick(() => {
        this.$store.commit('updateNoAuthData', null);
      });
    },
  },
};
</script>

<style lang="scss" scoped>
.no-authority {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.page-authority-container {
  display: flex;
  flex-flow: column;
  align-items: center;
  height: 100%;
  background-color: #fff;
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

.apply-authority-dialog-container {
  display: flex;
  flex-flow: column;
  align-items: center;

  .lock-icon {
    margin-bottom: 10px;
  }

  .title {
    font-size: 20px;
    color: #63656e;
    margin-bottom: 30px;
  }

  /deep/ .king-table {
    margin-bottom: 12px;

    .bk-table-body-wrapper {
      height: 128px;
      overflow-y: auto;
    }

    .related-resources-container {
      display: flex;
      flex-flow: column;
    }
  }
}
</style>
