import { Ref } from 'vue';

import { t } from '@/language/index';

/**
 * 冲突配置表单校验规则
 * @param conflictConfigRef - ConflictConfig 组件的 ref
 */
export const useConflictRules = (conflictConfigRef: Ref) => {
  const getConflictData = () => conflictConfigRef.value?.getData() ?? { strategy: 'manual', prefix: '', suffix: '' };

  const rules = {
    nameGeneration: [
      {
        required: true,
        validator: () => {
          const { strategy, prefix, suffix } = getConflictData();
          if (strategy === 'add_affix') {
            return !!(prefix || suffix);
          }
          return true;
        },
        message: () => {
          const mode = conflictConfigRef.value?.nameGeneration;
          return mode === 'add_suffix' ? t('请输入后缀') : t('请输入前缀');
        },
        trigger: 'blur',
      },
    ],
  };

  return { rules, getConflictData };
};
