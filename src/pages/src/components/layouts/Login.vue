<template>
  <div
    v-if="state.isShow"
    class="login-modal">
    <div
      class="login-modal__container"
      :style="styles">
      <iframe
        allowtransparency="true"
        border="0"
        frameborder="0"
        referrerpolicy="strict-origin-when-cross-origin"
        scrolling="no"
        :src="state.src" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed } from "vue";
import { watch } from "vue";

type LoginInfo = {
  src: string,
  width: number,
  height: number,
}

const state = reactive({
  src: '',
  width: 800,
  height: 510,
  isShow: false,
});

const styles = computed(() => ({ width: `${state.width}px`, height: `${state.height}px` }));

const showLogin = ({ src, width, height }: LoginInfo) => {
  state.src = src;
  state.width = width;
  state.height = height;
  state.isShow = true;
};

const hideLogin = () => {
  state.isShow = false;
};

watch(() => state.isShow, () => {
  window.login.isShow = state.isShow;
});

window.login = {
  isShow: state.isShow,
  showLogin,
  hideLogin,
};
</script>

<style lang="less" scoped>
.login-modal {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 99999;
  font-size: 0;
  background-color: rgba(0, 0, 0, 0.6);

  &__container {
    position: relative;
    display: block;
    width: 400px;
    height: 400px;
    margin: calc((100vh - 470px) / 2) auto;
    overflow: hidden;
    background-color: #fff;
    border-radius: 2px;
  }

  iframe {
    width: 100%;
    height: 100%;
  }
}
</style>
