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
      配置数据源
    </bk-button>
  </div>
</template>

<script setup lang="ts">
import typeImg from "@/images/type.png";
import sourceImg from "@/images/source.png";
import orgImg from "@/images/org.png";
import imgOne from "@/images/1.png";
import imgTwo from "@/images/2.png";
import imgThree from "@/images/3.png";
import { AngleDoubleRightLine } from "bkui-vue/lib/icon";

const list = [
  {
    img: typeImg,
    numberImg: imgOne,
    title: '选择数据源类型',
    content: '支持多种类、多平台异构数据源快速接入，助力全方位分析',
  },
  {
    img: sourceImg,
    numberImg: imgTwo,
    title: '配置数据源',
    content: '包含丰富图表组件，自由式拖拽布局轻松搞定仪表盘',
  },
  {
    img: orgImg,
    numberImg: imgThree,
    title: '查看组织架构',
    content: '快速指定与SQL齐飞, 入门与进阶方式任你挑选，满足多样化分析需求',
  },
];


</script>
<style lang="less" scoped>
.table-box {
  display: flex;
  flex-direction: column;
  flex: 1;
  height: 100%;
  width: 100%;

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
        width: 338px;
        height: 296px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;

        .content-item_img {
          width: 204.32px;
          height: 176.84px;
        }
        .content-item_title {
          height: 24px;
          font-family: MicrosoftYaHei-Bold;
          font-weight: 700;
          font-size: 16px;
          color: #63656e;
          letter-spacing: 0;
          line-height: 24px;
          margin-top: 31.16px;
        }
        .content-item_number {
          display: inline-block;
          font-family: Impact;
          vertical-align: middle;
          color: #a3c5fd;
          margin-right: 10px;
        }
      }
      .content-item_detail {
        width: 338px;
        height: 44px;
        font-family: MicrosoftYaHei;
        font-size: 14px;
        color: #63656e;
        letter-spacing: 0;
        text-align: justify;
        line-height: 22px;
        margin-top: 20px;
      }
      .content-item_icon {
        margin-left: 30.25px;
        padding-top: 91.13px;
        width: 20px;
        height: 100%;
        float: right;
      }
    }
  }
  .bottom {
    width: 102px;
    height: 32px;
    background: #3a84ff;
    border-radius: 2px;
    margin: 0 auto;
    margin-top: 52px;
  }
}
</style>
