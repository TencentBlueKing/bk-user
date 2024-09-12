import { onUnmounted } from "vue";
/**
 * @param intervalFn 倒计时内的回调方法
 * @param beforeClose 倒计时结束的回调方法
 * @param pollingInterval 倒计时间隔，默认1秒
 */
interface CountDownOptions  {
  intervalFn: () => void;
  beforeStart?: () => void;
  beforeClose?: () => void;
  pollingInterval?: number;
};

export const useCountDown = (options: CountDownOptions) => {
  const { intervalFn, beforeStart, beforeClose, pollingInterval = 1000 } = options;

  beforeStart && beforeStart();

  const time = setInterval(() => {
    intervalFn();
  }, pollingInterval);

  const closeTimePolling = () => {
    clearTimeout(time);
    beforeClose && beforeClose();
  };

  onUnmounted(() => {
    closeTimePolling();
  });

  return {
    closeTimePolling,
  };
};
