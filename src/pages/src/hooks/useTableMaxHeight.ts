import { computed, onBeforeUnmount, Ref, ref, unref } from 'vue';

export const useTableMaxHeight = (height: Ref<number> | number) => {
  const minHeight = 200;
  const innerHeight = ref(window.innerHeight);
  const tableHeight = computed(() => {
    const remainingHeight = innerHeight.value - unref(height);
    return remainingHeight > minHeight ? remainingHeight : minHeight;
  });

  const handleResize = () => {
    innerHeight.value = window.innerHeight;
  };

  window.addEventListener('resize', handleResize);
  onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize);
  });

  return tableHeight;
};
