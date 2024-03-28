<template>
  <div class="card-wrapper">
    <div class="card-header">
      <div class="card-header-right">
        <i :class="list.logo" />
        <div>
          <p class="title">{{ list.name }}</p>
          <p class="subtitle">{{ list.description }}</p>
        </div>
      </div>
      <slot name="header"></slot>
    </div>
    <div :class="['card-content', { 'active-card-content': list.isShow }]">
      <div class="step-bar">
        <slot name="header"></slot>
      </div>
      <slot name="content"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  list: {
    type: Object,
    default: () => ({}),
  },
  activeId: {
    type: String,
    default: '',
  },
});
</script>

<style lang="less" scoped>
.card-wrapper {
  margin-bottom: 12px;
  background: #fff;

  .card-header {
    display: flex;
    padding: 16px 24px;
    border-radius: 2px;
    box-shadow: 0 2px 4px 0 #1919290d;
    align-items: center;
    justify-content: space-between;

    &:hover {
      cursor: pointer;
      border: 1px solid #A3C5FD;
    }

    .card-header-right {
      display: flex;
      align-items: center;

      i {
        margin-right: 15px;
        font-size: 18px;
      }

      .title {
        font-size: 14px;
        line-height: 22px;
        color: #313238;
      }

      .subtitle {
        line-height: 18px;
        color: #979BA5;
      }
    }
  }

  .card-content {
    display: none;
    background: #FFF;
    border-radius: 2px;
    box-shadow: 0 2px 4px 0 #1919290d;

    .step-bar {
      text-align: center;
      background: #FAFBFD;
      box-shadow: 0 1px 0 0 #F0F1F5;
    }
  }

  .active-card-content {
    display: block;
  }
}
</style>
