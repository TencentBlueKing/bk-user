<!--
  - TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
  - Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
  - Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at http://opensource.org/licenses/MIT
  - Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
  - an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
  - specific language governing permissions and limitations under the License.
  -->
<template>
  <div class="recycle-strategy-wrapper" v-bkloading="{ isLoading: isLoading }">
    <header>{{ $t('回收策略设置') }}</header>
    <div class="recycle-strategy-content">
      <!-- 回收站数据保留天数 -->
      <div class="recycle-strategy-container">
        <div class="title-container">
          <h4 class="title">{{ $t('回收站数据保留天数') }}</h4>
          <span class="star">*</span>
        </div>
        <div class="bk-button-group">
          <bk-button
            v-for="(item, index) in daysList"
            :key="index"
            :class="{ 'is-selected': item.days === activeDays }"
            @click="activeDays = item.days">
            {{ item.text }}
          </bk-button>
        </div>
      </div>
      <div class="btn">
        <bk-button
          theme="primary"
          type="submit"
          class="mr8"
          @click="updateRecoverySetting('submit')">
          {{ $t('保存') }}
        </bk-button>
        <bk-button theme="default" @click="updateRecoverySetting('reset')">
          {{ $t('重置') }}
        </bk-button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RecycleStrategy',
  data() {
    return {
      activeDays: null,
      defaultDays: null,
      isLoading: true,
    };
  },
  computed: {
    // 保留天数
    daysList() {
      return this.$store.state.recycleDaysList;
    },
  },
  mounted() {
    this.initRecoverySetting();
  },
  methods: {
    async initRecoverySetting() {
      try {
        const res = await this.$store.dispatch('setting/getGlobalSettings');
        this.activeDays = res.data[0].value;
        this.defaultDays = res.data[0].default;
        this.isLoading = false;
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
    async updateRecoverySetting(type) {
      this.isLoading = true;
      this.activeDays = type === 'submit' ? this.activeDays : this.defaultDays;
      try {
        const params = [{
          key: 'retention_days',
          value: this.activeDays,
        }];
        await this.$store.dispatch('setting/putGlobalSettings', params);
        this.messageSuccess(type === 'submit' ? this.$t('回收策略保存成功') : this.$t('回收策略重置成功'));
        this.isLoading = false;
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.recycle-strategy-wrapper {
  height: 100%;
  background: #f5f7fa;
  header {
    height: 52px;
    line-height: 52px;
    color: #313238;
    font-size: 16px;
    padding-left: 24px;
    background: #ffffff;
    box-shadow: 0 1px 1px 0 rgba(0, 0, 0, 0.08);
  }

  .recycle-strategy-content {
    padding: 24px;
    .recycle-strategy-container {
      .title-container {
        display: flex;
        align-items: center;
        .title {
          font-size: 14px;
          color: #63656E;
          line-height: 24px;
        }
        .star {
          color: #EA3636;
          font-size: 12px;
          margin-left: 5px;
        }
      }
    }
    .btn {
      margin-top: 32px;
      button {
        width: 80px;
      }
    }
  }
}
</style>
