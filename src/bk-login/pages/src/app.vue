<template>
  <div class="main-content">
    <div class="bg-img right-top">
      <img src="../static/images/right-top.png" alt="">
    </div>
    <div class="bg-img right-bottom">
      <img src="../static/images/right-bottom.png" alt="">
    </div>
    <div class="bg-img left-bottom">
      <img src="../static/images/left-bottom.png" alt="">
    </div>
    <div class="login-model">
      <router-view></router-view>
    </div>
    <div id="particles-js"></div>
    <footer class="footer">
      <p>
        <a href="https://wpa1.qq.com/KziXGWJs?_type=wpa&amp;qidian=true">技术支持</a>
        | <a href="https://bk.tencent.com/s-mart/community/" target="_blank" class="link">社区论坛</a>
        | <a href="http://bk.tencent.com/" target="_blank" class="link">产品官网</a>
        |
        <bk-popover theme="light" placement="bottom">
          <a href="" target="_blank" class="link follow-us">
            关注我们
          </a>
          <template #content>
            <span class="qr-box"><img class="qr" src="../static/images/qr.png" alt=""></span>
          </template>
        </bk-popover>
      </p>
      <p>Copyright © 2012-{{ currentYear }} Tencent BlueKing. All Rights Reserved.</p>
      <p>蓝鲸智云 版权所有</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';

const currentYear = new Date().getFullYear();

onMounted(() => {
  particlesJS(
    'particles-js',
    {
      particles: {
        number: {
          value: 10,
          density: {
            enable: true,
            value_area: 800,
          },
        },
        color: {
          value: '#D0D9E2',
        },
        shape: {
          type: 'circle',
          stroke: {
            width: 0,
            color: '#000000',
          },
          polygon: {
            nb_sides: 5,
          },
          image: {
            src: 'img/github.svg',
            width: 100,
            height: 100,
          },
        },
        opacity: {
          value: 0.5,
          random: false,
          anim: {
            enable: false,
            speed: 1,
            opacity_min: 0.1,
            sync: false,
          },
        },
        size: {
          value: 7,
          random: false,
          anim: {
            enable: false,
            speed: 1,
            size_min: 0.1,
            sync: false,
          },
        },
        line_linked: {
          enable: true,
          distance: 150,
          color: '#D0D9E2',
          opacity: 0.4,
          width: 2,
        },
        move: {
          enable: true,
          speed: 1,
          direction: 'none',
          random: true,
          straight: false,
          out_mode: 'out',
          attract: {
            enable: false,
            rotateX: 600,
            rotateY: 1200,
          },
        },
      },
      interactivity: {
        detect_on: 'canvas',
        events: {
          onhover: {
            enable: true,
            mode: 'repulse',
          },
          onclick: {
            enable: true,
            mode: 'push',
          },
          resize: true,
        },
        modes: {
          grab: {
            distance: 400,
            line_linked: {
              opacity: 1,
            },
          },
          bubble: {
            distance: 400,
            size: 40,
            duration: 2,
            opacity: 8,
            speed: 1,
          },
          repulse: {
            distance: 50,
          },
          push: {
            particles_nb: 4,
          },
          remove: {
            particles_nb: 2,
          },
        },
      },
      retina_detect: true,
      config_demo: {
        hide_card: false,
        background_color: '#b61924',
        background_image: '',
        background_position: '50% 50%',
        background_repeat: 'no-repeat',
        background_size: 'cover',
      },
    },
  );
});
</script>

<style lang="postcss" scoped>
.login-model {
  z-index: 2;
  width: 480px;
  background: #FFFFFF;
  box-shadow: 0 4px 12px 0 #00000033;
  border-radius: 10px;
  position: absolute;
  left: 50%;
  top: 35%;
  transform: translate(-50%, -35%);
  padding: 32px 40px;
}
.main-content {
  height: 100%;
  background-color: #ebf2fa;
}

#particles-js {
  height: 100%;
}

.bg-img img {
  width: 100%;
}

.right-top {
  width: 52%;
  height: 0;
  position: absolute;
  right: 0;
  top: 0;
  padding-bottom: 10%;
  background-color: #ebf2fa;
}

.right-bottom {
  width: 31%;
  height: 0;
  position: absolute;
  right: 1%;
  bottom: 0;
  padding-bottom: 15%;
}

.left-bottom {
  width: 35%;
  height: 0;
  position: absolute;
  left: 0;
  bottom: 0;
  padding-bottom: 12%;
}

.footer {
  width: 100%;
  line-height: 20px;
  padding: 2% 0;
  position: absolute;
  bottom: 0;
  color: #bfcbd7;
  font-size: 12px;
  text-align: center;
  background: url(./images/footer.png) no-repeat center;
  background-size: 100% 100%;
}

.footer a {
  color: #bfcbd7;
  margin: 0 5px;

  &:hover {
    color: #fff;
  }
}
</style>
