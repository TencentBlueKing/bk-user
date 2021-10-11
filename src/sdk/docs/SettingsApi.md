# bkuser_sdk.SettingsApi

All URIs are relative to *http://localhost:8000/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_settings_create**](SettingsApi.md#v2_settings_create) | **POST** /api/v2/settings/ | 
[**v2_settings_delete**](SettingsApi.md#v2_settings_delete) | **DELETE** /api/v2/settings/{lookup_value}/ | 
[**v2_settings_list**](SettingsApi.md#v2_settings_list) | **GET** /api/v2/settings/ | 
[**v2_settings_partial_update**](SettingsApi.md#v2_settings_partial_update) | **PATCH** /api/v2/settings/{lookup_value}/ | 
[**v2_settings_read**](SettingsApi.md#v2_settings_read) | **GET** /api/v2/settings/{lookup_value}/ | 
[**v2_settings_update**](SettingsApi.md#v2_settings_update) | **PUT** /api/v2/settings/{lookup_value}/ | 

# **v2_settings_create**
> Setting v2_settings_create(body)



配置项

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.SettingsApi()
body = bkuser_sdk.SettingCreate() # SettingCreate | 

try:
    api_response = api_instance.v2_settings_create(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SettingsApi->v2_settings_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SettingCreate**](SettingCreate.md)|  | 

### Return type

[**Setting**](Setting.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_settings_delete**
> v2_settings_delete(lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)



删除对象

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.SettingsApi()
lookup_value = 'lookup_value_example' # str | 
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_instance.v2_settings_delete(lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)
except ApiException as e:
    print("Exception when calling SettingsApi->v2_settings_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lookup_value** | **str**|  | 
 **fields** | **str**| 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id | [optional] 
 **lookup_field** | **str**| 指定查询字段，内容为 lookup_value 所属字段, 例如: username | [optional] 
 **include_disabled** | **bool**| 是否包含已软删除的数据 | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_settings_list**
> list[Setting] v2_settings_list(category_id, key=key, namespace=namespace, region=region, domain=domain)



配置项

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.SettingsApi()
category_id = 56 # int | 
key = 'key_example' # str |  (optional)
namespace = 'namespace_example' # str |  (optional)
region = 'region_example' # str |  (optional)
domain = 'domain_example' # str |  (optional)

try:
    api_response = api_instance.v2_settings_list(category_id, key=key, namespace=namespace, region=region, domain=domain)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SettingsApi->v2_settings_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **int**|  | 
 **key** | **str**|  | [optional] 
 **namespace** | **str**|  | [optional] 
 **region** | **str**|  | [optional] 
 **domain** | **str**|  | [optional] 

### Return type

[**list[Setting]**](Setting.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_settings_partial_update**
> Setting v2_settings_partial_update(body, lookup_value)



配置项

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.SettingsApi()
body = bkuser_sdk.SettingUpdate() # SettingUpdate | 
lookup_value = 'lookup_value_example' # str | 

try:
    api_response = api_instance.v2_settings_partial_update(body, lookup_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SettingsApi->v2_settings_partial_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SettingUpdate**](SettingUpdate.md)|  | 
 **lookup_value** | **str**|  | 

### Return type

[**Setting**](Setting.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_settings_read**
> Setting v2_settings_read(lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)



获取详细信息

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.SettingsApi()
lookup_value = 'lookup_value_example' # str | 
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_response = api_instance.v2_settings_read(lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SettingsApi->v2_settings_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lookup_value** | **str**|  | 
 **fields** | **str**| 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id | [optional] 
 **lookup_field** | **str**| 指定查询字段，内容为 lookup_value 所属字段, 例如: username | [optional] 
 **include_disabled** | **bool**| 是否包含已软删除的数据 | [optional] 

### Return type

[**Setting**](Setting.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_settings_update**
> Setting v2_settings_update(body, lookup_value)



配置项

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.SettingsApi()
body = bkuser_sdk.SettingUpdate() # SettingUpdate | 
lookup_value = 'lookup_value_example' # str | 

try:
    api_response = api_instance.v2_settings_update(body, lookup_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SettingsApi->v2_settings_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SettingUpdate**](SettingUpdate.md)|  | 
 **lookup_value** | **str**|  | 

### Return type

[**Setting**](Setting.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

