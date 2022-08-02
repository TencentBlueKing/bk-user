<!--
  - Tencent is pleased to support the open source community by making Bk-User 蓝鲸用户管理 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
  -
  - License for Bk-User 蓝鲸用户管理:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->
<template>
  <div :class="['markdown-box', { 'focus-editor': isActive }]">
    <Toolbar
      class="toolbar-content"
      :editor="editor"
      :default-config="toolbarConfig"
      :mode="mode"
    />
    <Editor
      class="editor-content"
      v-model="html"
      :default-config="editorConfig"
      :mode="mode"
      @onCreated="onCreated"
      @onChange="onChange"
      @onFocus="onFocus"
      @onBlur="onBlur"
    />
  </div>
</template>

<script>
import Vue from 'vue';
import '@wangeditor/editor/dist/css/style.css';
import { Editor, Toolbar } from '@wangeditor/editor-for-vue';
export default Vue.extend({
  components: { Editor, Toolbar },
  props: {
    htmlText: {
      type: String,
    },
    toolbarConfig: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      editor: null,
      eitorConfig: { placeholder: this.$t('请输入内容') },
      mode: 'simple',
      isActive: false,
    };
  },
  computed: {
    html() {
      return this.htmlText;
    },
  },
  beforeDestroy() {
    const editor = this.editor;
    if (editor === null) return;
    editor.destroy(); // 组件销毁时，及时销毁编辑器
  },
  methods: {
    onCreated(editor) {
      this.editor = Object.seal(editor); // 一定要用 Object.seal() ，否则会报错
    },
    // 当编辑器选区、内容变化时，即触发
    onChange(editor) {
      this.$emit('updateContent', editor.getHtml(), editor.getText());
    },
    onFocus() {
      this.isActive = true;
    },
    onBlur() {
      this.isActive = false;
    },
  },
});
</script>

<style>

</style>
