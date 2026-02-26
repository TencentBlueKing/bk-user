<template>
  <div class="pl-[40px] pb-[8px]">
    <bk-form-item :label="$t('用户名冲突规则')" required>
      <bk-radio-group v-model="strategy" :disabled="disabled">
        <bk-radio-button label="manual">{{ $t('不配置，发生冲突时手动处理') }}</bk-radio-button>
        <bk-radio-button label="add_affix">{{ $t('为新数据的用户名添加前缀/后缀') }}</bk-radio-button>
      </bk-radio-group>
    </bk-form-item>

    <template v-if="strategy === 'add_affix'">
      <div class="relative">
        <bk-form-item :label="$t('用户名生成规则')" required>
          <div class="flex flex-col mt-[2px]">
            <bk-radio-group
              v-model="nameGeneration"
              class="leading-[22px] h-[22px]"
              :disabled="disabled"
            >
              <bk-radio label="add_prefix">{{ $t('添加前缀') }}</bk-radio>
              <bk-radio label="add_suffix">{{ $t('添加后缀') }}</bk-radio>
            </bk-radio-group>

            <div class="mt-[22px] flex items-center">
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

import { UsernameConfig } from '@/http/types/dataSourceFiles';

const props = withDefaults(defineProps<{
  config: UsernameConfig;
  disabled?: boolean;
}>(), {
  config: () => ({
    strategy: 'manual' as const,
    prefix: '',
    suffix: '',
  }),
  disabled: false,
});

const emit = defineEmits<{
  (e: 'preview'): void;
}>();

const connectorOptions = ['#', '_', '-'];
const defaultConnector = '#';

// 从前缀末尾解析连接符，如 "xxx#" => { value: "xxx", connector: "#" }
const parsePrefixConnector = (raw: string) => {
  const last = raw.slice(-1);
  if (connectorOptions.includes(last)) {
    return { value: raw.slice(0, -1), connector: last };
  }
  return { value: raw, connector: defaultConnector };
};

// 从后缀开头解析连接符，如 "#xxx" => { connector: "#", value: "xxx" }
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
const strategy = ref<UsernameConfig['strategy']>(props.config.strategy);
const nameGeneration = ref<'add_prefix' | 'add_suffix'>(props.config.suffix ? 'add_suffix' : 'add_prefix');
const prefix = ref(initPrefix.value);
const suffix = ref(initSuffix.value);
const prefixConnector = ref(initPrefix.connector);
const suffixConnector = ref(initSuffix.connector);

// watch props 更新内部数据
watch(() => props.config, (val) => {
  strategy.value = val.strategy;
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
const getData = (): UsernameConfig => {
  if (strategy.value === 'manual') {
    return { strategy: 'manual', prefix: '', suffix: '' };
  }
  if (nameGeneration.value === 'add_prefix') {
    return { strategy: 'add_affix', prefix: `${prefix.value}${prefixConnector.value}`, suffix: '' };
  }
  return { strategy: 'add_affix', prefix: '', suffix: `${suffixConnector.value}${suffix.value}` };
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

defineExpose({ getData });
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
</style>
