<template>
  <div class="fields-add-wrapper user-scroll-y">
    <bk-form ref="fieldsRef" form-type="vertical" :model="fieldsInfor" :rules="rulesFields">
      <bk-form-item :label="$t('字段名称')" property="display_name" required>
        <bk-input
          :placeholder="validate.fieldsDisplayName.message"
          v-model="fieldsInfor.display_name"
          @focus="handleChange" />
      </bk-form-item>
      <bk-form-item :label="$t('英文标识')" property="name" required>
        <bk-input
          :placeholder="validate.fieldsName.message"
          :disabled="isEdit"
          v-model="fieldsInfor.name"
          @focus="handleChange" />
      </bk-form-item>
      <bk-form-item :label="$t('字段类型')" required>
        <bk-select
          v-model="state.defaultSelected"
          :clearable="false"
          :disabled="isEdit"
          @change="selectedType">
          <bk-option
            v-for="(option, index) in typeList"
            :key="index"
            :id="option.id"
            :name="option.name"
          />
        </bk-select>
      </bk-form-item>
      <bk-form-item :label="$t('默认值')" v-if="fieldsInfor.data_type === 'string'">
        <bk-input
          v-model="fieldsInfor.default"
          :maxlength="64"
          @focus="handleChange"
        />
      </bk-form-item>
      <bk-form-item :label="$t('默认值')" v-else-if="fieldsInfor.data_type === 'number'">
        <bk-input
          type="number"
          v-model="fieldsInfor.default"
          :max="4294967296"
          :min="0"
          @focus="handleChange"
        />
      </bk-form-item>
      <bk-loading
        :loading="enumLoading"
        class="enumerate-wrapper"
        v-if="state.isShowEg || fieldsInfor.data_type.indexOf('enum') !== -1">
        <bk-form-item style="margin-bottom: 10px;" :label="$t('枚举类型')" required>
          <bk-radio-group class="king-radio-group" v-model="fieldsInfor.data_type">
            <bk-radio
              label="enum"
              name="egRadio"
              :disabled="isEdit"
            >{{ $t('单选') }}</bk-radio
            >
            <bk-radio
              label="multi_enum"
              name="egRadio"
              :disabled="isEdit"
            >{{ $t('多选') }}</bk-radio
            >
          </bk-radio-group>
        </bk-form-item>
        <div class="enum-title">
          <bk-form-item class="w-[200px]" :label="$t('选项ID')" required />
          <bk-form-item class="w-[184px]" :label="$t('选项值')" required />
          <bk-form-item class="w-[60px] ml-[12px]" :label="$t('为默认值')" />
        </div>
        <div
          class="enum-list"
          v-for="(item, index) in fieldsInfor.options"
          :key="index"
        >
          <bk-form class="enum-form" ref="enumRef" form-type="vertical" :model="item" :rules="rulesEnum">
            <bk-form-item class="w-[200px]" property="id" required error-display-type="tooltips">
              <bk-input
                v-model="item.id"
                :placeholder="$t('请输入ID')"
                @change="handleChange" />
            </bk-form-item>
            <bk-form-item class="w-[184px]" property="value" required error-display-type="tooltips">
              <bk-input
                v-model="item.value"
                :placeholder="$t('请输入值')"
                @change="handleChange"
              />
            </bk-form-item>
            <div class="input-container">
              <bk-radio-group
                v-if="fieldsInfor.data_type === 'enum'"
                :model-value="fieldsInfor.default"
                @change="changeRadio(index)">
                <bk-radio :label="index" :model-value="index" />
              </bk-radio-group>
              <bk-checkbox-group
                v-else
                :model-value="fieldsInfor.default"
                @change="changeCheckbox(index)">
                <bk-checkbox :label="index" :model-value="index" />
              </bk-checkbox-group>
            </div>
            <i
              :class="['user-icon icon-delete', { 'forbid': fieldsInfor.options.length <= 1 }]"
              @click="deleteEg(item, index)" />
          </bk-form>
        </div>
        <bk-button class="add-enum" text theme="primary" @click="addEg">
          <i class="user-icon icon-add-2 mr8" />
          {{ $t('添加选项') }}
        </bk-button>
      </bk-loading>
    </bk-form>
    <div class="select-type">
      <bk-checkbox
        :value="fieldsInfor.required"
        :disabled="isEdit"
        v-model="fieldsInfor.required"
        @change="handleChange">
        <span v-bk-tooltips="{ content: $t('该字段在用户信息里必须填写') }">{{ $t('必填') }}</span>
      </bk-checkbox>
      <bk-checkbox
        :value="fieldsInfor.unique"
        :disabled="uniqueDisabled"
        v-model="fieldsInfor.unique">
        <span v-bk-tooltips="{ content: uniqueText }">{{ $t('唯一') }}</span>
      </bk-checkbox>
      <bk-checkbox
        :value="fieldsInfor.manager_editable"
        v-model="fieldsInfor.manager_editable"
        :disabled="isEdit">
        <span v-bk-tooltips="{ content: $t('该字段在用户信息里可编辑') }">{{ $t('管理员可编辑') }}</span>
      </bk-checkbox>
    </div>
    <bk-form form-type="vertical">
      <bk-form-item :label="$t('在个人中心展示')">
        <div style="display: flex; align-items: center;">
          <bk-switcher
            size="large"
            v-model="fieldsInfor.personal_center_visible"
            theme="primary"
            :disabled="isEdit"
          />
          <bk-checkbox
            v-if="fieldsInfor.personal_center_visible"
            class="ml-[40px]"
            v-model="fieldsInfor.personal_center_editable"
            :disabled="isEdit">
            {{ $t('个人中心可编辑') }}
          </bk-checkbox>
        </div>
      </bk-form-item>
    </bk-form>
    <div class="submit-btn">
      <bk-button theme="primary" @click="submitInfor" :loading="state.btnLoading">{{ $t('保存') }}</bk-button>
      <bk-button theme="default" @click="$emit('handleCancel')">{{ $t('取消') }}</bk-button>
    </div>
    <!-- 枚举值删除确认弹框 -->
    <bk-dialog
      ext-cls="enum-dialog-wrapper"
      :is-show="enumDialog.isShow"
      title=""
      :theme="'primary'"
      :dialog-type="'show'"
      :quick-close="false"
      width="400"
      @closed="enumDialog.isShow = false"
    >
      <div class="enum-dialog-content">
        <div class="header">
          <p class="title">{{ $t('是否删除该枚举值？') }}</p>
          <p class="subtitle">
            <span class="name">{{ $t('枚举值：') }}</span>
            <span class="value">{{ enumDialog.item.id }}：{{ enumDialog.item.value }}</span>
          </p>
        </div>
        <p class="content-text">{{ $t('该枚举值删除后，请为已引用的记录指定其他值：') }}</p>
        <ul class="content-list">
          <li
            :class="['content-list-item', { 'active-item': enumDialog.activeId === item.id }]"
            v-for="(item, index) in enumDialog.list"
            :key="index"
            @click="handleEnumValue(item)">
            <span class="name">
              {{ item.id }}
            </span>
            <i :class="['user-icon icon-check-line', { 'active': enumDialog.activeId === item.id }]" />
          </li>
        </ul>
        <div class="content-btn">
          <bk-button
            class="mr-[3px]"
            theme="primary"
            :disabled="!enumDialog.activeId"
            :loading="btnLoading"
            @click="changeEnumValue"
          >{{ $t('确定') }}</bk-button>
          <bk-button
            theme="default"
            @click="enumDialog.isShow = false"
          >{{ $t('取消') }}</bk-button>
        </div>
      </div>
    </bk-dialog>
  </div>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips } from 'bkui-vue';
