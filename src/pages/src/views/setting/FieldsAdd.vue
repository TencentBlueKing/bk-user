<template>
  <div class="fields-add-wrapper user-scroll-y">
    <bk-form ref="fieldsRef" form-type="vertical" :model="fieldsInfor" :rules="rulesFields">
      <bk-form-item label="字段名称" property="name" required>
        <bk-input
          placeholder="最多不得超过12个字符（6个汉字）"
          :disabled="fieldsInfor.builtin"
          v-model="fieldsInfor.name" />
      </bk-form-item>
      <bk-form-item label="英文标识" property="key" required>
        <bk-input
          :disabled="isEdit"
          v-model="fieldsInfor.key" />
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
    <div class="enumerate-wrapper" v-if="state.isShowEg">
      <i class="arrow"></i>
      <h4 class="enum-title">
        <i class="icon icon-user-cog"></i>
        <span class="text">枚举设置</span>
      </h4>
      <div class="type-select-wrapper">
        <p class="desc">枚举类型</p>
        <bk-radio-group class="king-radio-group" v-model="fieldsInfor.type">
          <bk-radio
            label="one_enum"
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
                  v-if="fieldsInfor.type === 'one_enum'"
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
            <div class="select-box text-box">
              <input
                type="text"
                :class="['select-text', { 'input-error': item.isErrorValue }]"
                v-model="item.value"
                @keyup.enter="addEg"
                @blur="verifyEgValue(item)"
                @focus="hiddenEgError(item)"
              />
              <p class="hint" v-show="item.isErrorValue">
                该字段是必填项
              </p>
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
        :value="fieldsInfor.require"
        :disabled="fieldsInfor.builtin"
        v-model="fieldsInfor.require">
        <bk-popover content="该字段在用户信息里必须填写" placement="top">
          <span>必填</span>
        </bk-popover>
      </bk-checkbox>
      <bk-checkbox
        :value="fieldsInfor.unique"
        :disabled="isEdit"
        v-model="fieldsInfor.unique">
        <bk-popover content="该字段在不同用户信息里不能相同" placement="top">
          <span>唯一</span>
        </bk-popover>
      </bk-checkbox>
      <bk-checkbox
        :value="fieldsInfor.editable"
        v-model="fieldsInfor.editable"
        :disabled="fieldsInfor.builtin">
        <bk-popover content="该字段在用户信息里可编辑" placement="top">
          <span>可编辑</span>
        </bk-popover>
      </bk-checkbox>
    </div>
    <div class="submit-btn">
      <bk-button theme="primary" @click="submitInfor">保存</bk-button>
      <bk-button theme="default" @click="$emit('handleCancel')">取消</bk-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from 'vue';

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

const fieldsRef = ref();
let fieldsInfor = reactive({
  name: '',
  key: '',
  type: 'one_enum',
  require: false,
  unique: false,
  editable: true,
  builtin: false,
  default: 0,
  options: [{
    id: 0, value: '', isErrorValue: false,
  }, {
    id: 1, value: '', isErrorValue: false,
  }],
  multiple: ['editable'],
});
const state = reactive({
  defaultSelected: 'string',
  isDeleteOption: true,
  nameError: '',
  isRepeatClick: false,
  // 是否是枚举，显示对应的内容
  isShowEg: false,
});
const verifyInfor = reactive({
  name: false,
  englishMark: false,
  egId: false,
  egValue: false,
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
  name: [
    {
      required: true,
      message: '必填项',
      trigger: 'blur',
    },
    {
      validator: (value: string) => value.length <= 12,
      message: '最多不得超过12个字符（6个汉字）',
      trigger: 'blur',
    },
  ],
  key: [
    {
      required: true,
      message: '必填项',
      trigger: 'blur',
    },
    {
      validator: (value: string) => /^[a-zA-Z]+$/.test(value),
      message: '由英文字母组成',
      trigger: 'blur',
    },
  ],
};

const isEdit = computed(() => props?.setType === 'edit');

watch(() => fieldsInfor.type, (val) => {
  if (!props?.currentEditorData?.id) {
    fieldsInfor.default = val === 'multi_enum' ? [0] : 0;
  }
});

watch(() => fieldsInfor.options.length, (val) => {
  if (state.defaultSelected === 'enum') {
    state.isDeleteOption = !(val <= 1);
  }
});

const initData = () => {
  if (props?.currentEditorData?.id) {
    fieldsInfor = JSON.parse(JSON.stringify(props.currentEditorData));
    if (fieldsInfor.type === 'one_enum' || fieldsInfor.type === 'multi_enum') {
      state.defaultSelected = 'enum';
      fieldsInfor.default = fieldsInfor.type === 'one_enum'
        ? Number(fieldsInfor.default)
        : fieldsInfor.default.slice(1, fieldsInfor.default.length - 1).split(',')
          .map(item => Number(item));
    } else {
      state.defaultSelected = fieldsInfor.type;
    }
  }
};
initData();

// 下拉框 选择对应的类型，布尔值 字符串 枚举 数值
// eslint-disable-next-line no-unused-vars
const selectedType = (newType, oldType) => {
  window.changeInput = true;
  if (newType === 'enum') {
    state.isShowEg = true;
    // 如果选择了枚举值 type 设置为单选
    if (fieldsInfor.type.indexOf('enum') === -1) {
      fieldsInfor.type = 'one_enum';
    }
  } else {
    fieldsInfor.type = newType;
    state.isShowEg = false;
  }
};
// 失焦校验枚举
const verifyEgValue = (item) => {
  if (!item.value.length) {
    item.isErrorValue = true;
  }
};
// 获焦隐藏枚举的错误提示
const hiddenEgError = (item) => {
  item.isErrorValue = false;
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
    isErrorValue: false,
  };
  fieldsInfor.options.push(param);
};
const getByteLen = (str) => {
  // 匹配所有的中文
  const reg = /[\u4E00-\u9FA5]/;
  let len = 0;
  // 去掉前后空格
  str = str.replace(/(^\s+)|(\s+$)/g, '').replace(/\s/g, '');
  for (let i = 0; i < str.length; i++) {
    if (reg.test(str[i])) {
      len += 2;
    } else {
      len += 1;
    }
  }
  return len;
};
// 表单校验
const submitInfor = () => {
  fieldsRef.value.validate();
  if (state.isShowEg) {
    fieldsInfor.options.forEach((option) => {
      if (!option.value.length) {
        option.isErrorValue = true;
      }
    });
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

          &.text-box {
            width: 200px;
            margin: 0 20px;
          }

          > .select-text {
            width: 100%;
            height: 32px;
            padding-left: 10px;
            line-height: 32px;
            border: 1px solid #c4c6cc;
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
