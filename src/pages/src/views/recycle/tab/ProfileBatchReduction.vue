<template>
  <div class="reduction-content">
    <div class="content-header">
      <bk-search-select
        ext-cls="header-left"
        :placeholder="$t('搜索用户名、所属组织')"
        :data="searchFilterList"
        :show-condition="false"
        v-model="tableSearchKey"
      />
      <span class="header-right">
        <bk-popover :disabled="popover.disabled" :content="popover.content">
          <bk-button theme="default" :disabled="isDisabled">{{ $t('批量重新分配') }}</bk-button>
        </bk-popover>
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
      <bk-table
        :data="dataList"
        @select="handleSelect"
        @selection-change="handleSelectionChange">
        <bk-table-column type="selection" width="60"></bk-table-column>
        <bk-table-column :label="$t('用户名')" prop="username" />
        <bk-table-column :label="$t('所属目录')" prop="category_display_name" />
        <bk-table-column :label="$t('所属组织')">
          <template slot-scope="props">
            <p>{{ props.row.department_name || '--' }}</p>
          </template>
        </bk-table-column>
        <bk-table-column
          ref="table"
          :label="$t('还原校验')"
          sortable
          :filters="statusFilters"
          :filter-method="statusFilterMethod"
          :filter-multiple="true">
          <template slot-scope="props">
            <p class="restore-check" v-if="departmentName === ''">
              <i :class="props.row.status ? 'success' : 'danger'" />
              {{ props.row.status ? $t('可还原') : $t('错误：原组织已不存在，') }}
              <span v-if="!props.row.status" @click="handleClickAllocation(props.row)">{{ $t('重新分配') }}</span>
            </p>
            <p class="restore-check" v-else>
              <i class="success" />{{ $t('重新分配至：') }}
              {{ departmentName }}
              <span v-if="!props.row.status" @click="handleClickAllocation(props.row)">{{ $t('调整') }}</span>
            </p>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('操作')" width="60">
          <template slot-scope="props">
            <bk-button theme="primary" text @click="remove(props.row)">
              {{ $t('移除') }}
            </bk-button>
          </template>
        </bk-table-column>
      </bk-table>
    </div>
    <!-- 重新分配组织 -->
    <bk-dialog
      width="721"
      class="king-dialog department-dialog"
      header-position="left"
      :auto-close="false"
      :title="$t('重新分配')"
      v-model="isShowSetDepartments"
      @confirm="selectDeConfirmFn"
      @cancel="isShowSetDepartments = false">
      <div class="select-department-wrapper clearfix">
        <SetDepartment
          v-if="isShowSetDepartments"
          :current-category-id="currentCategoryId"
          :initial-departments="initialDepartments"
          @getDepartments="getDepartments" />
      </div>
    </bk-dialog>
  </div>
</template>

<script>
import SetDepartment from '@/components/organization/SetDepartment.vue';
export default {
  name: 'ProfileBatchReduction',
  components: {
    SetDepartment,
  },
  props: {
    dataList: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      searchFilterList: [{
        id: 'username',
        name: '用户名',
      }, {
        id: 'department',
        name: '所属组织',
      }],
      tableSearchKey: [],
      isDisabled: true,
      selectedList: [],
      batchSelectedList: [],
      popover: {
        content: this.$t('原目录不存在用户，无法重新分配'),
        disabled: true,
      },
      isShowSetDepartments: false,
      currentCategoryId: 1,
      initialDepartments: [],
      getSelectedDepartments: [],
      // 选中列表
      isCheckList: [],
      // 重新分配组织
      departmentName: '',
      statusFilters: [{ text: '正常', value: '正常' }, { text: '创建中', value: '创建中' }],
    };
  },
  computed: {
    statusNumber() {
      const reducibleList = [];
      const errorList = [];
      this.dataList.forEach((item) => {
        if (item.status) {
          reducibleList.push(item.status);
        } else {
          errorList.push(item.status);
        }
      });
      this.$emit('errorNumber', errorList.length);
      return { reducibleList, errorList };
    },
  },
  watch: {
    batchSelectedList(val) {
      const list = [];
      val.map((item) => {
        if (!item.status) {
          list.push(item);
        }
      });
      if (list.length > 0) {
        this.popover.disabled = false;
        this.isDisabled = true;
      } else {
        this.isDisabled = val.length === 0;
        this.popover.disabled = true;
      }
    },
  },
  methods: {
    statusFilterMethod(value, row, column) {
      const property = column.property;
      return row[property] === value;
    },
    handleSelect(selection) {
      this.batchSelectedList = selection;
    },
    handleSelectionChange(selection) {
      this.batchSelectedList = selection;
    },
    deleteError() {
      this.dataList.map((item) => {
        if (!item.status) {
          this.$emit('updateSelectList', item);
        }
      });
    },
    remove(row) {
      this.$emit('updateSelectList', row);
    },
    async handleClickAllocation(row) {
      console.log('row', row);
      if (this.getSelectedDepartments.length === 1) {
        this.initialDepartments = this.getSelectedDepartments;
      } else {
        this.initialDepartments = [];
      }
      this.isShowSetDepartments = true;
    },
    // 设置所在组织拿到的组织列表
    getDepartments(val) {
      this.getSelectedDepartments = val;
    },
    // 确定 设置所在组织
    async selectDeConfirmFn() {
      if (!this.getSelectedDepartments.length) {
        this.$bkMessage({
          message: this.$t('请选择组织'),
          theme: 'warning',
        });
        return;
      }
      this.departmentName = this.getSelectedDepartments.map(item => item.name).join(';');
      this.isShowSetDepartments = false;
      this.$bkMessage({
        message: this.$t('设置成功'),
        theme: 'success',
      });
    },
  },
};
</script>

<style lang="scss" scoped>
@import './reduction.scss';
</style>
