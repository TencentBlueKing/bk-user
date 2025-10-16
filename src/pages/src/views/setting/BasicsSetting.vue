<template>
  <div class="basics-setting-wrapper">
    <div class="mb-[24px]" v-if="isEdit">
      <bk-form
        ref="formRef"
        form-type="vertical"
        :model="formData"
        :rules="rules">
        <Row title="">
          <div class="flex items-center">
            <div class="w-[560px] mr-[100px]">
              <bk-form-item :label="$t('租户名称')" property="name" required>
                <bk-input v-model="formData.name" :placeholder="validate.name.message" />
              </bk-form-item>
              <bk-form-item :label="$t('租户ID')" property="id" required>
                <bk-input v-model="formData.id" readonly />
              </bk-form-item>
            </div>
            <bk-form-item :label="$t('租户logo')">
              <bk-upload
                theme="picture"
                with-credentials
                :multiple="false"
                :files="files"
                :handle-res-code="handleRes"
                :url="formData.logo"
                :custom-request="customRequest"
                :size="2"
                @delete="handleDelete"
                @error="handleError"
                :tip="$t('支持 jpg、png，尺寸不大于 1024px*1024px，不大于 256KB')"
              />
            </bk-form-item>
          </div>
          <bk-form-item :label="$t('用户数量')" required>
            <bk-radio-group
              v-model="formData.user_number_visible"
            >
              <bk-radio-button class="min-w-[100px]" :label="true">{{ $t('显示') }}</bk-radio-button>
              <bk-radio-button class="min-w-[100px]" :label="false">{{ $t('隐藏') }}</bk-radio-button>
            </bk-radio-group>
          </bk-form-item>

          <bk-form-item :label="$t('用户展示名')" required property="display_name_config">
            <UserDisplayNameConfig
              v-model:data="displayNameExpression"
              :preview-list="displayNameExpressionPreviewList"
              @change="handleExpressionChange"
              @preview="handlePreviewDisplayNameExpression" />
          </bk-form-item>
        </Row>
      </bk-form>
      <bk-button
        class="min-w-[88px] mr-[8px]"
        theme="primary"
        @click="saveEdit"
        :disabled="isDisabled"
      >
        {{ $t('保存') }}
      </bk-button>
      <bk-button
        class="min-w-[88px] mr-[8px]"
        @click="cancelEdit"
      >
        {{ $t('取消') }}
      </bk-button>
    </div>
    <div v-else>
      <Row title="">
        <div class="flex items-top justify-between">
          <div>
            <LabelContent :label="$t('租户名称')">{{ formData.name }}</LabelContent>
            <LabelContent :label="$t('租户ID')">{{ formData.id }}</LabelContent>
            <LabelContent :label="$t('用户数量')">{{ formData.user_number_visible ? $t('显示') : $t('隐藏') }}</LabelContent>
            <LabelContent :label="$t('用户展示名')">{{ displayNameExpressionView }}</LabelContent>
          </div>
          <LabelContent class="tenant-logo" :label="$t('租户logo')">
            <img v-if="formData.logo" class="user-logo" :src="formData.logo" alt="">
            <i v-else class="user-icon icon-yonghu" />
          </LabelContent>
          <bk-button
            class="min-w-[64px]"
            outline
            theme="primary"
            @click="isEdit = true"
          >
            {{ $t('编辑') }}
          </bk-button>
        </div>
      </Row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { computed, onMounted, ref, watch } from 'vue';

import Row from '@/components/layouts/ItemRow.vue';
import LabelContent from '@/components/layouts/LabelContent.vue';
import UserDisplayNameConfig from '@/components/user-display-name-config/userDisplayNameConfig.vue';
import { useValidate } from '@/hooks';
import { getDisplayNameExpression, getDisplayNameExpressionPreview, getTenantInfo, putDisplayNameExpression, PutTenantInfo } from '@/http';
import { t } from '@/language/index';
import { useFieldData, useMainViewStore } from '@/store';
import { getBase64 } from '@/utils';

const validate = useValidate();
const fieldData = useFieldData();
const store = useMainViewStore();
store.customBreadcrumbs = false;
const formRef = ref();

const formData = ref({
  id: '',
  name: '',
  logo: '',
  user_number_visible: true,
});
/** 可配置的用户展示名 */
const displayNameExpression = ref([]);

const displayNameExpressionView = computed(() => {
  let str = '';
  for (const item of displayNameExpression.value) {
    if (item.type === 'field') {
      str += fieldData.data.find(field => field.name === item.value).display_name;
    } else {
      str += item.value;
    }
  }
  return str;
})

/** 预览用户展示名list */
const displayNameExpressionPreviewList = ref<{ display_name: string }[]>([]);

const rules = {
  name: [validate.required, validate.name],
  id: [validate.required],
  display_name_config: [
    {
      message: t('表达式至少存在一个字段'),
      required: true,
      validator: () => displayNameExpression.value.length !== 0,
    },
    {
      message: t('表达式至少存在一个字段'),
      validator: () => {
        const selectedFieldValue = displayNameExpression.value.filter(item => item.type === 'field');
        if (selectedFieldValue.length >= 1) return true;
        return false;
      },
    },
    {
      message: t('表达式字段不能超过3个'),
      validator: () => {
        const selectedFieldValue = displayNameExpression.value.filter(item => item.type === 'field');
        if (selectedFieldValue.length <= 3) return true;
        return false;
      },
    },
    {
      message: t('表达式中非宇段部分的字符数不能超过16个'),
      validator: () => {
        const selectedSymbolValue = displayNameExpression.value.filter(item => item.type === 'symbol');
        if (selectedSymbolValue.length <= 16) return true;
        return false;
      },
    },
  ],
};