import { computed, defineEmits, defineProps, onMounted, reactive, ref, watch } from 'vue';

import { useValidate } from '@/hooks';
import { newCustomFields, putCustomFields } from '@/http';
import { t } from '@/language/index';

const props = defineProps({
  currentEditorData: {
    type: Object,
    default: {},
  },
  setType: {
    type: String,
    default: '',
  },
});
const emit = defineEmits(['handleCancel', 'submitData', 'updateFields']);

const validate = useValidate();
const fieldsRef = ref();
const enumRef = ref();
const fieldsInfor = reactive(JSON.parse(JSON.stringify({ ...props.currentEditorData })));
const state = reactive({
  defaultSelected: 'string',
  isDeleteOption: true,
  nameError: '',
  isRepeatClick: false,
  // 是否是枚举，显示对应的内容
  isShowEg: false,
  btnLoading: false,
});
const typeList = [
  {
    id: 'string',
    name: t('字符串'),
  },
  {
    id: 'enum',
    name: t('枚举'),
  },
  {
    id: 'number',
    name: t('数值'),
  },
  // {
  //   id: 'timer',
  //   name: t('日期'),
  // },
];

const rulesFields = {
  display_name: [validate.required, validate.fieldsDisplayName],
  name: [validate.required, validate.fieldsName],
};

