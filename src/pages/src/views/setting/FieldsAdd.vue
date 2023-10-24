<template>
  <div class="fields-add-wrapper user-scroll-y">
    <bk-form ref="fieldsRef" form-type="vertical" :model="fieldsInfor" :rules="rulesFields">
      <bk-form-item label="字段名称" property="display_name" required>
        <bk-input
          placeholder="最多不得超过12个字符（6个汉字）"
          v-model="fieldsInfor.display_name"
          @focus="handleChange" />
      </bk-form-item>
      <bk-form-item label="英文标识" property="name" required>
        <bk-input
          placeholder="由英文字母组成"
          :disabled="isEdit"
          v-model="fieldsInfor.name"
          @focus="handleChange" />
      </bk-form-item>
      <bk-form-item label="字段类型" required>
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
    </bk-form>
    <div class="enumerate-wrapper" v-if="state.isShowEg || fieldsInfor.data_type.indexOf('enum') !== -1">
      <i class="arrow"></i>
      <h4 class="enum-title">
        <i class="icon icon-user-cog"></i>
        <span class="text">枚举设置</span>
      </h4>
      <div class="type-select-wrapper">
        <p class="desc">枚举类型</p>
        <bk-radio-group class="king-radio-group" v-model="fieldsInfor.data_type">
          <bk-radio
            label="enum"
            name="egRadio"
            :disabled="isEdit"
          >单选</bk-radio
          >
          <bk-radio
            label="multi_enum"
            name="egRadio"
            :disabled="isEdit"
          >多选</bk-radio
          >
        </bk-radio-group>
      </div>
      <div class="enum-settings" data-test-id="fieldData">
        <p class="explain">
          <span class="default">默认选项</span>
          <span class="text">选项值</span>
        </p>
        <ul>
          <li
            class="content-list"
            v-for="(item, index) in fieldsInfor.options"
            :key="index"
          >
            <div class="select-box default-box">
              <div class="input-container">
                <label
                  v-if="fieldsInfor.data_type === 'enum'"
                  class="king-radio"
                >
                  <input
                    name="eg"
                    type="radio"
                    :value="index"
                    v-model="fieldsInfor.default"
                    :class="{ 'is-checked': fieldsInfor.default === index }"
                  />
                </label>
                <label v-else class="king-checkbox king-checkbox-small">
                  <input
                    name="egCheckbox"
                    type="checkbox"
                    :value="index"
                    v-model="fieldsInfor.default"
                  />
                </label>
              </div>
            </div>
            <div class="select-box icon-box">
              <bk-form ref="enumRef" :model="item" :rules="rulesEnum">
                <bk-form-item property="value" required>
                  <bk-input
                    type="text"
                    class="select-text"
                    v-model="item.value"
                    @change="handleChange"
                  />
                </bk-form-item>
              </bk-form>
            </div>
            <div class="select-box icon-box">
              <i
                class="user-icon icon-minus-fill"
                :class="{ 'forbid': !state.isDeleteOption }"
                @click="deleteEg(index)"
              ></i>
              <i
                class="user-icon icon-plus-fill"
                v-if="index === fieldsInfor.options.length - 1"
                @click="addEg" />
            </div>
          </li>
        </ul>
      </div>
    </div>
    <div class="select-type">
      <bk-checkbox
        :value="fieldsInfor.required"
        :disabled="fieldsInfor.builtin"
        v-model="fieldsInfor.required"
        @change="handleChange">
        <span v-bk-tooltips="{ content: '该字段在用户信息里必须填写' }">必填</span>
      </bk-checkbox>
      <!-- <bk-checkbox
        :value="fieldsInfor.unique"
        :disabled="isEdit"
        v-model="fieldsInfor.unique">
        <span v-bk-tooltips="{ content: '该字段在不同用户信息里不能相同' }">唯一</span>
      </bk-checkbox> -->
      <!-- <bk-checkbox
        :value="fieldsInfor.editable"
        v-model="fieldsInfor.editable"
        :disabled="fieldsInfor.builtin">
        <span v-bk-tooltips="{ content: '该字段在用户信息里可编辑' }">可编辑</span>
      </bk-checkbox> -->
    </div>
    <div class="submit-btn">
      <bk-button theme="primary" @click="submitInfor" :loading="state.btnLoading">保存</bk-button>
      <bk-button theme="default" @click="$emit('handleCancel')">取消</bk-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips } from 'bkui-vue';
import { computed, defineEmits, defineProps, nextTick, onMounted, reactive, ref, watch } from 'vue';

import useValidate from '@/hooks/use-validate';
import { newCustomFields, putCustomFields } from '@/http/settingFiles';

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
const emit = defineEmits(['handleCancel', 'submitData']);

const validate = useValidate();
const fieldsRef = ref();
const enumRef = ref();
const fieldsInfor = reactive({
  ...props.currentEditorData,
});
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
    name: '字符串',
  },
  {
    id: 'enum',
    name: '枚举',
  },
  {
    id: 'number',
    name: '数值',
  },
  {
    id: 'timer',
    name: '日期',
  },
];

const rulesFields = {
  display_name: [validate.required, validate.fieldsDisplayName],
  name: [validate.required, validate.fieldsName],
};

const rulesEnum = {
  value: [validate.required],
};

const isEdit = computed(() => props?.setType === 'edit');

