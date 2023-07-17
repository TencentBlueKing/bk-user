<template>
  <div class="main-container">
    <slot name="menu" />
    <div class="main-container-content">
      <div class="main-header">
        <slot name="main-header" />
      </div>
      <div class="main-content">
        <slot name="main-content" />
      </div>
    </div>
  </div>
</template>

<script setup lang="tsx"></script>

<style lang="less">
.main-container {
  display: flex;
  height: calc(100vh - 52px);
}

.main-container-content {
  position: relative;
  width: 0;
  height: 100%;
  min-width: 940px;
  flex: 1;
  .main-header {
    height: 52px;
    line-height: 52px;
    padding: 0 24px;
    font-size: 16px;
    color: #313238;
    background: #fff;
    box-shadow: 0 3px 4px 0 #0000000a;
  }
}
</style>
