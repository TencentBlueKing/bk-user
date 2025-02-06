<template>
  <bk-dialog
    :is-show="isShowRenewal"
    :title="$t('账号续期')"
    quick-close
    @closed="isShowRenewal = false"
    @confirm="confirmRenewal"
  >
    <div>
      <bk-form class="example" ref="formRef" form-type="vertical" :model="formData">
        <bk-form-item :label="$t('续期时长')" property="dateTime" required>
          <bk-select v-model="formData.dateTime" input-search>
            <bk-option
              v-for="(option, i) in dateOptions"
              :key="i"
              :id="option.id"
              :name="option.name"
              :disabled="option.id !== '-2'">
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item :label="$t('账号过期时间')" property="custom" required>
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
    </div>
  </bk-dialog>
</template>

<script setup lang="ts">
import dayjs, { ManipulateType } from 'dayjs';
import { computed, reactive } from 'vue';

import { batchAccountExpired } from '@/http/organizationFiles';
import { t } from '@/language/index';

const isShowRenewal = defineModel<boolean>('isShowRenewal');

const props = defineProps({
  userIds: {
    type: Array<String>,
  },
});
const emits = defineEmits(['batchRenewal']);

const formData = reactive({
  dateTime: '-2',
  custom: '',
});

const disabledDate = (date: Date) => date.valueOf() < Date.now();
const defineDateTime = (num: number, unit: ManipulateType) => dayjs(new Date()).add(num, unit)
  .format('YYYY-MM-DD');
const dateOptions = computed(() => {
  const expirationTimes = [
    { num: 1, unit: 'month', label: t('一个月') },
    { num: 3, unit: 'month', label: t('三个月') },
    { num: 6, unit: 'month', label: t('六个月') },
    { num: 1, unit: 'year', label: t('一年　') },
  ] as Array<{
    num: number
    unit: ManipulateType
    label: string
  }>;
  const options = expirationTimes.map(({ num, unit, label }) => {
    const date = defineDateTime(num, unit);
    return { id: `${date} 00:00:00`, name: `${label}` };
  });
  options.push(
    { id: '2100-1-1T00:00:00', name: t('永久') },
    { id: '-2', name: t('自定义') },
  );
  return options;
});

const confirmRenewal = async () => {
  const params = { user_ids: props.userIds, account_expired_at: '' };
  params.account_expired_at = dayjs(formData.custom).format('YYYY-MM-DD HH:mm:ss');
  await batchAccountExpired(params);
  formData.custom = '';
  emits('batchRenewal');
};


</script>

<style lang="less" scoped>

</style>
