<template>
  <div>
    <p @click="handleBack" style="cursor: pointer;">&lt; {{ $t('返回上一级') }}</p>
    <div class="content">
      <span class="success">
        <i class="user-icon icon-check-line" />
      </span>
      <p class="subtitle">{{ $t('已发送密码重设邮件') }}</p>
      <p class="email">
        <span>
          <i class="bk-sq-icon icon-email" />{{ $t('邮箱') }}：
        </span>
        <span style="color: #313238">{{ currentEmail }}</span>
      </p>
      <p class="desc">{{ $t('请查看邮件并根据提示进行操作') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineEmits, defineProps } from 'vue';

const emit = defineEmits(['emailSend']);

const props = defineProps({
  currentEmail: {
    type: String,
    default: '',
  },
});
const handleBack = () => {
  emit('emailSend', false, props.currentEmail);
};
</script>

<style lang="less" scoped>
.content {
  text-align: center;

  .success {
    position: relative;
    display: inline-block;
    width: 160px;
    height: 160px;
    margin: 16px 0 32px;
    background: #E5F6EA;
    border-radius: 50%;

    .icon-check-line {
      position: absolute;
      top: calc((160px - 65px) /2);
      left: calc((160px - 65px) /2);
      font-size: 65px;
      color: #3FC06D;
    }
  }

  .subtitle {
    margin-bottom: 20px;
    font-size: 24px;
    font-weight: 700;
    color: #313238;
  }

  .email {
    font-size: 14px;

    i {
      margin-right: 5px;
      font-size: 16px;
      color: #3A84FF;
    }
  }

  .desc {
    margin-top: 9px;
    font-size: 14px;
  }
}
</style>

