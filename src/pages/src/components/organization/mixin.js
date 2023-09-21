/**
* by making 蓝鲸智云-用户管理(Bk-User) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License");
* you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing,
* software distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and limitations under the License.
*/
/* eslint-disable no-useless-escape */
/* eslint-disable no-plusplus */
export default {
  data() {
    return {
      showImport: false,
      importId: '',
      importNode: {},
      // 不可用目录展示状态
      isDirectory: false,
    };
  },
  methods: {
    getAddOrganization(node) {
      let text = '';
      if (node.type === 'local') {
        text = this.$t('添加根组织');
      } else if (node.isLocalDepartment) {
        text = this.$t('添加下级组织');
      }
      return text;
    },
    stopBubbling(node) {
      if (this.isOperationConfig) {
        this.isOperationConfig = false;
      } else {
        window.event.cancelBubble = true;
        node.showOption = false;
      }
    },
    // 同步数据
    async syncCatalog(node) {
      if (!node.configured) return;
      try {
        this.stopBubbling(node);
        await this.$store.dispatch('catalog/ajaxSyncCatalog', { id: node.id });
        this.messageSuccess(this.$t('同步成功'));
      } catch (e) {
        console.warn(e);
      }
    },
    // 导出用户
    exportUser(node) {
      this.stopBubbling(node);
      if (!node.has_children) return;
      // 导出的下载链接
      let url = window.AJAX_URL;
      if (url.endsWith('/')) {
        // 去掉末尾的斜杠
        url = url.slice(0, url.length - 1);
      }
      if (!url.startsWith('http')) {
        // tips: 后端提供的 SITE_URL 需以 / 开头
        url = window.location.origin + url;
      }
      if (node.type) {
        url = `${url}/api/v1/web/categories/${this.currentCategoryId}/operations/export/?department_ids=${node.children.map(item => item.id).join(',')}`;
      }
      window.open(url);
    },
    // 导入用户
    importUser(node) {
      this.stopBubbling(node);
      this.importNode = node;
      this.importId = node.id;
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
      const uploadInfo = this.$refs.importUserRef.uploadInfo;
      formData.append('file', uploadInfo.fileInfo);
      formData.append('file_name', uploadInfo.name);
      formData.append('department_id', this.$refs.importUserRef.id);

      this.showImport = false;
      try {
        await this.$store.dispatch('catalog/ajaxImportUser', {
          id: this.importId,
          isOverwrite: uploadInfo.isOverwrite,
          data: formData,
        });
        this.$emit('handleClickTreeNode', this.importNode);
        this.messageSuccess(this.$t('同步成功'));
      } catch (e) {
        this.messageError(e);
      }
    },
    // 切换启停状态
    switchStatus(node) {
      this.stopBubbling(node);
      if (node.default) return;
      if (node.activated) {
        // 停用目录前需要确认
        this.$bkInfo({
          title: this.$t('确定停用该用户目录'),
          subTitle: this.$t('停用目录1') + node.display_name + this.$t('停用目录2'),
          confirmFn: this.confirmSwitchStatusSync.bind(this, node, false),
        });
      } else {
        // 激活目录
        this.confirmSwitchStatus(node, true);
      }
    },
    // 这里多一个步骤是为了避免 confirmFn 是 async 函数
    confirmSwitchStatusSync(node, activated) {
      this.confirmSwitchStatus(node, activated);
    },
    // 改变状态 启/停
    async confirmSwitchStatus(node, activated) {
      try {
        const res = await this.$store.dispatch('catalog/ajaxPatchCatalog', {
          id: node.id,
          data: { activated },
        });
        node.activated = res.data.activated;
        const msg = node.activated ? this.$t('启用成功') : this.$t('停用成功');
        this.isDirectory = true;
        this.messageSuccess(msg);
        this.$emit('updateAcitveNode');
      } catch (e) {
        console.warn(e);
      }
    },
  },
};
