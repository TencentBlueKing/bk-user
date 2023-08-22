<template>
  <div class="field-setting-content user-scroll-y">
    <bk-button class="add-field" theme="primary" @click="addField">
      <i class="user-icon icon-add-2 mr8" />
      添加字段
    </bk-button>
    <bk-table
      class="field-setting-table"
      :data="tableData"
      row-key="id"
      :border="['outer']"
      settings
      show-overflow-tooltip
      :pagination="pagination"
    >
      <template #empty>
        <Empty
          :is-data-empty="fieldData.isTableDataEmpty"
          :is-data-error="fieldData.isTableDataError"
          @handleEmpty="fetchFieldList"
          @handleUpdate="fetchFieldList"
        />
      </template>
      <bk-table-column prop="name" label="字段名称">
        <template #default="{ row }">
          <div class="field-name">
            <i class="user-icon icon-drag move" />
            <span class="name">{{ row.name }}</span>
            <bk-tag theme="info" v-if="row.builtin">内置</bk-tag>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column prop="key" label="英文标识"></bk-table-column>
      <bk-table-column prop="type" label="字段类型"></bk-table-column>
      <bk-table-column prop="require" label="是否必填">
        <template #default="{ row }">
          <i :class="fieldStatus(row.require)"></i>
        </template>
      </bk-table-column>
      <bk-table-column prop="unique" label="是否唯一">
        <template #default="{ row }">
          <i :class="fieldStatus(row.unique)"></i>
        </template>
      </bk-table-column>
      <bk-table-column prop="editable" label="是否可编辑">
        <template #default="{ row }">
          <i :class="fieldStatus(row.editable)"></i>
        </template>
      </bk-table-column>
      <bk-table-column label="操作">
        <template #default="{ row }">
          <bk-button text theme="primary" class="mr8" @click="editField(row)">
            编辑
          </bk-button>
          <bk-button text theme="primary" @click="deleteField(row)">
            删除
          </bk-button>
        </template>
      </bk-table-column>
    </bk-table>
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
        @handleCancel="handleCancel" />
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import InfoBox from 'bkui-vue/lib/info-box';
import Sortable from 'sortablejs';
import { inject, nextTick, reactive, ref } from 'vue';

import FieldsAdd from './FieldsAdd.vue';

import Empty from '@/components/Empty.vue';
import { useMainViewStore } from '@/store/mainView';

const store = useMainViewStore();
store.customBreadcrumbs = false;

const editLeaveBefore = inject('editLeaveBefore');
const fieldData = reactive({
  isShow: false,
  title: '添加字段',
  // 点击保存时打开 loading，临时在样式上隐藏侧边栏
  isHideBar: false,
  // 侧边栏区分添加字段、编辑字段
  setType: '',
  currentEditorData: {},
  isTableDataEmpty: false,
  isTableDataError: false,
});

const tableData: any = [
  {
    builtin: true,
    configurable: false,
    default: '',
    display_name: '用户名',
    editable: false,
    enabled: true,
    id: 1,
    key: 'username',
    name: '用户名',
    order: 1,
    require: true,
    type: 'string',
    unique: true,
    visible: true,
  },
  {
    builtin: true,
    configurable: true,
    default: '',
    display_name: '全名',
    editable: true,
    enabled: true,
    id: 2,
    key: 'display_name',
    name: '全名',
    order: 2,
    require: true,
    type: 'string',
    unique: false,
    visible: true,
  },
  {
    builtin: true,
    configurable: false,
    default: '',
    display_name: '邮箱',
    editable: true,
    enabled: true,
    id: 3,
    key: 'email',
    name: '邮箱',
    order: 3,
    require: true,
    type: 'string',
    unique: false,
    visible: true,
  },
];

const pagination = reactive({
  count: tableData.length,
  limit: 10,
  limitList: [10, 20, 50, 100],
});

// 展示字段状态
const fieldStatus = (type: boolean) => {
  if (type) {
    return 'user-icon icon-duihao-i';
  }
};

const initSortable = (className: string) => {
  // 获取表格row的父节点
  const table = document.querySelector(`.${className} .bk-table-body tbody`);
  // 创建拖拽实例
  Sortable.create(table, {
    handle: '.move',
    group: table,
    ghostClass: 'blue-background-class',
    animation: 150,
    onUpdate: (event: any) => {
      console.log('event', event);
    },
  });
};

nextTick(() => {
  initSortable('field-setting-table');
});

const addField = () => {
  fieldData.currentEditorData = {};
  fieldData.title = '添加字段';
  fieldData.setType = 'add';
  fieldData.isShow = true;
};

const editField = (item) => {
  fieldData.currentEditorData = item;
  fieldData.title = '编辑字段';
  fieldData.setType = 'edit';
  fieldData.isShow = true;
};

const deleteField = (item) => {
  InfoBox({
    title: '确认要删除吗？',
    confirmText: '确认删除',
    onConfirm: () => {
      Message({
        message: '删除成功',
        theme: 'success',
        delay: 1500,
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
};

const fetchFieldList = () => {};
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
      .move {
        font-size: 16px;
        color: #c8c8c8;
        cursor: move;
      }

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
