<template>
  <div class="reduction-content">
    <div class="content-header">
      <bk-search-select
        ext-cls="header-left"
        :placeholder="$t('搜索组织名、所属组织')"
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
        <bk-table-column :label="$t('组织名')" prop="department_name" />
        <bk-table-column :label="$t('所属目录')" prop="category_display_name" />
        <bk-table-column :label="$t('所属组织')">
          <template slot-scope="props">
            <p>{{ props.row.parent_name || '--' }}</p>
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
      width="480"
      header-position="left"
      :auto-close="false"
      :title="$t('重新分配父组织')"
      v-model="isShowSetDepartments"
      @confirm="selectDeConfirmFn"
      @cancel="isShowSetDepartments = false">
      <div class="select-department-wrapper clearfix">
        <bk-select
          ref="select"
          v-model="selectValue"
          :remote-method="searchSelect"
          :show-empty="false">
          <bk-tree
            ext-cls="tree-wrapper"
            :data="treeDataList"
            :node-key="'id'"
            :tpl="tpl"
            :show-icon="false"
            @on-expanded="handleClickToggle">
          </bk-tree>
        </bk-select>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
import mixin from '../../organization/mixin';
export default {
  name: 'DepartmentBatchReduction',
  mixins: [mixin],
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
      initialDepartments: [],
      // 组织
      selectValue: [],
      treeDataList: [],
      // 重新分配组织
      departmentName: '',
      statusFilters: [{ text: '正常', value: '正常' }, { text: '创建中', value: '创建中' }],
    };
  },
  computed: {
    statusNumber() {
      const reducibleList = [];
      const errorList = [];
      (this.dataList || []).forEach((item) => {
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
    tpl(node) {
      return <div class={node.showBackground ? 'show-background' : 'directory-warpper'}>
        {node.display_name ? <i class={['icon user-icon icon-root-node-i', { 'active-icon': node.showBackground }]} />
          : <i class={['icon icon-user-file-close-01', { 'active-icon': node.showBackground }]} />}
        <span class={node.showBackground ? 'node-title node-selected' : 'node-title'}
          domPropsInnerHTML={node.display_name || node.name}
          onClick={this.handleClickTreeNode.bind(this, node)} v-bk-overflow-tips></span>
      </div>;
    },
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
      try {
        console.log('row', row);
        this.isShowSetDepartments = true;
        await this.getTreeList();
      } catch (e) {
        console.warn(e);
      }
    },
    async getTreeList() {
      try {
        const res = await this.$store.dispatch('organization/getOrganizationTree');
        if (!res.data || !res.data.length) return;
        this.treeDataList = res.data;
        this.treeDataList.forEach((catalog) => {
          this.filterTreeData(catalog, this.treeDataList);
          catalog.children = catalog.departments;
          catalog.children.forEach((department) => {
            this.$set(department, 'category_id', catalog.id);
            this.filterTreeData(department, catalog, catalog.type === 'local');
          });
        });
        this.treeDataList[0] && (this.treeDataList[0].showChildren = true);
        // this.treeDataList[0].showBackground = true;
        // this.treeDataList[0].expanded = true;
      } catch (e) {
        console.warn(e);
      }
    },
    handleClickTreeNode(item) {
      this.handleClickToggle(item);
    },
    async handleClickToggle(item) {
      // 没有子节点，控制文件夹的开关样式
      if (item.has_children === false || (item.children && item.children.length)) {
        item.showChildren = !item.showChildren;
        return;
      }
      // 有子节点，但是还没加载 children 数据
      try {
        item.showLoading = true;
        const res = await this.$store.dispatch('organization/getDataById', { id: item.id });
        this.$set(item, 'children', res.data.children);
        item.children.forEach((element) => {
          this.filterTreeData(element, item, item.isLocalDepartment);
        });
        this.$set(item, 'showChildren', true);
      } catch (e) {
        console.warn(e);
      } finally {
        item.showLoading = false;
      }
    },
    // 搜索下拉框数据
    searchSelect(keyword) {
      this.$refs.tree && this.$refs.tree.filter(keyword);
    },
  },
};
</script>

<style lang="scss" scoped>
@import './reduction.scss';
</style>
