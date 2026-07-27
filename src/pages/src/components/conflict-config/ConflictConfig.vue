<template>
  <div :class="variant === 'default' ? 'pl-[40px] pb-[8px]' : ''">
    <bk-form-item :label="$t('用户名冲突规则')" :required="variant === 'default'">
      <!-- default 变体：使用 radio-button -->
      <template v-if="variant === 'default'">
        <bk-radio-group v-model="rule" :disabled="disabled">
          <bk-radio-button label="unchange">{{ $t('不配置，发生冲突时手动处理') }}</bk-radio-button>
          <bk-radio-button label="add_affix">{{ $t('为新数据源统一添加前后缀') }}</bk-radio-button>
        </bk-radio-group>
      </template>

      <!-- dialog 变体：竖向 radio 列表 -->
      <template v-else>
        <bk-radio-group v-model="rule" :disabled="disabled" class="conflict-radio-list">
          <div
            :class="['conflict-radio-item', { 'conflict-radio-item-active': rule === 'unchange' }]"
            @click="!disabled && (rule = 'unchange')"
          >
            <bk-radio label="unchange" :disabled="disabled">
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
        >
          <div class="flex flex-col mt-[2px]">
            <bk-radio-group
              v-model="nameGeneration"
              class="leading-[22px] h-[22px]"
              :disabled="disabled"
            >
              <bk-radio label="add_prefix">{{ $t('添加前缀') }}</bk-radio>
              <bk-radio label="add_suffix">{{ $t('添加后缀') }}</bk-radio>
            </bk-radio-group>

            <div class="mt-[2px] flex items-center bg-[#F5F7FA] p-[12px]">
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
          </div>
        </bk-form-item>
        <bk-popover
          ref="popoverRef"
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
import { computed, ref, watch } from 'vue';

import { UsernameGenerateConfig } from '@/http/types/dataSourceFiles';

const props = withDefaults(defineProps<{
  config: UsernameGenerateConfig;
  disabled?: boolean;
  variant?: 'default' | 'dialog';
}>(), {
  config: () => ({
    rule: 'unchange' as const,
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

// 暴露获取最终数据的方法，连接符直接拼到前缀/后缀中
const getData = (): UsernameGenerateConfig => {
  if (rule.value === 'unchange') {
    return { rule: 'unchange', prefix: '', suffix: '' };
  }
  if (nameGeneration.value === 'add_prefix') {
    return { rule: 'add_affix', prefix: prefix.value ? `${prefix.value}${prefixConnector.value}` : '', suffix: '' };
  }
  return { rule: 'add_affix', prefix: '', suffix: suffix.value ? `${suffixConnector.value}${suffix.value}` : '' };
};

const popoverRef = ref();

// 预览示例
const previewExample = computed(() => {
  const exampleUsername = 'zhangsan';
  if (nameGeneration.value === 'add_prefix') {
    return `${prefix.value}${prefixConnector.value}${exampleUsername}`;
  }
  return `${exampleUsername}${suffixConnector.value}${suffix.value}`;
});

const handleClickPreview = () => {
  if (!popoverRef.value?.localIsShow) {
    emit('preview');
  }
};

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
  background-color: #FAFBFD;

  :deep(.bk-select-trigger) {
    height: 30px;
    margin-top: -1px;

    .bk-input {
      height: 30px;
      border: none;
    }
  }
}

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
