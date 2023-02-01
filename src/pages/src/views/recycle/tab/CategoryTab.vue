<template>
  <div class="recycle-tab-wrapper">
    <div class="recycle-content-header">
      <div class="header-left">
        <bk-button
          theme="primary"
          class="mr8"
          :disabled="isDisabled"
          @click="handleBatchReduction">
          {{ $t('还原') }}
        </bk-button>
        <bk-button
          theme="default"
          :disabled="isDisabled"
          @click="handleBatchDelete">
          {{ $t('永久删除') }}
        </bk-button>
      </div>
      <bk-input
        ext-cls="header-right"
        clearable
        :placeholder="$t('搜索目录名、登录域')"
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
        :data="categoryList"
        :pagination="pagination"
        @select="handleSelect"
        @selection-change="handleSelectionChange"
        @page-change="handlePageChange"
        @page-limit-change="handlePageLimitChange"
      >
        <template slot="empty">
          <bk-exception type="empty" scene="part">
            <p class="empty-title">{{ $t('暂无数据') }}</p>
          </bk-exception>
        </template>
        <bk-table-column type="selection" width="60"></bk-table-column>
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
        <bk-table-column :label="$t('操作')">
          <div slot-scope="props" style="display: flex; flex-wrap: wrap;">
            <bk-button
              class="mr10"
              theme="primary"
              text
              @click="handleReduction(props.row)">
              {{ $t('还原') }}
            </bk-button>
            <bk-button
              theme="primary"
              text
              @click="handleDelete(props.row)">
              {{ $t('永久删除') }}
            </bk-button>
          </div>
        </bk-table-column>
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
    <!-- 永久删除 -->
    <bk-dialog
      ext-cls="delete-dialog-wrapper"
      v-model="deleteDialog.isShow"
      :title="deleteDialog.title"
      :header-position="deleteDialog.headerPosition"
      :width="deleteDialog.width"
      :loading="deleteDialog.loading">
      <div class="delete-content">
        <p>{{ $t('该操作会彻底清理当前目录数据，包括目录下的的所有用户数据及相关配置，永久无法恢复，请谨慎操作。') }}</p>
        <p>{{ $t('如需继续操作，请输入【确认删除】进行二次验证：') }}</p>
        <bk-input :placeholder="$t('请输入【确认删除】进行确认')" style="margin-top: 8px;" v-model="deleteText" />
      </div>
      <div slot="footer">
        <bk-button theme="primary" :disabled="deleteText !== '确认删除'" @click="confirmDelete">{{ $t('确认') }}</bk-button>
        <bk-button theme="default" @click="deleteDialog.isShow = false">{{ $t('取消') }}</bk-button>
      </div>
    </bk-dialog>
    <!-- 还原预览 -->
    <bk-sideslider
      ext-cls="reduction-wrapper"
      :width="960"
      :is-show.sync="reductionSetting.isShow">
      <div slot="header">{{ reductionSetting.title }}</div>
      <div slot="content">
        <!-- 批量预览 -->
        <CategoryBatchReduction
          v-if="isCategoryBatchReduction"
          :data-list="activeList"
          @updateSelectList="updateSelectList"
          @errorNumber="handleErrorNumber " />
        <CategoryReduction
          v-if="isCategoryReduction"
          :selected-list="selectedList"
          @remove="remove" />
        <div style="margin-top: 32px;">
          <bk-popover :disabled="!isError" :content="$t('请先处理错误项')">
            <bk-button :disabled="isError" theme="primary">{{ $t('执行还原') }}</bk-button>
          </bk-popover>
          <bk-button theme="default" @click="reductionSetting.isShow = false">{{ $t('取消') }}</bk-button>
        </div>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
import CategoryBatchReduction from './CategoryBatchReduction.vue';
import CategoryReduction from './CategoryReduction.vue';
import mixin from './mixin';
export default {
  name: 'CategoryTab',
  components: {
    CategoryBatchReduction,
    CategoryReduction,
  },
  mixins: [mixin],
  data() {
    return {
      deleteDialog: {
        isShow: false,
        loading: false,
        width: 480,
        headerPosition: 'left',
        title: this.$t('确认要永久删除当前目录？'),
      },
      reductionSetting: {
        isShow: false,
        title: this.$t('目录还原预览'),
      },
      isCategoryBatchReduction: false,
      isCategoryReduction: false,
      categoryMap: [{
        id: 'display_name',
        label: this.$t('目录名'),
        disabled: true,
      }, {
        id: 'domain',
        label: this.$t('登录域'),
      }, {
        id: 'type',
        label: this.$t('类型'),
      }, {
        id: 'department_count',
        label: this.$t('组织数'),
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
      categoryList: [],
      activeList: [{
        category_id: 14,
        category_display_name: 'testmad',
        check_status: true,
        error_message: '',
      }, {
        category_id: 15,
        category_display_name: 'testldap',
        check_status: false,
        error_message: '存在相同 ldap 连接域',
      }, {
        category_id: 16,
        category_display_name: 'testldap',
        check_status: false,
        error_message: '存在同名目录',
      }],
    };
  },
  watch: {
    dataList: {
      immediate: true,
      deep: true,
      handler(val) {
        if (val) {
          this.categoryList = [];
          val.forEach((item) => {
            const { department_count, expires, operator, profile_count } = item;
            const { display_name, domain, type, id } = item.category;
            this.categoryList.push({
              department_count,
              expires,
              operator,
              profile_count,
              display_name,
              domain,
              type,
              id,
            });
          });
          this.setting.fields = this.categoryMap;
          this.setting.selectedFields = this.categoryMap;
          this.$nextTick(() => {
            this.$refs.table.sort('expires', 'ascending');
          });
        }
      },
    },
  },
  methods: {
    // 批量还原
    handleBatchReduction() {
      // const ids = this.batchSelectedList.map(item => item.id);
      // console.log('ids', ids);
      // const data = {
      //   deleted_category_ids: this.batchSelectedList.map(item => item.id),
      // };
      // this.$store.dispatch('setting/categoriesCheck', { data }).then((res) => {
      //   console.log('res', res);
      // });
      this.isCategoryBatchReduction = true;
      this.isCategoryReduction = false;
      this.reductionSetting.isShow = true;
    },
    // 还原
    handleReduction(row) {
      this.selectedList = [row];
      this.isCategoryBatchReduction = false;
      this.isCategoryReduction = true;
      this.reductionSetting.isShow = true;
    },
    remove() {
      this.selectedList = [];
    },
  },
};
</script>

<style lang="scss" scoped>
@import './tab.scss';
</style>
