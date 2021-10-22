<!--
  - Tencent is pleased to support the open source community by making Bk-User 蓝鲸用户管理 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
  -
  - License for Bk-User 蓝鲸用户管理:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->
<template>
  <div class="segment-infor-wrapper">
    <div class="fill-text">
      <p class="desc">{{$t('字段名称')}}<span class="star">*</span></p>
      <div class="input-text">
        <input
          type="text"
          :placeholder="$t('最多不得超过12个字符（6个汉字）')"
          :class="['select-text', { 'input-error': verifyInfor.name, 'disable-input': fieldsInfor.builtin }]"
          :disabled="fieldsInfor.builtin"
          v-model="fieldsInfor.name"
          v-focus
          @blur="verifyInput('name')"
          @focus="hiddenVerify(arguments, 'name')" />
        <i class="icon icon-user-exclamation-circle-shape" v-show="verifyInfor.name"></i>
        <p class="hint" v-if="verifyInfor.name">
          <i class="arrow"></i>
          <i class="icon-user-exclamation-circle-shape"></i>
          <span class="text">{{nameError}}</span>
        </p>
      </div>
    </div>
    <div class="fill-text">
      <p class="desc">{{$t('英文标识')}}<span class="star">*</span></p>
      <div class="input-text">
        <!-- 有英文名就不能编辑，即只有新增字段才能编辑 -->
        <input
          type="text"
          :placeholder="$t('请输入')"
          :class="['select-text', { 'input-error': verifyInfor.englishMark, 'disable-input': !!currentEditorData.key }]"
          :disabled="!!currentEditorData.key"
          v-model="fieldsInfor.key"
          @blur="verifyInput('englishMark')"
          @focus="hiddenVerify(arguments, 'englishMark')" />
        <i class="icon icon-user-exclamation-circle-shape" v-show="verifyInfor.englishMark"></i>
        <p class="hint" v-show="verifyInfor.englishMark">
          <i class="arrow"></i>
          <i class="icon-user-exclamation-circle-shape"></i>
          <span class="text">{{$t('英文名称输入有误，请重新填写')}}</span>
        </p>
      </div>
    </div>
    <div class="fill-text">
      <p class="desc">{{$t('字段类型')}}<span class="star">*</span></p>
      <!-- 有英文名就不能编辑，即只有新增字段才能编辑 -->
      <bk-select v-model="defaultSelected"
                 :clearable="false"
                 :disabled="!!currentEditorData.key"
                 @change="selectedType">
        <bk-option v-for="(option, index) in typeList"
                   :key="index"
                   :id="option.id"
                   :name="option.name"
        ></bk-option>
      </bk-select>
    </div>
    <!-- 枚举类型可编辑值 内置职位字段隐藏 ID -->
    <div class="enumerate-wrapper" v-if="isShowEg || fieldsInfor.type.indexOf('enum') !== -1">
      <i class="arrow"></i>
      <h4 class="enum-title">
        <i class="icon icon-user-cog"></i>
        <span class="text">{{$t('枚举设置')}}</span>
      </h4>
      <div class="type-select-wrapper">
        <p class="desc">{{$t('枚举类型')}}</p>
        <bk-radio-group class="king-radio-group" v-model="fieldsInfor.type">
          <bk-radio value="one_enum" name="egRadio" :disabled="setType === 'edit'">{{$t('单选')}}</bk-radio>
          <bk-radio value="multi_enum" name="egRadio" :disabled="setType === 'edit'">{{$t('多选')}}</bk-radio>
        </bk-radio-group>
      </div>
      <div class="enum-settings" data-test-id="fieldData">
        <p class="explain">
          <span class="default">{{$t('默认选项')}}</span>
          <span class="text">{{$t('选项值')}}</span>
        </p>
        <ul>
          <li class="content-list" v-for="(item, index) in fieldsInfor.options" :key="index">
            <div class="select-box default-box">
              <div class="input-container">
                <label v-if="fieldsInfor.type === 'one_enum'" class="king-radio">
                  <input name="eg" type="radio" :value="index"
                         v-model="fieldsInfor.default" :class="{ 'is-checked': fieldsInfor.default === index }">
                </label>
                <label v-else class="king-checkbox king-checkbox-small">
                  <input name="egCheckbox" type="checkbox" :value="index" v-model="fieldsInfor.default">
                </label>
              </div>
            </div>
            <div class="select-box text-box">
              <input
                type="text"
                :placeholder="$t('请输入')"
                :class="['select-text', { 'input-error': item.isErrorValue }]"
                v-model="item.value"
                @keyup.enter="addEg"
                @blur="verifyEgValue(item)"
                @focus="hiddenEgError(item)" />
              <p class="hint" v-show="item.isErrorValue">
                {{$t('该字段是必填项')}}
              </p>
            </div>
            <div class="select-box icon-box">
              <i class="icon icon-user-minus_circle"
                 :class="{ 'forbid': !isDeleteOption }" @click="deleteEg(index)"></i>
              <i class="icon icon-user-plus_circle" v-if="index === fieldsInfor.options.length - 1" @click="addEg"></i>
            </div>
          </li>
        </ul>
      </div>
    </div>
    <!-- 必填 唯一 可编辑  -->
    <div class="select-type">
      <label class="king-checkbox king-checkbox-small">
        <!-- 内置字段不可设置：必填 -->
        <input type="checkbox" name="selectType"
               checked="checked"
               :disabled="currentEditorData.builtin"
               v-model="fieldsInfor.require">
        <span class="checkbox-text" v-bk-tooltips.top="$t('该字段在用户信息里必须填写')">{{$t('必填')}}</span>
      </label>
      <label class="king-checkbox king-checkbox-small">
        <!-- 编辑字段不可设置：唯一 -->
        <input type="checkbox" name="selectType" :disabled="setType === 'edit'" v-model="fieldsInfor.unique" />
        <span class="checkbox-text" v-bk-tooltips.top="$t('该字段在不同用户信息里不能相同')">{{$t('唯一')}}</span>
      </label>
      <label class="king-checkbox king-checkbox-small">
        <!-- 内置字段不能设置：可编辑 -->
        <input type="checkbox" name="selectType" v-model="fieldsInfor.editable" :disabled="currentEditorData.builtin" />
        <span class="checkbox-text" v-bk-tooltips.top="$t('该字段在用户信息里可编辑')">{{$t('可编辑')}}</span>
      </label>
    </div>
    <div class="submit-btn">
      <bk-button theme="primary" @click="submitInfor">{{$t('保存')}}</bk-button>
      <bk-button theme="default" @click="close">{{$t('取消')}}</bk-button>
    </div>
  </div>
