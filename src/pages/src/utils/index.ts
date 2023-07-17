import normalImg from "@/images/normal.svg";
import abnormalImg from "@/images/abnormal.svg";
import unknownImg from "@/images/unknown.svg";
import warningImg from "@/images/warning.svg";
import { Message } from "bkui-vue";

export const statusIcon = {
  'normal': {
    icon: normalImg,
    text: "正常",
  },
  'disabled': {
    icon: unknownImg,
    text: "禁用",
  },
  'locked': {
    icon: warningImg,
    text: "冻结",
  },
  'delete': {
    icon: abnormalImg,
    text: "删除",
  },
};

export const copy = (value: string) => {
  const textArea = document.createElement('textarea');
  textArea.value = value;

  textArea.style.zIndex = '-99999';
  textArea.style.position = 'fixed';

  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();

  try {
    const res = document.execCommand('copy');
    if (res) {
      Message({
        message: "复制成功",
        theme: 'success',
        delay: 1500,
      });
      return;
    }
    throw new Error();
  } catch (e) {
    Message({
      message: "复制失败",
      theme: 'error',
      delay: 1500,
    });
  }
};
