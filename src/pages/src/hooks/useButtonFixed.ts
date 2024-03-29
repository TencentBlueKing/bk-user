import { debounce } from 'bkui-vue/lib/shared';
import { addListener, removeListener } from 'resize-detector';
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue';

export const useButtonFixed = (boxRef: any, cardRef: any, height: number) => {
  const isScroll = ref(false);
  // 按钮超出屏幕吸底
  const handleResize = () => {
    isScroll.value = 32 >= (boxRef.value.clientHeight - cardRef.value.clientHeight - height);
  };

  onMounted(() => {
    const listenResize = debounce(300, () => handleResize());
    addListener(boxRef.value as HTMLElement, listenResize);
    nextTick(handleResize);
  });

  onBeforeUnmount(() => {
    removeListener(boxRef.value as HTMLElement, handleResize);
  });

  return isScroll;
};
