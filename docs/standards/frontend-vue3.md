# 前端开发规范

> 通用前端开发规范文档，适用于基于 Vue 3 + TypeScript + Vite 技术栈的中后台项目。

---

## 一、技术栈要求

| 技术 | 版本要求 | 用途 |
|------|---------|------|
| Vue | 3.5+ | 前端框架 |
| TypeScript | 5.x | 类型安全 |
| Vite | 5.x+ | 构建工具 |
| Pinia | 2.x | 状态管理 |
| vue-router | 4.x | 路由管理 |
| Axios | 1.x | HTTP 请求 |

---

## 二、项目结构

```
web/src/
├── api/                  # 网络请求封装
│   └── http.ts           # Axios 实例与拦截器
├── components/           # 公共组件
│   ├── PageHeader.vue
│   ├── StatusTag.vue
│   └── SearchInput.vue
├── composables/          # 组合式函数
│   ├── usePolling.ts
│   └── usePermission.ts
├── pages/                # 页面组件（按模块分目录）
│   └── {module}/
│       ├── index.vue
│       └── components/   # 页面私有组件
├── router/               # 路由配置
│   └── index.ts
├── services/             # API 桥接层
│   ├── generated/        # 自动生成代码（禁止手动修改）
│   └── {module}.ts       # 手写桥接层
├── stores/               # Pinia 状态管理
│   ├── user.ts
│   └── app.ts
├── types/                # 类型定义
│   └── {module}.ts
├── utils/                # 工具函数
├── App.vue
└── main.ts
```

### 目录职责说明

| 目录 | 职责 | 修改频率 |
|------|------|---------|
| `services/generated/` | Proto/OpenAPI 自动生成的 SDK，**禁止手动修改** | 低（仅重新生成） |
| `services/{module}.ts` | 桥接层：封装 generated 调用、类型转换、错误处理 | 中 |
| `types/{module}.ts` | 类型定义：重导 generated 类型 + 语义化别名 | 中 |
| `pages/{module}/` | 页面组件：组织 UI 与交互逻辑 | 高 |

---

## 三、编码规范

### 3.1 组件编写规范

```vue
<script setup lang="ts">
// 1. 导入区
import { ref, computed, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useUserStore } from '@/stores/user';
import type { ResourceItem } from '@/types/resource';

// 2. Props & Emits
interface Props {
  id: string;
  title?: string;
}
const props = withDefaults(defineProps<Props>(), {
  title: '默认标题',
});
const emit = defineEmits<{
  (e: 'update', value: string): void;
  (e: 'delete', id: string): void;
}>();

// 3. Store
const userStore = useUserStore();
const { userInfo } = storeToRefs(userStore);

// 4. 响应式状态
const loading = ref(false);
const list = ref<ResourceItem[]>([]);

// 5. 计算属性
const isEmpty = computed(() => list.value.length === 0);

// 6. 方法
const fetchData = async () => {
  loading.value = true;
  try {
    list.value = await resourceService.list(props.id);
  } finally {
    loading.value = false;
  }
};

// 7. 生命周期
onMounted(fetchData);
</script>

<template>
  <!-- 模板内容 -->
</template>

<style scoped>
/* 样式 */
</style>
```

**要点：**

- 统一使用 `<script setup lang="ts">` 语法
- Props 使用 TypeScript 接口定义 + `withDefaults`
- Emits 使用泛型函数签名定义
- 代码区块按"导入 → Props/Emits → Store → 状态 → 计算属性 → 方法 → 生命周期"排列

### 3.2 TypeScript 严格规范

| 规则 | 说明 |
|------|------|
| 启用 `strictTemplates` | `vue-tsc` 严格模板检查，捕获未定义组件和错误属性 |
| 禁止 `any` | 必须使用明确类型或 `unknown` |
| Props 类型化 | 所有 Props 使用 TypeScript 接口定义 |
| Ref 泛型 | `ref<Type>()` 必须指定泛型参数 |
| 路由参数类型化 | 使用 `typed-router` 或显式断言 |

### 3.3 命名约定

| 类型 | 规则 | 示例 |
|------|------|------|
| 组件文件 | PascalCase.vue | `UserList.vue` |
| 组合式函数 | use + PascalCase | `usePolling.ts` |
| Store 文件 | 小写名词 | `user.ts` |
| Store 导出 | use + PascalCase + Store | `useUserStore` |
| Service 文件 | 小写模块名 | `resource.ts` |
| 类型文件 | 小写模块名 | `resource.ts` |
| 工具函数 | camelCase | `formatDate.ts` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| CSS class | kebab-case | `.page-header` |

