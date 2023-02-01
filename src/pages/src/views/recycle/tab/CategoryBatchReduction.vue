<template>
  <div class="reduction-content">
    <div class="content-header">
      <bk-input
        :clearable="true"
        ext-cls="header-left"
        v-model="tableSearchKey"
        :placeholder="$t('搜索目录名')"
        :right-icon="'bk-icon icon-search'"
        @enter="handleSearch"
        @clear="handleClear"
      />
      <span class="header-right">
        <bk-button theme="default" @click="deleteError">{{ $t('一键移除错误项') }}</bk-button>
      </span>
    </div>
    <div class="content-table">
      <div class="table-title">
        <p class="title-left">
          {{ $t('共') }}
          <span>{{ dataList.length }}</span>
          {{ $t('个用户') }}
        </p>
        <p class="title-right">
          <span>{{ statusNumber.reducibleList.length }}</span>
          {{ $t('可还原，') }}
          <span>{{ statusNumber.errorList.length }}</span>
          {{ $t('校验错误') }}
        </p>
      </div>
      <bk-table :data="dataList">
        <bk-table-column :label="$t('目录名')" prop="category_display_name" />
        <bk-table-column
          :label="$t('还原校验')"
          prop="error_message"
          sortable
          :filters="statusFilters"
          :filter-method="statusFilterMethod"
          :filter-multiple="true">
          <template slot-scope="props">
            <p class="restore-check">
              <i :class="props.row.check_status ? 'success' : 'danger'" />
              {{ props.row.check_status ? $t('可还原') : $t('错误：') + props.row.error_message }}
            </p>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('操作')" width="80">
          <template slot-scope="props">
            <bk-button theme="primary" text @click="remove(props.row)">
              {{ $t('移除') }}
            </bk-button>
          </template>
        </bk-table-column>
      </bk-table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CategoryBatchReduction',
  props: {
    dataList: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      tableSearchKey: '',
      statusFilters: [],
      categoryList: [],
    };
  },
  computed: {
    statusNumber() {
      const reducibleList = [];
      const errorList = [];
      this.statusFilters = [];
      this.dataList.forEach((item) => {
        if (item.check_status) {
          reducibleList.push(item.check_status);
          this.statusFilters.push({ text: this.$t('可还原'), value: item.error_message });
        } else {
          errorList.push(item.check_status);
          this.statusFilters.push({ text: this.$t('错误：') + item.error_message, value: item.error_message });
        }
      });
      this.$emit('errorNumber', errorList.length);
      return { reducibleList, errorList };
    },
  },
  methods: {
    statusFilterMethod(value, row, column) {
      const property = column.property;
      return row[property] === value;
    },
    deleteError() {
      const list = this.dataList.filter(item => item.check_status);
      this.categoryList = this.categoryList.filter(item => item.check_status);
      this.$emit('updateSelectList', list);
    },
    remove(row) {
      const list = this.dataList.filter(item => item !== row);
      this.categoryList = this.categoryList.filter(item => item !== row);;
      this.$emit('updateSelectList', list);
    },
    handleSearch(value) {
      if (!value) {
        return this.$emit('updateSelectList', this.categoryList);
      }
      this.categoryList = this.dataList;
      const list = this.dataList.filter((item) => {
        return item.category_display_name.toUpperCase().indexOf(value.toUpperCase()) > -1;
      });
      this.$emit('updateSelectList', list);
    },
    handleClear(value) {
      const list = this.categoryList.filter((item) => {
        return item.category_display_name.toUpperCase().indexOf(value.toUpperCase()) > -1;
      });
      this.$emit('updateSelectList', list);
    },
  },
};
</script>

<style lang="scss" scoped>
@import './reduction.scss';
</style>
