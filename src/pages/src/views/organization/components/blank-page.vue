<template>
  <div class="table-box">
    <div class="content">
      <div class="content-item" v-for="(item, index) in list" :key="item.title">
        <div class="content-item_top">
          <img class="content-item_img" :src="item.img" alt="" srcset="" />
          <div class="content-item_title flex justify-center items-center">
            <img class="content-item_number" :src="item.numberImg" alt="" srcset="" style="vertical-align: middle" />
            <span>{{ item.title }}</span>
          </div>
          <div class="content-item_detail">{{ item.content }}</div>
        </div>
        <div class="content-item_icon">
          <AngleDoubleRightLine v-if="index !== 2" width="19.5px;" height="17.25px;" fill="#3A84FF" />
        </div>
      </div>
    </div>
    <bk-button class="bottom" size="large" theme="primary" @click="$router.push({ name: 'dataSource' })">
      {{ $t('配置数据源') }}
    </bk-button>
  </div>
</template>

<script setup lang="ts">
import { AngleDoubleRightLine } from 'bkui-vue/lib/icon';

import imgOne from '@/images/1.png';
import imgTwo from '@/images/2.png';
import imgThree from '@/images/3.png';
import orgImg from '@/images/org.png';
import sourceImg from '@/images/source.png';
import typeImg from '@/images/type.png';
import { t } from '@/language/index';

const list = [
  {
    img: typeImg,
    numberImg: imgOne,
    title: t('选择数据源类型'),
    content: t('支持本地导入、通用HTTP、企业微信、LDAP、MAD等多种数据源类型接入'),
  },
  {
    img: sourceImg,
    numberImg: imgTwo,
    title: t('配置数据源'),
    content: t('根据选择的数据源类型，提供页面化指引配置'),
  },
  {
    img: orgImg,
    numberImg: imgThree,
    title: t('查看组织架构'),
    content: t('数据源配置完成，可以查看组织架构和用户信息'),
  },
];


</script>
<style lang="less" scoped>
.table-box {
  display: flex;
  width: 100%;
  height: 100%;
  flex-direction: column;
  flex: 1;

  .content {
    display: flex;
    justify-content: center;
    width: 100%;
    margin-top: 269px;

    .content-item {
      display: flex;
      justify-content: center;
      align-items: center;

      .content-item_top {
        display: flex;
        width: 338px;
        height: 296px;
        flex-direction: column;
        justify-content: center;
        align-items: center;

        .content-item_img {
          width: 204.32px;
          height: 176.84px;
        }

        .content-item_title {
          height: 24px;
          margin-top: 31.16px;
          font-family: MicrosoftYaHei-Bold;
          font-size: 16px;
          font-weight: 700;
          line-height: 24px;
          letter-spacing: 0;
          color: #63656e;
        }

        .content-item_number {
          display: inline-block;
          margin-right: 10px;
          font-family: Impact;
          color: #a3c5fd;
          vertical-align: middle;
        }
      }

      .content-item_detail {
        width: 338px;
        height: 44px;
        margin-top: 20px;
        font-family: MicrosoftYaHei;
        font-size: 14px;
        line-height: 22px;
        letter-spacing: 0;
        color: #63656e;
        text-align: justify;
      }

      .content-item_icon {
        float: right;
        width: 20px;
        height: 100%;
        padding-top: 91.13px;
        margin-left: 30.25px;
      }
    }
  }

  .bottom {
    height: 32px;
    margin: 0 auto;
    margin-top: 52px;
    font-size: 14px;
    background: #3a84ff;
    border-radius: 2px;
  }
}
</style>
