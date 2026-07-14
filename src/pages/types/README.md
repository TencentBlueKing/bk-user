# TypeScript 类型声明文件说明

本目录包含项目的 TypeScript 类型声明文件，按功能模块组织，便于维护和扩展。

## 文件结构

```
types/
├── global.d.ts      # 全局类型声明（Window 接口扩展等）
├── modules.d.ts     # 静态资源模块声明（CSS、图片等）
├── vendors.d.ts     # 第三方库类型声明（无 TS 类型的包）
├── shims-vue.d.ts   # Vue 相关类型声明
└── README.md        # 本说明文件
```

## 各文件用途

### global.d.ts
存放全局类型声明，如：
- Window 对象的扩展属性
- 全局变量声明
- 全局接口定义

### modules.d.ts
声明静态资源模块类型，解决 TypeScript 无法识别静态资源导入的问题：
- CSS/SCSS/LESS 文件
- 图片文件（PNG、JPG、SVG 等）
- 其他静态资源

### vendors.d.ts
声明第三方库的类型，主要用于：
- 没有提供 TypeScript 类型定义的 npm 包
- 需要自定义类型的第三方库
- 第三方库的 CSS 文件导入

### shims-vue.d.ts
Vue 框架相关的类型声明

## 添加新的类型声明

### 添加新的第三方库声明
在 `vendors.d.ts` 中添加：

```typescript
// 包名 - 简短描述
declare module 'package-name' {
  const Component: any;
  export default Component;
}

// 如果有 CSS 文件
declare module 'package-name/dist/style.css';
```

### 添加新的静态资源类型
在 `modules.d.ts` 中添加：

```typescript
declare module '*.ext' {
  const value: string;
  export default value;
}
```

### 添加全局类型
在 `global.d.ts` 中添加：

```typescript
declare interface Window {
  NEW_PROPERTY: string;
}
```

## 最佳实践

1. **按功能分类**：不要把所有声明都放在一个文件中
2. **添加注释**：为每个声明添加简短的说明
3. **保持简洁**：只声明必要的类型，避免过度声明
4. **定期清理**：移除不再使用的类型声明

## 注意事项

- TypeScript 会自动加载 `types/` 目录下的所有 `.d.ts` 文件
- 修改类型声明文件后，可能需要重启 IDE 或 TypeScript 服务
- 对于复杂的第三方库，建议查找是否有 `@types/` 包可用
