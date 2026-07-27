import { Ref } from 'vue';

import { UsernameGenerateConfig } from '@/http/types/dataSourceFiles';
import { t } from '@/language/index';

/** ConflictConfig 组件通过 defineExpose 暴露的接口 */
interface ConflictConfigExposed {
  getData: () => UsernameGenerateConfig;
  nameGeneration: 'add_prefix' | 'add_suffix';
}

/**
 * 冲突配置表单校验规则
 * @param conflictConfigRef - ConflictConfig 组件的 ref
 */
export const useConflictRules = (conflictConfigRef: Ref<ConflictConfigExposed | null>) => {
  const getConflictData = () => conflictConfigRef.value?.getData() ?? { rule: 'unchange', prefix: '', suffix: '' };

  const rules = {
    nameGeneration: [
      {
        required: true,
        validator: () => {
          const { rule, prefix, suffix } = getConflictData();
          if (rule === 'add_affix') {
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

  return { rules };
};
