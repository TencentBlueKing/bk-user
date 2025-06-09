import { defineStore } from 'pinia';

import { getFields } from '@/http/settingFiles';

export const useFieldData = defineStore('useFieldData', {
  state: () => ({
    data: [],
  }),
  actions: {
    async initFieldsData() {
      const res = await getFields();
      const { builtin_fields, custom_fields } = res.data || {};
      this.data = [...builtin_fields, ...custom_fields];
    },
  },
});
