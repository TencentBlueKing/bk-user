<template>
  <div class="match-card">
    <div v-if="showHeader" class="match-card-header">
      <span class="match-card-title">{{ dataSourceName }}</span>
      <i class="user-icon icon-del match-card-close" @click="emit('remove', dataSourceId)" />
    </div>
    <div class="match-card-body">
      <slot name="label"></slot>
      <div class="item-flex-header">
        <bk-form-item :label="$t('数据源字段')" />
        <bk-form-item class="auth-source-fields" :label="$t('认证源字段')" />
      </div>
      <div class="item-flex-scroll">
        <div class="item-flex" v-for="(field, i) in fieldCompareRules" :key="i">
          <bk-form-item
            error-display-type="tooltips"
            :property="`data_source_match_rules.${ruleIndex}.field_compare_rules.${i}.target_field`"
            :rules="rulesData.target_field">
            <bk-select
              v-model="field.target_field"
              @change="emit('change')"
            >
              <bk-option
                class="option-select"
                v-for="option in fieldOptions"
                :key="option.name"
                :id="option.name"
                :name="option.name"
                :disabled="fieldCompareRules.some(c => c.target_field === option.name)">
                <span>{{option.name}}</span>
                <span>{{option.type}}</span>
              </bk-option>
            </bk-select>
          </bk-form-item>
          <bk-form-item
            error-display-type="tooltips"
            :property="`data_source_match_rules.${ruleIndex}.field_compare_rules.${i}.source_field`"
            :rules="rulesData.source_field">
            <bk-input v-model="field.source_field" @focus="emit('change')" />
          </bk-form-item>
          <i class="user-icon icon-plus-fill" @click="emit('add', i)" />
          <i
            :class="['user-icon icon-minus-fill', { 'forbid': fieldCompareRules.length === 1 }]"
            @click="fieldCompareRules.length > 1 && emit('delete', i)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useValidate } from '@/hooks';

interface IFieldCompareRule {
  target_field: string;
  source_field: string;
}

interface IProps {
  dataSourceId: number;
  dataSourceName: string;
  /** 当前卡片在父级 data_source_match_rules 中的下标，用于 bk-form 校验 property 路径，单卡片场景默认 0 */
  ruleIndex?: number;
  fieldCompareRules: IFieldCompareRule[];
  fieldOptions: { key: number; name: string; type: string }[];
  /** 是否显示卡片头部（标题+删除），仅认证源编辑侧栏需要 */
  showHeader?: boolean;
}

withDefaults(defineProps<IProps>(), {
  ruleIndex: 0,
  showHeader: false,
});
const emit = defineEmits<{
  remove: [id: number];
  /** 在 index 行后插入一行空规则，行增删由父级完成 */
  add: [index: number];
  /** 删除 index 行规则，行增删由父级完成；字段编辑经 v-model 直接写入规则对象 */
  delete: [index: number];
  change: [];
}>();

const validate = useValidate();

const rulesData = {
  target_field: [validate.required],
  source_field: [validate.required, validate.sourceField],
};
</script>

<style lang="less" scoped>
.match-card {
  margin-bottom: 16px;
  border-radius: 2px;
  min-width: 544px;

  .match-card-header {
    display: flex;
    height: 40px;
    padding: 0 16px;
    background: #F0F1F5;
    align-items: center;
    justify-content: space-between;

    .match-card-title {
      font-weight: 700;
      color: var(--title-color);
    }

    .match-card-close {
      font-size: 10px;
      color: #979BA5;
      cursor: pointer;

      &:hover {
        color: #63656E;
      }
    }
  }

  .match-card-body {
    padding: 12px;
    background: #F5F7FA;
  }

  .item-flex-scroll {
    max-height: 300px;
    padding-right: 4px;
    overflow-y: auto;
    // 主布局 user-scroll-x 的 scrollbar-color 会继承进来，非 auto 会禁用下方 webkit 自定义滚动条，须显式归位
    scrollbar-color: auto;
    scrollbar-width: auto;

    &::-webkit-scrollbar {
      width: 4px;
    }

    &::-webkit-scrollbar-thumb {
      border-radius: 2px;
      background: #dcdee5;
    }
  }
}

.item-flex-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) 16px 16px;
  column-gap: 8px;
  align-items: center;
  padding-right: 4px;

  :deep(.bk-form-item) {
    padding: 0;
    margin: 0;
    font-size: 14px;
  }

  // 列头标签字号设计稿定 12px；bkui 的 label 有独立字号，需直接覆盖
  :deep(.bk-form-label) {
    font-size: 12px;
  }
}

.item-flex {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) 16px 16px;
  column-gap: 8px;
  align-items: center;
  padding-bottom: 8px;

  :deep(.bk-form-item) {
    padding-bottom: 0;
    margin: 0;
    font-size: 14px;
  }

  .user-icon {
    font-size: 16px;
    color: #dcdee5;
    cursor: pointer;

    &:hover {
      color: #c4c6cc;
    }

    &.forbid {
      color: #EAEBF0;
      cursor: not-allowed;
    }
  }
}

.option-select {
  display: flex !important;
  justify-content: space-between;
}
</style>
