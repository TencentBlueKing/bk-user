<template>
  <div :class="['markdown-box', { 'focus-editor': isActive }]">
    <Toolbar
      class="toolbar-content"
      :editor="editorRef "
      :default-config="toolbarConfig"
      :mode="mode"
    />
    <Editor
      class="editor-content"
      v-model="valueHtml"
      :default-config="editorConfig"
      :mode="mode"
      @onCreated="handleCreated"
      @onChange="handleChange"
      @onFocus="handleFocus"
      @onBlur="handleBlur"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, defineEmits, defineProps, onBeforeUnmount, ref, shallowRef } from 'vue';

import { Editor, Toolbar } from '@wangeditor/editor-for-vue';

import '@wangeditor/editor/dist/css/style.css';

const props = defineProps({
  htmlText: {
    type: String,
    default: '',
  },
  toolbarConfig: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(['updateContent']);
// 编辑器实例，必须用 shallowRef
const editorRef = shallowRef();

// 内容 HTML
const valueHtml = computed(() => props.htmlText);
const editorConfig = { placeholder: '请输入内容...' };
const mode = ref('simple');
const isActive = ref(false);

// 组件销毁时，也及时销毁编辑器
onBeforeUnmount(() => {
  const editor = editorRef.value;
  if (editor === null) return;
  editor.destroy();
});

const handleCreated = (editor) => {
  editorRef.value = editor;
};

// 当编辑器选区、内容变化时，即触发
const handleChange = (editor) => {
  emit('updateContent', editor.getHtml(), editor.getText());
};

const handleFocus = () => {
  isActive.value = true;
};

const handleBlur = () => {
  isActive.value = false;
};
</script>

<style>
.w-e-modal {
  top: 30px !important;
  bottom: 40px !important;

  .babel-container {
    margin-bottom: 10px !important;

    span {
      margin-bottom: 5px !important;
    }
  }
}

.w-e-panel-content-color {
  width: 185px;
  height: 194px;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 4px;
    background-color: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background-color: #dcdee5;
    border-radius: 4px;
  }
}
</style>
