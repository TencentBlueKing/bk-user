import os
import yaml
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ==================== 字段处理器抽象基类 ====================
class BaseFieldHandler(ABC):
    """字段变更处理器基类

    负责监听和处理字段值的变更，生成审计日志所需的变更记录
    """

    def __init__(self, field_name: str, display_name: str):
        """
        Args:
            field_name: 字段名称
            display_name: 字段显示名称
        """
        self.field_name = field_name
        self.display_name = display_name

    def handle(
        self,
        old_profile: Optional["Profile"],
        new_profile: "Profile",
        is_create: bool
    ) -> Optional[dict]:
        """处理字段变更

        Args:
            old_profile: 旧的Profile对象
            new_profile: 新的Profile对象
            is_create: 是否为创建操作

        Returns:
            变更记录字典，如果无变更则返回None
        """
        old_value = self._get_value(old_profile) if old_profile else None
        new_value = self._get_value(new_profile)

        # 格式化值
        formatted_old = self._format_value(old_value)
        formatted_new = self._format_value(new_value)

        return self._create_change_record(formatted_old, formatted_new, is_create)

    @abstractmethod
    def _get_value(self, profile: "Profile") -> Any:
        """从Profile对象中获取字段值

        Args:
            profile: Profile对象

        Returns:
            字段值
        """
        pass

    def _format_value(self, value: Any) -> Any:
        """格式化字段值

        Args:
            value: 原始值

        Returns:
            格式化后的值
        """
        return value

    def _create_change_record(
        self,
        old_value: Any,
        new_value: Any,
        is_create: bool
    ) -> Optional[dict]:
        """创建变更记录

        Args:
            old_value: 旧值
            new_value: 新值
            is_create: 是否为创建操作

        Returns:
            变更记录字典
        """
        if is_create:
            # 创建操作：只记录新值
            return self._create_attribute_item(None, new_value)
        elif old_value != new_value:
            # 更新操作且值发生变更
            return self._create_attribute_item(old_value, new_value)
        else:
            # 更新操作但值未变更
            return self._create_attribute_item(None, None)

    def _create_attribute_item(self, before_value: Any, after_value: Any) -> dict:
        """创建属性变更项"""
        return {
            "name": self.display_name,
            "field": self.field_name,
            "before": before_value,
            "after": after_value
        }


# ==================== 基础字段处理器 ====================


class SimpleFieldHandler(BaseFieldHandler):
    """简单字段处理器

    处理普通的字符串、数字等简单类型字段
    """

    def _get_value(self, profile: "Profile") -> Any:
        return getattr(profile, self.field_name, None)

    def _format_value(self, value: Any) -> Optional[str]:
        """将值转换为字符串"""
        return str(value) if value is not None else None


class DateTimeFieldHandler(BaseFieldHandler):
    """日期时间字段处理器"""

    def _get_value(self, profile: "Profile") -> Any:
        return getattr(profile, self.field_name, None)

    def _format_value(self, value: Any) -> Optional[str]:
        """格式化日期时间值"""
        if value is None:
            return None
        if hasattr(value, 'strftime'):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return str(value)


class PasswordFieldHandler(BaseFieldHandler):
    """密码字段处理器

    对密码字段进行特殊处理，不显示明文密码
    """

    def _get_value(self, profile: "Profile") -> Any:
        return getattr(profile, self.field_name, None)

    def _create_change_record(
        self,
        old_value: Any,
        new_value: Any,
        is_create: bool
    ) -> Optional[dict]:
        """密码字段的特殊变更记录逻辑"""
        if is_create:
            return self._create_attribute_item(None, "已创建")
        elif old_value != new_value:
            return self._create_attribute_item("******", "已修改")
        else:
            return self._create_attribute_item(None, None)


# ==================== 列表字段处理器基类及实现 ====================


class BaseListFieldHandler(BaseFieldHandler):
    """列表字段处理器基类

    处理列表类型的字段，如部门列表、上级列表等
    """

    @abstractmethod
    def _get_list_attr_name(self) -> str:
        """获取列表属性名称

        Returns:
            列表属性名称，如 'departments_list', 'leader_list'
        """
        pass

    def _get_value(self, profile: "Profile") -> Any:
        """从Profile对象中获取列表值"""
        list_attr = self._get_list_attr_name()
        if not hasattr(profile, list_attr):
            return None
        return getattr(profile, list_attr, [])


class DepartmentsFieldHandler(BaseListFieldHandler):
    """部门字段处理器"""

    def _get_list_attr_name(self) -> str:
        return "departments_list"


class LeaderFieldHandler(BaseListFieldHandler):
    """上级字段处理器"""

    def _get_list_attr_name(self) -> str:
        return "leader_list"


# ==================== 自定义字段处理器 ====================