</template>

<script>
export default {
  directives: {
    focus: {
      // 指令的定义
      inserted(el) {
        el.focus();
      },
    },
  },
  props: {
    isShow: {
      type: Boolean,
      default: false,
    },
    currentEditorData: {
      type: Object,
      default: {},
    },
    setType: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      initDate: '',
      typeList: [
        {
          id: 'string',
          name: this.$t('字符串'),
        },
        {
          id: 'enum',
          name: this.$t('枚举'),
        },
        // {
        //     id: 'bool',
        //     name: this.$t('布尔值')
        // },
        {
          id: 'number',
          name: this.$t('数值'),
        },
        {
          id: 'timer',
          name: this.$t('日期'),
        },
      ],
      defaultSelected: 'string',
      verifyInfor: {
        name: false,
        englishMark: false,
        egId: false,
        egValue: false,
      },
      fieldsInfor: {
        name: '',
        key: '',
        type: 'string',
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
      },
      // 是否是枚举，显示对应的内容
      isShowEg: false,
      egErrorText: this.$t('该字段是必填项'),
      isDeleteOption: true,
      nameError: '',
      isRepeatClick: false,
    };
  },
  watch: {
    'fieldsInfor.options'(val) {
      if (this.defaultSelected === 'enum') {
        this.isDeleteOption = !(val.length <= 1);
      }
    },
    'fieldsInfor.type'(val) {
      if (!this.currentEditorData.id) {
        this.fieldsInfor.default = val === 'multi_enum' ? [0] : 0;
      }
    },
  },
  mounted() {
    this.$nextTick(() => {
      this.initData();
    });
  },
  methods: {
    initData() {
      if (this.currentEditorData.id) {
        this.fieldsInfor = JSON.parse(JSON.stringify(this.currentEditorData));
        if (this.fieldsInfor.type === 'one_enum' || this.fieldsInfor.type === 'multi_enum') {
          this.defaultSelected = 'enum';
        } else {
          this.defaultSelected = this.fieldsInfor.type;
        }
      }
    },
    // 下拉框 选择对应的类型，布尔值 字符串 枚举 数值
    // eslint-disable-next-line no-unused-vars
    selectedType(newType, oldType) {
      if (newType === 'enum') {
        this.isShowEg = true;
        // 如果选择了枚举值 type 设置为单选
        if (this.fieldsInfor.type.indexOf('enum') === -1) {
          this.fieldsInfor.type = 'one_enum';
        }
      } else {
        this.fieldsInfor.type = newType;
        this.isShowEg = false;
      }
    },
    // 失焦验证
    verifyInput(type) {
      // 验证字段名称
      const nameLength = this.getByteLen(this.fieldsInfor.name);
      if (type === 'name') {
        this.nameError = !this.fieldsInfor.name.length ? this.$t('字段名称输入有误，请重新填写') : this.$t('最多不得超过12个字符（6个汉字）');
        this.verifyInfor.name = (!this.fieldsInfor.name.length || nameLength > 12);
      }
      // 验证英文标识
      const englishName = /[^a-zA-Z]/;
      if (type === 'englishMark' && (!this.fieldsInfor.key.length || englishName.test(this.fieldsInfor.key))) {
        this.verifyInfor.englishMark = true;
      }
    },
    // 获焦隐藏错误提示
    hiddenVerify() {
      for (let i = 0; i < arguments.length; i++) {
        // eslint-disable-next-line prefer-rest-params
        const type = arguments[i];
        this.verifyInfor[type] = false;
      }
    },
    // 失焦校验枚举
    verifyEgValue(item) {
      if (!item.value.length) {
        item.isErrorValue = true;
      }
    },
    // 获焦隐藏枚举的错误提示
    hiddenEgError(item) {
      item.isErrorValue = false;
    },
    // 删除枚举
    deleteEg(index) {
      if (this.fieldsInfor.options.length <= 1) {
        return;
      }
      this.fieldsInfor.options.splice(index, 1);
    },
    // 添加枚举类型
    addEg() {
      if (this.fieldsInfor.options.length > 100) {
        return;
      }
      const param = {
        id: this.fieldsInfor.options.length,
        value: '',
        isErrorValue: false,
      };
      this.fieldsInfor.options.push(param);
      this.$nextTick(() => {
        // 增加选项后 focus
        const inputList = this.$el.querySelectorAll('.content-list input');
        inputList[inputList.length - 1].focus();
      });
    },
    // 取消
    close() {
      this.$emit('update:isShow', false);
    },
    // 保存: 1.验证规则  2.得到对应的数据  3.判断是添加 还是编辑   4.调用对应的接口
    submitInfor() {
      // 验证
      if (!this.submitVerify()) {
        return;
      }
      let fieldsData = {};
      if (this.fieldsInfor.id) {
        // 编辑字段
        if (this.fieldsInfor.builtin === true) {
          // 编辑内置字段
          fieldsData = {
            name: this.fieldsInfor.name,
          };
        } else {
          // 编辑自定义字段
          fieldsData = {
            name: this.fieldsInfor.name,
            require: this.fieldsInfor.require,
            editable: this.fieldsInfor.editable,
          };
        }
      } else {
        // 新增字段
        fieldsData = {
          name: this.fieldsInfor.name,
          key: this.fieldsInfor.key,
          type: this.fieldsInfor.type,
          require: this.fieldsInfor.require,
          unique: this.fieldsInfor.unique,
          editable: this.fieldsInfor.editable,
          builtin: this.fieldsInfor.builtin,
        };
      }
      // 枚举
      if (this.defaultSelected === 'enum') {
        fieldsData.options = this.fieldsInfor.options.map((item) => {
          return {
            id: item.id,
            value: item.value,
          };
        });
        fieldsData.default = this.fieldsInfor.default;
      }
      this.submitData(fieldsData);
    },
    // 保存验证各个字段
    submitVerify() {
      // 校验字段名称
      const nameLength = this.getByteLen(this.fieldsInfor.name);
      if (!this.fieldsInfor.name.length || nameLength > 12) {
        this.verifyInfor.name = true;
      }
      this.nameError = !this.fieldsInfor.name.length ? this.$t('字段名称输入有误，请重新填写') : this.$t('最多不得超过12个字符（6个汉字）');
      if (!this.fieldsInfor.key.length) {
        this.verifyInfor.englishMark = true;
      }
      // 验证枚举
      let isValue = false;
      if (this.isShowEg) {
        this.fieldsInfor.options.forEach((option) => {
          if (!option.value.length) {
            isValue = true;
            option.isErrorValue = true;
            this.egErrorText = this.$t('该字段是必填项');
          }
        });
      }
      return !(this.verifyInfor.name || this.verifyInfor.englishMark || isValue);
    },
    async submitData(data) {
      // 避免重复点击
      if (this.isRepeatClick) {
        return;
      }
      try {
        this.$emit('hideBar');
        this.isRepeatClick = true;
        const res = this.currentEditorData.id
          ? await this.$store.dispatch('setting/patchFields', { id: this.currentEditorData.id, data })
          : await this.$store.dispatch('setting/postFields', { data });
        if (res.result === true) {
          this.currentEditorData.id ? this.messageSuccess(this.$t('保存成功')) : this.messageSuccess(this.$t('添加字段成功'));
          this.$emit('getFields');
        }
      } catch (e) {
        console.warn(e);
        this.$emit('showBar');
      } finally {
        this.isRepeatClick = false;
      }
    },
    getByteLen(str) {
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
    },
  },
};
</script>

