<template>
  <bk-loading :loading="isLoading" class="field-setting-content user-scroll-y">
    <bk-button class="add-field" theme="primary" @click="addField">
      <i class="user-icon icon-add-2 mr8" />
      添加字段
    </bk-button>
    <div ref="rootRef">
      <bk-table
        class="field-setting-table"
        :data="tableData"
        :border="['outer']"
        :max-height="tableMaxHeight"
        show-overflow-tooltip>
        <template #empty>
          <Empty
            :is-data-empty="fieldData.isTableDataEmpty"
            :is-data-error="fieldData.isTableDataError"
            @handleUpdate="fetchFieldList"
          />
        </template>
        <bk-table-column prop="display_name" label="字段名称">
          <template #default="{ row }">
            <div class="field-name">
              <span class="name">{{ row.display_name }}</span>
              <bk-tag theme="info" v-if="row.builtin">内置</bk-tag>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column prop="name" label="英文标识"></bk-table-column>
        <bk-table-column prop="data_type" label="字段类型">
          <template #default="{ row }">
            <span>{{ switchType(row.data_type) }}</span>
          </template>
        </bk-table-column>
        <bk-table-column prop="required" label="是否必填">
          <template #default="{ row }">
            <i :class="fieldStatus(row.required)"></i>
          </template>
        </bk-table-column>
        <!-- <bk-table-column prop="unique" label="是否唯一">
          <template #default="{ row }">
            <i :class="fieldStatus(row.unique)"></i>
          </template>
        </bk-table-column> -->
        <bk-table-column prop="builtin" label="是否可编辑">
          <template #default="{ row }">
            <i :class="fieldStatus(!row.builtin)"></i>
          </template>
        </bk-table-column>
        <bk-table-column label="操作">
          <template #default="{ row }">
            <span v-bk-tooltips="{ content: '该内置字段，不支持修改', disabled: !row.builtin }">
              <bk-button text theme="primary" class="mr8" :disabled="row.builtin" @click="editField(row)">
                编辑
              </bk-button>
            </span>
            <span v-bk-tooltips="{ content: '内置字段，不能删除', disabled: !row.builtin }">
              <bk-button text theme="primary" :disabled="row.builtin" @click="deleteField(row)">
                删除
              </bk-button>
            </span>
          </template>
        </bk-table-column>
      </bk-table>
    </div>
    <!-- 添加字段的侧边栏 -->
    <bk-sideslider
      :width="520"
      :is-show="fieldData.isShow"
      :title="fieldData.title"
      :before-close="handleBeforeClose"
      quick-close>
      <FieldsAdd
        :set-type="fieldData.setType"
        :current-editor-data="fieldData.currentEditorData"
        @submitData="submitData"
        @handleCancel="handleCancel" />
    </bk-sideslider>
  </bk-loading>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips, Message } from 'bkui-vue';
import InfoBox from 'bkui-vue/lib/info-box';
import { inject, onMounted, reactive, ref } from 'vue';

import FieldsAdd from './FieldsAdd.vue';

import Empty from '@/components/Empty.vue';
import { useTableMaxHeight } from '@/hooks/useTableMaxHeight';
import { deleteCustomFields, getFields } from '@/http/settingFiles';
import { useMainViewStore } from '@/store/mainView';

const store = useMainViewStore();
store.customBreadcrumbs = false;

const tableMaxHeight = useTableMaxHeight(202);
const editLeaveBefore = inject('editLeaveBefore');
const fieldData = reactive({
  isShow: false,
  title: '添加字段',
  // 侧边栏区分添加字段、编辑字段
  setType: '',
  currentEditorData: {},
  isTableDataEmpty: false,
  isTableDataError: false,
});
const rootRef = ref();
const isLoading = ref(false);
const tableData = ref([]);

onMounted(() => {
  getFieldsList();
});

const getFieldsList = async () => {
  try {
    isLoading.value = true;
    tableData.value = [];
    const res = await getFields();
    const { builtin_fields: builtinFields, custom_fields: customFields } = res.data || {};
    [builtinFields, customFields].forEach((fields, index) => {
      fields.forEach((item) => {
        item.builtin = index === 0;
        tableData.value.push(item);
      });
    });
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
};

// 字段类型转换
const switchType = (type: string) => {
  const typeObj = {
    multi_enum: '枚举',
    string: '字符串',
    bool: '布尔值',
    number: '数值',
    timer: '日期',
    enum: '枚举',
  };
  return typeObj[type];
};

// 展示字段状态
const fieldStatus = (type: boolean) => {
  if (type) {
    return 'user-icon icon-duihao-i';
  }
};

const addField = () => {
  fieldData.title = '添加字段';
  fieldData.setType = 'add';
  fieldData.currentEditorData = {
    name: '',
    display_name: '',
    data_type: 'string',
    required: false,
    builtin: false,
    default: 0,
    options: [
      { id: 0, value: '' },
      { id: 1, value: '' },
    ],
  };
  fieldData.isShow = true;
};

const editField = (item) => {
  fieldData.currentEditorData = item;
  fieldData.title = '编辑字段';
  fieldData.setType = 'edit';
  fieldData.isShow = true;
};

const deleteField = (row) => {
  InfoBox({
    title: '确认要删除吗？',
    confirmText: '确认删除',
    onConfirm: () => {
      deleteCustomFields(row.id).then(() => {
        getFieldsList();
        Message({
          message: '删除成功',
          theme: 'success',
        });
      });
    },
  });
};
const handleBeforeClose = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
    fieldData.isShow = false;
  } else {
    fieldData.isShow = false;
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
};

const handleCancel = () => {
  fieldData.isShow = false;
  window.changeInput = false;
};

const submitData = (message) => {
  fieldData.isShow = false;
  window.changeInput = false;
  getFieldsList();
  Message({
    message,
    theme: 'success',
  });
};

const fetchFieldList = () => {
  getFieldsList();
};
</script>

<style lang="less" scoped>
.field-setting-content {
  height: calc(100vh - 104px);
  padding: 24px;

  .add-field {
    margin-bottom: 16px;
  }

  :deep(.field-setting-table) {
    .field-name {
      .name {
        margin: 0 8px;
        color: #63656e;
      }
    }

    .icon-duihao-i {
      font-size: 16px;
      color: #2dcb56;
    }

    .bk-table-footer {
      padding: 0 15px;
      background: #fff;
    }
  }
}

.blue-background-class {
  background: red;
}
</style>
