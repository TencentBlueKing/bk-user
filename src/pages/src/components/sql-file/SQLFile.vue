<template>
  <div
    ref="rootRef"
    class="sql-execute-editor">
    <div class="editor-layout-header">
      <span>{{ title }}</span>
      <div class="editro-action-box">
        <i
          class="user-icon icon-copy"
          @click="handleCopy" />
        <i
          class="user-icon icon-import"
          @click="handleDownload" />
        <i
          v-if="isFullscreen"
          class="user-icon icon-un-full-screen"
          @click="handleExitFullScreen" />
        <i
          v-else
          class="user-icon icon-full-screen"
          @click="handleFullScreen" />
      </div>
    </div>
    <div class="resize-wrapper">
      <div
        ref="editorRef"
        style="height: 100%;" />
    </div>
  </div>
</template>
<script setup lang="ts">
import * as monaco from 'monaco-editor';
import screenfull from 'screenfull';
import {
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from 'vue';

import { copy } from '@/utils';

interface Props {
  modelValue: string,
  title: string,
  readonly?: boolean,
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false,
  syntaxChecking: false,
});

const emits = defineEmits(['update:modelValue', 'change']);

const rootRef = ref();
const editorRef = ref();
const isFullscreen = ref(false);

let editor: monaco.editor.IStandaloneCodeEditor;

watch(() => props.modelValue, () => {
  if (props.modelValue !== editor.getValue()) {
    editor.setValue(props.modelValue);
  }
});

const handleToggleScreenfull = () => {
  if (screenfull.isFullscreen) {
    isFullscreen.value = true;
  } else {
    isFullscreen.value = false;
  }
  editor.layout();
};

const handleReize = () => {
  editor.layout();
};

const handleCopy = () => {
  copy(props.modelValue);
};

const handleDownload = () => {
  const link = document.createElement('a');
  link.download = `${props.title.replace(/\s/g, '')}.sql`;
  link.style.display = 'none';
  // 字符内容转变成blob地址
  const blob = new Blob([props.modelValue], { type: 'sql' });
  link.href = URL.createObjectURL(blob);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const handleFullScreen = () => {
  screenfull.toggle(rootRef.value);
};

const handleExitFullScreen = () => {
  screenfull.toggle(rootRef.value);
};

onMounted(() => {
  monaco.editor.defineTheme('logTheme', {
    base: 'vs',
    inherit: true,
    rules: [
      { token: 'error-token', foreground: '#EA3636' },
      { token: 'info-token', foreground: '#C4C6CC' },
      { token: 'warning-token', foreground: '#FF9C01' },
    ],
    colors: {
      'editor.foreground': '#EA3636',
      'editor.background': '#000000',
      'editorCursor.foreground': '#C4C6CC',
      'editor.lineHighlightBackground': '#000000', // 光标颜色
      'editorLineNumber.foreground': '#C4C6CC', // 序号颜色
      'editor.selectionBackground': '#1768EF', // 选中背景颜色
      'editor.inactiveSelectionBackground': '#000000', // 选中后失焦背景颜色
      'editorActiveLineNumber.foreground': '#C4C6CC',
    },
  });

  monaco.editor.setTheme('logTheme');

  monaco.languages.register({ id: 'logLanguage' });
  monaco.languages.setMonarchTokensProvider('logLanguage', {
    keywords: ['ERROR', 'INFO', 'WARNING'],
    header: /\[(\w+)\]/,
    tokenizer: {
      root: [
        [/^ERROR.*/, 'error-token'],
        [/^INFO.*/, 'info-token'],
        [/^WARNING.*/, 'warning-token'],
      ],
    },
  });

  editor = monaco.editor.create(editorRef.value, {
    value: 'ERROR This is an error\nWARNING This is an warning\nINFO This is an info',
    language: 'logLanguage',
    theme: 'logTheme',
    readOnly: props.readonly,
    minimap: {
      enabled: false,
    },
    wordWrap: 'bounded',
    scrollbar: {
      alwaysConsumeMouseWheel: false,
    },
    automaticLayout: true,
  });

  editor.onDidChangeModelContent(() => {
    const value = editor.getValue();
    emits('update:modelValue', value);
    emits('change', value);
  });
  screenfull.on('change', handleToggleScreenfull);
  window.addEventListener('resize', handleReize);
});

onBeforeUnmount(() => {
  editor.dispose();
  screenfull.off('change', handleToggleScreenfull);
  window.removeEventListener('resize', handleReize);
});

</script>
<style lang="less" scoped>
.sql-execute-editor {
  position: relative;
  z-index: 0;
  flex: 1;
  height: calc(100vh - 52px);
  padding: 16px;

  .editor-layout-header {
    display: flex;
    align-items: center;
    height: 40px;
    padding-right: 16px;
    padding-left: 25px;
    font-size: 14px;
    color: #c4c6cc;
    background: #2e2e2e;

    .editro-action-box {
      margin-left: auto;
      color: #979ba5;

      & > * {
        margin-left: 12px;
        cursor: pointer;
      }
    }
  }

  .resize-wrapper {
    height: calc(100% - 40px);
    background: #212121;
  }
}
</style>
