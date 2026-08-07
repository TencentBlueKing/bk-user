<template>
  <div :class="variant === 'default' ? 'pl-[40px] pb-[8px]' : ''">
    <bk-form-item :label="$t('用户名冲突规则')" :required="variant === 'default'">
      <!-- default 变体：使用 radio-button -->
      <template v-if="variant === 'default'">
        <bk-radio-group v-model="rule" :disabled="disabled">
          <bk-radio-button label="unchanged">{{ $t('不配置，发生冲突时手动处理') }}</bk-radio-button>
          <bk-radio-button label="add_affix">{{ $t('为新数据源统一添加前后缀') }}</bk-radio-button>
        </bk-radio-group>
      </template>

      <!-- dialog 变体：竖向 radio 列表 -->
      <template v-else>
        <bk-radio-group v-model="rule" :disabled="disabled" class="conflict-radio-list">
          <div
            :class="['conflict-radio-item', { 'conflict-radio-item-active': rule === 'unchanged' }]"
            @click="!disabled && (rule = 'unchanged')"
          >
            <bk-radio label="unchanged" :disabled="disabled">
              {{ $t('不配置，发生冲突时手动处理') }}
            </bk-radio>
          </div>
          <div
            :class="['conflict-radio-item', { 'conflict-radio-item-active': rule === 'add_affix' }]"
            @click="!disabled && (rule = 'add_affix')"
          >
            <bk-radio label="add_affix" :disabled="disabled">
              {{ $t('为新数据源统一添加前后缀') }}
            </bk-radio>
          </div>
        </bk-radio-group>
      </template>
    </bk-form-item>

    <template v-if="rule === 'add_affix'">
      <div class="relative">
        <bk-form-item
          :label="$t('用户名生成规则')"
          property="nameGeneration"
          required
          class="!mb-[90px]"
        >
          <div class="flex flex-col mt-[2px]">
            <bk-radio-group
              v-model="nameGeneration"
              class="leading-[22px] h-[22px]"
              :disabled="disabled"
              @change="handleOptionChange"
            >
              <bk-radio ref="prefixRadioRef" label="add_prefix">{{ $t('添加前缀') }}</bk-radio>
              <bk-radio ref="suffixRadioRef" label="add_suffix">{{ $t('添加后缀') }}</bk-radio>
            </bk-radio-group>
          </div>
        </bk-form-item>

        <!-- 输入区 popover：箭头指向当前选中的选项 -->
        <bk-popover
          ref="inputPopoverRef"
          trigger="manual"
          theme="light"
          placement="bottom"
          :is-show="inputPopoverShow"
          :target="currentOptionEl"
          ext-cls="username-rule-popover"
          :offset="inputPopoverOffset"
          :arrow="true"
        >
          <template #content>
            <div class="flex items-center bg-[#F5F7FA] p-[12px] min-w-[400px] w-[560px]">
              <span class="text-[14px] text-[#63656E] mr-[8px] whitespace-nowrap">
                {{ $t('新用户名 ( username )') }} =
              </span>

              <template v-if="nameGeneration === 'add_prefix'">
                <bk-input
                  v-model="prefix"
                  :placeholder="$t('请输入前缀')"
                  class="!w-[160px] mr-[8px]"
                  :disabled="disabled"
                >
                  <template #suffix>
                    <bk-select
                      v-model="prefixConnector"
                      class="connector-select connector-select-prefix"
                      :clearable="false"
                      :disabled="disabled"
                    >
                      <bk-option
                        v-for="item in connectorOptions"
                        :key="item"
                        :value="item"
                        :label="item"
                      />
                    </bk-select>
                  </template>
                </bk-input>

                <span class="text-[14px] text-[#494B50] whitespace-nowrap">
                  + {{ $t('用户名 ( username )') }}
                </span>
              </template>

              <template v-else-if="nameGeneration === 'add_suffix'">
                <span class="text-[14px] text-[#494B50] mr-[8px] whitespace-nowrap">
                  {{ $t('用户名 ( username )') }} +
                </span>
                <bk-input
                  v-model="suffix"
                  :placeholder="$t('请输入后缀')"
                  class="!w-[160px]"
                  :disabled="disabled"
                >
                  <template #prefix>
                    <bk-select
                      v-model="suffixConnector"
                      class="connector-select connector-select-suffix"
                      :clearable="false"
                      :disabled="disabled"
                    >
                      <bk-option
                        v-for="item in connectorOptions"
                        :key="item"
                        :value="item"
                        :label="item" />
                    </bk-select>
                  </template>
                </bk-input>
              </template>
            </div>
          </template>
        </bk-popover>

        <!-- 预览 popover：点击预览按钮弹出，显示示例文本 -->
        <bk-popover
          ref="previewPopoverRef"
          trigger="click"
          theme="light"
          placement="right">
          <div
            @click="handleClickPreview"
            class="cursor-pointer h-[24px] w-[52px] rounded-[2px] hover:bg-[#E1ECFF]
              flex justify-center items-center ml-[8px] absolute -top-[2px] left-[108px]">
            <Eye :width="16" :height="16" fill="#3A84FF" />
            <span class="select-none ml-[4px] text-[#3A84FF] text-[12px]">{{ $t('预览') }}</span>
          </div>
          <template #content>
            <span>{{ previewExample }}</span>
          </template>
        </bk-popover>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { Eye } from 'bkui-vue/lib/icon';
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';

