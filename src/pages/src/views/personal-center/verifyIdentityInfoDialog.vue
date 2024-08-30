<template>
  <bk-dialog
    v-model:is-show="isShow"
    render-directive="if"
    :close-icon="false"
    :quick-close="false">
    <template #header>
      <div class="pt-[20px] pl-[20px]">
        <span class="font-black text-[30px]">{{ dialogTitle }}</span>
        <div class="text-xs mt-[10px] text-[#8a8b92]">
          <slot name="header-tips"></slot>
          {{ unSupportEditEmail ? t('继承数据源邮箱不支持编辑，已为您切换为自定义模式进行编辑') : '' }}
        </div>
      </div>
    </template>
    <template #default>
      <bk-form :model="verifyForm" ref="verifyFormRef" :rules="verifyFormRules" form-type="vertical">
        <bk-tab v-model:active="active" type="unborder-card" ext-cls="verify-identity-info-tab-panel">
          <bk-tab-panel
            v-for="item in Panels"
            :key="item.name"
            :label="item.label"
            :name="item.name">
            <bk-form-item
              class="m-[10px] mt-[20px] !mb-[10px] h-[40px]"
              v-if="curFormItemList.includes(formItemPropName.inheritEmail)">
              <img :src="emailImg" class="verify-icon" />
              <span>
                {{ `${t('请输入')} ${curEmailText} ${'收到的邮箱验证码'}` }}
              </span>
            </bk-form-item>

            <bk-form-item
              class="m-[10px] mt-[20px] !mb-[10px] h-[40px]"
              v-if="curFormItemList.includes(formItemPropName.inheritPhone)">
              <img :src="phoneImg" class="verify-icon" />
              <span>
                {{ `${t('请输入')} ${curPhoneText} ${'收到的手机验证码'}` }}
              </span>
            </bk-form-item>
            <bk-form-item
              class="m-[10px] mt-[20px] !mb-[10px] h-[40px]"
              v-if="curFormItemList.includes(formItemPropName.customEmail)" property="email">
              <bk-input :placeholder="t('请输入邮箱以接收邮箱验证码')" v-model="verifyForm.email">
                <template #prefix>
                  <span class="input-icon flex items-center">
                    <img :src="emailImg" class="verify-icon ml-[5px]" />
                  </span>
                </template>
              </bk-input>
            </bk-form-item>

            <bk-form-item
              class="m-[10px] mt-[20px] !mb-[10px] h-[40px]"
              v-if="curFormItemList.includes(formItemPropName.customPhone)" property="phone">
              <bk-input :placeholder="t('请输入手机号以接收短信验证码')" v-model="verifyForm.phone">
                <template #prefix>
                  <span class="input-icon flex items-center">
                    <img :src="phoneImg" class="verify-icon ml-[5px]" />
                  </span>
                </template>
              </bk-input>
            </bk-form-item>

            <bk-form-item
              class="m-[10px] mt-[20px]"
              v-if="curFormItemList.includes(formItemPropName.captcha)">
              <div class="flex justify-center">
                <bk-input
                  :placeholder="t('请输入验证码')"
                  v-model="verifyForm.captcha"
                  property="captcha"
                  :disabled="unSupportEditEmail" />
                <bk-button
                  outline theme="primary" class="ml-[10px] w-[120px]"
                  :disabled="unSupportEditEmail || verifyFormCaptchaBtn.disabled"
                  @click="handleSendCaptcha">
                  {{ verifyFormCaptchaBtn.disabled ? `${verifyFormCaptchaBtn.times}s` : t('获取验证码') }}
                </bk-button>
              </div>
            </bk-form-item>

          </bk-tab-panel>
        </bk-tab>
      </bk-form>
    </template>
    <template #footer>
      <div class="pb-[20px] m-[10px] mb-[0px]">
        <bk-button
          class="w-[100%] mb-[10px] block" theme="primary" size="large" width="100%"
          :loading="submitBtnLoading"
          :disabled="unSupportEditEmail && currentVerifyConfig.active === OpenDialogActive.inherit"
          @click="handleSubmitVerifyForm">
          {{ t('确定') }}
        </bk-button>
        <bk-button class="w-[100%]" size="large" @click="handleCloseVerifyDialog">{{ t('取消') }}</bk-button>
      </div>
    </template>
  </bk-dialog>
</template>

<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { InfoBox } from 'bkui-vue';
import type { Props as BkInfoBoxConfig } from 'bkui-vue/lib/info-box/info-box';
import { computed, defineModel, defineProps, PropType, reactive, ref, watch } from 'vue';

import { formItemPropName, OpenDialogActive, OpenDialogMode, openDialogResult, OpenDialogType } from './openDialogType';

import { useCountDown } from '@/hooks';
import { postPersonalCenterUserEmailCaptcha, postPersonalCenterUserPhoneCaptcha } from '@/http/personalCenterFiles';
import emailImg from '@/images/email.svg';
import phoneImg from '@/images/phone.svg';
import { t } from '@/language/index';

interface VerifyConfig {
  type: OpenDialogType,
  mode: OpenDialogMode,
  active: OpenDialogActive
}

const props = defineProps({
  curEmailText: {
    type: String,
    default: '',
  },
  curPhoneText: {
    type: String,
    default: '',
  },
  userId: {
    type: String,
  },
  currentVerifyConfig: {
    type: Object as PropType<VerifyConfig>,
  },
});

