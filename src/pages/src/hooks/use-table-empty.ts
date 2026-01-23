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

  /**
   *
   * @param curFilter 当前过滤条件
   * @param visited 已遍历的对象
   * @returns
   */
  function deepFindFilter(curFilter: any[], visited = new WeakSet()): boolean {
    for (const item of curFilter) {
      if (item === null || item === undefined) {
        continue;
      }
      if (typeof item !== 'object' || item instanceof Date) {
        // 如果是基本类型或 Date 类型，检查是否非空
        if (!isValueEmpty(item)) {
          return true;
        }
      } else {
        // 防止循环引用
        if (visited.has(item)) continue;
        visited.add(item);

        if (Array.isArray(item)) {
          if (deepFindFilter(item, visited)) return true;
        } else {
          if (deepFindFilter(Object.values(item), visited)) return true;
        }
      }
    }
    return false;
  }

  function isValueEmpty(value: any) {
    if (Array.isArray(value)) return value.length === 0;
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
