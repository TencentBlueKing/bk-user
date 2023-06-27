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
  <div class="operation-config">
    <i class="icon bk-icon icon-more" @click="isOperationConfig = true" />
    <div
      v-if="isOperationConfig"
      :class="{ 'dropdown-list': true, 'chang-en': $i18n.locale === 'en' }"
      v-bk-clickoutside="handleClickOutSide"
      @click="isOperationConfig = false">
      <div class="specific-menu">
        <!-- 重命名 -->
        <a href="javascript:;" @click="$emit('handleRename', node)">{{ $t('重命名') }}</a>
        <!-- 同步 -->
        <a
          href="javascript:;"
          :class="['right', { 'delete-disable': !node.configured }]"
          v-if="node.type === 'mad' || node.type === 'ldap'"
          v-bk-tooltips.left="$t('目录未完成配置，无法操作')"
          :disabled="node.configured"
          @click="syncCatalog(node)">{{ $t('同步') }}</a>
        <!-- 导入导出 -->
        <template v-if="node.type === 'local'">
          <a href="javascript:;" @click="exportUser(node)">{{ $t('导出') }}</a>
          <a href="javascript:;" @click="importUser(node)">{{ $t('导入') }}</a>
        </template>
        <!-- 启停 -->
        <a
          href="javascript:;"
          :class="['right', { 'delete-disable': node.default }]"
          v-if="node.type"
          v-bk-tooltips.left="$t('默认目录不能被停用')"
          :disabled="!node.default"
          @click="switchStatus(node)">{{ node.activated ? $t('停用') : $t('启用') }}</a>
        <!-- 删除 -->
        <a
          href="javascript:;"
          :class="['right delete', {
            'delete-disable': node.default || (node.activated && node.configured) || node.has_children
          }]"
          :v-bk-tooltips="deleteConfig"
          :disabled="!node.default || (!node.activated && !node.configured) || !node.has_children"
          @click="deleteDepartment(node)">{{ $t('删除') }}</a>
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
  </div>
</template>

<script>
import mixin from './mixin';
import ImportUser from '../catalog/home/ImportUser.vue';
export default {
  name: 'OperationConfig',
  components: {
    ImportUser,
  },
  mixins: [mixin],
  props: {
    node: {
      type: Object,
      default: () => ({}),
    },
    currentCategoryId: {
      type: Number,
    },
  },
  data() {
    return {
      isOperationConfig: false,
      deleteConfig: {
        placement: 'left',
        content: '',
      },
    };
  },
  watch: {
    node(val, oldVal) {
      if (val !== oldVal) {
        if (val.default) {
          this.deleteConfig.content = this.$t('默认目录不能被删除');
        } else if (val.activated && val.configured) {
          this.deleteConfig.content = this.$t('请先停用，方可删除目录');
        } else if (val.has_children) {
          this.deleteConfig.content = this.$t('非空组织不能删除');
        }
      }
    },
  },
  methods: {
    handleClickOutSide() {
      this.isOperationConfig = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.operation-config {
  position: relative;
  .icon-more {
    width: 26px;
    height: 26px;
    display: inline-block;
    line-height: 25px;
    vertical-align: middle;
    border: 1px solid #c4c6cc !important;
    border-radius: 2px;
    &:hover {
      cursor: pointer;
    }
}
  .dropdown-list {
    display: block;
    position: absolute;
    right: 0;
    top: 50px;
    width: 174px;
    background: #fff;
    border-radius: 2px;
    border: 1px solid #dcdee5;
    box-shadow: 0 2px 6px rgba(51, 60, 72, .1);
    z-index: 1000000;
    // 英文
    &.chang-en {
      .specific-menu {
        a {
          padding: 0 10px;
          white-space: normal;
          line-height: 28px;
        }
      }
    }
    // 添加下级组织
    .specific-menu {
      position: relative;

      a {
        padding-left: 20px;
        font-size: 14px;
        display: block;
        color: #737987;
        line-height: 36px;
        text-decoration: none;
        white-space: nowrap;

        &.delete {
          color: #ec4848;
        }

        &:hover {
          color: #3b84ff;
          background: #e1ecff;
        }

        &.disable {
          cursor: not-allowed;
          color: #c4c6cc;
        }

        &.delete-disable {
          color: #c4c6cc;
          cursor: not-allowed;
        }
      }
    }
  }
}
</style>
