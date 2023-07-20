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
  <div class="user-table-wrapper">
    <bk-table
      ref="filterTable"
      ext-cls="user-table"
      :data="userMessage.userInforList"
      :pagination="pagination"
      :size="setting.size"
      @page-change="handlePageChange"
      @page-limit-change="handlePageLimitChange"
      @selection-change="handleSelectionChange"
      @row-click="handleRowClick">
      <template slot="empty">
        <EmptyComponent
          :is-data-empty="isTableDataEmpty"
          :is-search-empty="isEmptySearch"
          :is-data-error="isTableDataError"
          @handleEmpty="$emit('handleClickEmpty')"
          @handleUpdate="$emit('handleRefresh')" />
      </template>
      <bk-table-column type="selection" width="60"></bk-table-column>
      <template v-for="field in setting.selectedFields">
        <bk-table-column
          :label="field.name"
          :prop="field.key"
          :key="field.id"
          show-overflow-tooltip>
          <template slot-scope="props">
            <p>{{ getTableValue(props.row, field.key) || '--' }}</p>
          </template>
        </bk-table-column>
      </template>
      <bk-table-column :label="$t('操作')">
        <template slot-scope="props">
          <bk-button class="mr10" theme="primary" text>
            {{ $t('编辑') }}
          </bk-button>
          <bk-popover
            class="dot-menu" placement="bottom-start" theme="dot-menu light"
            trigger="mouseenter" :arrow="false" offset="15" :distance="0">
            <i class="icon bk-icon icon-more"></i>
            <ul class="dot-menu-list" slot="content">
              <li class="dot-menu-item" @click="changeStatus(props.row)">
                {{ props.row.status === 'DISABLED' ? $t('启用') : $t('禁用') }}
              </li>
              <li class="dot-menu-item" @click="$emit('deleteProfile', props.row)">{{ $t('删除') }}</li>
            </ul>
          </bk-popover>
        </template>
      </bk-table-column>
      <bk-table-column type="setting" :tippy-options="{ zIndex: 3000 }">
        <bk-table-setting-content
          :fields="setting.fields"
          :selected="setting.selectedFields"
          :max="setting.max"
          :size="setting.size"
          :limit="10"
          @setting-change="handleSettingChange">
        </bk-table-setting-content>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
import { dateConvert } from '@/common/util';
import EmptyComponent from '@/components/empty';
export default {
  components: { EmptyComponent },
  props: {
    fieldsList: {
      type: Array,
      required: true,
    },
    userMessage: {
      type: Object,
      default: {},
    },
    isEmptySearch: {
      type: Boolean,
      default: false,
    },
    // 控制设置所在组织、批量删除的显示
    isClick: {
      type: Boolean,
      default: false,
    },
    statusMap: {
      type: Object,
      default: {},
    },
    timerMap: {
      type: Array,
      required: true,
    },
    isTableDataError: {
      type: Boolean,
      default: false,
    },
    isTableDataEmpty: {
      type: Boolean,
      default: false,
    },
    pagination: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      // 固定展示字段
      fixedField: ['username', 'display_name', 'department_name', 'email'],
      setting: {
        max: 3,
        fields: [],
        selectedFields: [],
        size: 'small',
      },
      // 枚举字段
      enumField: [],
    };
  },
  watch: {
    fieldsList: {
      immediate: true,
      handler(val) {
        const list = [];
        this.enumField = [];
        val.forEach((item) => {
          this.$set(item, 'label', item.name);
          if (this.fixedField.includes(item.key)) {
            this.$set(item, 'disabled', true);
          }
          if (item.options.length > 0) {
            this.enumField.push(item.key);
          }
          if (item.visible) {
            list.push(item);
          }
        });
        this.setting.selectedFields = list;
        this.setting.fields = this.fieldsList;
      },
    },
    'setting.selectedFields': {
      immediate: true,
      deep: true,
      handler(value) {
        this.$emit('updateHeardList', value);
      },
    },
  },
  methods: {
    handleSettingChange({ fields, size }) {
      this.setting.size = size;
      this.setting.selectedFields = fields;
      const idList = fields.map(item => item.id);
      this.$emit('handleSetFieldList', idList);
    },
    handleClickEdit(row) {
      this.$emit('viewDetails', row);
    },
    handlePageLimitChange(limit) {
      this.$emit('handlePageLimitChange', limit);
    },
    handlePageChange(page) {
      this.$emit('handlePageChange', page);
    },
    handleSelectionChange(selection) {
      selection.length ? this.$emit('update:isClick', true) : this.$emit('update:isClick', false);
      this.$emit('isClickList', selection);
    },
    getTableValue(row, key) {
      let val = '';
      if (this.statusMap[key]) {
        val = this.$t(this.statusMap[key][row[key]]);
      } else if (key === 'department_name') {
        val = row[key].join(';');
      } else if (key === 'leader') {
        val = row[key].length ? row[key].map(item => item.username).join(';') : '--';
      } else if (this.timerMap.includes(key)) {
        val = dateConvert(row[key]);
      } else {
        val = row[key];
      }
      return val;
    },
    async changeStatus(row) {
      try {
        const isForbid = (row.status === 'DISABLED' || row.status === 'LOCKED');
        const status = isForbid ? 'NORMAL' : 'DISABLED';
        const res = await this.$store.dispatch('organization/patchProfile', {
          id: row.id,
          data: { status },
        });
        if (res.result === true) {
          row.status = status;
          const message = !isForbid ? this.$t('禁用') : this.$t('启用');
          this.messageSuccess(message + this.$t('成功'));
        }
      } catch (e) {
        console.warn(e);
      }
    },
    handleRowClick(row) {
      this.$emit('viewDetails', row);
    },
  },
};
</script>

<style lang="scss" scoped>
.icon-more {
  display: inline-block;
  font-size: 18px;
  border-radius: 50%;
  padding: 3px;
  color: #3a84ff;

  &:hover {
    cursor: pointer;
    background-color: rgba(235, 237, 240);
  }
}

.dot-menu {
  display: inline-block;
  vertical-align: middle;
}

.tippy-tooltip.dot-menu-theme {
  padding: 0;
}

.dot-menu-trigger {
  display: block;
  width: 30px;
  height: 30px;
  line-height: 30px;
  border-radius: 50%;
  text-align: center;
  font-size: 0;
  color: #979ba5;
  cursor: pointer;
}

.dot-menu-trigger:hover {
  color: #3a84ff;
  background-color: #ebecf0;
}

.dot-menu-trigger:before {
  content: "";
  display: inline-block;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background-color: currentColor;
  box-shadow: 0 -4px 0 currentColor, 0 4px 0 currentColor;
}

.dot-menu-list {
  margin: 0;
  padding: 5px 0;
  min-width: 50px;
  list-style: none;
}

.dot-menu-list .dot-menu-item {
  padding: 0 10px;
  font-size: 12px;
  line-height: 26px;
  cursor: pointer;

  &:hover {
    background-color: #eaf3ff;
    color: #3a84ff;
  }
}

.empty-title {
  color: #63656e;
}

::v-deep .user-table tr {
  cursor: pointer;
}
</style>
