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
  <div class="organization-tree-wrapper">
    <bk-tree
      ext-cls="top-tree"
      draggable
      drag-sort
      :data="availableDirectory"
      :node-key="'id'"
      :tpl="tpl"
      :show-icon="false"
      @on-expanded="handleClickToggle"
      @on-drag-node="handleDragNode"
      @async-load-nodes="handleClickToggle">
    </bk-tree>
    <div class="bottom-tree">
      <p :class="['bottom-tree-header', { 'show-header': isDirectory }]" @click="handleClickDirectory">
        <i :class="isDirectory ? 'bk-icon icon-angle-down' : 'bk-icon icon-angle-right'"></i>{{ $t('不可用目录') }}
      </p>
      <bk-tree
        :ext-cls="['bottom-tree-content', { 'show-content': isDirectory }]"
        draggable
        drag-sort
        :data="unavailableDirectory"
        :node-key="'id'"
        :tpl="tpl"
        :show-icon="false"
        @on-expanded="handleClickToggle"
        @on-drag-node="handleDragNode"
        @async-load-nodes="handleClickToggle">
      </bk-tree>
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
import mixin from '@/components/organization/mixin';
import ImportUser from '@/components/catalog/home/ImportUser.vue';
export default {
  name: 'OrganizationTree',
  components: {
    ImportUser,
  },
  mixins: [mixin],
  props: {
    treeDataList: {
      type: Array,
      default: [],
    },
    treeSearchResult: {
      type: Object,
      default: null,
    },
    currentCategoryId: {
      type: Number,
    },
  },
  data() {
    return {
      // 可用目录
      availableDirectory: [],
      // 不可用目录
      unavailableDirectory: [],
      treeScrollTop: 0,
    };
  },
  computed: {
    topTreeStyle() {
      return {
        'overflow-y': 'auto',
      };
    },
  },
  watch: {
    treeDataList: {
      // immediate: true,
      deep: true,
      handler(val) {
        this.availableDirectory = [];
        this.unavailableDirectory = [];
        val.map((item) => {
          if (item.activated && item.configured) {
            this.availableDirectory.push(item);
          } else {
            this.unavailableDirectory.push(item);
          }
        });
      },
    },
    treeSearchResult() {
      if (this.availableDirectory.length) {
        this.availableDirectory.forEach((item) => {
          this.$set(item, 'expanded', true);
        });
      } else {
        this.unavailableDirectory.forEach((item) => {
          this.isDirectory = true;
          this.$set(item, 'expanded', true);
        });
      }
    },
  },
  mounted() {
    const topTreeWrap = document.querySelector('.top-tree');
    topTreeWrap.addEventListener('scroll', this.scrollChange, true);
  },
  methods: {
    scrollChange(e) {
      this.treeScrollTop = e.target.scrollTop;
      this.$emit('updateScroll');
    },
    handleClickToggle(item) {
      this.$emit('handleClickToggle', item);
    },
    tpl(node) {
      return <div class={[
        'node-content',
        `${node.showBackground ? 'show-background' : 'directory-warpper'}`,
        { nodeTag: (node.configured && !node.activated && node.type) || (!node.configured && node.type) },
      ]}>
        {node.type && !node.children.length ? <i class={'hide-icon'} /> : ''}
        {node.display_name ? <i class={['icon user-icon icon-root-node-i', { 'active-icon': node.showBackground }]} />
          : <i class={['icon icon-user-file-close-01', { 'active-icon': node.showBackground }]} />}
        <span class={node.showBackground ? 'node-title node-selected' : 'node-title'}
          domPropsInnerHTML={node.display_name || node.name}
          onClick={() => this.$emit('handleClickTreeNode', node, event)} v-bk-overflow-tips></span>
        <div class="option">
          <i ref="more" class={['icon bk-icon icon-more', { 'show-more': node.showBackground }]}
          onClick={() => this.$emit('handleClickOption', node, event, this.treeScrollTop)}></i>
          {(node.configured && !node.activated && node.type)
            ? <bk-tag class={'show-tag'} type="filled">{this.$t('停用1')}</bk-tag>
            : ''}
          {(!node.configured && node.type)
            ? <bk-tag class={'show-tag'} theme="warning" type="filled">{this.$t('未完成')}</bk-tag>
            : ''}
          <div class={[node.showOption ? 'show-dropdown-list' : 'dropdown-list', { 'chang-en': this.$i18n.locale === 'en' }]}>
            <div class="specific-menu">
              <a href="javascript:;"
                class={{ 'delete-disable': node.level > 9 }}
                onMouseenter={this.checkAddTips.bind(this, node)}
                onMouseleave={this.closeAddTips.bind(this, node)}
                onClick={() => this.$emit('addOrganization', node, event)}>
                {this.getAddOrganization(node)}
              </a>
              <div class={['tooltip-content', { 'show-tooltip-content': node.showLevelTips }]}>
                <p class="inner">{this.$t('最多只能添加十级')}</p>
              </div>
              <a href="javascript:;" onClick={() => this.$emit('handleRename', node, event)}>{this.$t('重命名')}</a>
              {node.type
                ? <div class="specific-menu">
                    <a href="javascript:;" onClick={() => this.$emit('handleConfigDirectory', event)}>
                      {this.$t('目录配置')}
                    </a>
                    <a href="javascript:;"
                      class={{ 'delete-disable': node.default }}
                      onMouseenter={this.checkSwitchTips.bind(this, node)}
                      onMouseleave={this.closeSwitchTips.bind(this, node)}
                      onClick={this.switchStatus.bind(this, node)}>
                      {node.activated ? this.$t('停用') : this.$t('启用')}
                    </a>
                    <div class={['tooltip-content', { 'show-tooltip-content': node.showSwitchTips }]}>
                      <p class="inner">{this.$t('默认目录不能被停用')}</p>
                    </div>
                  </div>
                : ''}
              {(node.type && node.type !== 'local')
                ? <div class="specific-menu">
                    <a href="javascript:;"
                    class={{ 'delete-disable': !node.configured }}
                    onMouseenter={this.checkSyncTips.bind(this, node)}
                    onMouseleave={this.closeSyncTips.bind(this, node)}
                    onClick={this.syncCatalog.bind(this, node)}>
                    {this.$t('同步')}
                    </a>
                    <div class={['tooltip-content', { 'show-tooltip-content': node.showSyncTips }]}>
                      <p class="inner">{this.$t('目录未完成配置，无法操作')}</p>
                    </div>
                  </div>
                : ''}
              {node.type === 'local'
                ? <div class="specific-menu">
                    <a href="javascript:;"
                    class={{ 'delete-disable': !node.has_children }}
                    onMouseenter={this.checkExportTips.bind(this, node)}
                    onMouseleave={this.closeExportTips.bind(this, node)}
                    onClick={this.exportUser.bind(this, node)}>{this.$t('导出')}</a>
                    <a href="javascript:;" onClick={this.importUser.bind(this, node)}>{this.$t('导入')}</a>
                    <div class={['tooltip-content', { 'show-tooltip-content': node.showExportTips }]}>
                      <p class="inner">{this.$t('空目录无需导出')}</p>
                    </div>
                  </div>
                : ''}
            </div>
            <div class="specific-menu">
              <a href="javascript:;"
                class={['delete', { 'delete-disable': this.deleteDisabled(node) }]}
                onClick={() => this.$emit('deleteDepartment', node, event)}
                onMouseenter={this.checkDeleteTips.bind(this, node)}
                onMouseleave={this.closeDeleteTips.bind(this, node)}>
                {this.$t('删除')}
              </a>
              <div class={['tooltip-content', { 'show-tooltip-content': node.showDeleteTips }]}>
                {<p class="inner">{this.getDeleteTips(node)}</p>}
              </div>
            </div>
          </div>
        </div>
      </div>;
    },
    getDeleteTips(node) {
      let text = '';
      if (node.default) {
        text = this.$t('默认目录不能被删除');
      } else if (node.activated) {
        text = this.$t('请先停用，方可删除目录');
      } else if (!node.type && node.has_children) {
        text = this.$t('非空组织不能删除');
      }
      return text;
    },
    handleClickDirectory() {
      this.isDirectory = !this.isDirectory;
    },
    checkSyncTips(item) {
      if (!item.configured) {
        this.$set(item, 'showSyncTips', true);
      }
    },
    closeSyncTips(item) {
      item.showSyncTips = false;
    },
    checkExportTips(item) {
      if (!item.has_children) {
        this.$set(item, 'showExportTips', true);
      }
    },
    closeExportTips(item) {
      item.showExportTips = false;
    },
    checkSwitchTips(item) {
      if (item.default) {
        this.$set(item, 'showSwitchTips', true);
      }
    },
    closeSwitchTips(item) {
      item.showSwitchTips = false;
    },
    checkDeleteTips(item) {
      if (item.default || item.activated || item.has_children) {
        this.$set(item, 'showDeleteTips', true);
      }
      if (item.activated === false) {
        this.$set(item, 'showDeleteTips', false);
      }
    },
    closeDeleteTips(item) {
      item.showDeleteTips = false;
    },
    handleDragNode(node) {
      this.$emit('switchNodeOrder', node);
    },
    deleteDisabled(item) {
      let status = false;
      if (item.default || item.activated || item.has_children) {
        status = true;
      }
      if (item.activated === false) {
        status = false;
      }
      return status;
    },
    checkAddTips(item) {
      console.log('item', item);
      if (item.level > 9) {
        this.$set(item, 'showLevelTips', true);
      }
    },
    closeAddTips(item) {
      item.showLevelTips = false;
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../../../scss/mixins/scroller.scss';
.organization-tree-wrapper {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;

  .icon {
    font-size: 18px;
    color: #C4C6CC;
    vertical-align: middle;
  }
  .icon-user-file-close-01 {
    color: #a3c5fd;
  }
  .hide-icon {
    width: 16px;
    height: 16px;
    display: inline-block;
    position: absolute;
    background: #F5F7FA;
    top: 8px;
    left: -18px;
  }
  .show-tag {
    padding: 0;
    width: 55px;
    text-align: center;
    vertical-align: bottom;
  }
  .top-tree {
    flex: 1;
    padding: 0 16px;
    @include scroller($backgroundColor: #e6e9ea, $width: 4px);
    overflow-x: hidden;
  }
  .bottom-tree {
    font-size: 14px;
    width: 100%;
    max-height: 440px;
    bottom: 0;
    background: #F5F7FA;
    .bottom-tree-header {
      padding: 0 12px;
      height: 40px;;
      line-height: 40px;
      border-top: 1px solid #DCDEE5;
      i {
        font-size: 22px;
        vertical-align: middle;
      }
      &:hover {
        cursor: pointer;
        background: #FAFBFD;
      }
    }
    .show-header {
      background: #FAFBFD;
      border-bottom: 1px solid #F0F1F5;
    }
    .bottom-tree-content {
      display: none;
    }
    ::v-deep .show-content {
      display: block;
      padding: 0 16px 40px;
      max-height: 400px;
      overflow-y: auto;
      @include scroller($backgroundColor: #e6e9ea, $width: 4px);
      overflow-x: hidden;
      .node-content.nodeTag {
        width: calc(100% - 65px);
      }
      .tree-drag-node {
        .tree-node {
          position: relative;
          padding-left: 3px;
          .node-title {
            width: calc(100% - 40px);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            vertical-align: middle;
          }
          .show-background {
            .option {
              display: flex;
              .icon-more {
                visibility: visible;
              }
              .bk-tag span {
                display: block;
                width: 55px;
              }
            }
          }
          .directory-warpper {
            .option {
              display: flex;
              .icon-more {
                visibility: hidden;
              }
              .bk-tag span {
                display: block;
                width: 55px;
              }
            }
          }
        }
        &:hover {
          & > .tree-node > .directory-warpper {
            .icon-more {
              visibility: visible;
            }
          }
        }
      }
      .leaf .tree-node {
        width: 100%;
      }
    }
  }
}
::v-deep .bk-tree {
  li {
    position: static;
  }
  .tree-drag-node {
    position: relative;
    .directory-warpper {
      position: relative;
      line-height: 32px;
      height: 32px;
      .option {
        align-items: center;
        position: absolute;
        top: 5px;
        right: 0;
        height: 20px;
        width: 20px;
        display: none;
      }
    }
    .show-background {
      position: relative;
      line-height: 32px;
      height: 32px;
      .active-icon {
        color: #4b8fff;
      }
      .option {
        align-items: center;
        position: absolute;
        top: 5px;
        right: 0;
        height: 20px;
        width: 20px;
      }
      .show-more {
        color: #4b8fff;
        display: block;
        font-size: 20px;
        cursor: pointer;
      }
    }
    &::before {
      content: "";
      display: block;
      width: 1000px;
      height: 37px;
      position: absolute;
      right: -30px;
      z-index: 0;
    }
    &:hover::before {
      background: #f0f1f5;
    }
    &:hover {
      .hide-icon {
        background: #f0f1f5;
        z-index: 1;
      }
    }

    .tree-expanded-icon {
      vertical-align: sub;
    }
    .tree-node {
      position: relative;
      width: calc(100% - 14px);
      padding-left: 3px;
      .node-title {
        width: calc(100% - 40px);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        vertical-align: middle;
      }
    }
    &:hover {
      & > .tree-node > .directory-warpper {
        .option {
          display: block;
          align-items: center;
          position: absolute;
          top: 5px;
          right: 0;
          height: 20px;
          width: 20px;
          color: #737987;
        }
        .icon-more {
          color: #737987;
          display: block;
          font-size: 20px;
          cursor: pointer;
        }
      }
    }
  }
  .leaf .tree-node {
    width: 100%;
  }
  .node-li {
    &::before {
      background: #E2EDFF;
    }
    &:hover::before {
      background: #E2EDFF;
    }
    .hide-icon {
      background: #E2EDFF;
      z-index: 1;
    }
    &:hover {
      .hide-icon {
        background: #E2EDFF;
        z-index: 1;
      }
    }
  }
}
.option {
  .dropdown-list {
    display: none;
  }

  > .show-dropdown-list {
    display: block;
    position: fixed;
    width: 180px;
    background: #fff;
    border-radius: 2px;
    border: 1px solid #dcdee5;
    box-shadow: 0 2px 6px rgba(51, 60, 72, .1);
    z-index: 1000000;
    margin-left: 20px;
    // 英文
    &.chang-en {
      .specific-menu {
        a {
          padding: 0 10px;
          white-space: normal;
          line-height: 28px;
        }

        .tooltip-content {
          width: 300px;
        }
      }
    }
    // 添加下级组织
    .specific-menu {
      position: relative;

      .tooltip-content {
        opacity: 0;
        position: absolute;
        left: 94px;
        top: 2px;
        padding: 0 5px;
        font-size: 12px;
        line-height: 32px;
        width: 160px;
        text-align: center;
        background: #333;
        color: #fff;
        border-radius: 3px;
        z-index: 2000;
        transition: all .3s ease;

        &.show-tooltip-content {
          opacity: 1;
        }

        .arrow {
          position: absolute;
          top: 50%;
          left: -1px;
          width: 8px;
          height: 8px;
          border-top: 1px solid #333;
          border-left: 1px solid #333;
          transform: rotate(-45deg) translateY(-50%);
          z-index: 10;
          background: #333;
        }
      }

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
