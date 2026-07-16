import type { Directive } from 'vue';

// 定义指令参数类型
interface DirectiveOptions {
  type?: 'hide' | 'remove';
  // 可以扩展其他参数
}

const vIsMultipleTenant: Directive<HTMLElement, DirectiveOptions> = {
  mounted(el, binding) {
    const options: Required<DirectiveOptions> = {
      type: 'remove',
      ...binding.value, // 用户传入的参数会覆盖默认值
    };
    if (window.ENABLE_MULTI_TENANT_MODE === 'False') {
      if (options.type === 'remove') {
        el.remove();
      } else {
        el.style.display = 'none';
      }
    }
  },
};

export default vIsMultipleTenant;
