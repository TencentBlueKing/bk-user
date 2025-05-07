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
  <div data-test-id="profileInfo">
    <bk-form
      :model="profileInfoData"
      :rules="rules"
      ref="validateForm"
      form-type="vertical"
      v-if="profileInfoList.length">
      <bk-form-item
        class="infor-list"
        v-for="(item,index) in profileInfoList" :key="index"
        :label="item.display_name"
        :required="item.require"
        :property="item.key"
        :error-display-type="'normal'">
        <InputPhone
          ref="phone"
          v-if="item.key === 'telephone'"
          :item="item"
          :edit-status="editStatus"
          @phone="(val) => item.isError = val" />
        <template v-else-if="item.key.includes(dateKey)">
          <bk-date-picker
            ext-cls="ext-cls"
            v-model="item.value"
            @change="changSelect"
            format="yyyy-MM-dd"
            :placeholder="'选择日期时间'"
            :shortcuts="shortcuts"
            :type="'date'">
          </bk-date-picker>
        </template>
        <InputDate
          v-else-if="item.type === 'timer'"
          :item="item" :edit-status="editStatus" />
        <InputString
          v-else-if="item.type === 'string' || item.type === 'number'"
          :item="item"
          :edit-status="editStatus" />
        <InputSelect
          v-else-if="item.type.indexOf('enum') !== -1"
          :item="item"
          :edit-status="editStatus"
          :status-map="statusMap" />
      </bk-form-item>
    </bk-form>
  </div>

</template>

<script>
import InputString from './InputString';
import InputSelect from './InputSelect';
import InputDate from './InputDate';
import InputPhone from './InputPhone';
export default {
  components: {
    InputString,
    InputSelect,
    InputDate,
    InputPhone,
  },
  props: {
    editStatus: {
      type: Boolean,
      required: true,
    },
    profileInfoList: {
      type: Array,
      required: true,
    },
    statusMap: {
      type: Object,
      default: {},
    },
    rules: {
      type: Object,
      required: true,
    },
    expireDate: {
      type: Object,
      default: {},
    },
  },
  data() {
    return {
      dateKey: ['account_expiration_date'],
    };
  },
  computed: {
    shortcuts() {
      const dayTime = 24 * 60 * 60 * 1000;
      const nowTime = new Date().getTime();
      return this.$store.state.passwordValidDaysList.map((item) => {
        const date = item.days > 0 ? new Date(nowTime + dayTime * item.days) : '2100-01-01';
        return {
          text: item.text,
          value: () => new Date(date),
        };
      });
    },

    profileInfoData() {
      const obj = {};
      this.profileInfoList.forEach((item) => {
        if (item.key.includes(this.dateKey)) {
          item.value = (item.value && new Date(item.value)) || new Date();
        }
        this.$set(obj, item.key, item.value);
      });
      return obj;
    },
  },
  mounted() {
    window.changeInput = false;
  },
  methods: {
    changSelect() {
      window.changeInput = true;
    },
  },
};
</script>

<style lang="scss" scoped>
.infor-list {
  font-size: 14px;
  color: rgba(99, 101, 110, 1);

  &.no-verifica {
    .select-text {
      padding-right: 12px;
    }
  }

  &:nth-child(1),
  &:nth-child(2) {
    .input-text {
      width: 475px;

      .select-text {
        width: 475px;
      }
    }
  }

  .desc {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
    padding-top: 17px;
    line-height: 19px;

    .star {
      display: inline-block;
      vertical-align: middle;
      margin-left: 4px;
      color: #fe5c5c;
    }

    .account-msg {
      margin-left: 4px;
      outline: none;
      display: inline-block;
      vertical-align: middle;
      font-size: 16px;
    }
  }

  .input-text {
    position: relative;

    .select-text {
      display: block;
      padding: 0 30px 0 12px;
      width: 460px;

      &.active {
        color: #63656e !important;
      }

      &.disable {
        background-color: #fafbfd;
        cursor: not-allowed;
      }
    }

    .icon-user-exclamation-circle-shape {
      position: absolute;
      right: 10px;
      top: 10px;
      font-size: 16px;
      color: #ea3636;
    }
  }

  ::v-deep .form-error-tip {
    width: 475px;
  }
}
.tips-style {
  color: #ea3636;
}
.ext-cls {
  width: 100%;
}
</style>