const rulesEnum = {
  id: [
    validate.required,
    validate.checkSpace,
    {
      validator: (value: string) => {
        const result = blurId();
        return value !== result;
      },
      message: t('id不能重复'),
      trigger: 'blur',
    },
  ],
  value: [
    validate.required,
    validate.checkSpace,
    {
      validator: (value: string) => {
        const result = blurValue();
        return value !== result;
      },
      message: t('value不能重复'),
      trigger: 'blur',
    },
  ],
};

const isEdit = computed(() => props?.setType === 'edit');
const uniqueDisabled = ref(false);
const uniqueText = ref(t('该字段在不同用户信息里不能相同'));

watch(() => fieldsInfor.data_type, (val) => {
  uniqueDisabled.value = val === 'enum' || val === 'multi_enum' || props?.currentEditorData?.id;
  uniqueText.value = (val === 'enum' || val === 'multi_enum')
    ? t('枚举类型字段不允许设置唯一性')
    : t('该字段在不同用户信息里不能相同');

  if (!props?.currentEditorData?.id) {
    if (val === 'multi_enum') {
      fieldsInfor.default = [0];
    } else if (val === 'string') {
      fieldsInfor.default = '';
    } else {
      fieldsInfor.default = 0;
    }
  } else {
    const defaultIndex = id => fieldsInfor.options.findIndex(item => item.id === id);

    if (val === 'enum') {
      fieldsInfor.default = defaultIndex(fieldsInfor.default);
    } else if (val === 'multi_enum') {
      fieldsInfor.default = fieldsInfor.default.map(defaultIndex);
    }
  }
}, {
  deep: true,
  immediate: true,
});

watch(() => fieldsInfor.options.length, (val) => {
  if (state.defaultSelected === 'enum') {
    state.isDeleteOption = !(val <= 1);
  }
});


onMounted(() => {
  if (props?.currentEditorData?.id) {
    if (fieldsInfor.data_type === 'enum' || fieldsInfor.data_type === 'multi_enum') {
      state.defaultSelected = 'enum';
    } else {
      state.defaultSelected = fieldsInfor.data_type;
    }
  }
});

// 下拉框 选择对应的类型，布尔值 字符串 枚举 数值
const selectedType = (newType) => {
  window.changeInput = true;
  if (newType === 'enum') {
    state.isShowEg = true;
    // 如果选择了枚举值 type 设置为单选
    if (fieldsInfor.data_type.indexOf('enum') === -1) {
      fieldsInfor.data_type = 'enum';
    }
  } else {
    fieldsInfor.data_type = newType;
    state.isShowEg = false;
  }
};

const handleChange = () => {
  window.changeInput = true;
};
const enumLoading = ref(false);
const btnLoading = ref(false);
const enumDialog = ref({
  isShow: false,
  list: [],
  deleteId: '',
  activeId: '',
  item: { id: '', value: '' },
});

const handleEnumValue = (item: any) => {
  enumDialog.value.activeId = item.id;
};

