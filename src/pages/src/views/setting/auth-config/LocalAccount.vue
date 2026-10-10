<template>
  <div class="details-wrapper">
    <bk-form
      class="px-[24px] pt-[24px] pb-[60px] flex flex-col gap-[16px]"
      form-type="vertical"
      ref="formRef"
      :model="formData"
      :rules="rulesInfo"
      v-bkloading="{ loading: isLoading }">
      <Row :title="$t('基本信息')" class="!pb-[8px]">
        <bk-form-item :label="$t('名称')" property="name" required>
          <bk-input
            style="width: 600px;"
            v-model="formData.name"
            :placeholder="validate.loginName.message"
            @focus="handleChange" />
        </bk-form-item>
        <bk-form-item :label="$t('是否启用')" required>
          <bk-switcher
            :value="formData.config?.enable_password"
            theme="primary"
            size="large"
            @change="changeAccountPassword"
          />
        </bk-form-item>
      </Row>
      <EffectiveScopeEditor
        v-model="formData.data_source_ids"
        local-only
        @change="handleChange"
        @unenabled-change="handleUnenabledChange"
      />
    </bk-form>
    <div class="footer">
      <!-- 仅账密开关开启时，生效范围的未启用密码规则状态才拦截提交；关闭时不产生任何效果 -->
      <bk-button
        theme="primary"
        class="mr8"
        @click="handleSubmit"
        :loading="btnLoading"
        :disabled="isDisabled || !!(formData.config?.enable_password && hasUnenabledDataSource)">
        {{ $t('提交') }}
      </bk-button>
      <bk-button @click="emit('cancel')">{{ $t('取消') }}</bk-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { InfoBox } from 'bkui-vue';
import { onMounted, reactive, ref, watch } from 'vue';

import EffectiveScopeEditor from './EffectiveScopeEditor.vue';

import Row from '@/components/layouts/ItemRow.vue';
import { useValidate } from '@/hooks';
import {
  getDefaultConfig,
  postLocalIdps,
  putLocalIdps,
} from '@/http';
import { LocalIdpDetail, LocalIdpPluginConfig, NewLocalIdpsParams } from '@/http/types/authSourceFiles';
import { t } from '@/language/index';

interface IProps {
  data?: LocalIdpDetail;
}
const props = defineProps<IProps>();

const emit = defineEmits(['cancel', 'success']);

const validate = useValidate();

const rulesInfo = {
  name: [validate.required, validate.loginName],
};

const formRef = ref();
const isLoading = ref(false);
let originalData = {};
const isDisabled = ref(true);
/** 生效范围中存在未启用密码规则的数据源：禁止提交（原因由生效范围的 Alert 提示） */
const hasUnenabledDataSource = ref(false);

const formData = reactive({
  name: '',
  status: '',
  config: {} as LocalIdpPluginConfig,
  data_source_ids: [],
});

const btnLoading = ref(false);

const handleSubmit = async () => {
  try {
    const valid = await formRef.value?.validate?.().catch(() => false);
    if (!valid) return;
    btnLoading.value = true;
    const params: NewLocalIdpsParams = {
      name: formData.name,
      status: formData.config?.enable_password ? 'enabled' : 'disabled',
      plugin_config: formData.config,
      data_source_ids: formData.data_source_ids,
    };
    if (props.data?.id) {
      params.id = props.data?.id;
      await putLocalIdps(params);
      emit('success', formData.config?.enable_password);
    } else {
      await postLocalIdps(params);
      emit('success', formData.config?.enable_password);
    }
  } catch (e) {
    console.warn(e);
  } finally {
    btnLoading.value = false;
  }
};

const handleChange = () => {
  window.changeInput = true;
};

/** 生效范围中存在未启用密码规则的数据源时，禁止提交 */
const handleUnenabledChange = (hasUnenabled: boolean) => {
  hasUnenabledDataSource.value = hasUnenabled;
};

const changeAccountPassword = (value: boolean) => {
  if (!value) {
    InfoBox({
      title: t('确认要关闭账密登录吗？'),
      subTitle: t('关闭后用户将无法通过账密登录'),
      onConfirm() {
        formData.config.enable_password = value;
      },
      onCancel() {
        formData.config.enable_password = !value;
      },
      quickClose: false,
    });
  } else {
    formData.config.enable_password = value;
  }
  window.changeInput = true;
};

let isInitialized = false;

watch(formData, () => {
  if (!isInitialized) return;
  isDisabled.value = props?.data?.id ? JSON.stringify(originalData) === JSON.stringify(formData) : false;
  window.changeInput = !isDisabled.value;
}, { deep: true });

onMounted(async () => {
  isLoading.value = true;
  try {
    if (props.data?.id) {
      // 从查看态传入的详情数据直接回填，避免重复请求
      formData.name = props.data.name;
      formData.status = props.data.status;
      formData.config = props.data.plugin_config;
      formData.data_source_ids = props.data.data_source_ids;
    } else {
      // 新增态：回填认证源名称（父组件传入的默认对象）
      formData.name = props.data?.name || '';
      // 新增本地认证源：本地认证源依赖本地数据源（未配置本地数据源时无法进入此表单），
      // 默认配置（含账密开关 enable_password 的默认值）统一由 default-config 接口返回，前端不做覆盖；
      // 其他认证源（WeCom/Custom）的 plugin_config 结构固定，在组件内初始化默认结构即可，无需请求
      const res = await getDefaultConfig('local');
      formData.config = (res?.data?.config || {})  as LocalIdpPluginConfig;
    }
    originalData = JSON.parse(JSON.stringify(formData));
    isInitialized = true;
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
});
</script>

<style lang="less" scoped>
@import url('./Local.less');
</style>
