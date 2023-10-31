<template>
  <div>
    <div class="field-mapping">
      <div class="field-title">
        <bk-form-item class="w-[240px]" label="用户管理字段" required />
        <bk-form-item class="w-[100px]" label="映射关系" />
        <bk-form-item class="w-[240px]" label="API返回字段" required />
      </div>
      <div class="field-content" v-for="(item, index) in fieldSettingData.field_mapping.builtin_fields" :key="index">
        <div class="field-name">
          <bk-input :value="`${item.display_name}（${item.name}）`" readonly />
        </div>
        <bk-select
          class="field-conditions"
          :clearable="false"
          v-model="item.mapping_operation"
          disabled>
          <bk-option
            v-for="option in customConditions"
            :key="option.key"
            :id="option.key"
            :name="option.name">
            <span>{{option.name}}</span>
          </bk-option>
        </bk-select>
        <bk-form-item
          :property="`field_mapping.builtin_fields.${index}.source_field`"
          :rules="rules.source_field">
          <bk-select
            class="w-[240px]"
            v-model="item.source_field"
            @change="(val, oldVal) => emit('changeApiFields', val, oldVal)">
            <bk-option
              v-for="option in apiFields"
              :key="option.key"
              :id="option.key"
              :name="option.key"
              :disabled="option.disabled">
              <span>{{option.key}}</span>
            </bk-option>
          </bk-select>
        </bk-form-item>
      </div>
    </div>
    <div class="custom-field" v-for="(item, index) in fieldSettingData.addFieldList" :key="index">
      <bk-form-item
        :property="`addFieldList.${index}.target_field`"
        :rules="rules.target_field">
        <bk-select
          class="field-name"
          v-model="item.target_field"
          @change="(val, oldVal) => emit('changeCustomField', val, oldVal)">
          <bk-option
            v-for="option in fieldSettingData.field_mapping.custom_fields"
            :key="option.name"
            :id="option.name"
            :name="`${option.display_name}（${option.name}）`"
            :disabled="option.disabled">
            <span>{{option.display_name}}（{{option.name}}）</span>
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-select class="field-conditions" v-model="item.mapping_operation" disabled>
        <bk-option
          v-for="option in customConditions"
          :key="option.key"
          :id="option.key"
          :name="option.name">
          <span>{{option.name}}</span>
        </bk-option>
      </bk-select>
      <bk-form-item
        :property="`addFieldList.${index}.source_field`"
        :rules="rules.source_field">
        <bk-select
          class="field-name"
          v-model="item.source_field"
          @change="(val, oldVal) => emit('changeApiFields', val, oldVal)">
          <bk-option
            v-for="option in apiFields"
            :key="option.key"
            :id="option.key"
            :name="option.key"
            :disabled="option.disabled">
            <span>{{option.key}}</span>
          </bk-option>
        </bk-select>
      </bk-form-item>
      <i class="user-icon icon-minus-fill" @click="() => emit('handleDeleteField', item, index)" />
    </div>
    <bk-button class="add-field" text theme="primary" @click="() => emit('handleAddField')">
      <i class="user-icon icon-add-2 mr8" />
      新增字段映射
    </bk-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

defineProps({
  fieldSettingData: {
    type: Object,
    default: () => ({}),
  },
  apiFields: {
    type: Array,
    default: () => ([]),
  },
  rules: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(['changeApiFields', 'handleAddField', 'handleDeleteField', 'changeCustomField']);

const customConditions = ref([
  { name: '直接', key: 'direct' },
  { name: '表达式', key: 'expression' },
]);
</script>

<style lang="less" scoped>
.field-mapping {
  .field-title {
    display: flex;
  }

  .field-content {
    display: flex;
    margin-left: 64px;

    .field-name {
      width: 240px;
      margin-right: 16px;
      margin-bottom: 20px;
    }

    .field-conditions {
      width: 100px;
      margin-bottom: 20px;
    }
  }

  .bk-form-item {
    padding-bottom: 0 !important;
    margin-bottom: 0 !important;
    margin-left: 16px !important;

    &:first-child {
      margin-left: 64px !important;
    }
  }
}

.custom-field {
  display: flex;
  margin-bottom: 20px;
  align-items: center;

  .bk-form-item {
    padding-bottom: 0 !important;
    margin-bottom: 0 !important;
    margin-left: 0 !important;

    &:first-child {
      margin-left: 64px !important;
    }
  }

  .field-name, .bk-input {
    width: 240px;
  }

  .field-conditions {
    width: 100px;
    margin: 0 16px;
  }

  .icon-minus-fill {
    margin-left: 16px;
    font-size: 16px;
    color: #dcdee5;
    cursor: pointer;

    &:hover {
      color: #c4c6cc;
    }
  }
}

.add-field {
  margin-bottom: 24px;
  margin-left: 64px;
  font-size: 14px;
}
</style>