watch(() => fieldsInfor.data_type, (val) => {
  if (!props?.currentEditorData?.id) {
    fieldsInfor.default = val === 'multi_enum' ? [0] : 0;
  }
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
// 删除枚举
const deleteEg = (index) => {
  window.changeInput = true;
  if (fieldsInfor.options.length <= 1) {
    return;
  }
  fieldsInfor.options.splice(index, 1);
};
// 添加枚举类型
const addEg = () => {
  window.changeInput = true;
  if (fieldsInfor.options.length > 100) {
    return;
  }
  const param = {
    id: fieldsInfor.options.length,
    value: '',
  };
  fieldsInfor.options.push(param);
  nextTick(() => {
    const inputList = document.querySelectorAll('.content-list input');
    inputList[inputList.length - 1].focus();
  });
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

    if (isEdit.value) {
      await putCustomFields({
        id: fieldsInfor.id,
        display_name: fieldsInfor.display_name,
        required: fieldsInfor.required,
        default: fieldsInfor.default,
        options: fieldsInfor.options,
      });
      emit('submitData', '修改字段成功');
    } else {
      const newFieldData = {
        name: fieldsInfor.name,
        display_name: fieldsInfor.display_name,
        required: fieldsInfor.required,
        data_type: fieldsInfor.data_type,
      };

      if (isEnumType) {
        newFieldData.options = fieldsInfor.options;
        newFieldData.default = fieldsInfor.default;
      }

      await newCustomFields(newFieldData);
      emit('submitData', '添加字段成功');
    }
  } catch (e) {
    console.warn(e);
  } finally {
    state.btnLoading = false;
  }
};
</script>

<style lang="less" scoped>
.fields-add-wrapper {
  height: calc(100vh - 52px);
  padding: 24px 0;

  .bk-form {
    padding: 0 24px;
  }

  .enumerate-wrapper {
    position: relative;
    z-index: 10;
    padding: 0 30px;
    margin-bottom: 30px;
    color: rgb(99 101 110 / 100%);
    background: rgb(255 255 255 / 100%);
    border: 1px solid rgb(221 228 235 / 100%);
    border-radius: 2px;

    .arrow {
      position: absolute;
      top: -5px;
      left: 51px;
      z-index: 10;
      width: 8px;
      height: 8px;
      background: white;
      border-top: 1px solid #dde4eb;
      border-left: 1px solid #dde4eb;
      transform: rotate(45deg);
    }

    .enum-title {
      font-size: 0;
      font-weight: bold;
      line-height: 38px;
      color: rgb(115 121 135 / 100%);

      .text,
      .icon {
        display: inline-block;
        font-size: 14px;
        vertical-align: middle;
      }

      .icon {
        margin-right: 6px;
        font-size: 16px;
      }

      .text {
        width: 95%;
        border-bottom: 1px solid #dde4eb;
      }
    }

    .type-select-wrapper {
      display: flex;
      align-items: center;
      padding: 20px 0;

      .desc {
        padding-right: 12px;
        font-size: 14px;
      }

      .king-radio-group {
        display: flex;
        align-items: center;
        width: auto;
        height: 19px;
        line-height: 19px;

        .bk-form-radio {
          padding-right: 12px;
        }
      }
    }

    .enum-settings {
      .explain {
        margin-bottom: 20px;
        font-size: 0;

        span {
          display: inline-block;
          font-size: 14px;
          vertical-align: middle;

          &.default {
            width: 56px;
          }

          &.text {
            width: 200px;
            margin-right: 10px;
            margin-left: 20px;
          }
        }
      }

      .content-list {
        padding-bottom: 10px;
        margin-bottom: 10px;
        font-size: 0;

        .select-box {
          position: relative;
          display: inline-block;
          height: 32px;
          font-size: 14px;
          vertical-align: middle;

          &.default-box {
            width: 56px;

            .king-checkbox {
              position: relative;
              margin: 0;
              text-align: center;
              vertical-align: center;

              input {
                position: relative;
                display: inline-block;
                width: 16px;
                height: 16px;
                vertical-align: middle;
                border: 1px solid #979ba5;
                border-radius: 2px;
              }
            }
          }

          ::v-deep .bk-form-content {
            width: 200px;
            margin-left: 0 !important;
          }

          > .select-text {
            width: 100%;
            height: 32px;
            padding-left: 10px;
            line-height: 32px;
            border-radius: 2px;
            outline: none;
            resize: none;
          }

          > .input-container {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            width: 100%;
            height: 100%;

            > label {
              width: 16px;
              height: 16px;
            }

            > .king-radio {
              position: relative;
              display: inline-block;
              font-size: 14px;
              color: #63656e;

              > input[type="radio"] {
                width: 16px;
                height: 16px;
                color: #fff;
                cursor: pointer;
                background-color: #fff;
                border: 1px solid #979ba5;
                border-radius: 50%;
                outline: none;
                visibility: visible;
                background-clip: content-box;
                appearance: none;

                &.is-checked {
                  padding: 3px;
                  color: #3a84ff;
                  background-color: currentcolor;
                  border-color: currentcolor;
                }
              }
            }
          }

          > .user-icon {
            position: relative;
            top: 6px;
            margin-right: 5px;
            font-size: 20px;
            color: #c7d1da;
            cursor: pointer;

            &.forbid {
              color: #c4c6cc;
              cursor: not-allowed;
            }

            &:last-child {
              margin-right: 0;
            }
          }
        }

        .hint {
          position: absolute;
          top: 32px;
          left: 0;
          color: #ea3636;
        }
      }
    }
  }

  .select-type {
    display: flex;
    padding: 0 24px 30px;
  }

  .submit-btn {
    padding: 0 24px;

    .bk-button {
      width: 76px !important;
      margin-right: 10px;
    }
  }
}
</style>
