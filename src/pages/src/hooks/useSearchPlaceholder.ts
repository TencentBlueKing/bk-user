import { useI18n } from 'vue-i18n';
interface IPlaceholderOption {
  /** 标签列表，传入国际化 key，内部会自动进行国际化处理 */
  labels: string[];
  /** 超过多少个标签后展示省略号（不含等于），默认为 4 */
  maxShowCount?: number;
  /** 多个标签的分隔符，默认为 '、' */
  splitCode?: string;
  /** 组件类型：input 或 searchSelect */
  type?: 'input' | 'searchSelect';
}

/**
 * Placeholder 统一处理 Hook
 * @description 用于统一处理 placeholder，国际化词典仅需存入 labels，无需重复 "请搜索xxx"、"请输入xxx"
 *
 * @example
 * // input 类型，少量标签
 * const { createPlaceholder } = useSearchPlaceholder();
 * createPlaceholder({ type: 'input', labels: ['名称', 'ID'] })
 * // 输出: "搜索名称、ID关键字"
 *
 * @example
 * // input 类型，超过最大显示数量
 * createPlaceholder({ type: 'input', labels: ['名称', 'ID', '状态', '创建者', '更新者'] })
 * // 输出: "搜索名称、ID、状态、创建者等关键字"
 *
 * @example
 * // searchSelect 类型
 * createPlaceholder({ type: 'searchSelect', labels: ['名称', 'ID'] })
 * // 输出: "搜索名称、ID"
 */
export function useSearchPlaceholder() {
  const { t } = useI18n();

  /**
   * 创建标签字符串（带省略号处理）
   * @param labels - 标签数组
   * @param maxShowCount - 最大显示数量
   * @param splitCode - 分隔符
   * @returns 处理后的标签字符串
   */
  const createLabelsString = (labels: string[], maxShowCount: number, splitCode: string): string => {
    let suffix = '';
    if (labels.length > maxShowCount) {
      suffix = '...';
    }
    return `${labels.slice(0, maxShowCount).join(splitCode)}${suffix}`;
  };

  /**
   * 根据类型和标签数量获取对应的国际化模板 key
   * @param type - 组件类型
   * @param labelsCount - 标签数量
   * @param maxShowCount - 最大显示数量
   * @returns 国际化模板 key
   */
  const getPlaceholderTemplateKey = (
    type: 'input' | 'searchSelect',
    labelsCount: number,
    maxShowCount: number,
  ): string => {
    if (type === 'input') {
      // input 类型：根据标签数量决定使用哪个模板
      if (labelsCount <= maxShowCount) {
        return '搜索{0}关键字';
      }
      return '搜索{0}等关键字';
    }

    if (type === 'searchSelect') {
      return '搜索{0}';
    }

    return '';
  };

  /**
   * 根据配置创建 placeholder
   * @param option - 配置选项
   * @returns 生成的 placeholder
   */
  const createPlaceholder = (option: IPlaceholderOption): string => {
    const { type = 'input', labels, splitCode = '、', maxShowCount = 4 } = option;

    // 如果没有标签，返回空字符串
    if (!labels || labels.length === 0) {
      return '';
    }

    // 对 labels 进行国际化处理
    const translatedLabels = labels.map(label => t(label));

    // 创建标签字符串
    const labelsStr = createLabelsString(translatedLabels, maxShowCount, splitCode);

    // 获取模板 key
    const templateKey = getPlaceholderTemplateKey(type, labels.length, maxShowCount);

    // 返回国际化后的 placeholder
    return templateKey ? t(templateKey, [labelsStr]) : '';
  };

  return {
    createPlaceholder,
  };
}
