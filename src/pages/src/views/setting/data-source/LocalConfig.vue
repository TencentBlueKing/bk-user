<template>
  <bk-loading
    :loading="contentLoading || submitLoading"
    class="data-source-content user-scroll-y"
    :z-index="10"
  >
    <!-- 创建态：三步向导（步骤1落库创建 → 步骤2导入 → 步骤3密码规则），全程不改 URL -->
    <StepLayout v-if="!isEdit" :step="step" :steps="createSteps">
      <template #step-1>
        <BasicInfoPanel
          ref="basicInfoRef"
          v-model:name="formModel.name"
          :conflict-config="conflictConfig"
          :has-other-data-source="hasOtherDataSource"
          show-tips
        />
        <div class="data-source-footer-btn !border-t-0">
          <bk-button
            v-for="btn in createFooterButtons[1]"
            :key="btn.text"
            :theme="btn.theme"
            :loading="btn.loading"
            :disabled="btn.disabled"
            @click="btn.onClick"
          >
            {{ btn.text }}
          </bk-button>
        </div>
      </template>
      <template #step-2>
        <ImportDataPanel
          ref="importPanelRef"
          :data-source-id="createdDataSourceId"
          :data-source-name="formModel.name"
          show-created-tip
          @file-change="onFileChange"
        />
        <div class="data-source-footer-btn !border-t-0">
          <bk-button
            v-for="btn in createFooterButtons[2]"
            :key="btn.text"
            :theme="btn.theme"
            :loading="btn.loading"
            :disabled="btn.disabled"
            @click="btn.onClick"
          >
            {{ btn.text }}
          </bk-button>
        </div>
      </template>
      <template #step-3>
        <PasswordConfigPanel
          ref="passwordPanelRef"
          v-model:config="formModel.config"
          :is-password-rule-switch-locked="isPasswordRuleSwitchLocked"
        />
        <div class="data-source-footer-btn !border-t-0">
          <bk-button
            v-for="btn in createFooterButtons[3]"
            :key="btn.text"
            :theme="btn.theme"
            :loading="btn.loading"
            :disabled="btn.disabled"
            @click="btn.onClick"
          >
            {{ btn.text }}
          </bk-button>
        </div>
      </template>
    </StepLayout>
    <!-- 编辑态：三页签独立保存（基础信息 / 导入数据 / 密码规则）；导入任务进行中禁止切换，避免面板卸载后丢失任务结果 -->
    <bk-tab
      v-else
      v-model:active="activeTab"
      :before-change="() => !importLoading"
      render-directive="if"
      type="unborder-card"
      class="edit-data-source-tab"
      @change="handleTabChange"
    >
      <bk-tab-panel name="base" :label="$t('基础信息')">
        <BasicInfoPanel
          ref="basicInfoRef"
          v-model:name="formModel.name"
          :conflict-config="conflictConfig"
          conflict-disabled
        />
      </bk-tab-panel>
      <bk-tab-panel name="import" :label="$t('导入数据')">
        <ImportDataPanel
          ref="importPanelRef"
          :data-source-id="props.dataSourceId"
          @file-change="onFileChange"
        />
      </bk-tab-panel>
      <bk-tab-panel name="password" :label="$t('密码规则')">
        <PasswordConfigPanel
          ref="passwordPanelRef"
          v-model:config="formModel.config"
          :is-password-rule-switch-locked="isPasswordRuleSwitchLocked"
        />
      </bk-tab-panel>
    </bk-tab>

    <div v-if="isEdit" class="data-source-footer-btn !border-t-0">
      <bk-button
        v-for="btn in editFooterButtons"
        :key="btn.text"
        :theme="btn.theme"
        :loading="btn.loading"
        :disabled="btn.disabled"
        @click="btn.onClick"
      >
        {{ btn.text }}
      </bk-button>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import BasicInfoPanel from './components/basic-info-panel.vue';
import ImportDataPanel from './components/import-data-panel.vue';
import PasswordConfigPanel from './components/password-config-panel.vue';
import StepLayout from './StepLayout.vue';

import { isNil } from '@/common/util';
import { getIdps, getIdpsDetails } from '@/http';
import {
  getDataSourceDetails,
  getDefaultConfig,
  newDataSource,
  putDataSourceDetails,
} from '@/http/dataSourceFiles';
import { LocalDataSourcePluginConfig, UsernameGenerateConfig } from '@/http/types/dataSourceFiles';
import { t } from '@/language/index';
import { useDataSourceStore } from '@/store';

interface Props {
  dataSourceId: number | null;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  cancel: [];
  updateSuccess: [payload: { text: string; dataSourceId: number; name: string }];
}>();

