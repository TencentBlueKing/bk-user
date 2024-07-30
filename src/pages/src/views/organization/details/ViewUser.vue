<template>
  <ul class="details-content">
    <li>
      <div class="details-content-info">
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('用户ID') }}：</span>
          <span class="details-content-value">{{ userData.id }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('用户名') }}：</span>
          <span class="details-content-value">{{ userData.username }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('姓名') }}：</span>
          <span class="details-content-value">{{ userData.full_name }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('邮箱') }}：</span>
          <span class="details-content-value">{{ userData.email || '--' }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('手机号') }}：</span>
          <span class="details-content-value">{{ userData.phone_country_code ? `(+${userData.phone_country_code}) ${userData.phone}` : userData.phone || '--' }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('所属组织') }}：</span>
          <span
            class="details-content-value" v-if="userData.departments.length > 0"
            v-bk-tooltips="{ content: (userData.organization_paths || []).join('\n'),
                             placement: 'top',
                             disabled: userData.departments.length === 0 }"
          >
            <!-- {{ formatConvert(userData.departments) }} -->
            {{detail.organization_paths}}
            {{ userData.departments.join('、') || '--' }}
          </span>
          <span class="details-content-value" v-else>{{ '--' }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('直属上级') }}：</span>
          <span class="details-content-value" v-if="(detail.leaders || []).length > 0">
            {{ formatConvert(detail.leaders) || '--' }}
          </span>
          <span class="details-content-value" v-else>{{ '--' }}</span>
        </div>
        <div class="details-content-item">
          <span class="details-content-key">{{ $t('账号过期时间') }}：</span>
          <span class="details-content-value">
            {{ remainingDays(detail.account_expired_at) }}
          </span>
          <button v-if="isShowBtn" class="text-[#3A84FF] ml-[16px] text-[14px]" @click="renewalClick">
            {{ $t('续期') }}
          </button>
        </div>
        <CustomFieldsView :extras="detail.extras" />
      </div>
      <img v-if="detail.logo" class="user-logo" :src="detail.logo" alt="" />
      <img v-else class="user-logo" src="@/images/avatar.png" alt="" />
    </li>
  </ul>
  <bk-dialog :is-show="isShowRenewal" :title="$t('账号续期')" quick-close @confirm="handleConfirm" @closed="handleClosed">
    <div class="mb-[21px]">{{ $t('过期时间：') }}{{ detail.account_expired_at?.split(' ')[0] }}</div>
    <bk-form class="example" ref="formRef" form-type="vertical" :model="formData">
      <bk-form-item :label="$t('续期时长')" property="dateTime" required>
        <bk-select v-model="formData.dateTime" input-search @change="dateChange">
          <bk-option v-for="(option, i) in dateOptions" :key="i" :id="option.id" :name="option.name"></bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item v-if="showExpirationTime" :label="$t('账号过期时间')" property="custom" required>
        <bk-date-picker
          v-model="formData.custom"
          :disabled-date="disabledDate"
          :placeholder="$t('自定义')"
          type="datetime"
          format="yyyy-MM-dd HH:mm:ss"
          append-to-body>
        </bk-date-picker>
      </bk-form-item>
    </bk-form>
  </bk-dialog>
</template>

<script setup lang="ts">
import dayjs from 'dayjs';
import { computed, defineEmits, defineProps, ref } from 'vue';

import CustomFieldsView from '@/components/custom-fields/view.vue';
import { getTenantUserValidityPeriod, updateAccountExpiredAt } from '@/http';
import { t } from '@/language/index';
import { formatConvert } from '@/utils';

const props = defineProps({
  userData: {
    type: Object,
    default: () => ({}),
  },
  detail: {
    type: Object,
    default: () => ({}),
  },
  isShowBtn: {
    type: Boolean,
  },
});

const emit = defineEmits(['updateUsers']);
const isShowRenewal = ref(false); // 续期
const disabledDate = date => date.valueOf() < Date.now();
const showExpirationTime = ref(false);
const formRef = ref();
const formData = ref({
  dateTime: '',
  custom: '',
});
const expirationTime = ref(props.detail.account_expired_at?.split(' ')[0]); // 过期时间
const expirationTimes = [
  { num: 1, unit: 'month', label: t('一个月') },
  { num: 3, unit: 'month', label: t('三个月') },
  { num: 6, unit: 'month', label: t('六个月') },
  { num: 1, unit: 'year', label: t('一年　') },
];

const defineDateTime = (num, unit) => dayjs(expirationTime.value).add(num, unit)
  .format('YYYY-MM-DD');
const dateOptions = expirationTimes.map(({ num, unit, label }) => {
  const date = defineDateTime(num, unit);
  return { id: `${date} 00:00:00`, name: `${label} (至${date})` };
});

dateOptions.push(
  { id: '2100-1-1T00:00:00', name: t('永久') },
  { id: '-2', name: t('自定义') },
);

const handleConfirm = async () => {
  await formRef.value.validate();
  const  params = {
    account_expired_at: formData.value.dateTime === '-2' ? formData.value.custom : formData.value.dateTime,
  };
  updateAccountExpiredAt(props.detail.id, params).then(() => {
    handleClosed();
    emit('updateUsers', t('更新成功'));
  });
};
const handleClosed = () => {
  formRef.value.clearValidate();
  isShowRenewal.value = false;
};
// 续期
const renewalClick = async () => {
  isShowRenewal.value = true;
  const res = await getTenantUserValidityPeriod();
  const { validity_period } = res.data;
  let dateTime;
  if (res.data.validity_period === -1) {
    dateTime = '2100-1-1T00:00:00';
  } else {
    const unit = validity_period === 365 ? 'year' : 'month';
    const num = validity_period === 365 ? 1 : validity_period / 30;
    dateTime = `${defineDateTime(num, unit)} 00:00:00`;
  }
  formData.value.dateTime = dateTime;
};

// 日期改变
const dateChange = (val) => {
  // 续期时长选择自定义时， 弹出过期时间选择框
  showExpirationTime.value = val === '-2';
};

// 处理续期的展示
const remainingDays = computed(() => (params) => {
  const futureDate = Date.UTC(2100, 0, 1);
  const specifiedTimestamp = new Date(params).getTime();
  if (specifiedTimestamp === futureDate) return t('永久');
  const diffInDays = Math.ceil((new Date(params) - new Date()) / (24 * 60 * 60 * 1000));
  return diffInDays > 0 ? `${params} (${t('剩余x天', { diffInDays })})` : `${params} (${t('已过期')})`;
});
</script>

<style lang="less" scoped>
@import url("@/css/viewUser.less");
</style>
