<!--
  - TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
  - Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
  - Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at http://opensource.org/licenses/MIT
  - Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
  - an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
  - specific language governing permissions and limitations under the License.
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
