import { reactive } from 'vue';

import { t } from '@/language/index';

export const useTableFields = () => {
  const tableSettings = reactive({
    fields: [
      {
        name: t('用户名'),
        field: 'username',
        data_type: 'string',
        options: [],
        disabled: true,
      },
      {
        name: t('全名'),
        field: 'full_name',
        data_type: 'string',
        options: [],
      },
      {
        name: t('手机号'),
        field: 'phone',
        data_type: 'number',
        options: [],
      },
      {
        name: t('邮箱'),
        field: 'email',
        data_type: 'string',
        options: [],
      },
      {
        name: t('所属组织'),
        field: 'departments',
        data_type: 'multi_enum',
        options: [],
      },
    ],
    checked: ['username', 'full_name', 'phone', 'email', 'departments'],
    size: 'small',
    trigger: 'click',
  });

  const handleSettingChange = ({ checked, size }) => {
    tableSettings.checked = checked;
    tableSettings.size = size;
  };

  return {
    tableSettings,
    handleSettingChange,
  };
};
