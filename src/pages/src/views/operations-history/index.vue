<template>
  <div class="h-[100vh]">
    <div class="grid place-items-center">
      <!-- 筛选表单 -->
      <Transition>
        <div
          v-if="!isFold.curFold"
          :class="['filter-operation-history-container', isFold.preFold ? 'overflow-hidden' : '']">
          <bk-form
            form-type="vertical"
            ref="formRef"
            :model="formData"
            class="w-full mt-[24px]">
            <bk-form-item class="inline-block ml-[24px]" :label="$t('操作人')">
              <UserSelector
                class="!w-[300px]"
                v-model:value="formData.creator"
                :multiple="false" />
            </bk-form-item>
            <bk-form-item class="inline-block ml-[20px]" :label="$t('操作对象')">
              <bk-select class="items-select" v-model="formData.object_type">
                <bk-option
                  v-for="item in curOperationType"
                  :key="item.key"
                  :id="item.key"
                  :name="item.label" />
              </bk-select>
            </bk-form-item>
            <bk-form-item class="inline-block ml-[20px]" :label="$t('操作类型')">
              <bk-select class="items-select" v-model="formData.operation">
                <bk-option
                  v-for="item in curOperationOptions"
                  :key="item.key"
                  :id="item.key"
                  :name="item.label" />
              </bk-select>
            </bk-form-item>
            <bk-form-item class="inline-block ml-[20px]" :label="$t('操作实例')">
              <bk-input class="items-input" clearable v-model="formData.object_name" />
            </bk-form-item>
            <bk-form-item class="inline-block ml-[24px]" :label="$t('操作时间')">
              <bk-date-picker
                class="items-picker"
                v-model="formData.operation_time"
                type="datetimerange" />
            </bk-form-item>
            <bk-form-item class="ml-[24px]">
              <bk-button
                class="w-[88px] h-[32px]"
                theme="primary"
                :loading="isLoading"
                @click="() => handleFetchAudit('search')"
              >
                {{ $t('查询') }}
              </bk-button>
              <bk-button
                class="w-[88px] h-[32px] ml-[8px]"
                @click="handleReset"
                :loading="isLoading"
              >
                {{ $t('重置') }}
              </bk-button>
            </bk-form-item>
          </bk-form>
        </div>
      </Transition>
      <!-- 折叠按钮 -->
      <div class="flex justify-center w-full h-[24px]">
        <div @mouseover="handleHoverFoldBtn" @mouseleave="handleLeaveFoldBtn" v-if="!isFold.curFold">
          <bk-button
            v-if="isHover" theme="primary"
            @click="toggleFold"
            @mousedown="togglePreFold"
            class="w-[120px] !h-[24px] text-bold !border-none">
            <i class="user-icon icon-angle-up text-[30px]"></i>
          </bk-button>
          <bk-button
            v-else
            @click="toggleFold"
            @mousedown="togglePreFold"
            class="w-[120px] !h-[24px] !bg-[#DCDEE5] !text-[#ffffff] text-bold !border-none">
            <i class="user-icon icon-angle-up text-[30px]"></i>
          </bk-button>
        </div>
        <div v-else>
          <bk-button
            theme="primary"
            @click="toggleFold"
            @mousedown="togglePreFold"
            class="w-[120px] !h-[24px] text-bold !border-none">
            <i class="user-icon icon-angle-down text-[30px]"></i>
          </bk-button>
        </div>
      </div>
      <!-- 展示列表 -->
      <div class="data-operation-history-container">
        <bk-table
          v-bkloading="{ loading: isLoading }"
          :pagination="pagination"
          remote-pagination
          :data="tableData"
          :settings="settings"
          class="operation-history-table"
          @page-limit-change="pageLimitChange"
          @page-value-change="pageCurrentChange"
          :show-overflow-tooltip="true"
          :max-height="curTableMaxHeight"
          :height="curTableHeight"
          :pagination-height="paginationHeight"
          :thead="{ height: headHeight }"
          :row-height="lineHeight"
          @setting-change="handleSettingChange"
          @column-sort="handleSortBy"
        >
          <template #empty>
            <Empty
              :is-data-empty="isDataEmpty"
              :is-search-empty="isEmptySearch"
              :is-data-error="isDataError"
              @handle-empty="handleReset"
              @handle-update="handleFetchAudit('search')"
            />
          </template>
          <bk-table-column :label="$t('操作类型')" prop="operation" width="100">
            <template #default="{ row }">
              <span>{{ getOperationLabel(row.operation) }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('操作对象')" prop="object_type" width="100">
            <template #default="{ row }">
              <span>{{ getOperationTypeLabel(row.object_type) }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('操作实例')" prop="object_name" width="100">
            <template #default="{ row }">
              <span>{{ row.object_name || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('操作人')" prop="creator" width="100">
            <template #default="{ row }">
              <bk-user-display-name :user-id="row.creator"></bk-user-display-name>
            </template>
          </bk-table-column>
          <bk-table-column
            :label="$t('操作时间')"
            :sort="sortConfig"
            prop="created_at"
            width="100">
            <template #default="{ row }">
              <span>{{ row.created_at || '--' }}</span>
            </template>
          </bk-table-column>
        </bk-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs';
import { computed, onMounted, reactive, ref, watch } from 'vue';

import { getCurrentOperationOptions, operationType } from './operations';

import Empty from '@/components/SearchEmpty.vue';
import UserSelector from '@/components/UserSelector.vue';
import { useTableMaxHeight } from '@/hooks';
import { getAudit } from '@/http/operationHistoryFiles';
import { t } from '@/language';


const isHover = ref(false);
const isFold = reactive({
  curFold: false,
  preFold: false,
});

const formRef = ref();
const isLoading = ref(false);
const tableData = ref([]);

// 固定表头行高分页器高度，便于切换行高时计算高度
const paginationHeight = 60;
const headHeight = 42;
const lineHeight = ref(42);
// 使用max-height来限制表格高度
const curTableMaxHeight = computed(() => {
  // header(52) + button-height(24) + margin-bottom(24) 固定表格最大高度，对当前高度进行响应式计算，纵享丝滑
  const tableMaxHeight = window.innerHeight - 100;
  // 计算当前分页下table高度
  const targetTableHeight = headHeight + lineHeight.value * pagination.limit + paginationHeight;
  // 若超出页面允许的最大高度，返回最大高度，否则返回数据铺满高度，防止出现空白区域未铺满数据的情况
  if (targetTableHeight < tableMaxHeight) return targetTableHeight;
  return tableMaxHeight;
});
// header(52) + form-height(248) + button-height(24) + margin-bottom(24)
const curRedundantHeight = computed(() => {
  const redundantHeight = {
    unfold: 348,
    fold: 100,
  };
  if (isFold.curFold) {
    return redundantHeight.fold;
  }
  return redundantHeight.unfold;
});
// table height继续采用响应式hook，用于处理window resize以及折叠功能高度的计算(curRedundantHeight is ref data)
const curTableHeight = useTableMaxHeight(curRedundantHeight);

// 更改表格设置时，更新当前行高
const handleSettingChange = (data: { height: number; }) => {
  lineHeight.value = data.height;
};

interface SearchFromData {
  creator: string,
  operation: string,
  object_type: string,
  object_name: string,
  operation_time: [string, string]
}

const formData = reactive<SearchFromData>({
  creator: '',  // 操作人
  operation: '', // 操作类型
  object_type: '', // 操作对象
  object_name: '', // 操作实例
  operation_time: ['', ''], // 操作时间
});

const sortType = ref('null');
const sortConfig = computed(() => ({ SortScope: 'all', value: sortType.value }));
const settings = {
  fields: [
    {
      label: t('操作类型'),
      field: 'operation',
    },
    {
      label: t('操作对象'),
      field: 'object_type',
    },
    {
      label: t('操作实例'),
      field: 'object_name',
    },
    {
      label: t('操作人'),
      field: 'creator',
    },
    {
      label: t('操作时间'),
      field: 'created_at',
    },
  ],
  checked: ['operation', 'object_type', 'object_name', 'creator', 'created_at'],
};
const pagination = reactive({
  current: 1,
  count: 0,
  limit: 10,
  limitList: [10, 20, 50],
});

const isDataEmpty = ref(false);
const isEmptySearch = ref(false);
const isDataError = ref(false);

// 获取audit数据
const handleFetchAudit = async (type = '') => {
  try {
    isLoading.value = true;
    isDataEmpty.value = false;
    isEmptySearch.value = false;
    isDataError.value = false;
    const isSearch = type === 'search';
    if (isSearch) {
      pagination.count = 0;
      pagination.current = 1;
    }
    const params = {
      page: pagination.current,
      page_size: pagination.limit,
      operation: formData.operation,
      object_type: formData.object_type,
      object_name: formData.object_name,
      creator: formData.creator,
      start_at: formData.operation_time[0] ? dayjs(formData.operation_time[0]).format('YYYY-MM-DD HH:mm:ss') : '',
      end_at: formData.operation_time[1] ? dayjs(formData.operation_time[1]).format('YYYY-MM-DD HH:mm:ss') : '',
    };
    const res = await getAudit(params);
    if (res.data?.count === 0) {
      isDataEmpty.value = !isSearch;
      isEmptySearch.value = isSearch;
    }
    pagination.count = res.data?.count;
    tableData.value = res.data?.results;
  } catch (e) {
    console.warn(e);
    isDataError.value = true;
  } finally {
    isLoading.value = false;
  }
};

// pageSize更改回调方法
const pageLimitChange = (pageSize: number) => {
  pagination.limit = pageSize;
  pagination.current = 1;
  handleFetchAudit();
};

// page更改回调方法
const pageCurrentChange = (page: number) => {
  pagination.current = page;
  handleFetchAudit();
};

const handleSortBy = (curSort: any) => {
  sortType.value = curSort.type;
};

// 折叠button处理
const handleHoverFoldBtn = () => isHover.value = true;
const handleLeaveFoldBtn = () => isHover.value = false;
const togglePreFold = () =>  isFold.preFold = !isFold.preFold;
const toggleFold = () => {
  isFold.curFold = !isFold.curFold;
  isHover.value = false;
};

const handleReset = () => {
  formData.operation_time = ['', ''];
  formData.creator = '';
  formData.object_name = '';
  formData.object_type = '';
  formData.operation = '';
  handleFetchAudit('search');
};

// 当前关联操作对象，当操作类型或操作对象有数据时，“锁死”操作类型及操作对象的option，当且仅当两者均为空，relyKey才可以为null
const relyKey = ref(null);
// 所有的操作类型
const operationOptions = getCurrentOperationOptions();

// 基于relyKey筛选后的操作类型
const curOperationOptions = computed(() => {
  if (relyKey.value) {
    return operationOptions
      .filter((option: {key: string, label: string, relyKey: string}) => option.relyKey === relyKey.value);
  }
  return operationOptions;
});

// 基于relyKey筛选后的操作对象，操作对象选项不完全被relyKey限制，除非操作类型有数据
const curOperationType = computed(() => {
  if (relyKey.value && formData.operation !== '') {
    return operationType.filter((type: {key: string, label: string}) => type.key === relyKey.value);
  }
  return operationType;
});

// 根据后台返回的操作对象的值，找对应label
const getOperationTypeLabel = (key: string) => {
  const curType = operationType.find((type: {key: string, label: string}) => type.key === key);
  return curType ? curType.label : '--';
};

// 根据后台返回的操作类型的值，找对应的label
const getOperationLabel = (key: string) => {
  const curOperation = operationOptions.find((type: {key: string, label: string}) => type.key === key);
  return curOperation ? curOperation.label : '--';
};

// 监听操作类型，若操作对象此时未选择，可以清空relyKey
watch(() => formData.operation, (value) => {
  if (value === '' && formData.object_type === '') {
    relyKey.value = '';
  } else {
    const curRelyKey = (curOperationOptions.value.find(option => option.key === value))?.relyKey;
    if (curRelyKey) {
      // 更新relyKey
      relyKey.value = curRelyKey;
      // 同步操作对象数据
      formData.object_type = curRelyKey;
    }
  }
});

// 监听操作对象，若操作类型此时未选择，可以清空relyKey
watch(() => formData.object_type, (value) => {
  if (value === '' && formData.operation === '') {
    relyKey.value = '';
  } else if (value) {
    relyKey.value = value;
  }
});

onMounted(() => {
  handleFetchAudit();
});

</script>

<style lang="less" scoped>
@container-width: 1312px;

.filter-operation-history-container {
  width: @container-width;
  height: 248px;
  background: #FFFFFF;
  box-shadow: 0 2px 4px 0 #1919290d;
  border-radius: 2px;

  .items-input, .items-select, .items-picker {
    width: 298px;
  }

  ::v-deep .bk-picker-panel-body {
    width: 298px !important;
  }
}

.data-operation-history-container {
  width: @container-width;
  background-color: #fff;
  border-radius: 2px;
  border: 1px solid #DCDEE5;
  box-shadow: 0 2px 4px 0 #1919290d;

  .operation-history-table {
    transition: height 0.5s ease;
  }
}

.v-enter-active,
.v-leave-active {
  transition: height 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  height: 0px;
}
</style>
