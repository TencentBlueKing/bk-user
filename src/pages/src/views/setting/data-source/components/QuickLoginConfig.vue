<template>
  <!-- page：成功页，勾选区在表单外；dialog：弹窗，勾选区是表单里的「登录方式」项 -->
  <div class="quick-login-config" :class="{ 'is-page': layout === 'page' }">
    <template v-if="layout === 'page'">
      <QuickLoginChecks
        v-if="detailsLoaded"
        v-model="checked"
        :is-local="props.isLocal"
        :local-enable-password="localEnablePassword"
        :wecom-exists="wecomExists"
      />
      <bk-form
        v-if="wecomChecked"
        ref="formRef"
        class="login-match-form"
        form-type="vertical"
        :model="formData">
        <DataSourceMatchCard
          :data-source-id="props.dataSourceId"
          :data-source-name="dataSourceName"
          :field-compare-rules="formData.data_source_match_rules[0].field_compare_rules"
          :field-options="fieldOptions"
          @remove="removeWecom"
          @add="addItem"
          @delete="deleteItem"
          @change="handleChange"
        >
          <template #label>
            <bk-form-item class="!mb-[8px] match-label-item" :label="$t('登录认证匹配')" required />
          </template>
        </DataSourceMatchCard>
      </bk-form>
    </template>
    <template v-else>
      <bk-form ref="formRef" form-type="vertical" :model="formData">
        <bk-form-item :label="$t('登录方式')" required>
          <QuickLoginChecks
            v-if="detailsLoaded"
            v-model="checked"
            :is-local="props.isLocal"
            :local-enable-password="localEnablePassword"
            :wecom-exists="wecomExists"
          />
        </bk-form-item>
        <template v-if="wecomChecked">
          <!-- 登录认证匹配标签与卡片保持平级：bkui 的 required 星号是后代选择器，嵌套会渗透给卡片内的字段标签 -->
          <bk-form-item class="!mt-[16px] !mb-[12px]" :label="$t('登录认证匹配')" required />
          <div class="login-match-list">
            <DataSourceMatchCard
              :data-source-id="props.dataSourceId"
              :data-source-name="dataSourceName"
              :field-compare-rules="formData.data_source_match_rules[0].field_compare_rules"
              :field-options="fieldOptions"
              @remove="removeWecom"
              @add="addItem"
              @delete="deleteItem"
              @change="handleChange"
            />
          </div>
        </template>
      </bk-form>
    </template>
  </div>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { computed, onMounted, ref, watch } from 'vue';

import DataSourceMatchCard from '../../auth-config/DataSourceMatchCard.vue';

import QuickLoginChecks from './QuickLoginChecks.vue';

import { useCustomPlugin } from '@/hooks';
import { useIdpFields } from '@/hooks/useIdpFields';
import { getDataSourceDetails, getIdps, getIdpsDetails, getIdpsPlugins, postIdps, putIdps } from '@/http';
import type { LocalDataSourcePluginConfig } from '@/http/types/dataSourceFiles';
import { t } from '@/language/index';

interface IMatchRule {
  data_source_id: number;
  field_compare_rules: { source_field: string; target_field: string }[];
}

interface IIdpDetail {
  id: string;
  name: string;
  status: string;
  plugin_config: Record<string, unknown>;
  data_source_match_rules: IMatchRule[];
}

interface IProps {
  dataSourceId: number;
  /** 仅本地数据源可勾选账密登录 */
  isLocal: boolean;
  /** 弹窗由父级传入；成功页取数据源详情里的名称 */
  dataSourceName?: string;
  /** 成功页只加不减，不启用移除 */
  enableRemove?: boolean;
  /** page：挂载即加载；dialog：首次打开加载，之后每次打开仅重建勾选态 */
  layout?: 'page' | 'dialog';
  /** dialog 布局用于触发首次加载 */
  visible?: boolean;
}

const props = withDefaults(defineProps<IProps>(), {
  dataSourceName: '',
  enableRemove: false,
  layout: 'page',
  visible: false,
});
const emit = defineEmits<{
  loading: [];
  ready: [];
}>();