---

## 四、状态管理规范（Pinia）

### 4.1 推荐写法：Setup Store

```typescript
// src/stores/user.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useUserStore = defineStore('user', () => {
  // State
  const userInfo = ref<UserInfo | null>(null);
  const loading = ref(false);

  // Getter
  const username = computed(() => userInfo.value?.name ?? '');
  const isLoggedIn = computed(() => !!userInfo.value);

  // Action
  const fetchUserInfo = async () => {
    if (userInfo.value) return userInfo.value;
    loading.value = true;
    try {
      userInfo.value = await http.get('/user/info');
    } finally {
      loading.value = false;
    }
    return userInfo.value;
  };

  const logout = () => {
    userInfo.value = null;
  };

  return { userInfo, loading, username, isLoggedIn, fetchUserInfo, logout };
});
```

### 4.2 使用规范

| 规则 | 说明 |
|------|------|
| 使用 `storeToRefs` | 解构 state/getter 时保持响应性 |
| Action 直接调用 | `store.action()` 不需要 `storeToRefs` |
| 单例模式 | 不要重复 `new`，直接 `useXxxStore()` |
| 异步初始化 | 在 `App.vue` 或路由守卫中完成 |

```typescript
// ✅ 正确
const userStore = useUserStore();
const { userInfo, loading } = storeToRefs(userStore);
userStore.fetchUserInfo();

// ❌ 错误：解构丢失响应性
const { userInfo } = useUserStore(); // 不是响应式！
```

---

## 五、网络请求规范

### 5.1 统一 Axios 封装

```typescript
// src/api/http.ts
import axios from 'axios';

const http = axios.create({
  baseURL: '/api',
  timeout: 60000,
});

// 响应拦截器：自动剥壳
http.interceptors.response.use(
  (res) => {
    const { data } = res;
    // 兼容旧版协议（含 code 字段）
    if (data.code !== undefined) {
      if (data.code !== 0) {
        showError(data.message);
        return Promise.reject(new Error(data.message));
      }
      return data.data;
    }
    // 新版协议（直接返回 data）
    return data.data ?? data;
  },
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/login';
    }
    showError(error.message);
    return Promise.reject(error);
  },
);

export default http;
```

### 5.2 核心规则

| 规则 | 说明 |
|------|------|
| 统一入口 | 所有请求必须通过 `src/api/http.ts` 发起 |
| 自动剥壳 | 拦截器自动提取 `data` 字段，业务代码直接拿数据 |
| 401 自动跳转 | 未登录自动跳转登录页 |
| 统一错误提示 | 错误信息统一通过 Toast/Message 提示 |
| 禁止裸用 `axios` | 禁止在业务代码中直接 `import axios from 'axios'` |

---

## 六、三层代码架构

前端接入后端接口时，必须遵循**三层分离**：

```
┌────────────────────────────────────────────────┐
│  Pages 层（页面组件）                             │
│  - 组织 UI 和交互逻辑                            │
│  - 调用 Services 层获取数据                       │
│  - 不直接调用 generated 代码                      │
├────────────────────────────────────────────────┤
│  Services 层（桥接层）                            │
│  - services/{module}.ts                         │
│  - 封装 generated 调用                           │
│  - 类型转换（snake_case → camelCase）            │
│  - 错误处理、业务工具函数                         │
├────────────────────────────────────────────────┤
│  Generated 层（自动生成，禁止手动修改）              │
│  - services/generated/{module}/                 │
│  - 由 Proto/OpenAPI 自动生成                     │
│  - 接口定义的直接映射                             │
└────────────────────────────────────────────────┘
```

### 各层职责

| 层级 | 职责 | 修改规则 |
|------|------|---------|
| Generated 层 | Proto/OpenAPI 的 TypeScript 镜像 | **禁止手改**，仅通过重新生成更新 |
| Services 层 | 桥接 generated → 页面；类型适配、缓存、重试 | 可修改，注意向下兼容 |
| Pages 层 | UI 组件，引用 Services 和 Types | 自由修改 |

### 旧实现迁移规则

- 旧接口函数标记 `@deprecated`，不直接删除
- 新实现放在同一文件或新文件中
- 迁移完成后全局搜索确认无引用再清理

---

## 七、Vue 3 最佳实践

### 7.1 响应式规则

