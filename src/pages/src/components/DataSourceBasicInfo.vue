<template>
  <Row :title="$t('基础信息')">
    <bk-form-item
      class="w-[560px]"
      :label="$t('数据源名称')"
      property="name"
      :rules="formRules.name"
      required
    >
      <bk-input
        v-model="name"
        :maxlength="64"
        :placeholder="$t('请输入数据源名称')"
      />
    </bk-form-item>
  </Row>
</template>

<script setup lang="ts">
import Row from '@/components/layouts/ItemRow.vue';
import { t } from '@/language/index';

const name = defineModel<string>({ required: true });

const formRules = {
  name: [
    {
      validator: (value: string) => Boolean(value?.trim()),
      message: t('请输入数据源名称'),
      trigger: 'blur',
    },
  ]
};

</script>

