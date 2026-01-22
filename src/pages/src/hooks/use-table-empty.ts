import { debounce } from 'lodash';
import { computed, ref, watch } from 'vue';

interface FilterOptions {
  filters: any[] | Record<string, any>;
  ignoreKeys?: string[];
}
type TableEmptyType = 'empty' | 'error' | 'search';
/**
 * 表格空状态管理 Hook
 *
 * 用于自动判断表格的空状态类型（空数据/搜索无结果/错误）
 *
 * @example
 * const { curExceptionType, setTypeToError, clearErrorType } = useTableEmpty({
 *   filters: searchValue,           // 监听的筛选条件
 *   ignoreKeys: ['dateRange']       // 可选：忽略某些字段的监听
 * });
 *
 * // curExceptionType 会自动返回: 'empty' | 'search' | 'error'
 */
export default function useTableEmpty(opts: FilterOptions) {
  const isSearch = ref(false);
  const isError = ref(false);

  const curExceptionType = computed((): TableEmptyType => {
    if (isError.value) return 'error';
    if (isSearch.value) return 'search';
    return 'empty';
  });

  /**
   * 设置当前表格状态为错误状态
   * 通常在接口请求失败时调用
   */
  function setTypeToError() {
    isError.value = true;
  }

  /**
   * 清除错误状态
   * 通常在重新请求数据前调用
   */
  function clearErrorType() {
    isError.value = false;
  }

  function deepFindFilter(curFilter: any[]): boolean {
    for (const item of curFilter) {
      if (item === null || item === undefined) {
        continue;
      }
      if (typeof item !== 'object' || item instanceof Date) {
        // 如果是基本类型或 Date 类型，检查是否非空
        if (!isValueEmpty(item)) {
          return true;
        }
      } else if (Array.isArray(item)) {
        // 如果是数组，递归检查
        if (deepFindFilter(item)) {
          return true;
        }
      } else {
        // 如果是对象，检查其值
        if (deepFindFilter(Object.values(item))) {
          return true;
        }
      }
    }
    return false;
  }

  function isValueEmpty(value: any) {
    return value === '' || value === null || value === undefined;
  }

  // 使用防抖优化，避免频繁触发导致的性能问题
  const updateSearchState = debounce((val: any) => {
    let result = false;
    if (Array.isArray(val)) {
      result = deepFindFilter(val);
    } else {
      const values = Object.entries(val)
        .filter(([key]) => !opts?.ignoreKeys?.includes(key))
        .map(([key, value]) => value);
      result = deepFindFilter(values);
    }
    isSearch.value = result;
  }, 300);

  watch(
    opts.filters,
    (val) => {
      updateSearchState(val);
    },
    { deep: true },
  );

  return {
    setTypeToError,
    clearErrorType,
    curExceptionType,
  };
}
