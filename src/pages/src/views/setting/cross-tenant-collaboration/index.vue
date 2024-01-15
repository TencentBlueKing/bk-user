<template>
  <div v-bkloading="{ loading: isLoading, zIndex: 9 }" class="collaboration-wrapper">
    <bk-button class="add" theme="primary" @click="handleClick('add')">
      <i class="user-icon icon-add-2 mr8" />
      {{ $t('新建') }}
    </bk-button>
    <bk-table
      :data="tableData"
      :border="['outer']"
      :max-height="tableMaxHeight"
      show-overflow-tooltip>
      <template #empty>
        <Empty
          :is-data-empty="isDataEmpty"
          :is-data-error="isDataError"
          @handleUpdate="handleUpdate"
        />
      </template>
      <bk-table-column prop="name" :label="$t('策略名称')">
        <template #default="{ row }">
          <bk-button text theme="primary" @click="handleClick('view', row)">
            {{ row.name }}
          </bk-button>
        </template>
      </bk-table-column>
      <bk-table-column prop="target" :label="$t('目标租户')">
        <template #default="{ row }">
          <span>{{ row.target?.map(item => item.name).join(', ') || '--' }}</span>
        </template>
      </bk-table-column>
      <bk-table-column prop="operator" :label="$t('创建人')"></bk-table-column>
      <bk-table-column prop="created_at" :label="$t('创建时间')"></bk-table-column>
      <bk-table-column prop="enable" :label="$t('启/停')" :filter="{ list: statusFilters }">
        <template #default="{ row }">
          <bk-switcher
            theme="primary"
            size="small"
            v-model="row.enable"
            @change="handleChange(row)"
          />
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('操作')">
        <template #default="{ row }">
          <bk-button text theme="primary" class="mr8" @click="handleClick('edit', row)">
            {{ $t('编辑') }}
          </bk-button>
          <span v-bk-tooltips="{ content: $t('删除前必须停用该策略'), disabled: !row.enable }">
            <bk-button text theme="primary" :disabled="row.enable" @click="handleDelete(row)">
              {{ $t('删除') }}
            </bk-button>
          </span>
        </template>
      </bk-table-column>
    </bk-table>
    <bk-sideslider
      :ext-cls="['details-wrapper', { 'details-edit-wrapper': !isView }]"
      :width="960"
      :is-show="detailsConfig.isShow"
      :title="detailsConfig.title"
      :before-close="handleBeforeClose"
      quick-close>
      <template #header>
        <span>{{ detailsConfig.title }}</span>
        <div v-if="isView">
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
          @handleCancelEdit="handleCancelEdit"
        />
      </template>
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips, InfoBox } from 'bkui-vue';
import { computed, inject, onMounted, reactive, ref } from 'vue';

import OperationDetails from './OperationDetails.vue';
import ViewDetails from './ViewDetails.vue';

import Empty from '@/components/Empty.vue';
import { useTableMaxHeight } from '@/hooks';
import { t } from '@/language/index';
import { useMainViewStore } from '@/store';

const store = useMainViewStore();
store.customBreadcrumbs = false;
const tableMaxHeight = useTableMaxHeight(202);
const editLeaveBefore = inject('editLeaveBefore');
const isLoading = ref(false);
const tableData = ref([]);
const isDataEmpty = ref(false);
const isDataError = ref(false);

onMounted(() => {
  isLoading.value = true;
  isDataEmpty.value = false;
  isDataError.value = false;
  setTimeout(() => {
    tableData.value = getTableData();
    if (tableData.value.length === 0) {
      isDataEmpty.value = true;
    }
    isLoading.value = false;
  }, 3000);
});

const getTableData = () => [
  {
    name: '腾讯公司协同1',
    target: [
      { id: 141456745634, name: '腾讯科技深圳总公司' },
      { id: 24546732, name: '嘉为科技' },
      { id: 234645753873, name: '联通总公司' },
      { id: 23468888, name: '移动苏州分公司' },
    ],
    operator: 'admin',
    created_at: '2021-01-01',
    enable: false,
  },
  {
    name: '腾讯公司协同2',
    target: [
      { id: 141456745634, name: '腾讯科技深圳总公司' },
      { id: 24546732, name: '嘉为科技' },
      { id: 234645753873, name: '联通总公司' },
    ],
    operator: 'admin',
    created_at: '2021-01-01',
    enable: true,
  },
  {
    name: '腾讯公司协同3',
    target: [
      { id: 141456745634, name: '腾讯科技深圳总公司' },
      { id: 24546732, name: '嘉为科技' },
    ],
    operator: 'admin',
    created_at: '2021-01-01',
    enable: true,
  },
];

const statusFilters = [
  { text: t('启用'), value: true },
  { text: t('停用'), value: false },
];

const handleDelete = (row) => {
  InfoBox({
    title: t('是否删除当前协同？'),
    subTitle: t('删除后，目标租户的用户数据也会同步删除'),
    onConfirm() {
      console.log('删除成功', row);
    },
  });
};

const detailsConfig = reactive({
  isShow: false,
  title: '',
  type: '',
  data: {
    name: 'name',
    tenant_id: '',
    tenant_name: '',
    methods: 'organization',
    sync_type: 'all',
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
    detailsConfig.isShow = false;
  } else {
    detailsConfig.isShow = false;
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
};
</script>

<style lang="less" scoped>
.collaboration-wrapper {
  height: calc(100vh - 104px);
  padding: 24px;

  .add {
    margin-bottom: 16px;
  }
}

.details-wrapper {
  :deep(.bk-sideslider-title) {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px 0 50px !important;

    .bk-button {
      padding: 5px 17px !important;
    }
  }
}

.details-edit-wrapper {
  :deep(.bk-modal-content) {
    height: calc(100vh - 52px);
    background: #f5f7fa;

    &::-webkit-scrollbar {
      width: 4px;
      background-color: transparent;
    }

    &::-webkit-scrollbar-thumb {
      background-color: #dcdee5;
      border-radius: 4px;
    }
  }
}
</style>
