<template>
  <div class="recycle-tab-wrapper">
    <div class="recycle-content-header">
      <bk-input
        ext-cls="header-right"
        clearable
        :placeholder="$t('搜索用户名、全名')"
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
        :data="profileList"
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
              <p>{{ props.row[field.id] || '--' }}</p>
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
  name: 'ProfileTab',
  components: { EmptyComponent },
  mixins: [mixin],
  data() {
    return {
      profileMap: [{
        id: 'username',
        label: this.$t('用户名'),
        disabled: true,
      }, {
        id: 'display_name',
        label: this.$t('全名'),
      }, {
        id: 'category_display_name',
        label: this.$t('所属目录'),
      }, {
        id: 'department_name',
        label: this.$t('所属组织'),
      }, {
        id: 'operator',
        label: this.$t('删除操作者'),
      }, {
        id: 'expires',
        label: this.$t('过期时间'),
        disabled: true,
      }],
      profileList: [],
    };
  },
  watch: {
    dataList: {
      immediate: true,
      deep: true,
      handler(val) {
        if (val) {
          this.profileList = [];
          val.forEach((item) => {
            const { category_display_name, expires, operator } = item;
            const { display_name, username } = item.profile;
            const departmentName = item.profile.department.map(key => key.name).join(';');
            this.profileList.push({
              category_display_name,
              expires,
              operator,
              display_name,
              username,
              department_name: departmentName,
            });
          });
          this.setting.fields = this.profileMap;
          this.setting.selectedFields = this.profileMap;
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
