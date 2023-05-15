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
  <div class="pull-user-wrapper">
    <bk-select
      searchable
      multiple
      display-tag
      v-model="tags"
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
        this.copyList.push(...res.data.results);
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
