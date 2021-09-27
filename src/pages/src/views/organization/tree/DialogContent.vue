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
  <div class="child-department-wrapper">
    <div class="add-child-wrapper" v-if="handleTabData.title === $t('添加下级组织')" data-test-id="organizationInfo">
      <ul>
        <li class="infor-list">
          <p class="desc">{{$t('组织名称')}}<span class="star">*</span></p>
          <div class="input-text">
            <input
              type="text"
              :placeholder="$t('请输入')"
              :class="['select-text',{ 'input-error': handleTabData.isNameError }]"
              v-model="childDepartment"
              v-focus
              @keydown.enter="$emit('onEnter')"
              @input="handleInputChildDepartment" />
            <i class="icon icon-user-exclamation-circle-shape" v-if="handleTabData.isNameError"></i>
            <p class="hint" v-show="handleTabData.isNameError">
              <i class="arrow"></i>
              <i class="icon-user-exclamation-circle-shape"></i>
              <span class="text">{{$t('长度为1-64位')}}</span>
            </p>
          </div>
        </li>
        <li class="infor-list">
          <p class="desc">{{$t('上级组织')}}</p>
          <p class="input-text">
            <input type="text" :placeholder="handleTabData.departName" class="select-text" disabled />
          </p>
        </li>
      </ul>
    </div>
    <!-- 重命名 -->
    <div class="editor-department-wrapper" v-if="handleTabData.title === $t('重命名')" data-test-id="catalogInfo">
      <ul>
        <li class="infor-list">
          <p class="desc">{{ renameData.type === 'catalog' ? $t('目录名称') : $t('组织名称')}}<span class="star">*</span></p>
          <div class="input-text">
            <input
              type="text"
              v-model="departmentName"
              :class="['select-text',{ 'input-error': handleTabData.isNameError }]"
              v-focus
              @keydown.enter="$emit('onEnter')"
              @input="handleInputDepartmentName" />
            <i class="icon icon-user-exclamation-circle-shape" v-if="handleTabData.isNameError"></i>
            <p class="hint" v-show="handleTabData.isNameError">
              <i class="arrow"></i>
              <i class="icon-user-exclamation-circle-shape"></i>
              <span class="text">{{$t('长度为1-64位')}}</span>
            </p>
          </div>
        </li>
      </ul>
    </div>
    <div class="set-list-name-wrapper" v-if="handleTabData.title === $t('设置列表字段')" data-test-id="fieldsData">
      <p class="description">{{$t('最多显示 10 个字段，已选')}}
        <span :class="{ 'show-error': isShowError }">{{selectLength}}</span> {{$t('个字段')}}
      </p>
      <ul class="clearfix">
        <li class="select-infor-list" v-for="(item, index) in localSetTableFields" :key="index">
          <div class="king-checkbox">
            <label class="label-text" :class="[mustSelect(item) && 'select-checked',
                                               selectLength >= 10 && !item.visible && 'not-allowed']">
              <input type="checkbox" class="checkbox select-checked" disabled v-if="mustSelect(item)">
              <input type="checkbox" class="checkbox" v-model="item.visible"
                     @click="handleCheck($event, item.visible)" v-else>
              {{item.name}}
            </label>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  directives: {
    focus: {
      // 指令的定义
      inserted(el) {
        setTimeout(() => {
          el.focus();
        }, 40);
      },
    },
  },
  props: {
    handleTabData: {
      type: Object,
      default() {
        return {};
      },
    },
    setTableFields: {
      type: Array,
      default() {
        return [];
      },
    },
    renameData: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      localSetTableFields: [],
      departmentName: '',
      childDepartment: '',
      isShowError: false,
    };
  },
  computed: {
    selectLength() {
      return this.localSetTableFields.filter(item => item.visible).length;
    },
  },
  created() {
    this.localSetTableFields = JSON.parse(JSON.stringify(this.setTableFields));
    // eslint-disable-next-line vue/no-mutating-props
    this.handleTabData.isNameError = false;
    if (this.handleTabData.title === this.$t('重命名')) {
      this.departmentName = this.renameData.item.display_name || this.renameData.item.name;
    }
  },
  methods: {
    mustSelect(item) {
      return item.key === 'username' || item.key === 'display_name' || item.key === 'department_name' || item.key === 'email';
    },
    handleInputChildDepartment() {
      this.childDepartment = this.filterValue(this.childDepartment);
    },
    handleInputDepartmentName() {
      this.departmentName = this.filterValue(this.departmentName);
    },
    filterValue(value) {
      value = value.replace(/\/|\s/g, '');
      const length = this.$getStringLength(value);
      // eslint-disable-next-line vue/no-mutating-props
      this.handleTabData.isNameError = length > 64 || length < 1;
      return value;
    },
    handleCheck(e, visible) {
      if (this.selectLength >= 10 && !visible) {
        e.preventDefault();
        this.isShowError = true;
      } else {
        this.isShowError = false;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.infor-list {
  margin-bottom: 17px;
  font-size: 14px;
  color: rgba(99, 101, 110, 1);

  &:last-child {
    margin-bottom: 0;
  }

  .desc {
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
    width: 100%;
    line-height: 36px;

    .select-text {
      display: block;
      padding: 0 36px 0 12px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  .icon-user-exclamation-circle-shape {
    position: absolute;
    right: 10px;
    top: 8px;
    font-size: 16px;
    color: #ea3636;
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

.set-list-name-wrapper {
  position: relative;

  > ul {
    margin-bottom: -16px;
  }

  .description {
    margin-bottom: 18px;
    font-size: 14px;
    color: #63656e;
    line-height: 19px;

    .show-error {
      color: red;
    }
  }
}

.select-infor-list {
  float: left;
  font-size: 0;

  > .king-checkbox {
    display: flex;
    align-items: center;
    margin: 0 10px 18px 0;
    font-size: 14px;

    .label-text {
      display: flex;
      align-items: center;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      width: 190px;
      cursor: pointer;

      .checkbox {
        flex-shrink: 0;
        width: 14px;
        height: 14px;
        margin-right: 6px;
        background-position: 0 -95px;

        &.select-checked {
          background-position: -99px -95px;
        }

        &:checked {
          background-position: -33px -95px;
        }
      }

      &.select-checked {
        cursor: not-allowed;

        .select-checked {
          cursor: not-allowed;
        }
      }

      &.not-allowed {
        cursor: not-allowed;

        input {
          cursor: not-allowed;
        }
      }
    }
  }
}
</style>