const formRef = ref();
const detailsLoaded = ref(false);
const loadedName = ref('');
const dataSourceName = computed(() => props.dataSourceName || loadedName.value);

// 接口数据不对外暴露
const idpPlugins = ref<{ id: string; name: string }[]>([]);
const wecomDetail = ref<IIdpDetail | null>(null);
const localIdpDetail = ref<IIdpDetail | null>(null);
/** 本地数据源是否开启密码功能，未开启时账密登录勾选禁用 */
const localEnablePassword = ref(false);

const { fieldOptions, loadFields } = useIdpFields();

const localChecked = ref(false);
const wecomChecked = ref(false);
/** 勾选态经 v-model 与 QuickLoginChecks 双向绑定，回写时记录为需要随保存落库的编辑意图；程序内重置仍直接改上面的 ref */
const checked = computed({
  get: () => ({ local: localChecked.value, wecom: wecomChecked.value }),
  set: (value) => {
    window.changeInput = true;
    localChecked.value = value.local;
    wecomChecked.value = value.wecom;
  },
});
/** 企微登录的匹配规则副本，勾选期间保留编辑内容 */
const ruleStore = ref<IMatchRule | null>(null);
const formData = ref({ data_source_match_rules: [] as IMatchRule[] });

/** 企微认证源是否已创建 */
const wecomExists = computed(() => !!wecomDetail.value);

/** 当前数据源是否已在企微认证源生效范围内 */
const wecomConfigured = computed(() => !!wecomDetail.value?.data_source_match_rules
  .some(rule => rule.data_source_id === props.dataSourceId));
/** 当前数据源是否已在账密登录生效范围内 */
const localConfigured = computed(() => !!localIdpDetail.value?.data_source_match_rules
  .some(rule => rule.data_source_id === props.dataSourceId));

/** 同步匹配表单规则数组：勾选时始终只有一条企微规则 */
const syncFormData = () => {
  if (!wecomChecked.value) {
    formData.value.data_source_match_rules = [];
    return;
  }
  if (!ruleStore.value) {
    const existing = wecomDetail.value?.data_source_match_rules
      ?.find(rule => rule.data_source_id === props.dataSourceId);
    // 已在生效范围的复制详情规则为副本，卡片编辑只落在副本上，取消/关闭天然不污染缓存
    ruleStore.value = existing
      ? JSON.parse(JSON.stringify(existing))
      : {
        data_source_id: props.dataSourceId,
        field_compare_rules: [{ target_field: '', source_field: '' }],
      };
  }
  formData.value.data_source_match_rules = [ruleStore.value];
};

const dataSourceList = ref([]);
const { handleChange, handleAddItem, handleDeleteItem } = useCustomPlugin(formData, dataSourceList);

// 卡片关闭等同于取消勾选企微登录
function removeWecom() {
  window.changeInput = true;
  wecomChecked.value = false;
}

function addItem(itemIndex: number) {
  handleAddItem(formData.value.data_source_match_rules[0].field_compare_rules, itemIndex);
}

function deleteItem(itemIndex: number) {
  handleDeleteItem(0, formData.value.data_source_match_rules[0].field_compare_rules, itemIndex);
}

/** 按当前生效范围重建勾选态：展示态与保存态同源 */
const resetCheckedState = () => {
  localChecked.value = localConfigured.value;
  ruleStore.value = null;
  wecomChecked.value = wecomConfigured.value;
  // 勾选值未变时 watch 不触发，这里显式重建，避免重开面板沿用上次编辑副本
  syncFormData();
};

/**
 * 拉取插件、认证源及其详情并填充内部缓存，完成后按生效范围重建勾选态。
 * needDataSourceDetail 为 false 时跳过数据源详情查询（非本地数据源不需要账密开关）
 */