/** 编辑模式（三页签）与创建模式（三步向导）共用容器 */
const isEdit = computed(() => !isNil(props.dataSourceId));

const basicInfoRef = ref();
const importPanelRef = ref();
const passwordPanelRef = ref();
const conflictConfig = ref<UsernameGenerateConfig>({
  rule: 'unchanged',
  prefix: '',
  suffix: '',
});

const formModel = ref<{ name: string; config: LocalDataSourcePluginConfig }>({
  name: '',
  // 初始化四段空骨架：首帧即渲染完整表单结构，接口数据到位后仅填值，避免分批出现
  config: {
    enable_password: false,
    password_rule: {},
    password_initial: { notification: { enabled_methods: [], templates: [] } },
    password_expire: { valid_time: 90, notification: { enabled_methods: [], templates: [] } },
    login_limit: { max_retries: 5 },
  } as LocalDataSourcePluginConfig,
});

const route = useRoute();
const router = useRouter();

// 创建向导当前步骤：步骤1「下一步」即落库创建，此后不可回退到步骤1（名称与冲突规则不可再改）；步骤3可「上一步」回步骤2补导入
const step = ref(1);
const createSteps = [
  { title: t('基础信息') },
  { title: t('导入数据') },
  { title: t('密码规则') },
];

// 编辑态页签：支持 section=password 深链（账密登录「去设置」直达密码规则页签）
const activeTab = ref<'base' | 'import' | 'password'>(route.query.section === 'password' ? 'password' : 'base');
// 页签间共享 formModel，切换本身不丢数据、不弹确认；按页签记录未保存修改，
// 保存只清当前页签的标记，页面离开提示由汇总后的 window.changeInput 驱动
const dirtyTabs = ref<Record<'base' | 'password', boolean>>({
  base: false,
  password: false,
});

let previousTab = activeTab.value;
const handleTabChange = (tab: 'base' | 'import' | 'password') => {
  // 同一时刻只有当前页签可编辑，切走时把全局脏标记归账到刚离开的页签；
  // 全局标记无法区分来源，宁可多记（多一次离开确认）也不漏记（静默丢失）。
  // 导入页签的脏状态由文件选择状态推导，不参与归账
  if (window.changeInput && previousTab !== 'import') dirtyTabs.value[previousTab] = true;
  previousTab = tab;
  router.replace({ query: { ...route.query, section: tab === 'password' ? 'password' : undefined } });
};

const dataSourceStore = useDataSourceStore();
const hasOtherDataSource = computed(() => dataSourceStore.dataSource.length > 0);

const submitLoading = ref(false);
// 导入动作由容器驱动（面板 expose importFile），loading 与失败态由返回值推导，用于按钮文案切换
const importLoading = ref(false);
const importFailed = ref(false);
// 面板上报的文件选中状态：未选文件时禁用「导入」
const hasImportFile = ref(false);
// 最近一次导入是否成功：成功后禁用导入按钮，文件变化时恢复
const imported = ref(false);

// 汇总页面脏标记：导入页签的脏状态可直接推导——选了文件但尚未导入成功（导入失败、换文件后重算）
const syncChangeInput = () => {
  window.changeInput = dirtyTabs.value.base
    || dirtyTabs.value.password
    || (hasImportFile.value && !imported.value);
};
// 创建态是否已成功导入过：控制步骤 2「跳过」按钮显示为「下一步」，文件变化不重置
const importDone = ref(false);

// 步骤 × 状态 → 按钮组映射：向导各步按钮的文案/loading/禁用集中于此，流程一目了然
const handlePrevStep = () => {
  // 回到第 2 步面板会重挂载，文件与失败原因已清空，容器的失败标记需同步重置，否则按钮文案与实际状态不符
  importFailed.value = false;
  step.value = 2;
};

interface FooterButton {
  text: string;
  theme?: 'primary';
  loading?: boolean;
  disabled?: boolean;
  onClick: () => void;
}

// 步骤 2 右侧按钮文案：失败提示可稍后补导；已成功导入则引导进入下一步；默认跳过导入
const skipButtonText = computed(() => {
  if (importFailed.value) return t('跳过，稍后导入');
  if (importDone.value) return t('下一步');
  return t('跳过');
});

