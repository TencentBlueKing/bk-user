<template>
  <ul class="details-content">
    <li>
      <div class="details-content-info">
        <div class="details-content-item">
          <span class="details-content-key">用户名：</span>
          <span class="details-content-value">{{ usersData.username }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">全名：</span>
          <span class="details-content-value">{{ usersData.full_name }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">邮箱：</span>
          <span class="details-content-value">{{ usersData.email }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">手机号：</span>
          <span class="details-content-value">{{ usersData.phone }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">所属组织：</span>
          <div class="details-content-value" v-if="usersData.departments.length > 0">
            <span v-for="(item, index) in usersData.departments" :key="index">
              {{ item.name}}
            </span>
          </div>
          <span class="details-content-value" v-else>{{ '--' }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">直属上级：</span>
          <div class="details-content-value" v-if="usersData.leaders.length > 0">
            <span v-for="(item, index) in usersData.leaders" :key="index">
              {{ item.username }}
            </span>
          </div>
          <span class="details-content-value" v-else>{{ '--' }}</span>
        </div>
      </div>
      <img v-if="usersData.logo" class="user-logo" :src="usersData.logo" alt="" />
      <img v-else class="user-logo" src="@/images/avatar.png" alt="" />
    </li>
  </ul>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

defineProps({
  usersData: {
    type: Object,
    default: () => ({}),
  },
});
</script>

<style lang="less" scoped>
.details-content {
  padding: 0 40px;

  li {
    position: relative;
    padding: 20px 0;
    list-style: none;
    border-bottom: 1px solid #dcdee5;

    .details-content-info {
      width: calc(100% - 100px);

      .details-content-item {
        display: flex;
        width: 100%;
        line-height: 40px;

        .details-content-key {
          display: inline-block;
          width: 100px;
          overflow: hidden;
          font-size: 14px;
          color: #63656e;
          text-align: right;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .details-content-value {
          display: flex;
          width: calc(100% - 100px);
          font-size: 14px;
          color: #313238;
          flex-wrap: wrap;

          span {
            display: inline-block;
            width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
        }
      }
    }

    .user-logo {
      position: absolute;
      top: 20px;
      right: 0;
      width: 96px;
      height: 96px;
      border: 1px dashed #c4c6cc;
      object-fit: contain;
    }
  }

  li:last-child {
    border-bottom: none;
  }
}
</style>