const loadConfig = async ({ needDataSourceDetail = true } = {}) => {
  const dsDetailTask = needDataSourceDetail ? getDataSourceDetails(props.dataSourceId) : null;
  const [pluginsRes, idpsRes] = await Promise.all([getIdpsPlugins(), getIdps(''), loadFields()]);
  const dsDetailRes = dsDetailTask ? await dsDetailTask : null;
  idpPlugins.value = pluginsRes.data || [];
  const pluginConfig = dsDetailRes?.data?.plugin_config as LocalDataSourcePluginConfig | undefined;
  localEnablePassword.value = !!pluginConfig?.enable_password;

  // 只取账密与企微两个认证源的详情：保存时原样透传脱敏凭证（后端回填），并判断当前数据源是否已在其生效范围
  await Promise.all((idpsRes.data || []).map(async (item) => {
    if (item.plugin.id !== 'local' && item.plugin.id !== 'wecom') return;
    const detailRes = await getIdpsDetails(item.id);
    if (item.plugin.id === 'local') {
      localIdpDetail.value = detailRes.data;
    } else {
      wecomDetail.value = detailRes.data;
    }
  }));
  resetCheckedState();
  return { dataSourceName: dsDetailRes?.data?.name || '' };
};

const putIdpRules = async (detail: IIdpDetail, rules: IMatchRule[]) => {
  await putIdps({
    id: detail.id,
    name: detail.name,
    status: detail.status,
    plugin_config: detail.plugin_config,
    data_source_match_rules: rules,
  });
};

/** 回查 local 认证源详情并同步本地缓存 */
const syncLocalDetail = async () => {
  const listRes = await getIdps('');
  const localItem = (listRes.data || []).find(item => item.plugin.id === 'local');
  if (localItem) {
    const detailRes = await getIdpsDetails(localItem.id);
    localIdpDetail.value = detailRes.data;
  }
};

/** 追加当前数据源到企微认证源生效范围并同步本地详情；详情缺失返回 false */
const appendWecomBinding = async (fieldCompareRules: IMatchRule['field_compare_rules']) => {
  if (!wecomDetail.value) return false;
  const rule = { data_source_id: props.dataSourceId, field_compare_rules: fieldCompareRules };
  await putIdpRules(wecomDetail.value, [...wecomDetail.value.data_source_match_rules, rule]);
  wecomDetail.value.data_source_match_rules.push(rule);
  return true;
};

/** 以卡片副本覆盖当前数据源在企微认证源中的匹配规则；内容未变化时跳过请求 */
const writeBackWecomBinding = async (fieldCompareRules: IMatchRule['field_compare_rules']) => {
  if (!wecomDetail.value) return false;
  const target = wecomDetail.value.data_source_match_rules
    .find(rule => rule.data_source_id === props.dataSourceId);
  // target 缺失说明详情已与后端不一致（正常链路不可达），此时不写不报，避免空跑误报保存成功
  if (!target) return false;
  if (JSON.stringify(target.field_compare_rules) === JSON.stringify(fieldCompareRules)) {
    return false;
  }
  Object.assign(target, {
    data_source_id: props.dataSourceId,
    field_compare_rules: fieldCompareRules,
  });
  await putIdpRules(wecomDetail.value, wecomDetail.value.data_source_match_rules);
  return true;
};

/** 把当前数据源移出企微认证源生效范围并同步本地详情，重开弹窗与后续保存不再携带已删关联 */
const removeWecomBinding = async () => {
  if (!wecomDetail.value) return false;
  const rest = wecomDetail.value.data_source_match_rules
    .filter(rule => rule.data_source_id !== props.dataSourceId);
  await putIdpRules(wecomDetail.value, rest);
  wecomDetail.value.data_source_match_rules = rest;
  return true;
};

/** 把当前数据源加入账密登录生效范围；认证源不存在时先创建 */
const appendLocalBinding = async () => {
  const rule = {
    data_source_id: props.dataSourceId,
    // 本地账密的字段匹配规则后端约定写死 id -> id
    field_compare_rules: [{ source_field: 'id', target_field: 'id' }],
  };
  // 本地详情缺失时先回查兜底，避免把已存在的认证源误判为未配置而重复创建
  if (!localIdpDetail.value) {
    await syncLocalDetail();
  }
  if (localIdpDetail.value) {
    await putIdpRules(localIdpDetail.value, [...localIdpDetail.value.data_source_match_rules, rule]);
    localIdpDetail.value.data_source_match_rules.push(rule);
  } else {
    await postIdps({
      name: idpPlugins.value.find(plugin => plugin.id === 'local')?.name || 'local',
      status: 'enabled',
      plugin_id: 'local',
      // local 认证源后端忽略 plugin_config，按匹配规则自动生成
      plugin_config: {},
      data_source_match_rules: [rule],
    });
    // 新建后回查详情，保证本地缓存与后端一致
    await syncLocalDetail();
  }
  return true;
};

