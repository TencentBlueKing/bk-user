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
  <div class="pull-user-wrapper">
    <bk-tag-input
      ref="pullUser"
      v-model="tags"
      has-delete-icon
      :placeholder="$t('搜索用户名/账户')"
      :list="userList"
    ></bk-tag-input>
    <div class="input-loading" @click.stop v-show="basicLoading">
      <img src="../../../images/svg/loading.svg" alt="">
    </div>
  </div>
</template>

<script>
export default {
  props: {
    id: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      tags: [],
      userList: [],
      basicLoading: true,
    };
  },
  watch: {
    tags(newTags) {
      this.$emit('getPullUser', newTags);
    },
  },
  created() {
    this.getUserList();
  },
  methods: {
    // 获取已有人员列表
    async getUserList() {
      try {
        const res = await this.$store.dispatch('organization/getAllUser', { id: this.id });
        this.userList = res.data.map(v => ({
          id: v.id,
          username: v.username,
          display_name: v.display_name,
          name: v.display_name ? `${v.username}(${v.display_name})` : v.username,
        }));
        this.$nextTick(() => {
          this.$refs.pullUser.$el.click();
        });
      } catch (e) {
        console.warn(e);
      } finally {
        this.basicLoading = false;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.pull-user-wrapper {
  min-height: 32px;
  position: relative;
}

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
</style>
