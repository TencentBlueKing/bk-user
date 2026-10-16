<template>
  <div class="details-wrapper">
    <bk-form
      class="px-[24px] pt-[24px] pb-[60px] flex flex-col gap-[16px]"
      form-type="vertical"
      ref="formRef"
      :model="formData"
      :rules="rulesInfo">
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
            :value="formData.enabled"
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
      <!-- 生效范围中存在未启用密码规则的数据源时始终拦截提交：后端对生效范围强校验，不区分认证源启停状态 -->
      <bk-button
        theme="primary"
        class="mr8"
        @click="handleSubmit"
        :loading="btnLoading"
        :disabled="isDisabled || hasUnenabledDataSource">
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
  postIdps,
  putIdps,
} from '@/http';
import type { IdpDetail, NewIdpsParams } from '@/http/types/authSourceFiles';
import { t } from '@/language/index';

interface IProps {
  /** 编辑态为完整详情，新增态仅传默认名称 */
  data?: Partial<IdpDetail>;
}
const props = defineProps<IProps>();

const emit = defineEmits(['cancel', 'success']);

const validate = useValidate();

const rulesInfo = {
  name: [validate.required, validate.loginName],
};

const formRef = ref();
let originalData = {};
const isDisabled = ref(true);
/** 生效范围中存在未启用密码规则的数据源：禁止提交（原因由生效范围的 Alert 提示） */
const hasUnenabledDataSource = ref(false);

const formData = reactive({
  name: '',
  /** 账密登录启用，与认证源 status（enabled/disabled）等价，默认开启 */
  enabled: true,
  data_source_ids: [] as number[],
});

const btnLoading = ref(false);

const handleSubmit = async () => {
  try {
    const valid = await formRef.value?.validate?.().catch(() => false);
    if (!valid) return;
    btnLoading.value = true;
    const params: Omit<NewIdpsParams, 'plugin_id'> = {
      name: formData.name,
      status: formData.enabled ? 'enabled' : 'disabled',
      plugin_config: {},
      // local 认证源的字段比对规则按后端约定写死为 id 对 id（固定字符串，无业务含义）
      data_source_match_rules: formData.data_source_ids.map(id => ({
        data_source_id: id,
        field_compare_rules: [{ source_field: 'id', target_field: 'id' }],
      })),
    };
    if (props.data?.id) {
      await putIdps({ ...params, id: props.data.id });
    } else {
      await postIdps({ ...params, plugin_id: 'local' });
    }
    emit('success', formData.enabled);
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
        formData.enabled = value;
      },
      onCancel() {
        formData.enabled = !value;
      },
      quickClose: false,
    });
  } else {
    formData.enabled = value;
  }
  window.changeInput = true;
};

let isInitialized = false;

watch(formData, () => {
  if (!isInitialized) return;
  isDisabled.value = props?.data?.id ? JSON.stringify(originalData) === JSON.stringify(formData) : false;
  window.changeInput = !isDisabled.value;
}, { deep: true });

onMounted(() => {
  if (props.data?.id) {
    // 从查看态传入的详情数据直接回填，避免重复请求
    formData.name = props.data.name ?? '';
    formData.enabled = props.data.status === 'enabled';
    formData.data_source_ids = (props.data.data_source_match_rules ?? []).map(item => item.data_source_id);
  } else {
    // 新增态：回填认证源名称（父组件传入的默认对象），开关默认开启，无异步取数
    formData.name = props.data?.name || '';
  }
  originalData = JSON.parse(JSON.stringify(formData));
  isInitialized = true;
});
</script>

<style lang="less" scoped>
@import url('./Local.less');
</style>
