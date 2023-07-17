<template>
  <ul class="details-content">
    <li>
      <div class="details-content-title">基本信息</div>
      <div class="details-content-info">
        <div
          class="details-content-item"
          v-for="(item, index) in basicData"
          :key="index"
        >
          <span class="details-content-key">{{ item.name }}：</span>
          <span class="details-content-value">{{ item.value }}</span>
        </div>
      </div>
      <div class="details-content-img"></div>
    </li>
    <li>
      <div class="details-content-title">管理员</div>
      <bk-table
        class="details-content-table"
        :data="userData"
        :columns="columns"
      />
    </li>
  </ul>
</template>

<script setup lang="tsx">
import { ref, computed, reactive } from "vue";

const props = defineProps({
  basicInfo: {
    type: Object,
    default: {},
  },
  userData: {
    type: Array,
    default: [],
  },
});

const columns = [
  {
    label: "用户名",
    field: "username",
  },
  {
    label: "全名",
    field: "display_name",
  },
  {
    label: "邮箱",
    field: "email",
  },
  {
    label: "手机号",
    field: "telephone",
  },
];

const basicData = reactive([
  {
    name: "公司名称",
    value: props.basicInfo.name,
  },
  {
    name: "公司ID",
    value: props.basicInfo.id,
  },
  {
    name: "人员数量",
    value: props.basicInfo.isShow ? "显示" : "隐藏",
  },
]);
</script>

<style lang="less" scoped>
.details-content {
  padding: 0 40px;
  li {
    list-style: none;
    padding: 20px 0;
    border-bottom: 1px solid #dcdee5;
    position: relative;
    .details-content-title {
      font-size: 14px;
      color: #63656e;
      font-weight: 700;
      line-height: 40px;
    }
    .details-content-info {
      width: calc(100% - 92px);
      .details-content-item {
        line-height: 40px;
        width: 100%;
        .details-content-key {
          font-size: 14px;
          color: #63656e;
          display: inline-block;
          width: 100px;
          text-align: right;
        }
        .details-content-value {
          font-size: 14px;
          color: #313238;
          display: inline-block;
          width: calc(100% - 100px);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          vertical-align: top;
        }
      }
    }
    .details-content-img {
      font-size: 50px;
      color: #c4c6cc;
      position: absolute;
      top: calc(50% - 25%);
      right: 0;
    }
  }
  li:last-child {
    border-bottom: none;
  }
}
.details-content-table {
  margin-top: 16px;
  :deep(.bk-fixed-bottom-border) {
    border-top: none;
  }
}
</style>
