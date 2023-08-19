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

// file 转 base64
export const getBase64 = (file: any) => {
  return new Promise((resolve, reject) => {
    ///FileReader类就是专门用来读文件的
    const reader = new FileReader();
    //开始读文件
    //readAsDataURL: dataurl它的本质就是图片的二进制数据， 进行base64加密后形成的一个字符串，
    reader.readAsDataURL(file);
    // 成功和失败返回对应的信息，reader.result一个base64，可以直接使用
    reader.onload = () => resolve(reader.result);
    // 失败返回失败的信息
    reader.onerror = error => reject(error);
  });
}

// 无logo首字母色彩取值范围
export const logoColor = [
  "#3A84FF", "#699DF4", "#18B456", "#51BE68", "#FF9C01", "#FFB848", "#EA3636", "#FF5656",
  "#3762B8", "#3E96C2", "#61B2C2", "#85CCA8", "#FFC685", "#FFA66B", "#F5876C", "#D66F6B",
];

export const dataSourceType = {
  local: {
    icon: 'user-icon icon-shujuku',
    text: "本地",
  },
  mad: {
    icon: 'user-icon icon-win',
    text: "MAD",
  },
  ldap: {
    icon: 'user-icon icon-ladp',
    text: "OpenLDAP",
  },
  wechat: {
    icon: 'user-icon icon-qiyeweixin',
    text: "企业微信",
  },
}