const createFooterButtons = computed<Record<1 | 2 | 3, FooterButton[]>>(() => ({
  1: [
    { text: t('下一步'), theme: 'primary', loading: submitLoading.value, onClick: handleCreateDataSource },
    { text: t('取消'), disabled: submitLoading.value, onClick: handleCancel },
  ],
  2: [
    {
      text: importFailed.value ? t('重新导入') : t('导入'),
      theme: 'primary',
      loading: importLoading.value,
      disabled: !hasImportFile.value || imported.value,
      onClick: handleImport,
    },
    {
      text: skipButtonText.value,
      // 导入成功后主操作转移到「下一步」，加主色引导，避免用户误以为页面卡住
      theme: importDone.value ? 'primary' : undefined,
      disabled: importLoading.value,
      onClick: handleSkipImport,
    },
  ],
  3: [
    { text: t('上一步'), disabled: submitLoading.value, onClick: handlePrevStep },
    { text: t('提交'), theme: 'primary', loading: submitLoading.value, onClick: handleFinishCreate },
    { text: t('稍后设置'), disabled: submitLoading.value, onClick: handleCancel },
  ],
}));

// 编辑态页签 × 按钮组：三个页签统一带取消，与创建态去向一致
const editFooterButtons = computed<FooterButton[]>(() => {
  if (activeTab.value === 'import') {
    return [
      {
        text: t('导入'),
        theme: 'primary',
        loading: importLoading.value,
        disabled: !hasImportFile.value || imported.value,
        onClick: handleImport,
      },
      { text: t('取消'), disabled: importLoading.value, onClick: handleCancel },
    ];
  }
  return [
    { text: t('保存'), theme: 'primary', loading: submitLoading.value, onClick: handleEditSave },
    { text: t('取消'), disabled: submitLoading.value, onClick: handleCancel },
  ];
});

// 新增模式：步骤1创建成功后的数据源 id
const createdDataSourceId = ref<number | null>(null);

// 编辑模式取数（基础信息 + 密码相关配置）期间的整页 loading
const contentLoading = ref(false);

// 启用中的本地账密（认证源）生效范围是否已引用当前数据源：引用后不允许关闭密码规则（开关置灰），认证源关闭时不锁
const isPasswordRuleReferenced = ref(false);
// 开关锁定仅作用于「关闭」方向：被引用但规则未启用时允许打开，避免存量脏数据死锁
const isPasswordRuleSwitchLocked = computed(() => (
  isPasswordRuleReferenced.value && (formModel.value.config?.enable_password ?? false)
));

/**
 * 从登录设置「去设置」跳入时（from=login），保存/取消统一返回登录设置并自动展开本地账密详情侧栏
 * @returns 是否已执行跳转，调用方据此跳过各自的默认去向
 */
const backToLoginIfNeeded = () => {
  if (route.query.from !== 'login') return false;
  router.push({ name: 'login', query: { type: 'local' } });
  return true;
};

// ===== 创建向导：步骤流转与提交编排 =====

// 步骤1「下一步」：校验通过即创建数据源（名称与冲突规则落库，之后不可修改）
const handleCreateDataSource = async () => {
  const valid = await basicInfoRef.value?.validate();
  if (!valid) return;
  submitLoading.value = true;
  try {
    const result = await newDataSource({
      plugin_id: 'local',
      name: formModel.value.name,
      plugin_config: formModel.value.config,
      username_generate_config: basicInfoRef.value?.getData(),
    });
    const dataSourceId = result.data?.id;
    createdDataSourceId.value = dataSourceId;
    // 名称已随创建落库，清除步骤 1 输入产生的脏标记
    syncChangeInput();
    step.value = 2;
  } catch (e) {
    // 接口错误已由 http 拦截器统一提示，此处仅记录日志
    console.error(e);
  } finally {
    submitLoading.value = false;
  }
};

// 步骤2「导入 / 重新导入」与编辑导入页签「导入」共用：
// 成功后停留当前步骤展示结果 Alert（创建态由「跳过→下一步」按钮继续），失败停留原地可重试
const handleImport = async () => {
  importLoading.value = true;
  try {
    const success = await importPanelRef.value?.importFile();
    importFailed.value = !success;
    // 成功后禁用导入按钮，文件变化时恢复，防止对同一份文件重复导入
    imported.value = success;
    // 导入成功清除待导入脏标记，失败保持
    syncChangeInput();
    // 创建态据此把「跳过」切换为「下一步」；跳过进入第 3 步不置位，回上一步仍显示「跳过」
    importDone.value = success;
  } finally {
    importLoading.value = false;
  }
};

// 文件变化即恢复导入按钮：上一次的导入结果只对当时的文件有效
const onFileChange = (hasFile: boolean) => {
  hasImportFile.value = hasFile;
  imported.value = false;
  syncChangeInput();
};

// 步骤 2 右侧按钮（「跳过 / 下一步」共用）：不导入直接进入密码规则步骤，后续可在编辑页导入页签补导
const handleSkipImport = () => {
  step.value = 3;
};

