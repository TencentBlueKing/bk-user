<template>
  <div class="recycle-tab-wrapper">
    <div class="recycle-content-header">
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
        <bk-button theme="primary" :disabled="deleteText !== $t('确认删除')" @click="confirmDelete">
          {{ $t('确认') }}
        </bk-button>
        <bk-button theme="default" @click="deleteDialog.isShow = false">{{ $t('取消') }}</bk-button>
      </div>
    </bk-dialog>
    <!-- 还原 -->
    <bk-dialog
      class="reduction-dialog-wrapper"
      v-model="reductionDialog.isShow"
      :title="reductionDialog.title"
      :header-position="reductionDialog.headerPosition"
      :width="reductionDialog.width">
      <div v-if="clashText.length > 0">
        <p v-for="(item, index) in clashText" :key="index">
          <i class="danger" />
          <span>{{ $t('错误：') + item }}</span>
        </p>
      </div>
      <div v-else>
        <i class="success" />
        <span>{{ $t('可还原') }}</span>
      </div>
      <div slot="footer">
        <bk-button theme="primary" :disabled="clashText.length > 0" @click="confirmReduction">{{ $t('确认') }}</bk-button>
        <bk-button theme="default" @click="reductionDialog.isShow = false">{{ $t('取消') }}</bk-button>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
import mixin from './mixin';
import EmptyComponent from '@/components/empty';
export default {
  name: 'CategoryTab',
  components: { EmptyComponent },
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
      reductionDialog: {
        isShow: false,
        width: 480,
        headerPosition: 'left',
        title: this.$t('确认要还原当前目录？'),
      },
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
      clashText: [],
      categoryId: null,
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
    // 还原
    async handleReduction(row) {
      try {
        this.categoryId = row.id;
        this.reductionDialog.isShow = true;
        const res = await this.$store.dispatch('setting/categoriesCheck', {
          category_id: this.categoryId,
        });
        this.clashText = res.data;
      } catch (e) {
        console.warn(e);
      }
    },
    confirmReduction() {
      this.$store.dispatch('setting/categoriesRevert', {
        category_id: this.categoryId,
      }).then((res) => {
        if (res.result) {
          this.reductionDialog.isShow = false;
          this.messageSuccess(this.$t('目录还原成功'));
          this.$emit('updateList');
        }
      })
        .catch((e) => {
          console.warn(e);
          this.reductionDialog.isShow = false;
        });
    },
    // 永久删除
    handleDelete(row) {
      this.categoryId = row.id;
      this.deleteDialog.isShow = true;
      this.deleteText = '';
    },
    confirmDelete() {
      this.$store.dispatch('setting/categoriesHardDelete', {
        category_id: this.categoryId,
      }).then((res) => {
        if (res.result) {
          this.deleteDialog.isShow = false;
          this.messageSuccess(this.$t('目录删除成功'));
          this.$emit('updateList');
        }
      })
        .catch((e) => {
          console.warn(e);
          this.deleteDialog.isShow = false;
        });
    },
  },
};
</script>

<style lang="scss" scoped>
@import './tab.scss';
.reduction-dialog-wrapper {
  i {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 5px;
  }
  .success {
    background: #E5F6EA;
    border: 1px solid #3FC06D;
  }
  .danger {
    background: #FFE6E6;
    border: 1px solid #EA3636;
  }
}
</style>
