<!--
  - TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
  - Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
  - Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at http://opensource.org/licenses/MIT
  - Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
  - an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
  - specific language governing permissions and limitations under the License.
  -->
<template>
  <div class="user-content" v-show="type === 'set'">
    <div class="user-item" v-for="(item, index) in setFieldList" :key="index">
      <bk-select v-model="item.key" class="custom-select" :clearable="false" @change="handleChange">
        <bk-option
          class="custom-option"
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
      <i class="icon-user-minus_circle i-del" @click="handleClickDel(item,index)"></i>
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
      default: () => ([]),
    },
    customField: {
      type: Object,
      default: () => ({}),
    },
    current: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      setFieldList: [],
    };
  },
  watch: {
    setFieldList(val) {
      this.$emit('upSetFieldList', val);
    },
    current: {
      immediate: true,
      handler(val) {
        if (val === 3) {
          if (Object.keys(this.extendFields).length === 0 || this.extendFields.length === 0) {
            this.setFieldList.push({ key: '', value: '' });
          } else {
            this.extendFields.forEach((item) => {
              this.customField.forEach((k) => {
                if (item.key === k.key) {
                  k.disabled = true;
                }
              });
              this.setFieldList.push(item);
            });
          }
        }
      },
    },
  },
  methods: {
    handleClickAdd() {
      this.setFieldList.push({ key: '', value: '' });
    },
    handleClickDel(item, index) {
      if (index === 0 && this.setFieldList.length === 1) {
        this.handleClickAdd();
      }
      this.setFieldList.splice(index, 1);
      this.customField.forEach((element) => {
        if (element.key === item.key) {
          element.disabled = false;
        }
      });
    },
    handleChange(newValue, oldValue) {
      this.customField.forEach((element) => {
        if (element.key === newValue) {
          element.disabled = true;
        } else if (element.key === oldValue) {
          element.disabled = false;
        }
      });
    },
  },
};
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
