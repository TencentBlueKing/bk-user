<template>
  <div class="details-info-wrapper user-scroll-y">
    <div class="details-info-main">
      <p>基本信息</p>
      <div class="details-info-content">
        <div class="details-info-item">
          <div>
            <span class="details-info-label">公司名称：</span>
            <span class="details-info-value">总公司</span>
          </div>
          <div>
            <span class="details-info-label">公司ID：</span>
            <span class="details-info-value">12345</span>
          </div>
        </div>
        <div class="details-info-item">
          <div>
            <span class="details-info-label">公司状态：</span>
            <span class="details-info-value">启用</span>
          </div>
          <div>
            <span class="details-info-label">人员数量：</span>
            <span class="details-info-value">显示</span>
          </div>
        </div>
        <div class="details-info-item">
          <div>
            <span class="details-info-label">更新时间：</span>
            <span class="details-info-value">2023-06-01</span>
          </div>
        </div>
      </div>
    </div>
    <div class="details-info-main">
      <p>公司管理员</p>
      <bk-table
        class="user-info-table"
        :columns="userColumns"
        :data="userData"
      />
    </div>
  </div>
</template>

<script setup lang="tsx">
const userData = [];
const userColumns = [
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
</script>

<style lang="less" scoped>
.details-info-wrapper {
  padding: 24px;
  height: calc(100vh - 140px);
  .details-info-main {
    background: #fff;
    box-shadow: 0 2px 4px 0 #1919290d;
    border-radius: 2px;
    margin-bottom: 16px;
    padding: 16px 24px;
    p {
      font-size: 14px;
      font-weight: 700;
      margin-bottom: 16px;
    }
    .details-info-content {
      display: flex;
      .details-info-item {
        width: 33%;
        font-size: 14px;
        line-height: 40px;
        .details-info-label {
          display: inline-block;
          width: 100px;
          text-align: right;
        }
        .details-info-value {
          color: #313238;
        }
      }
    }
  }
}
</style>