const isShow = defineModel<boolean>('isShow', { required: true });

const dialogTitle = computed(() => {
  if (props.currentVerifyConfig.mode === OpenDialogMode.Edit) {
    return props.currentVerifyConfig.type === OpenDialogType.email ? t('编辑邮箱') : t('编辑手机号');
  }
  if (props.currentVerifyConfig.mode === OpenDialogMode.Verify) {
    return props.currentVerifyConfig.type === OpenDialogType.email ? t('邮箱验证') : t('手机号验证');
  }
  return '';
});

const curFormItemList = computed(() => {
  let formItemList = Object.values({ ...formItemPropName });
  if (active.value === OpenDialogActive.inherit) {
    formItemList = formItemList.filter(item => !item.includes(OpenDialogActive.custom));
  }
  if (active.value === OpenDialogActive.custom) {
    formItemList = formItemList.filter(item => !item.includes(OpenDialogActive.inherit));
  }
  if (props.currentVerifyConfig.type === OpenDialogType.email) {
    formItemList = formItemList.filter(item => !item.includes(OpenDialogType.phone));
  }
  if (props.currentVerifyConfig.type === OpenDialogType.phone) {
    formItemList = formItemList.filter(item => !item.includes(OpenDialogType.email));
  }
  return formItemList;
});

const active = ref(props.currentVerifyConfig.active);
const Panels = ref([
  {
    label: t('继承数据源'),
    name: OpenDialogActive.inherit,
    slotName: OpenDialogActive.inherit,
  },
  {
    label: t('自定义'),
    name: OpenDialogActive.custom,
    slotName: OpenDialogActive.custom,
  },
]);

interface VerifyForm {
  email: string,
  phone: string,
  captcha: string,
};

const verifyFormCaptchaBtn = reactive({
  disabled: false,
  times: 0,
});

// 发送验证码
const handleSendCaptcha = async () => {
  console.log(verifyFormRef);
  const validate = await verifyFormRef.value.validate();
  console.log(validate);
  return;

  const captchaCoolingTime = 10;
  const shutDownPointTime = 0;
  const { closeTimePolling } = useCountDown({
    beforeStart: () => {
      (async () => {
        verifyFormCaptchaBtn.times = captchaCoolingTime;
        verifyFormCaptchaBtn.disabled = true;
        const { userId } = props;
        if (props.currentVerifyConfig.type === OpenDialogType.email) {
          const result = await postPersonalCenterUserEmailCaptcha(userId, {
            email: verifyForm.email,
          });
          console.log(result);
        }
        // else if (props.currentVerifyConfig.type === OpenDialogType.phone) {
        //   const result = await postPersonalCenterUserPhoneCaptcha(userId,{

        //   });
        // }
      })();
    },
    intervalFn: () => verifyFormCaptchaBtn.times -= 1,
    beforeClose: () => verifyFormCaptchaBtn.disabled = false,
  });

  watch([() => verifyFormCaptchaBtn.times, isShow], ([curBtnTimes, curShow]) => {
    curBtnTimes === shutDownPointTime && closeTimePolling();
    !curShow && closeTimePolling();
  });
  return;
};

const verifyForm = reactive<VerifyForm>({
  email: '',
  phone: '',
  captcha: '',
});
const verifyFormRef = ref(null);
const verifyFormRules = {
  email: [
    {
      validator: (value: string) => !!value,
      message: t('邮箱不允许为空'),
      trigger: 'blur',
    },
  ],
  phone: [
    {
      validator: (value: string) => !!value,
      message: t('手机号不允许为空'),
      trigger: 'blur',
    },
  ],
};

const resetCustomForm = () => {
  verifyForm.email = '';
  verifyForm.phone = '';
  verifyForm.captcha = '';
};

const unSupportEditEmail = computed(() => props.currentVerifyConfig.type === OpenDialogType.email
&& props.currentVerifyConfig.mode === OpenDialogMode.Edit);

const handleCloseVerifyDialog = () => {
  isShow.value = false;
  resetCustomForm();
};

const submitBtnLoading = ref(false);
const handleSubmitVerifyForm = async () => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { type, mode, active } = props.currentVerifyConfig;
  const { email, phone } = OpenDialogType;
  const { inherit, custom } = OpenDialogActive;
  const { success, fail } = openDialogResult;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  submitBtnLoading.value = true;
  const infoBoxConfig: Partial<BkInfoBoxConfig> = {
    type: success,
    title: '',
    closeIcon: false,
  };
  // console.log(type, mode, active);

  // if (type === email && active === custom)

  if (type === email && infoBoxConfig.type === success) infoBoxConfig.title = t('邮箱验证成功');
  if (type === email && infoBoxConfig.type === fail) infoBoxConfig.title = t('邮箱验证失败');
  if (type === phone && infoBoxConfig.type === success) infoBoxConfig.title = t('手机号验证成功');
  if (type === phone && infoBoxConfig.type === fail) infoBoxConfig.title = t('手机号验证失败');

  submitBtnLoading.value = false;
  // handleCloseVerifyDialog();
  // InfoBox(infoBoxConfig);
};

</script>

<style lang="less">
.verify-identity-info-tab-panel {
  margin-top: -10px;
  height: 170px;
  .bk-tab-header {
    justify-content: center;
  }
}

.verify-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  margin-right: 5px;
  vertical-align: middle;
}
</style>