const isEdit = ref(false);

watch(() => isEdit.value, (val) => {
  window.changeInput = val;
}, {
  deep: true,
});

onMounted(() => {
  initTenantInfo();
  fieldData.initFieldsData();
});

/** 获取display_name_expression */
const initDisplayNameExpression = async () => {
  const res = await getDisplayNameExpression();
  displayNameExpression.value = processTemplateString(res.data.expression);
};

/** 初始化display_name_expression 转换成可配置的组件数据 */
const processTemplateString = (template: string) => {
  // 1. 创建存储字段名的数组
  const fields: string[] = [];

  // 2. 定义正则表达式匹配 {xxx} 模式
  const regex = /\{([^{}]+)\}/g;

  // 3. 使用唯一标识符替换 {xxx} 并收集字段名
  const placeholder = '\uFFFD'; // 使用 Unicode 替换字符作为标识符
  let currentIndex = 0;

  const replaced = template.replace(regex, (_, field) => {
    fields.push(field);
    return placeholder; // 用唯一标识符替换
  });

  // 4. 分割处理后的字符串
  const parts = replaced.split('');

  // 5. 将字段名回填到标识符位置
  const result = parts.map((char) => {
    if (char === placeholder && currentIndex < fields.length) {
      // 如果是占位符且还有字段，返回字段对象
      return { type: 'field' as const, value: fields[currentIndex++] };
    }
    // 否则返回文本对象
    return { type: 'symbol' as const, value: char };
  });
  return result;
};

/** 将用户展示名组件数据转换成params参数 */
const handleTransformDisplayNameExpression = (): string => {
  let str = '';
  for (const item of displayNameExpression.value) {
    if (item.type === 'field') {
      str += `{${item.value}}`;
    } else {
      str += item.value;
    }
  }
  return str;
};

/** 获取用户展示名预览数据 */
const initDisplayNameExpressionPreview = async () => {
  try {
    fieldData.isPreviewLoading = true;
    const res = await getDisplayNameExpressionPreview({
      expression: handleTransformDisplayNameExpression(),
    });
    displayNameExpressionPreviewList.value = res?.data || [];
  } catch (err) {
    console.error(err);
  } finally {
    fieldData.isPreviewLoading = false;
  }
};

const handlePreviewDisplayNameExpression = () => {
  initDisplayNameExpressionPreview();
};

const handleExpressionChange = () => {
  isDisabled.value = false;
  formRef.value.clearValidate();
};

let originalData = {};
const isDisabled = ref(true);
const initTenantInfo = async () => {
  const res = await getTenantInfo();
  originalData = JSON.stringify(res.data);
  formData.value = res.data;
  await initDisplayNameExpression();
};

watch(formData, () => {
  isDisabled.value = originalData  === JSON.stringify(formData.value);
}, { deep: true });

// 上传头像
const files = computed(() => {
  const img = [];
  if (formData.value.logo !== '') {
    img.push({
      url: formData.value.logo,
    });
    return img;
  }
  return [];
});

const handleRes = (response: any) => {
  if (response.id) {
    return true;
  }
  return false;
};

const customRequest = (event) => {
  getBase64(event.file).then((res) => {
    formData.value.logo = res;
  })
    .catch((e) => {
      console.warn(e);
    });
};

const handleDelete = () => {
  formData.value.logo = '';
};

const handleError = (file) => {
  if (file.size > (2 * 1024 * 1024)) {
    Message({ theme: 'error', message: t('图片大小超出限制，请重新上传') });
  }
};

const saveEdit = async () => {
  try {
    const result = await formRef.value.validate().catch(() => false);
    if (!result) return;
    const { id, ...params } = formData.value;
    await Promise.all([
      PutTenantInfo(params),
      putDisplayNameExpression({ expression: handleTransformDisplayNameExpression() }),
    ]);
    isEdit.value = false;
    Message({ theme: 'success', message: t('保存成功，用户展示名配置将于10秒之后生效，其他设置立即生效') });
    initTenantInfo();
  } catch (err) {
    console.error(err);
  }
};

const cancelEdit = () => {
  isEdit.value = false;
  initTenantInfo();
};
</script>

<style lang="less" scoped>
.basics-setting-wrapper {
  padding: 24px;

  .tenant-logo {
    position: relative;
  }

  .user-logo {
    position: absolute;
    top: 10px;
    width: 72px;
    height: 72px;
    border: 1px dashed #C4C6CC;
    border-radius: 2px;
  }

  .icon-yonghu {
    position: absolute;
    top: 10px;
    padding: 16px;
    font-size: 40px;
    color: #DCDEE5;
    background: #FAFBFD;
    border: 1px dashed #C4C6CC;
    border-radius: 2px;
  }
}

:deep(.bk-upload__tip) {
  color: #999
}
</style>