import { UsernameGenerateConfig } from '@/http/types/dataSourceFiles';

const props = withDefaults(defineProps<{
  config: UsernameGenerateConfig;
  disabled?: boolean;
  variant?: 'default' | 'dialog';
}>(), {
  config: () => ({
    rule: 'unchanged' as const,
    prefix: '',
    suffix: '',
  }),
  disabled: false,
  variant: 'default',
});

const emit = defineEmits<{
  (e: 'preview'): void;
}>();

const connectorOptions = ['_', '-'];
const defaultConnector = '_';

// 从前缀末尾解析连接符，如 "xxx_" => { value: "xxx", connector: "_" }
const parsePrefixConnector = (raw: string) => {
  const last = raw.slice(-1);
  if (connectorOptions.includes(last)) {
    return { value: raw.slice(0, -1), connector: last };
  }
  return { value: raw, connector: defaultConnector };
};

// 从后缀开头解析连接符，如 "_xxx" => { connector: "_", value: "xxx" }
const parseSuffixConnector = (raw: string) => {
  const first = raw.slice(0, 1);
  if (connectorOptions.includes(first)) {
    return { value: raw.slice(1), connector: first };
  }
  return { value: raw, connector: defaultConnector };
};

// 初始化：从 prefix/suffix 中解析出纯值和连接符
const initPrefix = parsePrefixConnector(props.config.prefix);
const initSuffix = parseSuffixConnector(props.config.suffix);

// 内部状态
const rule = ref<UsernameGenerateConfig['rule']>(props.config.rule);
const nameGeneration = ref<'add_prefix' | 'add_suffix'>(props.config.suffix ? 'add_suffix' : 'add_prefix');
const prefix = ref(initPrefix.value);
const suffix = ref(initSuffix.value);
const prefixConnector = ref(initPrefix.connector);
const suffixConnector = ref(initSuffix.connector);

// 暴露获取最终数据的方法，连接符直接拼到前缀/后缀中
const getData = (): UsernameGenerateConfig => {
  if (rule.value === 'unchanged') {
    return { rule: 'unchanged', prefix: '', suffix: '' };
  }
  if (nameGeneration.value === 'add_prefix') {
    return { rule: 'add_affix', prefix: prefix.value ? `${prefix.value}${prefixConnector.value}` : '', suffix: '' };
  }
  return { rule: 'add_affix', prefix: '', suffix: suffix.value ? `${suffixConnector.value}${suffix.value}` : '' };
};

const previewPopoverRef = ref();
const inputPopoverRef = ref();
const prefixRadioRef = ref();
const suffixRadioRef = ref();
// 输入区 popover 显隐，选中 radio 后展开，不再因重复点击同一项而关闭
const inputPopoverShow = ref(false);

// 当前选中的选项元素，作为输入区 popover 锚点（箭头自动指向选中项）
const currentOptionEl = computed(() => (
  nameGeneration.value === 'add_prefix'
    ? prefixRadioRef.value?.$el
    : suffixRadioRef.value?.$el
));

/** 输入区 popover 的垂直间距 */
const INPUT_POPOVER_MAIN_AXIS = 10;
/** 输入区 popover 面板宽度 fallback（首次测量前的兜底，对应设计稿 min-w-[400px] + 内容） */
const PANEL_WIDTH_FALLBACK = 540;

// 实时测量的 popover 面板渲染宽度（因 renderDirective="if" 未显示时 DOM 不存在，需延迟/监听采集）
const popoverPanelWidth = ref(0);
const measurePanel = () => {
  const el = document.querySelector('.username-rule-popover') as HTMLElement | null;
  if (el) {
    const w = Math.round(el.getBoundingClientRect().width);
    if (w > 0) popoverPanelWidth.value = w;
  }
};

// 设计稿参照位置：当前 radio 所在 form-item 的 label 左缘
// （面板左缘应对齐到此位置，通过 closest 查找避免硬编码坐标）
const alignTargetLeft = computed(() => {
  const prefixEl = prefixRadioRef.value?.$el as HTMLElement | undefined;
  if (!prefixEl) return 0;
  const item = prefixEl.closest('.bk-form-item');
  const label = item?.querySelector('.bk-form-label') as HTMLElement | null;
  return label ? Math.round(label.getBoundingClientRect().left) : 0;
});