<style lang="scss" scoped>
    @import '../../scss/mixins/scroller';

    .segment-infor-wrapper {
      height: 100%;
      padding-top: 10px;
      overflow: hidden;
      overflow-y: auto;

      @include scroller($backgroundColor: #e6e9ea, $width: 4px);

      .timer-wrapper {
        padding: 20px 0 0 30px;

        .title {
          margin-bottom: 10px;
          display: block;
          font-size: 14px;
          color: rgba(99, 101, 110, 1);
        }
      }
    }

    .fill-text {
      padding: 0 30px;
      margin-top: 17px;
      font-size: 14px;
      color: rgba(99, 101, 110, 1);

      .desc {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        line-height: 19px;

        .star {
          display: inline-block;
          vertical-align: middle;
          margin-left: 4px;
          color: #fe5c5c;
        }
      }

      .input-text {
        position: relative;

        .select-text {
          display: block;
          padding: 0 30px 0 12px;
          background: #fff;

          &.active {
            color: #63656e !important;
          }

          &.disable {
            color: #aaa;
          }
        }

        .icon-user-exclamation-circle-shape {
          position: absolute;
          right: 10px;
          top: 7px;
          font-size: 16px;
          color: #ea3636;
        }
      }

      .hint {
        padding: 0 10px;
        position: absolute;
        top: -42px;
        right: 0;
        height: 36px;
        line-height: 36px;
        color: #fff;
        font-size: 0;
        border-radius: 4px;
        background: #000;

        .arrow {
          position: absolute;
          bottom: -2px;
          right: 14px;
          width: 6px;
          height: 6px;
          border-top: 1px solid #000;
          border-left: 1px solid #000;
          transform: rotate(45deg);
          z-index: 10;
          background: #000;
        }

        .text,
        .icon-user-exclamation-circle-shape {
          display: inline-block;
          vertical-align: middle;
          font-size: 12px;
        }

        .icon-user-exclamation-circle-shape {
          font-size: 16px;
          margin-right: 10px;
          position: relative;
          right: 0;
          top: 0;
          color: #fff;
        }
      }
    }

    .enumerate-wrapper {
      position: relative;
      padding: 0 30px;
      margin-top: 11px;
      // max-height: 400px;
      color: rgba(99, 101, 110, 1);
      background: rgba(255, 255, 255, 1);
      border-radius: 2px;
      border: 1px solid rgba(221, 228, 235, 1);
      z-index: 10;
      // overflow: hidden;
      // overflow-y: auto;
      // @include scroller($backgroundColor: #e6e9ea, $width: 4px);
      .arrow {
        position: absolute;
        top: -5px;
        left: 51px;
        width: 8px;
        height: 8px;
        border-top: 1px solid #dde4eb;
        border-left: 1px solid #dde4eb;
        transform: rotate(45deg);
        z-index: 10;
        background: white;
      }

      .enum-title {
        line-height: 38px;
        font-weight: bold;
        color: rgba(115, 121, 135, 1);
        font-size: 0;

        .text,
        .icon {
          display: inline-block;
          vertical-align: middle;
          font-size: 14px;
        }

        .icon {
          font-size: 16px;
          margin-right: 6px;
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
            vertical-align: middle;
            font-size: 14px;

            &.default {
              width: 56px;
            }

            &.text {
              margin-left: 20px;
              margin-right: 10px;
              width: 200px;
            }
          }
        }

        .content-list {
          padding-bottom: 10px;
          font-size: 0;
          margin-bottom: 10px;

          .select-box {
            position: relative;
            display: inline-block;
            vertical-align: middle;
            font-size: 14px;
            height: 32px;

            &.default-box {
              width: 56px;

              .king-checkbox {
                position: relative;
                margin: 0;
                text-align: center;
                vertical-align: center;

                input {
                  position: absolute;
                  top: 50%;
                  left: 50%;
                  transform: translate(-50%, -50%);
                  margin: 0;
                }
              }
            }

            &.text-box {
              margin-left: 20px;
              margin-right: 10px;
              width: 200px;
            }

            > .select-text {
              padding-left: 10px;
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

                > input[type=radio] {
                  width: 16px;
                  height: 16px;
                  border: 1px solid #979ba5;
                  border-radius: 50%;
                  background-color: #fff;
                  background-clip: content-box;
                  outline: none;
                  color: #fff;
                  visibility: visible;
                  cursor: pointer;
                  appearance: none;

                  &.is-checked {
                    padding: 3px;
                    color: #3a84ff;
                    border-color: currentColor;
                    background-color: currentColor;
                  }
                }
              }
            }

            > .icon {
              position: relative;
              top: 6px;
              cursor: pointer;
              margin-right: 5px;
              font-size: 20px;
              color: #c7d1da;

              &.forbid {
                cursor: not-allowed;
                color: #c4c6cc;
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
      padding: 30px 30px 40px 30px;

      label.king-checkbox {
        display: flex;
        align-items: center;
        margin-right: 30px;
      }

      .checkbox-text {
        color: #666;
        font-size: 14px;
        outline: none;
        cursor: pointer;
      }

      > .king-checkbox > input[disabled] {
        cursor: not-allowed;

        + span {
          color: #ccc;
          cursor: not-allowed;
        }
      }
    }

    .submit-btn {
      padding: 0 30px;

      .bk-button {
        width: 76px !important;
        margin-right: 10px;
      }
    }

    .disable-input {
      color: #c4c6cc;
      background-color: #fafbfd!important;
      cursor: not-allowed;
      border-color: #dcdee5!important;
    }
</style>
