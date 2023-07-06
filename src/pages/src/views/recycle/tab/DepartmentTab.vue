<template>
  <div class="recycle-tab-wrapper">
    <div class="recycle-content-header">
      <bk-input
        ext-cls="header-right"
        clearable
        :placeholder="$t('搜索组织名')"
        :right-icon="'bk-icon icon-search'"
        v-model="tableSearchKey"
        @enter="handleEnter"
        @clear="handleClear">
      </bk-input>
    </div>
    <div class="recycle-content-table">
      <bk-table
        ref="table"
        ext-cls="user-table"
        :data="departmentList"
        :pagination="pagination"
        :size="setting.size"
        @page-change="handlePageChange"
        @page-limit-change="handlePageLimitChange"
      >
        <template slot="empty">
          <EmptyComponent
            :is-data-empty="isDataEmpty"
            :is-search-empty="isSearchEmpty"
            :is-data-error="isDataError"
            @handleEmpty="handleClear"
            @handleUpdate="handleEnter" />
        </template>
        <template v-for="field in setting.selectedFields">
          <bk-table-column
            v-if="field.id !== 'expires'"
            :label="field.label"
            :prop="field.id"
            :key="field.id"
            show-overflow-tooltip>
            <template slot-scope="props">
              <p>{{ props.row[field.id] === '' ? '--' : props.row[field.id]}}</p>
            </template>
          </bk-table-column>
          <bk-table-column
            v-else
            :label="field.label"
            :prop="field.id"
            :key="field.id"
            show-overflow-tooltip
            sortable>
            <template slot-scope="props">
              <p>{{ props.row.expires }}&nbsp;{{ $t('天后') }}</p>
            </template>
          </bk-table-column>
        </template>
        <bk-table-column type="setting" :tippy-options="{ zIndex: 3000 }">
          <bk-table-setting-content
            :fields="setting.fields"
            :selected="setting.selectedFields"
            :max="setting.max"
            :size="setting.size"
            @setting-change="handleSettingChange"
          >
          </bk-table-setting-content>
        </bk-table-column>
      </bk-table>
    </div>
  </div>
</template>

<script>
import mixin from './mixin';
import EmptyComponent from '@/components/empty';
export default {
  name: 'DepartmentTab',
  components: { EmptyComponent },
  mixins: [mixin],
  data() {
    return {
      departmentMap: [{
        id: 'department_name',
        label: this.$t('组织名'),
        disabled: true,
      }, {
        id: 'category_display_name',
        label: this.$t('所属目录'),
      }, {
        id: 'parent_name',
        label: this.$t('所属父组织'),
      }, {
        id: 'children_count',
        label: this.$t('子组织数'),
      }, {
        id: 'profile_count',
        label: this.$t('用户数'),
      }, {
        id: 'operator',
        label: this.$t('删除操作者'),
      }, {
        id: 'expires',
        label: this.$t('过期时间'),
        disabled: true,
      }],
      departmentList: [],
    };
  },
  watch: {
    dataList: {
      immediate: true,
      handler(val) {
        if (val) {
          this.departmentList = [];
          val.forEach((item) => {
            const { category_display_name, expires, operator, profile_count } = item;
            const { children_count, name, parent_name } = item.department;
            this.departmentList.push({
              category_display_name,
              expires,
              operator,
              profile_count,
              children_count,
              department_name: name,
              parent_name,
            });
          });
          this.setting.fields = this.departmentMap;
          this.setting.selectedFields = this.departmentMap;
          this.$nextTick(() => {
            this.$refs.table.sort('expires', 'ascending');
          });
        }
      },
    },
  },
};
</script>

<style lang="scss" scoped>
@import './tab.scss';
</style>