// 动态计算 popover 偏移：
// floating-ui 中 crossAxis 是相对锚点中心的水平位移（面板默认居中于锚点），
// 目标：面板左缘 = 参照元素（form-item label）左缘
// → crossAxis = targetLeft − anchorCenter + panelWidth / 2
// 选中后缀时再减 (suffixCenter − prefixCenter) 抵消锚点右移，使面板水平保持静止
const inputPopoverOffset = computed(() => {
  const prefixEl = prefixRadioRef.value?.$el as HTMLElement | undefined;
  const suffixEl = suffixRadioRef.value?.$el as HTMLElement | undefined;
  const targetLeft = alignTargetLeft.value;
  const halfPanel = (popoverPanelWidth.value || PANEL_WIDTH_FALLBACK) / 2;
  let crossAxis = 0;
  if (prefixEl) {
    const pR = prefixEl.getBoundingClientRect();
    crossAxis = targetLeft - (pR.left + pR.width / 2) + halfPanel;
  }
  if (nameGeneration.value === 'add_suffix' && prefixEl && suffixEl) {
    const sR = suffixEl.getBoundingClientRect();
    const pR = prefixEl.getBoundingClientRect();
    crossAxis -= (sR.left + sR.width / 2) - (pR.left + pR.width / 2);
  }
  return { mainAxis: INPUT_POPOVER_MAIN_AXIS, crossAxis };
});

// 切换选项：保持 popover 展开，并重新定位到新锚点
// 注意：updatePopover 第二参需传当前 props，否则 offset/placement/arrow 等配置会被重置
const handleOptionChange = () => {
  inputPopoverShow.value = true;
  nextTick(() => {
    inputPopoverRef.value?.updatePopover?.(currentOptionEl.value, inputPopoverRef.value.$props);
  });
};

// 预览示例
const previewExample = computed(() => {
  const exampleUsername = 'zhangsan';
  if (nameGeneration.value === 'add_prefix') {
    return `${prefix.value}${prefixConnector.value}${exampleUsername}`;
  }
  return `${exampleUsername}${suffixConnector.value}${suffix.value}`;
});

const handleClickPreview = () => {
  if (!previewPopoverRef.value?.localIsShow) {
    emit('preview');
  }
};

// watch props 更新内部数据
watch(() => props.config, (val) => {
  rule.value = val.rule;
  const p = parsePrefixConnector(val.prefix);
  const s = parseSuffixConnector(val.suffix);
  prefix.value = p.value;
  suffix.value = s.value;
  prefixConnector.value = p.connector;
  suffixConnector.value = s.connector;
  if (val.suffix) {
    nameGeneration.value = 'add_suffix';
  } else if (val.prefix) {
    nameGeneration.value = 'add_prefix';
  }
}, { deep: true });

// 默认值已有选中项时，初始化展开
onMounted(() => {
  if (nameGeneration.value) {
    inputPopoverShow.value = true;
  }
  // popover 默认 renderDirective="if"，未显示时内容 DOM 不存在，分阶段采集面板宽
  [0, 50, 200, 500].forEach(delay => setTimeout(measurePanel, delay));
  // 监听后续变化（切 radio / 内容变更 / 窗口尺寸改变都可能影响面板宽）
  const ro = new ResizeObserver(measurePanel);
  ro.observe(document.body);
  const mo = new MutationObserver(measurePanel);
  mo.observe(document.body, { childList: true, subtree: true });
  onUnmounted(() => {
    ro.disconnect();
    mo.disconnect();
  });
});

defineExpose({ getData, nameGeneration });
</script>

<style lang="less" scoped>
.preview-tag {
  background-color: #F0F1F5;
  height: 24px;
  line-height: 24px;
  padding: 0 8px;
  margin-top: 8px;
  cursor: pointer;
  user-select: none;
  border-radius: 2px;
  font-size: 12px;
  color: #63656E;
}

.connector-select {
  width: 45px;
  height: 32px;
  background-color: #FAFBFD;
  // 修正 bk-select 容器与 input 的 1px 错位，使上下边框与 input 合并成单线
  margin-top: -1px;

  :deep(.bk-select-trigger) {
    height: 32px;

    .bk-input {
      height: 32px;
      border: none;
    }
  }
}

// 连接符 select 作为 input 的 suffix/prefix 嵌在 input 内部，
// 顶/底/外侧边框由 input 外框提供，select 只保留与输入区相邻一侧的分割线（前缀留左、后缀留右）
.connector-select-prefix {
  :deep(.bk-select-trigger) {
    .bk-input {
      border-left: 1px solid #C4C6CC;
    }
  }
}

.connector-select-suffix {
  :deep(.bk-select-trigger) {
    .bk-input {
      border-right: 1px solid #C4C6CC;
    }
  }
}

.conflict-radio-list {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 0;

  :deep(.bk-radio-group) {
    flex-direction: column;
  }
}

.conflict-radio-item {
  display: flex;
  align-items: center;
  margin-top: 8px;
  padding: 0 12px;
  height: 32px;
  cursor: pointer;
  font-size: 14px;
  color: #4D4F56;
  transition: background-color 0.2s;
  background-color: #F5F7FA;

  &:first-child {
    margin-top: unset;
  }

  &-active {
    background-color: #E1ECFF;

    &:hover {
      background-color: #E1ECFF;
    }
  }
}
</style>

<style lang="less">
.username-rule-popover {
  .bk-pop2-arrow {
    background-color: #F5F7FA !important;
  }
  padding: 0 !important;
  box-shadow: none !important;
}
</style>
