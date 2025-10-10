<template>
  <div class="result-wrapper">
    <div class="result-box-content">
      <div class="content">
        <template v-if="isSuccess">
          <span class="success-icon">
            <i class="user-icon icon-check-line" />
          </span>
          <p class="subtitle">{{ $t('绑定成功') }}</p>
          <p class="tips">
            <span class="count-down-time">{{ countDownTime }}</span>
            <span>{{ $t('s 后自动关闭页面') }}</span>
          </p>
          <bk-button theme="primary" class="action" @click="handleJump">
            {{ $t('直接关闭') }}
          </bk-button>
        </template>
        <template v-else>
          <span class="error-icon">
            <error class="icon-error" />
          </span>
          <p class="subtitle">{{ $t('绑定失败') }}</p>
          <p class="tips">
            <span>{{ $t('请稍后重试，若无法解决，请联系管理员处理') }}</span>
          </p>
          <bk-button theme="primary" class="action" @click="handleJump">
            {{ $t('关闭') }}
          </bk-button>
        </template>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { Error } from 'bkui-vue/lib/icon';
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

import { useCountDown } from '@/hooks';
const route = useRoute();
const countDownTime = ref(3);

const isSuccess = computed(() => Number(route.query.status) === 1);

const handleJump = () => {
  window.close();
};

onMounted(() => {
  const { closeTimePolling } = useCountDown({
    intervalFn: () => {
      if (countDownTime.value > 0) {
        countDownTime.value -= 1;
      } else {
        closeTimePolling();
        handleJump();
      }
    },
  });
});
</script>

<style lang="less" scoped>
.result-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: linear-gradient(180deg, #CDDFFE 0%, #F0F5FF 100%);

  .result-box-content {
    position: absolute;
    inset: 0;
    width: 480px;
    height: 404px;
    padding: 58px 40px 48px;
    margin: auto;
    background: #FFF;
    border-radius: 10px;
    box-shadow: 0 4px 12px 0 #0003;

    .content {
      text-align: center;

      .success-icon {
        position: relative;
        display: inline-block;
        width: 130px;
        height: 130px;
        margin: 0 0 32px;
        background: #E5F6EA;
        border-radius: 50%;

        .icon-check-line {
          position: absolute;
          top: calc((130px - 65px) /2);
          left: calc((130px - 65px) /2);
          font-size: 65px;
          color: #3FC06D;
        }
      }

      .error-icon {
        position: relative;
        display: inline-block;
        width: 130px;
        height: 130px;
        margin: 0 0 32px;
        background: #FFDDDD;
        border-radius: 50%;

        .icon-error {
          position: absolute;
          top: calc((130px - 65px) /2);
          left: calc((130px - 65px) /2);
          font-size: 65px;
          color: #EA3636;
        }
      }

      .subtitle {
        margin-bottom: 16px;
        font-size: 24px;
        font-weight: 700;
        color: #313238;
      }

      .tips {
        font-size: 14px;
        color: #4D4F56;
        margin-bottom: 24px;

        .count-down-time {
          display: inline-block;
          width: 16px;
          height: 24px;
          line-height: 24px;
          background-color: #F0F1F5;
          color: #4D4F56;
          font-weight: bold;
        }
      }

      .action {
        width: 96px;
        height: 40px;
        font-size: 16px;
      }
    }
  }
}
</style>
