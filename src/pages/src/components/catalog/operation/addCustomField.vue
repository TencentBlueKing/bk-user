<template>
  <div class="user-content" v-show="type === 'add'">
    <div class="user-item" v-for="(item, index) in addFieldList" :key="index">
      <bk-select v-model="item.key" class="custom-select" @change="handleChange">
        <bk-option
          class="custom-option"
          v-for="option in customField"
          :key="option.key"
          :id="option.key"
          :name="option.key"
          :disabled="option.disabled">
          <span>{{option.key}}</span>
        </bk-option>
      </bk-select>
      <bk-input class="user-value" v-model="item.value" />
      <i class="icon-user-plus_circle i-add" @click="handleClickAdd"></i>
      <i class="icon-user-minus_circle i-del" @click="handleClickDel(item, index)"></i>
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
    customField: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      addFieldList: [{ key: '', value: '' }],
    };
  },
  watch: {
    addFieldList(val) {
      this.$emit('upAddFieldList', val);
    },
  },
  methods: {
    handleClickAdd() {
      this.addFieldList.push({ key: '', value: '' });
    },
    handleClickDel(item, index) {
      if (index === 0) {
        this.addFieldList.push({ key: '', value: '' });
      }
      this.addFieldList.splice(index, 1);
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