const deleteList = ref([]);
// 修改枚举值
const changeEnumValue = async () => {
  try {
    btnLoading.value = true;
    enumLoading.value = true;
    const { deleteId, activeId } = enumDialog.value;
    deleteList.value.push({ [deleteId]: activeId });
    fieldsInfor.mapping = transformArrayToObject(deleteList.value);

    if (fieldsInfor.data_type === 'enum') {
      fieldsInfor.default = fieldsInfor.options.some(item => item.id === activeId) ? activeId : fieldsInfor.default;
    } else {
      const newDefault = fieldsInfor.default.map(index => fieldsInfor.options[index]?.id);
      if (!newDefault.includes(activeId)) {
        newDefault.push(activeId);
      }
      fieldsInfor.default = newDefault.filter(id => id !== deleteId);
    }
    fieldsInfor.options = fieldsInfor.options.filter(item => item.id !== deleteId);

    enumDialog.value.isShow = false;

    const findIndexById = id => fieldsInfor.options.findIndex(item => item.id === id);
    fieldsInfor.default = fieldsInfor.data_type === 'enum' ? findIndexById(fieldsInfor.default)
      : fieldsInfor.data_type === 'multi_enum' ? fieldsInfor.default?.map(findIndexById)
        : fieldsInfor.default;
  } catch (error) {
    console.warn(error);
  } finally {
    btnLoading.value = false;
    enumLoading.value = false;
  }
};

// 将数组转换为对象
const transformArrayToObject = (array) => {
  const keyValueMap = {};
  array.forEach((obj) => {
    for (const [key, value] of Object.entries(obj)) {
      keyValueMap[key] = value;
    }
  });

  const result = {};
  array.forEach((obj) => {
    for (const [key, value] of Object.entries(obj)) {
      result[key] = keyValueMap[value] || value;
    }
  });

  return result;
};

// 删除枚举
const deleteEg = (item: any, index: number) => {
  if (fieldsInfor.options.length <= 1) {
    return;
  }
  window.changeInput = true;
  enumDialog.value = {
    isShow: false,
    list: [],
    deleteId: '',
    activeId: '',
    item: { id: '', value: '' },
  };
  if (props.setType === 'edit') {
    enumDialog.value.item = item;
    fieldsInfor.options.forEach((k) => {
      if (k.id === item.id) {
        enumDialog.value.deleteId = k.id;
        enumDialog.value.isShow = true;
      } else {
        if (!item.id) {
          fieldsInfor.options.splice(index, 1);
        }
        enumDialog.value.list.push(k);
      }
    });
  } else {
    if (fieldsInfor.data_type === 'enum' && fieldsInfor.default === index) {
      if (index === 0) {
        fieldsInfor.default = index;
      } else {
        fieldsInfor.default = index - 1;
      }
    }
    fieldsInfor.options.splice(index, 1);
  }
};
// 添加枚举类型
const addEg = () => {
  window.changeInput = true;
  if (fieldsInfor.options.length > 100) {
    return;
  }
  const param = {
    id: '',
    value: '',
  };
  fieldsInfor.options.push(param);
};
// 变更枚举值
const changeRadio = (val) => {
  fieldsInfor.default = val;
};

const changeCheckbox = (val) => {
  if (fieldsInfor.default.includes(val)) {
    fieldsInfor.default = fieldsInfor.default.filter(item => item !== val);
  } else {
    fieldsInfor.default.push(val);
  }
};
// 表单校验
const submitInfor = async () => {
  try {
    const isEnumType = fieldsInfor.data_type === 'enum' || fieldsInfor.data_type === 'multi_enum';

    if (isEnumType) {
      await Promise.all([
        fieldsRef.value.validate(),
        ...enumRef.value.map(item => item.validate()),
      ]);
    } else {
      await fieldsRef.value.validate();
    }

    state.btnLoading = true;

    const newFieldData = {
      ...(isEdit.value ? { id: fieldsInfor.id } : { name: fieldsInfor.name }),
      ...fieldsInfor,
    };
    newFieldData.options = [];
    if (isEnumType) {
      const defaultIndex = fieldsInfor.data_type === 'enum' ? [fieldsInfor.default] : fieldsInfor.default;
      newFieldData.options = fieldsInfor.options;
      newFieldData.default = fieldsInfor.options
        .filter((_, index) => defaultIndex.includes(index))
        .map(item => item.id);
      if (fieldsInfor.data_type === 'enum') {
        newFieldData.default = newFieldData.default[0] || null;
      }
      newFieldData.mapping = fieldsInfor?.mapping || {};
    }

    const action = isEdit.value ? putCustomFields : newCustomFields;
    const successMessage = isEdit.value ? t('修改字段成功') : t('添加字段成功');

    await action(newFieldData);
    emit('submitData', successMessage);
  } catch (e) {
    console.warn(e);
  } finally {
    state.btnLoading = false;
  }
};

