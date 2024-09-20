<template>
  <div>
    <bk-form-item
      v-for="(item, index) in extras"
      :key="index"
      :label="item.display_name"
      :property="item.name"
      :required="item.required"
      :rules="rules.default">
      <!-- :property="`extras.${index}.default`" -->
      <bk-input
        v-if="item.data_type === 'string'"
        v-model.trim="item.value"
        :maxlength="64"
        :disabled="!item.manager_editable"
        @focus="handleChange"
      />
      <bk-input
        v-else-if="item.data_type === 'number'"
        type="number"
        v-model.trim="item.value"
        :disabled="!item.manager_editable"
        :max="4294967296"
        :min="0"
        @focus="handleChange"
      />
      <bk-select
        v-else
        v-model="item.value"
        :clearable="!item.required"
        :multiple="item.data_type === 'multi_enum'"
        :disabled="!item.manager_editable"
        @change="handleChange">
        <bk-option
          v-for="(option, i) in item.options"
          :key="i"
          :id="option.id"
          :name="option.value">
        </bk-option>
      </bk-select>
    </bk-form-item>
  </div>
</template>

<script setup lang="ts">
defineProps({
  extras: {
    type: Array,
    default: () => ([]),
  },
  rules: {
    type: Object,
    default: () => ({}),
  },
});

const handleChange = () => {
  window.changeInput = true;
};
</script>

<style>

</style>
