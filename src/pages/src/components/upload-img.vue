<template>
  <bk-upload
    theme="picture"
    :accept="accept"
    :multiple="false"
    :files="files"
    :url="imgUrl"
    :custom-request="customRequest"
    :size="maxSize"
    @delete="handleDelete"
    @error="handleError"
    :tip="isShowTip ? $t('支持 jpg、jpeg、png，尺寸不大于 1024px*1024px，不大于 256KB') : ''"
  >
    <template #trigger v-if="$slots.trigger">
      <slot name="trigger"></slot>
    </template>
  </bk-upload>
</template>

<script lang="ts" setup>
import { Message } from 'bkui-vue';
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import { getBase64 } from '@/utils';

/**
 * @description 如需用到以下props，需要做国际化兼容，当下使用默认参数即可
 */
interface IProps {
  maxSize?: number
  maxWidth?: number
  maxHeight?: number
  accept?: string
  isShowTip?: boolean
  afterUpload?: (url: string) => void
}

const imgUrl = defineModel<string>('');
const props = withDefaults(defineProps<IProps>(), {
  maxSize: 0.25, // 256kb
  maxWidth: 1024,
  maxHeight: 1024,
  accept: 'image/png,image/jpeg,image/jpg',
  isShowTip: true,
});
const emit = defineEmits(['success', 'delete', 'error']);

const { t } = useI18n();

const files = ref([]);

const customRequest = async (event: any) => {
  const { file } = event;
  // 1. 验证文件类型
  if (!validateFileType(file)) {
    Message({ theme: 'error', message: t('图片格式不符合要求，请重新上传') });
    clearImgUrl();
    return;
  }
  // 2. 验证图片尺寸
  const res = await validateFileResolution(file);
  if (!res) {
    Message({ theme: 'error', message: t('图片尺寸超出限制，请重新上传') });
    clearImgUrl();
    return;
  }
  // 3. 所有验证通过，上传图片
  const url = await getBase64(event.file) as string;
  props?.afterUpload?.(url);
  setImgUrl(url);
  emit('success');
};

const handleDelete = () => {
  clearImgUrl();
  emit('delete');
};

const handleError = (file: File) => {
  // bk-upload对超出size的文件直接抛出error，因此只能在这里处理超出大小的逻辑
  if (!validateFileSize(file)) {
    Message({ theme: 'error', message: t('图片大小超出限制，请重新上传') });
    clearImgUrl();
    return;
  }
  emit('error', file);
};

const clearImgUrl = () => imgUrl.value = '';

const setImgUrl = (url: string) => imgUrl.value = url;

const updateFiles = (url: string) => {
  if (!url) {
    files.value = [];
    return;
  }
  files.value = [{ url }];
};

/** 验证文件类型 bk-upload、input 对accept的检查并不严格，因此这里对文件type做检查 */
const validateFileType = (file: File) => {
  const { type } = file;
  const acceptTypes = props.accept.split(',');
  if (!acceptTypes.includes(type)) {
    return false;
  }
  return true;
};

/** 验证文件大小 */
const validateFileSize = (file: File) => {
  if (file.size > 1024 * 1024 * props.maxSize) {
    return false;
  }
  return true;
};

/** 验证图片尺寸 */
const validateFileResolution = (file: File): Promise<boolean> => new Promise(async (resolve) => {
  if (!file || !file.type.startsWith('image/')) {
    resolve(false);
    return;
  }
  const reader = new FileReader();
  reader.onerror = () => {
    resolve(false);
  };

  reader.onload = async () => {
    const img = new Image();
    img.onload = () => {
      try {
        if (img.width > props.maxWidth || img.height > props.maxHeight) {
          resolve(false);
          return;
        }
        resolve(true);
      } catch (err) {
        resolve(false);
      }
    };
    img.onerror = () => {
      resolve(false);
    };
    img.src = reader.result as string;
  };
  reader.readAsDataURL(file);
});

watch(imgUrl, (val: string) => updateFiles(val));
</script>
