<template>
  <div class="recycle-tab-wrapper">
    <div class="recycle-content-header">
      <div class="header-left">
        <bk-popover :disabled="false" :content="$t('暂不支持该操作')">
          <bk-button
            theme="primary"
            class="mr8"
            :disabled="true"
            @click="handleBatchReduction">
            {{ $t('还原') }}
          </bk-button>
          <bk-button
            theme="default"
            :disabled="true"
            @click="handleBatchDelete">
            {{ $t('永久删除') }}
          </bk-button>
        </bk-popover>
      </div>
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
        <bk-table-column :label="$t('操作')">
          <bk-popover slot-scope="props" :disabled="false" :content="$t('暂不支持该操作')">
            <bk-button
              class="mr10"
              theme="primary"
              text
              :disabled="true"
              @click="handleReduction(props.row)">
              {{ $t('还原') }}
            </bk-button>
            <bk-button
              theme="primary"
              text
              :disabled="true"
              @click="handleDelete">
              {{ $t('永久删除') }}
            </bk-button>
          </bk-popover>
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
        <p>{{ $t('该操作会彻底清理当前用户数据，永久无法恢复，请谨慎操作。') }}</p>
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
        <ProfileBatchReduction
          v-if="isProfileBatchReduction"
          :data-list="batchSelectedList"
          @updateSelectList="updateSelectList"
          @errorNumber="handleErrorNumber " />
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
import ProfileBatchReduction from './ProfileBatchReduction.vue';
import mixin from './mixin';
export default {
  name: 'ProfileTab',
  components: {
    ProfileBatchReduction,
  },
  mixins: [mixin],
  data() {
    return {
      deleteDialog: {
        isShow: false,
        loading: false,
        width: 480,
        headerPosition: 'left',
        title: this.$t('确认要永久删除当前用户？'),
      },
      reductionSetting: {
        isShow: false,
        title: this.$t('用户还原预览'),
      },
      isProfileBatchReduction: false,
      isProfileReduction: false,
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
  methods: {
    // 批量还原
    handleBatchReduction() {
      this.isProfileBatchReduction = true;
      this.reductionSetting.isShow = true;
    },
    // 还原
    handleReduction(row) {
      this.selectedList = [row];
      this.isProfileReduction = true;
      this.reductionSetting.isShow = true;
    },
  },
};
</script>

<style lang="scss" scoped>
@import './tab.scss';
</style>
