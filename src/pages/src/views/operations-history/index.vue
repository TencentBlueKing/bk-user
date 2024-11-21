<template>
  <div class="h-[100vh]">
    <div class="grid place-items-center">
      <!-- 筛选表单 -->
      <transition>
        <div
          v-if="!isFold.curFold"
          :class="['filter-operation-history-container', isFold.preFold ? 'overflow-hidden' : '']">
          <bk-form
            form-type="vertical"
            ref="formRef"
            :model="formData"
            class="w-full mt-[24px]">
            <bk-form-item class="inline-block ml-[24px]" :label="$t('操作人')">
              <bk-input class="items-input" v-model="formData.creator" clearable />
            </bk-form-item>
            <bk-form-item class="inline-block ml-[20px]" :label="$t('操作类型')">
              <bk-select class="items-select" v-model="formData.operation">
                <bk-option
                  v-for="(value, key) in operationMap"
                  :key="key"
                  :id="key"
                  :name="value" />
              </bk-select>
            </bk-form-item>
            <bk-form-item class="inline-block ml-[20px]" :label="$t('操作对象')">
              <bk-select class="items-select" v-model="formData.object_type">
                <bk-option
                  v-for="(value, key) in operationTypeMap"
                  :key="key"
                  :id="key"
                  :name="value" />
              </bk-select>
            </bk-form-item>
            <bk-form-item class="inline-block ml-[20px]" :label="$t('操作实例')">
              <bk-input class="items-input" clearable v-model="formData.object_name" />
            </bk-form-item>
            <bk-form-item class="inline-block ml-[24px]" :label="$t('操作时间')">
              <bk-date-picker class="items-picker" v-model="formData.created_at" type="datetime" />
            </bk-form-item>
            <bk-form-item class="ml-[24px]">
              <bk-button
                class="w-[88px] h-[32px]"
                theme="primary"
                :loading="isLoading"
                @click="initAudit"
              >
                {{ $t('查询') }}
              </bk-button>
              <bk-button
                class="w-[88px] h-[32px] ml-[8px]"
                @click="handleReset"
              >
                {{ $t('重置') }}
              </bk-button>
            </bk-form-item>
          </bk-form>
        </div>
      </transition>
      <!-- 折叠按钮 -->
      <div class="flex justify-center w-full">
        <div @mouseover="handleHoverFoldBtn" @mouseleave="handleLeaveFoldBtn" v-if="!isFold.curFold">
          <bk-button
            v-if="isHover" theme="primary"
            @click="toggleFold"
            @mousedown="togglePreFold"
            class="w-[120px] h-[24px] text-bold border-none">
            <i class="user-icon icon-angle-up text-[30px]"></i>
          </bk-button>
          <bk-button
            v-else
            @click="toggleFold"
            @mousedown="togglePreFold"
            class="w-[120px] h-[24px] !bg-[#DCDEE5] !text-[#ffffff] text-bold border-none">
            <i class="user-icon icon-angle-up text-[30px]"></i>
          </bk-button>
        </div>
        <div v-else>
          <bk-button
            theme="primary"
            @click="toggleFold"
            @mousedown="togglePreFold"
            class="w-[120px] h-[24px] text-bold border-none">
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
          settings
          @page-limit-change="pageLimitChange"
          @page-value-change="pageCurrentChange"
        >
          <bk-table-column :label="$t('操作人')" prop="creator" width="100"></bk-table-column>
          <bk-table-column :label="$t('操作时间')" sort prop="created_at" width="100"></bk-table-column>
          <bk-table-column :label="$t('操作对象')" prop="object_type" width="100">
            <template #default="{ row }">
              <span>{{ operationTypeMap[row.object_type as keyof typeof operationTypeMap] }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('操作实例')" prop="object_name" width="100"></bk-table-column>
          <bk-table-column :label="$t('操作类型')" prop="operation" width="100">
            <template #default="{ row }">
              <span>{{ operationMap[row.operation as keyof typeof operationMap] }}</span>
            </template>
          </bk-table-column>
        </bk-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs';
import { onMounted, reactive, ref } from 'vue';

import { getAudit } from '@/http/operationHistoryFiles';
import { t } from '@/language/index';

const isHover = ref(false);
const isFold = reactive({
  curFold: false,
  preFold: false,
});

const formRef = ref();
const operationMap = {
  create_data_source: t('创建数据源'),
  modify_data_source: t('修改数据源'),
  delete_data_source: t('删除数据源'),
  sync_data_source: t('同步数据源'),
};
const operationTypeMap = {
  data_source: t('数据源'),
};
const isLoading = ref(false);
const tableData = ref([]);
const formData = reactive({
  creator: '',  // 操作人
  operation: '', // 操作类型
  object_type: '', // 操作对象
  object_name: '', // 操作实例
  created_at: '', // 操作时间
});
const pagination = reactive({
  current: 1,
  count: 0,
  limit: 10,
});

onMounted(() => {
  initAudit();
});

const initAudit = async () => {
  try {
    isLoading.value = true;
    const params = {
      page: pagination.current,
      pageSize: pagination.limit,
      operation: formData.operation,
      object_type: formData.object_type,
      object_name: formData.object_name,
      creator: formData.creator,
      created_at: formData.created_at ? dayjs(formData.created_at).format('YYYY-MM-DD HH:mm:ss') : '',
    };
    const res = await getAudit(params);
    pagination.count = res.data?.count;
    tableData.value = res.data?.results;
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
};

const pageLimitChange = (pageSize: number) => {
  pagination.limit = pageSize;
  initAudit();
};

const pageCurrentChange = (page: number) => {
  pagination.current = page;
  initAudit();
};

const handleHoverFoldBtn = () => isHover.value = true;

const handleLeaveFoldBtn = () => isHover.value = false;

const togglePreFold = () =>  isFold.preFold = !isFold.preFold;

const toggleFold = () => {
  isFold.curFold = !isFold.curFold;
  isHover.value = false;
};

const handleReset = () => {
  formData.created_at = '';
  formData.creator = '';
  formData.object_name = '';
  formData.object_type = '';
  formData.operation = '';
};
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