// 步骤3「完成」：提交密码相关配置后进入成功页
const handleFinishCreate = async () => {
  const valid = await passwordPanelRef.value?.validate();
  if (!valid) return;
  submitLoading.value = true;
  try {
    const detailsRes = await getDataSourceDetails(createdDataSourceId.value);
    await putDataSourceDetails(createdDataSourceId.value, {
      name: formModel.value.name,
      plugin_config: formModel.value.config,
      field_mapping: detailsRes?.data?.field_mapping,
    });
    window.changeInput = false;
    if (backToLoginIfNeeded()) return;
    emit('updateSuccess', {
      text: t('新建成功'),
      dataSourceId: createdDataSourceId.value,
      name: formModel.value.name,
    });
  } catch (e) {
    console.error(e);
  } finally {
    submitLoading.value = false;
  }
};

// ===== 编辑态：三页签独立保存 =====

/** 保存成功后只清当前页签的脏标记（另一页签未保存的修改仍在表单中，由其自己的标记追踪）；from=login 仍跳回登录设置 */
const handleSaveSuccess = () => {
  // 仅 base/password 走表单保存，导入页签的脏标记由导入结果推导
  if (activeTab.value !== 'import') dirtyTabs.value[activeTab.value] = false;
  syncChangeInput();
  if (backToLoginIfNeeded()) return;
  Message({ theme: 'success', message: t('保存成功') });
};

// 基础信息页签：仅更新名称，plugin_config/field_mapping 取最新落库值，避免覆盖密码页签未保存的输入
// 密码规则页签：仅更新 plugin_config，name 取最新落库值，同理互不覆盖
const handleEditSave = async () => {
  const saveBase = activeTab.value === 'base';
  const valid = saveBase
    ? await basicInfoRef.value?.validate()
    : await passwordPanelRef.value?.validate();
  if (!valid) return;
  submitLoading.value = true;
  try {
    const detailsRes = await getDataSourceDetails(props.dataSourceId);
    await putDataSourceDetails(props.dataSourceId, {
      name: saveBase ? formModel.value.name : detailsRes?.data?.name,
      plugin_config: saveBase ? detailsRes?.data?.plugin_config : formModel.value.config,
      field_mapping: detailsRes?.data?.field_mapping,
    });
    handleSaveSuccess();
  } catch (e) {
    console.error(e);
  } finally {
    submitLoading.value = false;
  }
};

const handleCancel = () => {
  if (backToLoginIfNeeded()) return;
  emit('cancel');
};

/**
 * 判断当前数据源的密码规则是否被「启用中」的本地账密（认证源）的生效范围引用，用于锁定密码规则开关；
 * 认证源关闭时不锁（规则可编辑），非法中间态由认证源编辑页的未启用拦截兜底；
 * 请求失败按「未引用」降级，不影响表单初始化
 */
const checkPasswordRuleReferenced = async () => {
  try {
    const idpsRes = await getIdps('');
    const localIdp = idpsRes?.data?.find(item => item.plugin?.id === 'local');
    if (!localIdp) return;
    const idpDetailRes = await getIdpsDetails(localIdp.id);
    const scopeIds = (idpDetailRes?.data?.data_source_match_rules ?? []).map(item => item.data_source_id);
    isPasswordRuleReferenced.value = scopeIds.includes(props.dataSourceId);
  } catch (e) {
    console.error(e);
  }
};

/** 初始化表单：编辑模式回填数据源详情，新增模式以插件默认配置初始化 */
const initForm = async () => {
  contentLoading.value = true;
  try {
    if (isEdit.value) {
      const detailsRes = await getDataSourceDetails(props.dataSourceId);
      const details = detailsRes?.data;
      formModel.value.name = details?.name ?? '';
      // 冲突配置回填：编辑态仅回显（后端不支持更新），无数据时兜底为不配置
      conflictConfig.value = details?.username_generate_config
        || { rule: 'unchanged', prefix: '', suffix: '' };
      // 密码相关配置取数：已迁移至数据源详情的 plugin_config（存量数据由后端迁移），为空时保留骨架默认值
      if (details?.plugin_config && Object.keys(details.plugin_config).length > 0) {
        formModel.value.config = details.plugin_config as LocalDataSourcePluginConfig;
      }
      // 生效范围在本地账密（认证源）上，据此判断密码规则是否已被引用
      await checkPasswordRuleReferenced();
    } else {
      // 新增模式：以插件默认配置初始化表单，用户修改后原样提交
      const res = await getDefaultConfig('local');
      formModel.value.config = res?.data?.config as LocalDataSourcePluginConfig;
    }
  } catch (e) {
    console.error(e);
  } finally {
    contentLoading.value = false;
  }
};

onMounted(initForm);
</script>

<style lang="less" scoped>
.edit-data-source-tab {
  background: #fff;
  border-radius: 2px;

  :deep(.bk-tab-content) {
    padding: 10px 0 0 0;
  }
}
</style>
