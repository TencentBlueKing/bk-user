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
  <div class="input-text">
    <!-- eslint-disable vue/no-mutating-props -->
    <bk-select
      v-model="item.value"
      font-size="14"
      class="member-infor-king-select"
      :clearable="!item.require"
      :multiple="item.type === 'multi_enum'"
      :disabled="editStatus && !item.editable"
      :ext-cls="item.isError ? 'input-error' : ''"
      @change="changSelect">
      <bk-option
        v-for="(option, index) in item.options"
        :key="index"
        :id="option.id"
        :name="$t(statusMap[item.key][option.id])">
      </bk-option>
    </bk-select>
  </div>
</template>

<script>
export default {
  props: {
    item: {
      type: Object,
      required: true,
    },
    editStatus: {
      type: Boolean,
      required: true,
    },
    statusMap: {
      type: Object,
      default: {},
    },
  },
  methods: {
    changSelect() {
      window.changeInput = true;
    },
  },
};
</script>

<style lang="scss" scoped>
.input-text {
  position: relative;
  background-color: #fff;
  .input-error {
    border: 1px solid #ea3636;
  }
}

.select-text {
  display: block;
  padding: 0 30px 0 12px;

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
</style>
