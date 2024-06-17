<template>
  <div
    v-bkloading="{ loading: isLoading, zIndex: 9 }"
    :class="['collaboration-wrapper user-scroll-y', { 'has-alert': userStore.showAlert }]">
    <header>
      <bk-button theme="primary" @click="handleClick('add')">
        <i class="user-icon icon-add-2 mr8" />
        {{ $t('新建') }}
      </bk-button>
      <bk-input
        class="header-right"
        v-model="search"
        type="search"
        clearable
        :placeholder="$t('搜索策略名称')"
      />
    </header>
    <bk-table
      :data="searchList"
      :border="['outer']"
      :max-height="tableMaxHeight"
      show-overflow-tooltip
      @column-filter="handleFilter"
    >
      <template #empty>
        <Empty
          :is-data-empty="isDataEmpty"
          :is-search-empty="isSearchEmpty"
          :is-data-error="isDataError"
          @handle-empty="search = ''"
          @handle-update="fetchToStrategies"
        />
      </template>
      <bk-table-column prop="name" :label="$t('策略名称')">
        <template #default="{ row }">
          <bk-button text theme="primary" @click="handleClick('view', row)">
            {{ row.name }}
          </bk-button>
        </template>
      </bk-table-column>
      <bk-table-column prop="target_tenant_id" :label="$t('目标租户')" />
      <bk-table-column prop="creator" :label="$t('创建人')" />
      <bk-table-column prop="created_at" :label="$t('创建时间')"></bk-table-column>
      <bk-table-column
        prop="source_status" :label="$t('启/停')">
        <!-- :filter="{ list: statusFilters }"> -->
        <template #default="{ row }">
          <bk-switcher
            theme="primary"
            size="small"
            :value="row.source_status === 'enabled'"
            @change="handleChange(row)"
          />
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('操作')">
        <template #default="{ row }">
          <bk-button text theme="primary" class="mr8" @click="handleClick('edit', row)">
            {{ $t('编辑') }}
          </bk-button>
          <span v-bk-tooltips="{ content: $t('删除前必须停用该策略'), disabled: row.source_status === 'disabled' }">
            <bk-button text theme="primary" :disabled="row.source_status === 'enabled'" @click="handleDelete(row.id)">
              {{ $t('删除') }}
            </bk-button>
          </span>
        </template>
      </bk-table-column>
    </bk-table>
    <bk-sideslider
      :class="['details-wrapper', { 'details-edit-wrapper': !isView }]"
      :width="960"
      :is-show="detailsConfig.isShow"
      :title="detailsConfig.title"
      :before-close="handleBeforeClose"
      render-directive="if"
      quick-close>
      <template #header>
        <span>{{ detailsConfig.title }}</span>
        <div v-if="isView" class="mr-[24px]">
          <bk-button
            outline
            theme="primary"
            @click="handleClick('edit', detailsConfig.data)"
          >{{ $t('编辑') }}</bk-button
          >
        </div>
      </template>
      <template #default>
        <ViewDetails v-if="isView" :data="detailsConfig.data" />
        <OperationDetails
          v-else
          :config="detailsConfig"
          @handle-cancel-edit="handleCancelEdit"
          @update-list="updateList"
        />
      </template>
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips, InfoBox, Message } from 'bkui-vue';
import { computed, defineProps, inject, reactive, ref, watch, watchEffect } from 'vue';

import OperationDetails from './OperationDetails.vue';
import ViewDetails from './ViewDetails.vue';

import Empty from '@/components/Empty.vue';
import { useTableMaxHeight } from '@/hooks';
import { deleteToStrategies, getToStrategies, putToStrategiesStatus } from '@/http';
import { t } from '@/language/index';
import { useMainViewStore, useUser } from '@/store';

const props = defineProps({
  active: {
    type: String,
    default: '',
  },
});
const store = useMainViewStore();
store.customBreadcrumbs = false;
const userStore = useUser();

const tableMaxHeight = useTableMaxHeight(202);
const editLeaveBefore = inject('editLeaveBefore');
const isLoading = ref(false);
const tableData = ref([]);
const isDataEmpty = ref(false);
const isDataError = ref(false);
const isSearchEmpty = ref(false);
const search = ref('');

