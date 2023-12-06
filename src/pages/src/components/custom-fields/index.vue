<template>
  <div>
    <bk-form-item
      v-for="(item, index) in extras"
      :key="index"
      :label="item.display_name"
      :property="`extras.${index}.default`"
      :required="item.required"
      :rules="rules.default">
      <bk-input
        v-if="item.data_type === 'string' || item.data_type === 'number'"
        :type="inputType(item.data_type)"
        v-model="item.default"
        @focus="handleChange"
      />
      <bk-select
        v-else
        v-model="item.default"
        :clearable="!item.require"
        :multiple="item.data_type === 'multi_enum'"
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
import { ref } from 'vue';

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

const inputType = (type: string) => {
  const text = ref('');
  if (type === 'string') {
    text.value = 'text';
  } else if (type === 'number') {
    text.value = 'number';
  }
  return text.value;
};

const handleChange = () => {
  window.changeInput = true;
};
</script>

<style>

</style>
