<template>
  <Row :title="$t('生效范围')" class="!pb-[8px]">
    <bk-form-item
      :label="$t('数据源')"
      required
      property="data_source"
      :rules="formRules.data_source"
    >
      <div class="flex items-center">
        <bk-select
          class="flex-1"
          v-model="modelValue"
          multiple
          multiple-mode="tag"
          collapse-tags
          :clearable="false"
          :loading="selectLoading"
          :placeholder="$t('请选择生效的数据源')"
          @change="handleChange"
        >
          <bk-option
            v-for="item in availableOptions"
            :key="item.id"
            :value="item.id"
            :label="item.name"
            :name="item.name"
          />
        </bk-select>
        <bk-button
          text
          theme="primary"
          class="ml-[8px]"
          @click="handleRefresh"
        >
          <i class="user-icon icon-refresh" />
        </bk-button>
      </div>
      <div v-if="unenabledDataSources.length" class="mt-[8px]">
        <bk-alert
          v-for="item in unenabledDataSources"
          :key="item.id"
          theme="danger"
          class="mb-[8px] w-[calc(100%_-_20px)]"
        >
          <template #title>
            <div class="flex items-center justify-between w-full">
              <span>{{ item.name }} {{ $t('尚未启用密码规则，请前往数据源配置中设置') }}</span>
              <bk-button text theme="primary" @click="goToDataSourceSetting(item)">{{ $t('去设置') }}</bk-button>
            </div>
          </template>
        </bk-alert>
      </div>
    </bk-form-item>
  </Row>
</template>

<script setup lang="ts">
import { debounce } from 'bkui-vue/lib/shared';
import { computed, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import Row from '@/components/layouts/ItemRow.vue';
import { getCurrentTenant } from '@/http';
import type { CurrentTenantData } from '@/http/types/organizationFiles';

interface ScopeOption {
  id: number;
  name: string;
  plugin_id: string;
  /** 密码规则是否启用（由当前租户接口 data_sources 提供） */
  enable_password?: boolean;
}

const modelValue = defineModel<number[]>({ default: () => [] });

const props = withDefaults(defineProps<{
  localOnly?: boolean;
}>(), {
  localOnly: false,
});

const emit = defineEmits<{
  change: [value: number[]];
  unenabledChange: [hasUnenabled: boolean];
}>();

const router = useRouter();
const { t } = useI18n();

const formRules = {
  data_source: [{
    required: true,
    message: t('请选择生效的数据源'),
    validator: () => modelValue.value?.length > 0,
    trigger: 'change',
  }],
};

// 当前租户下的数据源：名称与密码规则启用状态均由 getCurrentTenant 的 data_sources 提供
const tenantDataSources = ref<CurrentTenantData['data_sources']>([]);
const selectLoading = ref(false);

const scopeOptions = computed<ScopeOption[]>(() => tenantDataSources.value.map(item => ({
  id: item.id,
  plugin_id: item.plugin_id,
  name: item.name,
  enable_password: item.enable_password,
})));
const availableOptions = computed(() => (
  props.localOnly ? scopeOptions.value.filter(item => item.plugin_id === 'local') : scopeOptions.value
));

// 未启用密码规则的选中项；仅本地数据源参与判断——密码规则是本地数据源级的配置
const unenabledDataSources = computed<ScopeOption[]>(() => {
  const selectedIds = new Set(modelValue.value);
  return availableOptions.value.filter(item => (
    props.localOnly
    && item.plugin_id === 'local'
    && selectedIds.has(item.id)
    && item.enable_password === false
  ));
});

// 存在未启用密码规则的选中项时通知父级（禁用提交），原因由 Alert 提示；immediate 覆盖编辑回填场景
watch(unenabledDataSources, (list) => {
  emit('unenabledChange', list.length > 0);
}, { immediate: true });

const fetchTenantDataSources = async () => {
  selectLoading.value = true;
  try {
    const res = await getCurrentTenant();
    tenantDataSources.value = res?.data?.data_sources ?? [];
  } catch (e) {
    console.error(e);
  } finally {
    selectLoading.value = false;
  }
};

const handleChange = (value: number[]) => {
  emit('change', value);
};

/** 前往对应本地数据源编辑页的密码设置步骤（query.step 直达，多个本地数据源按提示逐个处理） */
const goToDataSourceSetting = (item: ScopeOption) => {
  router.push({
    name: 'newDataSource',
    query: { type: 'local', id: item.id, step: 2 },
  });
};

onMounted(fetchTenantDataSources);

/** 手动刷新：防抖避免连点重复请求（首次挂载不走防抖，请求中另有 loading 态兜底） */
const handleRefresh = debounce(300, fetchTenantDataSources);
</script>