| 规则 | 说明 |
|------|------|
| `ref` vs `reactive` | 优先使用 `ref`，避免 `reactive` 丢失响应性 |
| `storeToRefs` | 解构 Store 时必须使用 |
| `watch` 深度监听 | 数组用 `{ deep: true }`，Vue 3.5+ 支持 `watch.length` |
| `computed` | 只读派生数据优先用 `computed` |

### 7.2 组件通信

| 场景 | 方案 |
|------|------|
| 父 → 子 | Props |
| 子 → 父 | Emits |
| 跨层级 | Provide/Inject 或 Pinia |
| 兄弟组件 | 共同父组件提升状态，或 Pinia |

### 7.3 性能优化

| 技术 | 适用场景 |
|------|---------|
| `v-memo` | 大列表中不频繁变化的项 |
| `shallowRef` | 大对象只需整体替换 |
| 虚拟滚动 | 列表 > 100 条时 |
| 路由懒加载 | 所有页面组件 |
| 组件异步加载 | 弹窗、抽屉等低频组件 |

---

## 八、UI 组件使用规范

### 8.1 基本原则

| 原则 | 说明 |
|------|------|
| 组件优先 | 优先使用 UI 库组件，禁止使用原生 `<table>`、`<button>` 等 |
| 布局组件化 | 页面骨架必须使用 UI 库提供的布局组件 |
| 样式统一 | 使用 UI 库提供的原子类或 Design Token |
| Icon 规范 | 从 UI 库包导入，禁止使用 CDN 图标 |

### 8.2 页面布局模式

| 页面类型 | 布局方案 |
|---------|---------|
| 列表页 | 搜索栏 + 操作区 + 表格 + 分页 |
| 详情页 | 面包屑 + 信息卡片 + Tab 面板 |
| 表单页 | 分步表单 / 单页表单 + 提交按钮 |
| 仪表盘 | 统计卡片 + 图表网格 |

### 8.3 常见错误

| 错误 | 正确做法 |
|------|---------|
| 手写 div 布局 | 使用 UI 库 Navigation/Layout 组件 |
| 内联样式过多 | 使用 CSS class 或 UI 库原子类 |
| 组件属性写错（如拼写错误） | 查阅组件库文档，开启 `strictTemplates` 检查 |
| 直接操作 DOM | 使用 Vue ref + 组件 API |

---

## 九、质量保证

### 9.1 提交前自验三件套

```bash
# 类型检查
npx vue-tsc --noEmit

# 单元测试
npx vitest run

# 构建验证
npm run build
```

**每次提交前必须全部通过。**

### 9.2 单元测试规范

| 规则 | 说明 |
|------|------|
| 工具函数必须测试 | `utils/`、`composables/` 下的函数 |
| Service 桥接层 | Mock HTTP 请求，验证类型转换正确 |
| 组件测试 | 关键交互路径（点击、输入、状态切换） |
| 覆盖率要求 | 工具函数 ≥ 80%，组件 ≥ 60% |

### 9.3 代码审查清单

- [ ] TypeScript 类型完整，无 `any`
- [ ] 网络请求通过统一封装发起
- [ ] 新状态通过 Pinia Store 管理
- [ ] 组件 Props/Emits 类型化
- [ ] 无直接操作 DOM
- [ ] 错误边界处理完善
- [ ] 路由懒加载
- [ ] 三件套全部通过

---

## 十、常见陷阱与避坑

| # | 陷阱 | 解决方案 |
|---|------|---------|
| 1 | Store 解构丢失响应性 | 使用 `storeToRefs()` |
| 2 | `watch` 首次不执行 | 添加 `{ immediate: true }` |
| 3 | 异步组件未处理加载态 | 使用 `<Suspense>` 或手动 loading |
| 4 | 路由参数变化页面不刷新 | `watch(route.params, ...)` 或设置 `:key` |
| 5 | v-model 在自定义组件不工作 | 使用 `defineModel()` (Vue 3.4+) |
| 6 | CSS scoped 穿透失败 | 使用 `:deep()` 选择器 |
| 7 | int64 类型 JSON 精度丢失 | 后端 JSON 中 int64 序列化为 string，前端做 coerce |
| 8 | 401 循环跳转 | 登录页排除拦截器 |
| 9 | 数据双层嵌套 | 检查拦截器是否多剥一层 `.data` |
| 10 | 列表不刷新 | 操作成功后手动调用加载 + 轮询兜底 |
