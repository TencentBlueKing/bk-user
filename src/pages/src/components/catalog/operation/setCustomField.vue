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
  <div class="user-content" v-show="type === 'set'">
    <div class="user-item" v-for="(item, index) in setFieldList" :key="index">
      <bk-select v-model="item.key" class="custom-select" :clearable="false" @change="handleChange" >
        <bk-option class="custom-option"
          v-for="(value,key) in customField"
          :key="key"
          :id="value.key"
          :name="value.key"
          :disabled="value.disabled">
          <span>{{value.key}}</span>
        </bk-option>
      </bk-select>
      <bk-input class="user-value" v-model="item.value" />
      <i class="icon-user-plus_circle i-add" @click="handleClickAdd"></i>
      <i :class="['icon-user-minus_circle i-del', {'delete': setFieldList.length === 1}]" @click="handleClickDel(item,index)"></i>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    type: {
      type: String,
      default: '',
    },
    extendFields: {
      type: Array,
      default: () => {[]},
    },
    customField: {
      type: Object,
      default: () => {},
    },
    setFieldList: {
      type: Array,
      default: () => {[]}
    }
  },
  data() {
    return {}
  },
  watch: {
    extendFields: {
      immediate: true,
      handler(val) {
        if (JSON.stringify(val) == '{}') {
          this.setFieldList.push({ key: '', value: '' });
        } else {
          val.forEach(item => {
            this.customField.forEach(k => {
              if (item.key === k.key) {
                k.disabled = true;
              }
            })
            this.setFieldList.push(item);
          })
          
        }
      }
    }
  },
  methods: {
    handleClickAdd() {
      this.setFieldList.push({ key: '', value: '' });
    },
    handleClickDel(item, index) {
      this.setFieldList.splice(index, 1);
      this.customField.forEach(element => {
        if (element.key === item.key) {
          element.disabled = false;
        } 
      });
    },
    handleChange(newValue, oldValue) {
      this.customField.forEach(element => {
        if (element.key === newValue) {
          element.disabled = true;
        } else if (element.key === oldValue) {
          element.disabled = false;
        }
      });
    }
  },
}
</script>

<style lang="scss" scoped>
.user-content {
  .user-item {
    display: flex;
    margin: 15px 0;
    .bk-form-control {
      width: 400px;
      margin-left: 30px;
    }
    .custom-select {
      width: 400px;
      margin-left: 30px;
    }
    .i-add, .i-del {
      font-size: 18px;
      color: #3A84FF;
      line-height: 32px;
      margin-left: 15px;
      &:hover {
        cursor: pointer;
      }
    }
    .delete {
      pointer-events: none;
      cursor: default;
    }
    .user-key {
      position: relative;
      &::before {
        content: '*';
        display: inline;
        width: 30px;
        height: 30px;
        position: absolute;
        left: -19px;
        top: 9px;
        font-size: 14px;
        color: #EA3536;
      }
    }
    .user-value {
      position: relative;
      &::before {
        content: '=';
        display: inline;
        width: 30px;
        height: 30px;
        position: absolute;
        left: -20px;
        top: 5px;
        font-size: 14px;
        color: #FE9C00;
      }
    }
  }
}
</style>