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
      <bk-tab v-model:active="active" type="unborder-card" ext-cls="verify-identity-info-tab-panel">
        <bk-tab-panel
          v-for="item in Panels"
          :key="item.name"
          :label="item.label"
          :name="item.name">
          <bk-form :model="customForm" form-type="vertical">
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
              v-if="curFormItemList.includes(formItemPropName.customEmail)">
              <bk-input :placeholder="t('请输入邮箱以接收邮箱验证码')" v-model="customForm.email">
                <template #prefix>
                  <span class="input-icon flex items-center">
                    <img :src="emailImg" class="verify-icon ml-[5px]" />
                  </span>
                </template>
              </bk-input>
            </bk-form-item>

            <bk-form-item
              class="m-[10px] mt-[20px] !mb-[10px] h-[40px]"
              v-if="curFormItemList.includes(formItemPropName.customPhone)">
              <bk-input :placeholder="t('请输入手机号以接收短信验证码')" v-model="customForm.phone">
                <template #prefix>
                  <span class="input-icon flex items-center">
                    <img :src="phoneImg" class="verify-icon ml-[5px]" />
                  </span>
                </template>
              </bk-input>
            </bk-form-item>

            <bk-form-item
              class="m-[10px] mt-[0px]"
              v-if="curFormItemList.includes(formItemPropName.captcha)">
              <div class="flex justify-center">
                <bk-input
                  :placeholder="t('请输入验证码')"
                  v-model="inheritForm.captcha"
                  property="captcha"
                  :disabled="unSupportEditEmail" />
                <bk-button
                  outline theme="primary" class="ml-[10px] w-[120px]"
                  :disabled="unSupportEditEmail || inheritFormCaptchaBtn.disabled"
                  @click="handleSendCaptcha(OpenDialogActive.inherit)">
                  {{ inheritFormCaptchaBtn.disabled ? `${inheritFormCaptchaBtn.times}s` : t('获取验证码') }}
                </bk-button>
              </div>
            </bk-form-item>

          </bk-form>
        </bk-tab-panel>
      </bk-tab>
    </template>
    <template #footer>
      <div class="pb-[20px] m-[10px] mb-[0px]">
        <bk-button
          class="w-[100%] mb-[10px] block" theme="primary" size="large" width="100%"
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

interface InheritForm {
  captcha: string,
}
const inheritForm = reactive<InheritForm>({
  captcha: '',
});
const resetInheritForm = () => {
  inheritForm.captcha = '';
};

interface CustomForm {
  email: string,
  phone: string,
  captcha: string,
}

const inheritFormCaptchaBtn = reactive({
  disabled: false,
  times: 0,
});

const customFormCaptchaBtn = reactive({
  disabled: false,
  times: 0,
});

const handleSendCaptcha = (active: OpenDialogActive) => {
  const captchaCoolingTime = 10;
  const shutDownPointTime = 0;
  if (active === OpenDialogActive.inherit) {
    const { closeTimePolling } = useCountDown({
      beforeStart: () => {
        inheritFormCaptchaBtn.times = captchaCoolingTime;
        inheritFormCaptchaBtn.disabled = true;
      },
      intervalFn: () => inheritFormCaptchaBtn.times -= 1,
      beforeClose: () => inheritFormCaptchaBtn.disabled = false,
    });

    watch([() => inheritFormCaptchaBtn.times, isShow], ([curBtnTimes, curShow]) => {
      curBtnTimes === shutDownPointTime && closeTimePolling();
      !curShow && closeTimePolling();
    });
    return;
  }
  if (active === OpenDialogActive.custom) {
    const { closeTimePolling } = useCountDown({
      beforeStart: () => {
        customFormCaptchaBtn.times = captchaCoolingTime;
        customFormCaptchaBtn.disabled = true;
      },
      intervalFn: () => customFormCaptchaBtn.times -= 1,
      beforeClose: () => inheritFormCaptchaBtn.disabled = false,
    });

    watch([() => customFormCaptchaBtn.times, isShow], ([curBtnTimes, curShow]) => {
      curBtnTimes === shutDownPointTime && closeTimePolling();
      !curShow && closeTimePolling();
    });
    return;
  }
};


const customForm = reactive<CustomForm>({
  email: '',
  phone: '',
  captcha: '',
});
const resetCustomForm = () => {
  customForm.email = '';
  customForm.phone = '';
  customForm.captcha = '';
};

const unSupportEditEmail = computed(() => props.currentVerifyConfig.type === OpenDialogType.email
&& props.currentVerifyConfig.mode === OpenDialogMode.Edit);

const handleCloseVerifyDialog = () => {
  isShow.value = false;
  resetInheritForm();
  resetCustomForm();
};

const handleSubmitVerifyForm = async () => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { type, mode, active } = props.currentVerifyConfig;
  const { email, phone } = OpenDialogType;
  const { success, fail } = openDialogResult;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { inherit, custom } = OpenDialogActive;

  const infoBoxConfig: Partial<BkInfoBoxConfig> = {
    type: success,
    title: '',
    closeIcon: false,
  };

  // console.log(type, mode, active);

  if (type === email && infoBoxConfig.type === success) infoBoxConfig.title = t('邮箱验证成功');
  if (type === email && infoBoxConfig.type === fail) infoBoxConfig.title = t('邮箱验证失败');
  if (type === phone && infoBoxConfig.type === success) infoBoxConfig.title = t('手机号验证成功');
  if (type === phone && infoBoxConfig.type === fail) infoBoxConfig.title = t('手机号验证失败');

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