class ExtrasFieldHandler(BaseFieldHandler):
    """自定义字段(extras)处理器

    处理Profile中的extras字典字段，支持动态字段
    """

    def __init__(self, field_name: str, display_name: str, field_display_names: dict):
        """
        Args:
            field_name: 字段名称（固定为'extras'）
            display_name: 字段显示名称
            field_display_names: 字段显示名称映射字典
        """
        super().__init__(field_name, display_name)
        self.field_display_names = field_display_names

    def handle(
        self,
        old_profile: Optional["Profile"],
        new_profile: "Profile",
        is_create: bool
    ) -> list:
        """处理extras字段，返回多个变更记录

        Returns:
            变更记录列表
        """
        old_extras = old_profile.extras if old_profile and old_profile.extras else {}
        new_extras = new_profile.extras if new_profile and new_profile.extras else {}

        all_extra_keys = set(old_extras.keys()) | set(new_extras.keys())

        changes = []
        for key in all_extra_keys:
            field_name = f"extras.{key}"
            display_name = self.field_display_names.get(field_name, f"自定义字段-{key}")
            old_value = old_extras.get(key)
            new_value = new_extras.get(key)

            # 创建变更记录
            if is_create:
                change = self._create_attribute_item_with_name(field_name, display_name, None, new_value)
            elif old_value != new_value:
                change = self._create_attribute_item_with_name(field_name, display_name, old_value, new_value)
            else:
                change = self._create_attribute_item_with_name(field_name, display_name, None, None)

            changes.append(change)

        return changes

    def _get_value(self, profile: "Profile") -> Any:
        """ExtrasFieldHandler不使用此方法"""
        return getattr(profile, self.field_name, {})

    def _create_attribute_item_with_name(
        self,
        field_name: str,
        display_name: str,
        before_value: Any,
        after_value: Any
    ) -> dict:
        """创建带自定义名称的属性变更项"""
        return {
            "name": display_name,
            "field": field_name,
            "before": before_value,
            "after": after_value
        }


# ==================== 配置加载器 ====================


class FieldHandlerConfigLoader:
    """字段处理器配置加载器

    从YAML配置文件加载字段处理器映射关系
    """

    _config = None
    _config_file = os.path.join(
        os.path.dirname(__file__),
        'field_handlers_config.yaml'
    )

    @classmethod
    def load_config(cls) -> dict:
        """加载配置文件

        Returns:
            配置字典
        """
        if cls._config is None:
            try:
                with open(cls._config_file, 'r', encoding='utf-8') as f:
                    cls._config = yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Failed to load field handler config: {e}, using default config")
                cls._config = cls._get_default_config()

        return cls._config

    @classmethod
    def get_handler_type(cls, field_name: str) -> str:
        """获取字段对应的处理器类型

        Args:
            field_name: 字段名称

        Returns:
            处理器类型
        """
        config = cls.load_config()
        field_handlers = config.get('field_handlers', {})

        if field_name in field_handlers:
            return field_handlers[field_name].get('handler_type', config.get('default_handler', 'simple'))

        return config.get('default_handler', 'simple')

    @classmethod
    def _get_default_config(cls) -> dict:
        """获取默认配置（当配置文件加载失败时使用）

        Returns:
            默认配置字典
        """
        return {
            'field_handlers': {
                'password': {'handler_type': 'password'},
                'departments': {'handler_type': 'departments'},
                'leader': {'handler_type': 'leader'},
                'extras': {'handler_type': 'extras'},
                'password_update_time': {'handler_type': 'datetime'},
                'account_expiration_date': {'handler_type': 'datetime'},
            },
            'default_handler': 'simple'
        }


# ==================== 字段处理器工厂 ====================


def create_field_handler(
    field_name: str,
    display_name: str,
    field_display_names: dict
) -> BaseFieldHandler:
    """工厂方法：根据字段名称创建对应的处理器

    从配置文件读取字段类型映射，提高扩展性

    Args:
        field_name: 字段名称
        display_name: 字段显示名称
        field_display_names: 字段显示名称映射字典

    Returns:
        对应的字段处理器实例
    """
    # 从配置文件获取处理器类型
    handler_type = FieldHandlerConfigLoader.get_handler_type(field_name)

    # 根据处理器类型创建对应的实例
    handler_map = {
        'password': lambda: PasswordFieldHandler(field_name, display_name),
        'departments': lambda: DepartmentsFieldHandler(field_name, display_name),
        'leader': lambda: LeaderFieldHandler(field_name, display_name),
        'extras': lambda: ExtrasFieldHandler(field_name, display_name, field_display_names),
        'datetime': lambda: DateTimeFieldHandler(field_name, display_name),
        'simple': lambda: SimpleFieldHandler(field_name, display_name),
    }

    handler_factory = handler_map.get(handler_type)
    if handler_factory:
        return handler_factory()

    # 默认使用简单字段处理器
    logger.warning(f"Unknown handler type '{handler_type}' for field '{field_name}', using SimpleFieldHandler")
    return SimpleFieldHandler(field_name, display_name)
