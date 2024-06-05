<template>
  <bk-popover
    placement="bottom-start"
    theme="light"
    width="500"
    trigger="manual"
    :is-show="isShow"
    @after-hidden="Cancel"
    z-index="2000"
  >
    <bk-button v-if="count === 0" text theme="primary" @click="handleShow">
      <i class="user-icon icon-canshu mr-[6px]"></i>
      {{ $t('配置查询参数') }}
    </bk-button>
    <bk-button v-else text theme="primary" @click="handleShow">
      <i class="user-icon icon-canshu"></i>
      {{ $t('已配置x项查询参数', { count }) }}
    </bk-button>
    <template #content>
      <div class="config-params">
        <p class="title">
          <i class="user-icon icon-info-i"></i>
          {{ $t('查询参数(Query Parameters)：如/staffs？name=value: 出现在？后面，由&分隔。') }}
        </p>
        <bk-form
          class="config-form user-scroll-y"
          ref="formRef"
          form-type="vertical"
          :model="dataList">
          <div
            class="content"
            v-for="(item, index) in dataList"
            :key="index">
            <bk-form-item
              class="w-[200px] mr-[8px]"
              error-display-type="tooltips"
              :property="`${index}.key`"
              :rules="rules.key">
              <bk-input
                :placeholder="$t('请输入Key')"
                v-model="item.key"
                @input="$emit('updateStatus')" />
            </bk-form-item>
            <bk-form-item
              class="w-[200px] mr-[10px]"
              error-display-type="tooltips"
              :property="`${index}.value`"
              :rules="rules.value">
              <bk-input
                :placeholder="$t('请输入Value')"
                v-model="item.value"
                @input="$emit('updateStatus')" />
            </bk-form-item>
            <i class="user-icon icon-plus-fill" @click="addParams" />
            <bk-button
              text
              :disabled="dataList.length === 1"
              @click="deleteParams(index)">
              <i :class="['user-icon icon-minus-fill', { 'forbid': dataList.length === 1 }]" />
            </bk-button>
          </div>
        </bk-form>
        <div class="footer">
          <bk-button theme="primary" size="small" @click="handleVerify">
            {{ $t('确定') }}
          </bk-button>
          <bk-button size="small" @click="Cancel">
            {{ $t('取消') }}
          </bk-button>
        </div>
      </div>
    </template>
  </bk-popover>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';

import { useValidate } from '@/hooks';

const validate = useValidate();

const emit = defineEmits(['saveParams', 'updateStatus']);
const props = defineProps({
  paramsList: {
    type: Array,
    default: () => ([]),
  },
  currentId: {
    type: Number,
  },
});

const dataList = ref(JSON.parse(JSON.stringify(props.paramsList)));
const formRef = ref();
const isShow = ref(false);
const count = ref(0);

const rules = {
  key: [validate.required],
  value: [validate.required],
};
// 已配置查询数量
watch(() => props.paramsList, (value) => {
  count.value = value.every(({ key, value }) => !key && !value) ? 0 : value.length;
  if (count.value === 0) dataList.value = JSON.parse(JSON.stringify(props.paramsList));
}, {
  deep: true,
  immediate: true,
});

onMounted(() => {
  if (props.currentId) {
    setTimeout(() => {
      dataList.value = JSON.parse(JSON.stringify(props.paramsList));
    }, 500);
  }
});

const handleShow = () => {
  if (!props.paramsList.length) {
    dataList.value.push({ key: '', value: '' });
    emit('saveParams', dataList.value);
  }
  isShow.value = true;
};

const Cancel = () => {
  dataList.value = JSON.parse(JSON.stringify(props.paramsList));
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
      margin-right: 6px;
      font-size: 14px;
      color: #979BA5;
    }
  }

  .config-form {
    max-height: 300px;
    margin-bottom: 12px;
    overflow-x: hidden;
  }

  .content {
    display: flex;
    align-items: center;
    margin-bottom: 8px;

    ::v-deep .bk-form-item {
      margin-bottom: 0;
    }

    .user-icon {
      margin: 0 7px;
      font-size: 16px;
      color: #dcdee5;
      cursor: pointer;

      &:hover {
        color: #c4c6cc;
      }

      &.forbid {
        color: #EAEBF0;
      }
    }
  }

  .footer {
    padding-bottom: 10px;
    text-align: right;

    .bk-button {
      width: 64px;
      margin-right: 8px;
    }
  }
}
</style>