// 获取协同策略列表
const fetchToStrategies = async () => {
  try {
    isLoading.value = true;
    isDataEmpty.value = false;
    isDataError.value = false;
    isSearchEmpty.value = false;
    const res = await getToStrategies();
    tableData.value = res?.data;
    if (tableData.value.length === 0) {
      isDataEmpty.value = true;
    }
  } catch (error) {
    isDataError.value = true;
  } finally {
    isLoading.value = false;
  }
};

watchEffect(() => {
  if (props.active === 'local') {
    fetchToStrategies();
  }
});

const statusFilters = [
  { text: t('启用'), value: 'enabled' },
  { text: t('停用'), value: 'disabled' },
];

const handleFilter = ({ checked }) => {
  if (checked.length === 0) return isDataEmpty.value = false;
  isDataEmpty.value = !tableData.value.some(item => checked.includes(item.status));
};

// 搜索协同列表
const searchList = computed(() => tableData.value.filter(item => !search.value || item.name.includes(search.value)));

watch(() => search.value, (val) => {
  isSearchEmpty.value = val && !searchList.value.length;
});

const handleChange = (row: any) => {
  putToStrategiesStatus(row.id).then((res) => {
    row.source_status = res?.data?.source_status;
  });
};

// 删除协同策略
const handleDelete = (id: number) => {
  InfoBox({
    title: t('是否删除当前协同？'),
    subTitle: t('删除后，目标租户的用户数据也会同步删除'),
    onConfirm: async () => {
      await deleteToStrategies(id);
      Message({ theme: 'success', message: t('删除成功') });
      fetchToStrategies();
    },
  });
};

const detailsConfig = reactive({
  isShow: false,
  title: '',
  type: '',
  data: {
    name: '',
    target_tenant_id: '',
    source_config: {
      organization_scope_type: 'all',
      organization_scope_config: {},
      field_scope_type: 'all',
      field_scope_config: {},
    },
  },
});

const enumData = {
  view: {
    title: t('协同策略详情'),
    type: 'view',
  },
  add: {
    title: t('新建协同策略'),
    type: 'add',
  },
  edit: {
    title: t('编辑协同策略'),
    type: 'edit',
  },
};

const isView = computed(() => detailsConfig.type === 'view');

watch(() => detailsConfig.isShow, (val) => {
  if (!val) {
    detailsConfig.data = {
      name: '',
      target_tenant_id: '',
      source_config: {
        organization_scope_type: 'all',
        organization_scope_config: {},
        field_scope_type: 'all',
        field_scope_config: {},
      },
    };
  }
});

const handleClick = (type: string, item?: any) => {
  if (type !== 'add') {
    detailsConfig.data = item;
  }
  detailsConfig.title = enumData[type].title;
  detailsConfig.type = enumData[type].type;
  detailsConfig.isShow = true;
};

const handleCancelEdit = () => {
  window.changeInput = false;
  if (detailsConfig.type === 'add') {
    detailsConfig.isShow = false;
  } else {
    detailsConfig.type = 'view';
    detailsConfig.title = t('协同策略详情');
  }
};

const handleBeforeClose = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
    detailsConfig.isShow = !enableLeave;
  } else {
    detailsConfig.isShow = false;
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
};

const updateList = () => {
  detailsConfig.isShow = false;
  window.changeInput = false;
  fetchToStrategies();
};
</script>

<style lang="less" scoped>
.has-alert {
  height: calc(100vh - 180px) !important;
}

.collaboration-wrapper {
  height: calc(100vh - 140px);
  padding: 24px;

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .header-right {
      width: 400px;
    }
  }
}

.details-wrapper {
  :deep(.bk-sideslider-title) {
    display: flex;
    justify-content: space-between;
    align-items: center;
    // padding: 0 24px 0 50px !important;

    .bk-button {
      padding: 5px 17px !important;
    }
  }
}

.details-edit-wrapper {
  :deep(.bk-modal-content) {
    height: calc(100vh - 52px) !important;
    background: #f5f7fa !important;

    // &::-webkit-scrollbar {
    //   width: 4px;
    //   background-color: transparent;
    // }

    // &::-webkit-scrollbar-thumb {
    //   background-color: #dcdee5;
    //   border-radius: 4px;
    // }
  }
}
</style>
