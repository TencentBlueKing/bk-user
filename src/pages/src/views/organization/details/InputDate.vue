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
  <div :class="['input-text', { 'mark-red': item.isError }]">
    <bk-date-picker
      font-size="14"
      class="king-date-picker"
      :placeholder="$t('请选择日期')"
      :value="item.value === $t('永久') ? '2100-01-01' : item.value"
      :disabled="editStatus && !item.editable"
      :options="starttimePickerOptions"
      @change="changeDate">
    </bk-date-picker>
  </div>
</template>

<script>
import moment from 'moment';
export default {
  props: {
    item: {
      type: Object,
      required: true,
    },
    editStatus: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      starttimePickerOptions: {},
    };
  },
  mounted() {
    // 初始化高级配置启动时间
    this.starttimePickerOptions = {
      disabledDate(time) {
        return (
          time.getTime() < moment(new Date())
            .subtract(1, 'days')
            .valueOf()
        );
      },
    };
  },
  methods: {
    changeDate(date) {
      // eslint-disable-next-line vue/no-mutating-props
      this.item.value = date;
      // eslint-disable-next-line vue/no-mutating-props
      this.item.isError = false;
      window.changeInput = true;
    },
  },
};
</script>

<style lang="scss">
.input-text .king-date-picker {
  width: 100%;
}

.mark-red .king-date-picker input {
  border: 1px solid #ea3636;
}
</style>
