<template>
  <div class="operation-wrapper user-scroll-y">
    <bk-form
      class="operation-content"
      ref="basicRef"
      form-type="vertical"
      :model="formData"
      :rules="rulesBasicInfo">
      <div class="operation-card">
        <div class="operation-content-title">{{ $t('基本信息') }}</div>
        <div class="operation-content-info">
          <bk-form-item class="w-[590px]" :label="$t('策略名称')" property="name" required>
            <bk-input v-model="formData.name" :placeholder="validate.name.message" @focus="handleChange" />
          </bk-form-item>
        </div>
      </div>
      <div class="operation-card">
        <div class="operation-content-title">{{ $t('目标租户1') }}</div>
        <div class="operation-content-info flex">
          <bk-form-item class="w-[340px]" :label="$t('租户ID')" property="tenant_id" required>
            <bk-input
              v-model="formData.tenant_id"
              type="textarea"
              autosize
              :resize="false"
              @focus="handleChange" />
          </bk-form-item>
          <i class="user-icon icon-arrow-right"></i>
          <bk-form-item class="w-[340px]" :label="$t('租户名称')" required>
            <div class="tenant-name"></div>
          </bk-form-item>
        </div>
      </div>
      <!-- 一期不做 -->
      <!-- <div class="operation-card">
        <div class="operation-content-title">{{ $t('协同数据') }}</div>
        <div class="operation-content-info">
          <bk-form-item :label="$t('协同范围')" required>
            <bk-radio-group v-model="formData.methods">
              <bk-radio-button label="organization">{{ $t('组织架构选择') }}</bk-radio-button>
              <bk-radio-button label="manual">{{ $t('手动输入') }}</bk-radio-button>
            </bk-radio-group>
            <SetDepartment v-if="formData.methods === 'organization'" :initial-departments="[]" />
          </bk-form-item>
        </div>
      </div> -->
      <div class="operation-card">
        <div class="operation-content-title">{{ $t('字段设置') }}</div>
        <div class="operation-content-info flex">
          <bk-form-item class="w-[350px]" :label="$t('同步范围')" required>
            <bk-radio-group
              v-model="formData.sync_type"
            >
              <bk-radio label="all">{{ $t('所有字段') }}</bk-radio>
              <bk-radio label="appoint">{{ $t('指定字段') }}</bk-radio>
              <bk-radio label="basics">{{ $t('仅基础字段') }}</bk-radio>
            </bk-radio-group>
          </bk-form-item>
          <bk-form-item
            v-if="formData.sync_type === 'appoint'"
            class="w-[450px]"
            :label="$t('字段选择')"
            required
          >
            <bk-select
              v-model="formData.fields"
              class="bk-select"
              filterable
              multiple
            >
              <bk-option
                v-for="(item, index) in dataSourceList"
                :id="item.value"
                :key="index"
                :name="item.label"
              />
            </bk-select>
          </bk-form-item>
        </div>
        <div class="operation-content-info mt-[24px]">
          <bk-form-item class="w-[800px]" :label="$t('字段预览')">
            <bk-table
              :data="tableData"
              :border="['outer']"
              show-overflow-tooltip>
              <template #empty>
                <Empty
                  :is-data-empty="isDataEmpty"
                  :is-data-error="isDataError"
                  @handleUpdate="handleUpdate"
                />
              </template>
              <bk-table-column prop="username" :label="$t('用户名')" />
              <bk-table-column prop="full_name" :label="$t('中文名')" />
              <bk-table-column prop="email" :label="$t('邮箱')" />
              <bk-table-column prop="phone" :label="$t('手机号')" />
              <bk-table-column prop="organization" :label="$t('组织')" />
            </bk-table>
          </bk-form-item>
        </div>
      </div>
    </bk-form>
    <div class="footer fixed">
      <bk-button theme="primary" @click="handleSave">
        {{ $t('保存并启用') }}
      </bk-button>
      <bk-button @click="() => $emit('handleCancelEdit')">
        {{ $t('取消') }}
      </bk-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';

import Empty from '@/components/Empty.vue';
import { useValidate } from '@/hooks';

defineEmits(['handleCancelEdit']);

const props = defineProps({
  config: {
    type: Object,
    default: {},
  },
});

const validate = useValidate();
const basicRef = ref();

const formData = reactive({
  ...props.config.data,
});

const dataSourceList = ref([
  {
    value: 'climbing',
    label: '爬山',
  },
  {
    value: 'fitness',
    label: '健身',
  },
  {
    value: 'bike',
    label: '骑车',
  },
  {
    value: 'dancing',
    label: '跳舞',
  },
  {
    value: 'sleep',
    label: '睡觉',
    disabled: true,
  },
]);

const rulesBasicInfo = {
  name: [validate.required, validate.name],
  tenant_id: [validate.required],
};

const tableData = ref([]);
const isDataEmpty = ref(false);
const isDataError = ref(false);

onMounted(() => {
  isDataEmpty.value = false;
  isDataError.value = false;
  setTimeout(() => {
    if (tableData.value.length === 0) {
      isDataEmpty.value = true;
    }
  }, 1000);
});

const handleChange = () => {
  window.changeInput = true;
};

const handleSave = async () => {
  await basicRef.value.validate();
};
</script>

<style lang="less" scoped>
.operation-wrapper {
  position: relative;
  height: 100%;
  padding-bottom: 48px;
  overflow: auto;
  background: #f5f7fa;

  .operation-content {
    padding: 0 24px;

    .operation-card {
      padding-bottom: 24px;
      margin: 16px 0;
      list-style: none;
      background: #fff;
      border-radius: 2px;
      box-shadow: 0 2px 4px 0 #1919290d;

      .operation-content-title {
        padding: 16px 0 16px 24px;
        font-size: 14px;
        font-weight: 700;
        color: #63656e;
      }

      .operation-content-info {
        padding-left: 64px;

        :deep(.bk-form-item) {
          &:last-child {
            margin-bottom: 0;
          }
        }
      }

      .flex {
        display: flex;
        align-items: center;

        :deep(.bk-form-item) {
          margin-bottom: 0;
        }

        .user-icon {
          margin: 26px 18px 0;
          font-size: 18px;
          color: #C4C6CC;
        }

        .tenant-name {
          min-height: 32px;
          padding: 0 12px;
          background: #F5F7FA;
          border-radius: 2px;
        }
      }
    }
  }

  .footer {
    position: absolute;
    padding: 0 24px;

    .bk-button {
      min-width: 88px;
      margin-right: 8px;
    }
  }

  .fixed {
    position: fixed;
    bottom: 0;
    z-index: 9;
    width: 100%;
    height: 48px;
    margin-bottom: 0;
    line-height: 48px;
    background: #FAFBFD;
    box-shadow: 0 -1px 0 0 #DCDEE5;
  }
}

.set-department-wrapper {
  width: 640px;
  padding: 24px 0;
  margin-top: 12px;
  border: 1px solid #DCDEE5;
  border-radius: 2px;
}
</style>
