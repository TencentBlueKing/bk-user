<template>
  <bk-form
    ref="formRef"
    :model="formModel"
    :rules="rules"
    form-type="vertical"
    class="flex flex-col divide-y divide-[#EAEBF0]"
  >
    <DataSourceBasicInfo v-model="name" />
    <Row :title="$t('冲突配置')">
      <div class="w-[560px]">
        <ConflictTips
          v-if="showTips"
          type="alert"
          :has-other-data-source="hasOtherDataSource"
        />
        <ConflictConfig
          ref="conflictConfigRef"
          :config="conflictConfig"
          :disabled="conflictDisabled"
          class="mt-[16px]"
        />
      </div>
    </Row>
  </bk-form>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';

import ConflictConfig from '@/components/conflict-config/ConflictConfig.vue';
import ConflictTips from '@/components/conflict-config/ConflictTips.vue';
import DataSourceBasicInfo from '@/components/DataSourceBasicInfo.vue';
import Row from '@/components/layouts/ItemRow.vue';
import { useConflictRules } from '@/hooks/useConflictRules';
import { UsernameGenerateConfig } from '@/http/types/dataSourceFiles';

interface Props {
  conflictConfig: UsernameGenerateConfig;
  /** 编辑态冲突配置只读（后端不支持更新） */
  conflictDisabled?: boolean;
  hasOtherDataSource?: boolean;
  /** 冲突规则提示仅创建态展示 */
  showTips?: boolean;
}

const name = defineModel<string>('name', { required: true });

withDefaults(defineProps<Props>(), {
  conflictDisabled: false,
  hasOtherDataSource: false,
  showTips: false,
});

const formRef = ref();
const conflictConfigRef = ref();
const { rules } = useConflictRules(conflictConfigRef);

const formModel = computed(() => ({ name: name.value }));

/** 校验名称与冲突规则，供容器在「下一步 / 保存」前调用 */
const handleValidate = async () => formRef.value?.validate().catch(() => false) ?? false;

const getData = () => conflictConfigRef.value?.getData() ?? { rule: 'unchanged', prefix: '', suffix: '' };

defineExpose({
  validate: handleValidate,
  getData,
});
</script>
