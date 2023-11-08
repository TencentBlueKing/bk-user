<template>
  <bk-popover
    placement="bottom-start"
    theme="light"
    width="480"
    trigger="click"
    :is-show="isShow"
    @after-hidden="Cancel"
  >
    <bk-button v-if="count === 0" text theme="primary" @click="handleShow">
      <i class="user-icon icon-canshu"></i>
      配置查询参数
    </bk-button>
    <bk-button v-else text theme="primary" @click="handleShow">
      <i class="user-icon icon-canshu"></i>
      已配置{{ count }}项查询参数
    </bk-button>
    <template #content>
      <div class="config-params">
        <p class="title">
          <i class="user-icon icon-info-i"></i>
          查询参数(Query Parameters)：如/staffs?name=value: 出现在?后面, 由&分隔。
        </p>
        <bk-form
          ref="formRef"
          form-type="vertical"
          :model="dataList">
          <div
            class="content"
            v-for="(item, index) in dataList"
            :key="index">
            <bk-form-item
              :property="`${index}.key`"
              :rules="rules.key">
              <bk-input
                class="key"
                placeholder="请输入Key"
                v-model="item.key"
                @change="handleChange" />
            </bk-form-item>
            <bk-form-item
              :property="`${index}.value`"
              :rules="rules.value">
              <bk-input
                class="value"
                placeholder="请输入Value"
                v-model="item.value"
                @change="handleChange" />
            </bk-form-item>
            <i class="user-icon icon-minus-fill" @click="deleteParams(index)" />
          </div>
        </bk-form>
        <div class="add-query-params">
          <bk-button text theme="primary" @click="addParams">
            <i class="user-icon icon-add-2 mr8" />
            新增查询参数
          </bk-button>
          <div>
            <bk-button theme="primary" size="small" class="mr8" @click="handleVerify">
              确定
            </bk-button>
            <bk-button class="mr8" size="small" @click="Cancel">
              取消
            </bk-button>
          </div>
        </div>
      </div>
    </template>
  </bk-popover>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';

import useValidate from '@/hooks/use-validate';

const validate = useValidate();

const emit = defineEmits(['saveParams']);
const props = defineProps({
  paramsList: {
    type: Array,
    default: () => ([]),
  },
  currentId: {
    type: Number,
  },
});

const dataList = ref([]);
const formRef = ref();
const isShow = ref(false);
const count = ref(0);

const rules = {
  key: [validate.required],
  value: [validate.required],
};

onMounted(() => {
  if (props.currentId) {
    setTimeout(() => {
      dataList.value = props.paramsList;
      count.value = props.paramsList.length;
    }, 500);
  }
});

const handleShow = () => {
  isShow.value = true;
};

const handleChange = () => {
  window.changeInput = true;
};

const Cancel = () => {
  dataList.value = props.paramsList.filter(item => item.key !== '' && item.value !== '');
  isShow.value = false;
};

const handleVerify = async () => {
  await formRef.value.validate();
  isShow.value = false;
  window.changeInput = true;
  emit('saveParams', dataList.value);
  count.value = dataList.value.length;
};

const addParams = () => {
  dataList.value.push({ key: '', value: '' });
};

const deleteParams = (index) => {
  dataList.value.splice(index, 1);
};
</script>

<style lang="less" scoped>
.config-params {
  .title {
    margin: 12px 0;
    font-size: 12px;
    color: #63656e;

    .icon-info-i {
      margin-right: 8px;
      font-size: 14px;
      color: #979BA5;
    }
  }

  .content {
    display: flex;
    align-items: center;
    margin-bottom: 20px;

    ::v-deep .bk-form-item {
      margin-bottom: 0;
    }

    .key {
      width: 200px;
      margin-right: 8px;
    }

    .value {
      width: 200px;
      margin-right: 16px;
    }

    .icon-minus-fill {
      font-size: 16px;
      color: #dcdee5;
      cursor: pointer;

      &:hover {
        color: #c4c6cc;
      }
    }
  }

  .add-query-params {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 0 16px;
  }
}
</style>