/** 把当前数据源移出账密登录生效范围并同步本地详情 */
const removeLocalBinding = async () => {
  if (!localIdpDetail.value) return false;
  const rest = localIdpDetail.value.data_source_match_rules
    .filter(rule => rule.data_source_id !== props.dataSourceId);
  await putIdpRules(localIdpDetail.value, rest);
  localIdpDetail.value.data_source_match_rules = rest;
  return true;
};

/**
 * 计算勾选态与生效范围的差异并落库，返回是否有实际保存。
 * 快照在进入时取：追加/写回/移除互斥，每个认证源只发一个最终请求
 */
const commitChanges = async (validate?: () => unknown) => {
  const wecomConfiguredBefore = wecomConfigured.value;
  const localConfiguredBefore = localConfigured.value;

  // 详情加载失败时不在保存范围，避免访问缺失详情抛错
  if (wecomChecked.value && wecomDetail.value && ruleStore.value && validate) {
    await validate();
  }
  let savedAny = false;
  if (wecomChecked.value && wecomDetail.value && ruleStore.value) {
    const { field_compare_rules: fieldCompareRules } = ruleStore.value;
    savedAny = wecomConfiguredBefore
      ? await writeBackWecomBinding(fieldCompareRules)
      : await appendWecomBinding(fieldCompareRules);
  }
  // 移除：此前已配置但被取消勾选；成功页只加不减，enableRemove=false 时整体跳过
  if (props.enableRemove) {
    if (wecomConfiguredBefore && !wecomChecked.value) {
      savedAny = (await removeWecomBinding()) || savedAny;
    }
    if (!localChecked.value && localConfiguredBefore) {
      savedAny = (await removeLocalBinding()) || savedAny;
    }
  }
  // 账密：勾选且此前未配置 → 加入生效范围
  if (props.isLocal && localChecked.value && !localConfiguredBefore) {
    savedAny = (await appendLocalBinding()) || savedAny;
  }
  return savedAny;
};

/** 保存勾选态与生效范围的差异并结束编辑态，有实际保存时提示成功 */
const save = async () => {
  const savedAny = await commitChanges(() => formRef.value?.validate());
  window.changeInput = false;
  if (savedAny) {
    Message({ theme: 'success', message: t('保存成功') });
  }
  return savedAny;
};

const runLoad = async () => {
  emit('loading');
  try {
    const res = await loadConfig({
      // 成功页需要数据源名称；弹窗场景非本地数据源不需要账密开关
      needDataSourceDetail: props.layout === 'page' || props.isLocal,
    });
    loadedName.value = res.dataSourceName;
    detailsLoaded.value = true;
  } catch (error) {
    console.error(error);
  } finally {
    emit('ready');
  }
};

watch(wecomChecked, syncFormData, { immediate: true });

// 弹窗内容随 isShow 渲染，visible 可能在挂载时已为 true，故用 immediate 兜住两种渲染时序
watch(() => props.visible, (val) => {
  if (props.layout !== 'dialog' || !val) return;
  if (detailsLoaded.value) {
    resetCheckedState();
    return;
  }
  runLoad();
}, { immediate: true });

onMounted(() => {
  if (props.layout === 'page') {
    runLoad();
  }
});

defineExpose({ save });
</script>

<style lang="less" scoped>
.quick-login-config {
  text-align: left;

  &.is-page {
    .login-match-form {
      margin-top: 16px;
    }

    .login-options {
      justify-content: center;
    }
  }

  .match-label-item {
    :deep(.bk-form-label) {
      color: #4D4F56;
      font-size: 12px;
    }
  }

  .login-match-list {
    display: flex;
    flex-direction: column;
  }
}
</style>