// 校验重复值
const findFirstDuplicate = (key) => {
  const obj = {};
  const result = ref('');
  fieldsInfor.options.forEach((item, index) => {
    if (!obj[item[key]]) {
      obj[item[key]] = new Set();
    }
    obj[item[key]].add(index);
  });

  for (const [itemKey, value] of Object.entries(obj)) {
    if (value.size > 1) {
      result.value = itemKey;
      break;
    }
  }
  return result.value;
};

const blurId = () => findFirstDuplicate('id');
const blurValue = () => findFirstDuplicate('value');
</script>

<style lang="less">
.enum-dialog-wrapper .enum-dialog-content {
  .header {
    margin-bottom: 12px;
    text-align: center;

    .title {
      margin-bottom: 8px;
      font-size: 20px;
      line-height: 32px;
      color: #313238;
    }

    .subtitle {
      .name {
        color: #313238;
      }

      .value {
        display: inline-block;
        height: 22px;
        padding: 0 8px;
        font-size: 12px;
        background: #F0F1F5;
      }
    }
  }

  .content-text {
    margin-bottom: 12px;
  }

  .content-list {
    .content-list-item {
      position: relative;
      height: 32px;
      margin-bottom: 8px;
      line-height: 32px;
      text-align: center;
      background: #F0F1F5;
      border-radius: 2px;

      .name {
        color: #313238;
      }

      .user-icon {
        position: absolute;
        top: 8px;
        right: 8px;
        display: none;
        font-size: 14px;
        color: #C4C6CC;
      }

      &:hover {
        cursor: pointer;

        .user-icon {
          display: inline-block;
        }
      }
    }

    .active-item {
      background: #E1ECFF;

      .active {
        display: inline-block;
        color: #3A84FF;
      }
    }
  }

  .content-btn {
    margin-top: 24px;
    text-align: center;

    .bk-button {
      width: 88px;
    }
  }
}
</style>

<style lang="less" scoped>
.fields-add-wrapper {
  height: calc(100vh - 52px);
  padding: 24px 0;

  .bk-form {
    padding: 0 40px;
  }

  .enumerate-wrapper {
    padding: 16px 24px;
    margin-bottom: 18px;
    background: #F5F7FA;
    border-radius: 2px;

    .enum-title {
      display: flex;
      align-items: center;

      .bk-form-item {
        margin-right: 12px;
        margin-bottom: 0;
      }

    }

    .enum-list {
      .enum-form {
        display: flex;
        padding: 0;
        align-items: center;
        margin-bottom: 12px;

        .bk-form-item {
          margin: 0 12px 0 0;
        }

        ::v-deep .input-container {
          width: 60px;
          margin-left: 12px;

          .bk-checkbox-label, .bk-radio-label {
            visibility: hidden;
          }
        }

        .icon-delete {
          margin-left: 12px;
          font-size: 16px;
          color: #FF5656;
          cursor: pointer;

          &.forbid {
            color: #EAEBF0;
            cursor: not-allowed;
          }
        }
      }
    }

    .add-enum {
      font-size: 14px;
    }
  }

  .select-type {
    display: flex;
    padding: 0 40px 22px;
  }

  .submit-btn {
    padding: 0 40px;

    .bk-button {
      width: 76px !important;
      margin-right: 10px;
    }
  }
}
</style>
