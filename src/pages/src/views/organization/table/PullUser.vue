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
    <bk-select
      searchable
      multiple
      display-tag
      v-model="tags"
      :remote-method="selectData"
      @toggle="handleBranchToggle"
      ext-popover-cls="scrollview"
      :scroll-height="188">
      <bk-option
        v-for="option in userList"
        :key="option.id"
        :id="option.id"
        :name="option.username">
      </bk-option>
    </bk-select>
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
      searchValue: '',
      paginationConfig: {
        current: 1,
        count: 1,
        limit: 10,
      },
      timer: null,
      copyList: [],
    };
  },
  watch: {
    tags(newTags) {
      this.$emit('getPullUser', newTags);
    },
  },
  created() {
    // 进入页面获取数据
    this.searchValue = '';
    this.paginationConfig.current = 1;
    this.initRtxList(this.searchValue, this.paginationConfig.current);
  },
  methods: {
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
    async initRtxList(searchValue, curPage) {
      try {
        const params = {
          id: this.id,
          pageSize: this.paginationConfig.limit,
          page: curPage,
          keyword: searchValue,
        };
        this.showLeaderLoading = true;
        const res = await this.$store.dispatch('organization/getSupOrganization', params);
        this.paginationConfig.count = res.data.count;
        this.copyList.push(...res.data.data);
        this.userList = this.copyList.filter(item => item.username);
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
