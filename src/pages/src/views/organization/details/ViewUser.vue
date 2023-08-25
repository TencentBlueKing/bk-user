<template>
  <ul class="details-content">
    <li>
      <div class="details-content-info">
        <div class="details-content-item">
          <span class="details-content-key">用户ID：</span>
          <span class="details-content-value">{{ props.userData.id }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">用户名：</span>
          <span class="details-content-value">{{ props.userData.username }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">全名：</span>
          <span class="details-content-value">{{ props.userData.full_name }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">邮箱：</span>
          <span class="details-content-value">{{ props.userData.email }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">手机号：</span>
          <span class="details-content-value">{{ props.userData.phone }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">所属组织：</span>
          <div class="details-content-value" v-if="props.userData.departments.length > 0">
            <span v-for="(item, index) in props.userData.departments" :key="index">
              {{ item.name}}
            </span>
          </div>
          <span class="details-content-value" v-else>{{ '--' }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">直属上级：</span>
          <div class="details-content-value" v-if="props.userData.leaders.length > 0">
            <span v-for="(item, index) in props.userData.leaders" :key="index">
              {{ item.username }}
            </span>
          </div>
          <span class="details-content-value" v-else>{{ '--' }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">账号过期时间：</span>
          <span class="details-content-value">{{ dateConvert(props.userData.account_expired_at) }}</span>
        </div>
      </div>
      <img v-if="props.userData.logo" class="user-logo" :src="props.userData.logo" alt="" />
      <img v-else class="user-logo" src="@/images/avatar.png" alt="" />
    </li>
  </ul>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue';
import moment from 'moment';
import { dateConvert } from '@/utils';

const props = defineProps({
  userData: {
    type: Object,
    default: {},
  },
});
</script>

<style lang="less" scoped>
.details-content {
  padding: 20px 40px;

  li {
    position: relative;
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
          overflow: hidden;
          font-size: 14px;
          color: #313238;
          text-overflow: ellipsis;
          white-space: nowrap;
          vertical-align: top;
          flex-wrap: wrap;
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
