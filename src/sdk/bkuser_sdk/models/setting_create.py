# coding: utf-8

"""
    蓝鲸用户管理 API

    蓝鲸用户管理后台服务 API  # noqa: E501

    OpenAPI spec version: v2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six


class SettingCreate(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'key': 'str',
        'value': 'object',
        'namespace': 'str',
        'region': 'str',
        'category_id': 'int'
    }

    attribute_map = {
        'key': 'key',
        'value': 'value',
        'namespace': 'namespace',
        'region': 'region',
        'category_id': 'category_id'
    }

    def __init__(self, key=None, value=None, namespace=None, region='default', category_id=None):  # noqa: E501
        """SettingCreate - a model defined in Swagger"""  # noqa: E501
        self._key = None
        self._value = None
        self._namespace = None
        self._region = None
        self._category_id = None
        self.discriminator = None
        self.key = key
        self.value = value
        self.namespace = namespace
        if region is not None:
            self.region = region
        self.category_id = category_id

    @property
    def key(self):
        """Gets the key of this SettingCreate.  # noqa: E501


        :return: The key of this SettingCreate.  # noqa: E501
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, key):
        """Sets the key of this SettingCreate.


        :param key: The key of this SettingCreate.  # noqa: E501
        :type: str
        """
        if key is None:
            raise ValueError("Invalid value for `key`, must not be `None`")  # noqa: E501

        self._key = key

    @property
    def value(self):
        """Gets the value of this SettingCreate.  # noqa: E501


        :return: The value of this SettingCreate.  # noqa: E501
        :rtype: object
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this SettingCreate.


        :param value: The value of this SettingCreate.  # noqa: E501
        :type: object
        """
        if value is None:
            raise ValueError("Invalid value for `value`, must not be `None`")  # noqa: E501

        self._value = value

    @property
    def namespace(self):
        """Gets the namespace of this SettingCreate.  # noqa: E501


        :return: The namespace of this SettingCreate.  # noqa: E501
        :rtype: str
        """
        return self._namespace

    @namespace.setter
    def namespace(self, namespace):
        """Sets the namespace of this SettingCreate.


        :param namespace: The namespace of this SettingCreate.  # noqa: E501
        :type: str
        """
        if namespace is None:
            raise ValueError("Invalid value for `namespace`, must not be `None`")  # noqa: E501

        self._namespace = namespace

    @property
    def region(self):
        """Gets the region of this SettingCreate.  # noqa: E501


        :return: The region of this SettingCreate.  # noqa: E501
        :rtype: str
        """
        return self._region

    @region.setter
    def region(self, region):
        """Sets the region of this SettingCreate.


        :param region: The region of this SettingCreate.  # noqa: E501
        :type: str
        """

        self._region = region

    @property
    def category_id(self):
        """Gets the category_id of this SettingCreate.  # noqa: E501


        :return: The category_id of this SettingCreate.  # noqa: E501
        :rtype: int
        """
        return self._category_id

    @category_id.setter
    def category_id(self, category_id):
        """Sets the category_id of this SettingCreate.


        :param category_id: The category_id of this SettingCreate.  # noqa: E501
        :type: int
        """
        if category_id is None:
            raise ValueError("Invalid value for `category_id`, must not be `None`")  # noqa: E501

        self._category_id = category_id

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(SettingCreate, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, SettingCreate):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
