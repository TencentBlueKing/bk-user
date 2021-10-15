# bkuser_sdk.ProfilesApi

All URIs are relative to *http://localhost:8000/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_profiles_create**](ProfilesApi.md#v2_profiles_create) | **POST** /api/v2/profiles/ | 
[**v2_profiles_delete**](ProfilesApi.md#v2_profiles_delete) | **DELETE** /api/v2/profiles/{lookup_value}/ | 
[**v2_profiles_generate_token**](ProfilesApi.md#v2_profiles_generate_token) | **POST** /api/v2/profiles/{lookup_value}/token/ | 
[**v2_profiles_get_departments**](ProfilesApi.md#v2_profiles_get_departments) | **GET** /api/v2/profiles/{lookup_value}/departments/ | 
[**v2_profiles_get_leaders**](ProfilesApi.md#v2_profiles_get_leaders) | **GET** /api/v2/profiles/{lookup_value}/leaders/ | 
[**v2_profiles_list**](ProfilesApi.md#v2_profiles_list) | **GET** /api/v2/profiles/ | 
[**v2_profiles_modify_password**](ProfilesApi.md#v2_profiles_modify_password) | **POST** /api/v2/profiles/{lookup_value}/modify_password/ | 
[**v2_profiles_partial_update**](ProfilesApi.md#v2_profiles_partial_update) | **PATCH** /api/v2/profiles/{lookup_value}/ | 
[**v2_profiles_read**](ProfilesApi.md#v2_profiles_read) | **GET** /api/v2/profiles/{lookup_value}/ | 
[**v2_profiles_restoration**](ProfilesApi.md#v2_profiles_restoration) | **POST** /api/v2/profiles/{lookup_value}/restoration/ | 
[**v2_profiles_update**](ProfilesApi.md#v2_profiles_update) | **PUT** /api/v2/profiles/{lookup_value}/ | 
[**v2_retrieve_by_token**](ProfilesApi.md#v2_retrieve_by_token) | **GET** /api/v2/token/{token}/ | 

# **v2_profiles_create**
> Profile v2_profiles_create(body)



创建用户

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.ProfilesApi()
body = bkuser_sdk.CreateProfile() # CreateProfile | 

try:
    api_response = api_instance.v2_profiles_create(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProfilesApi->v2_profiles_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CreateProfile**](CreateProfile.md)|  | 

### Return type

[**Profile**](Profile.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_profiles_delete**
> v2_profiles_delete(lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)



删除用户 目前采用软删除

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.ProfilesApi()
lookup_value = 'lookup_value_example' # str | 
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_instance.v2_profiles_delete(lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)
except ApiException as e:
    print("Exception when calling ProfilesApi->v2_profiles_delete: %s\n" % e)
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

# **v2_profiles_generate_token**
> ProfileToken v2_profiles_generate_token(body, lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)



生成用户 Token 生成代表用户的 Token

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.ProfilesApi()
body = NULL # object | 
lookup_value = 'lookup_value_example' # str | 
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_response = api_instance.v2_profiles_generate_token(body, lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProfilesApi->v2_profiles_generate_token: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | 
 **lookup_value** | **str**|  | 
 **fields** | **str**| 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id | [optional] 
 **lookup_field** | **str**| 指定查询字段，内容为 lookup_value 所属字段, 例如: username | [optional] 
 **include_disabled** | **bool**| 是否包含已软删除的数据 | [optional] 

### Return type

[**ProfileToken**](ProfileToken.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_profiles_get_departments**
> list[SimpleDepartment] v2_profiles_get_departments(lookup_value, ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled, with_family=with_family, with_ancestors=with_ancestors)



获取用户所属部门信息

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.ProfilesApi()
lookup_value = 'lookup_value_example' # str | 
ordering = 'ordering_example' # str | Which field to use when ordering the results. (optional)
page = 56 # int | A page number within the paginated result set. (optional)
page_size = 56 # int | Number of results to return per page. (optional)
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)
with_family = true # bool | 是否返回所有祖先（兼容） (optional)
with_ancestors = true # bool | 是否返回所有祖先 (optional)

try:
    api_response = api_instance.v2_profiles_get_departments(lookup_value, ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled, with_family=with_family, with_ancestors=with_ancestors)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProfilesApi->v2_profiles_get_departments: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lookup_value** | **str**|  | 
 **ordering** | **str**| Which field to use when ordering the results. | [optional] 
 **page** | **int**| A page number within the paginated result set. | [optional] 
 **page_size** | **int**| Number of results to return per page. | [optional] 
 **fields** | **str**| 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id | [optional] 
 **lookup_field** | **str**| 指定查询字段，内容为 lookup_value 所属字段, 例如: username | [optional] 
 **include_disabled** | **bool**| 是否包含已软删除的数据 | [optional] 
 **with_family** | **bool**| 是否返回所有祖先（兼容） | [optional] 
 **with_ancestors** | **bool**| 是否返回所有祖先 | [optional] 

### Return type

[**list[SimpleDepartment]**](SimpleDepartment.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_profiles_get_leaders**
> list[SimpleDepartment] v2_profiles_get_leaders(lookup_value, ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)



获取用户上级信息 包含该用户关联的所有上级信息

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.ProfilesApi()
lookup_value = 'lookup_value_example' # str | 
ordering = 'ordering_example' # str | Which field to use when ordering the results. (optional)
page = 56 # int | A page number within the paginated result set. (optional)
page_size = 56 # int | Number of results to return per page. (optional)
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_response = api_instance.v2_profiles_get_leaders(lookup_value, ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProfilesApi->v2_profiles_get_leaders: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lookup_value** | **str**|  | 
 **ordering** | **str**| Which field to use when ordering the results. | [optional] 
 **page** | **int**| A page number within the paginated result set. | [optional] 
 **page_size** | **int**| Number of results to return per page. | [optional] 
 **fields** | **str**| 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id | [optional] 
 **lookup_field** | **str**| 指定查询字段，内容为 lookup_value 所属字段, 例如: username | [optional] 
 **include_disabled** | **bool**| 是否包含已软删除的数据 | [optional] 

### Return type

[**list[SimpleDepartment]**](SimpleDepartment.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_profiles_list**
> object v2_profiles_list(ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, exact_lookups=exact_lookups, fuzzy_lookups=fuzzy_lookups, wildcard_search=wildcard_search, wildcard_search_fields=wildcard_search_fields, best_match=best_match, time_field=time_field, since=since, until=until, include_disabled=include_disabled)



获取用户列表

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.ProfilesApi()
ordering = 'ordering_example' # str | Which field to use when ordering the results. (optional)
page = 56 # int | A page number within the paginated result set. (optional)
page_size = 56 # int | Number of results to return per page. (optional)
fields = ['fields_example'] # list[str] | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 查询字段，针对 exact_lookups,fuzzy_lookups 生效 (optional)
exact_lookups = ['exact_lookups_example'] # list[str] | 精确查询 lookup_field 所指定的字段, 支持多选，以逗号分隔，例如: cat,dog,fish (optional)
fuzzy_lookups = ['fuzzy_lookups_example'] # list[str] | 模糊查询 lookup_field 所指定的字段, 支持多选，以逗号分隔，例如: cat,dog,fish (optional)
wildcard_search = 'wildcard_search_example' # str | 在多个字段模糊搜索的内容 (optional)
wildcard_search_fields = ['wildcard_search_fields_example'] # list[str] | 指定多个模糊搜索字段 (optional)
best_match = true # bool | 是否按照最短匹配排序 (optional)
time_field = 'time_field_example' # str | 时间过滤字段，支持 update_time, create_time (optional)
since = '2013-10-20T19:20:30+01:00' # datetime | 筛选某个时间点后的记录 (optional)
until = '2013-10-20T19:20:30+01:00' # datetime | 筛选某个时间点前的记录 (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_response = api_instance.v2_profiles_list(ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, exact_lookups=exact_lookups, fuzzy_lookups=fuzzy_lookups, wildcard_search=wildcard_search, wildcard_search_fields=wildcard_search_fields, best_match=best_match, time_field=time_field, since=since, until=until, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProfilesApi->v2_profiles_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ordering** | **str**| Which field to use when ordering the results. | [optional] 
 **page** | **int**| A page number within the paginated result set. | [optional] 
 **page_size** | **int**| Number of results to return per page. | [optional] 
 **fields** | [**list[str]**](str.md)| 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id | [optional] 
 **lookup_field** | **str**| 查询字段，针对 exact_lookups,fuzzy_lookups 生效 | [optional] 
 **exact_lookups** | [**list[str]**](str.md)| 精确查询 lookup_field 所指定的字段, 支持多选，以逗号分隔，例如: cat,dog,fish | [optional] 
 **fuzzy_lookups** | [**list[str]**](str.md)| 模糊查询 lookup_field 所指定的字段, 支持多选，以逗号分隔，例如: cat,dog,fish | [optional] 
 **wildcard_search** | **str**| 在多个字段模糊搜索的内容 | [optional] 
 **wildcard_search_fields** | [**list[str]**](str.md)| 指定多个模糊搜索字段 | [optional] 
 **best_match** | **bool**| 是否按照最短匹配排序 | [optional] 
 **time_field** | **str**| 时间过滤字段，支持 update_time, create_time | [optional] 
 **since** | **datetime**| 筛选某个时间点后的记录 | [optional] 
 **until** | **datetime**| 筛选某个时间点前的记录 | [optional] 
 **include_disabled** | **bool**| 是否包含已软删除的数据 | [optional] 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_profiles_modify_password**
> Empty v2_profiles_modify_password(body, lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)



修改用户密码 不同于直接更新 password 字段，修改密码 API 面向普通用户，需要校验原密码

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.ProfilesApi()
body = bkuser_sdk.ProfileModifyPassword() # ProfileModifyPassword | 
lookup_value = 'lookup_value_example' # str | 
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_response = api_instance.v2_profiles_modify_password(body, lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProfilesApi->v2_profiles_modify_password: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ProfileModifyPassword**](ProfileModifyPassword.md)|  | 
 **lookup_value** | **str**|  | 
 **fields** | **str**| 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id | [optional] 
 **lookup_field** | **str**| 指定查询字段，内容为 lookup_value 所属字段, 例如: username | [optional] 
 **include_disabled** | **bool**| 是否包含已软删除的数据 | [optional] 

### Return type

[**Empty**](Empty.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_profiles_partial_update**
> Profile v2_profiles_partial_update(body, lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)



更新用户部分字段

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.ProfilesApi()
body = bkuser_sdk.UpdateProfile() # UpdateProfile | 
lookup_value = 'lookup_value_example' # str | 
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_response = api_instance.v2_profiles_partial_update(body, lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProfilesApi->v2_profiles_partial_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**UpdateProfile**](UpdateProfile.md)|  | 
 **lookup_value** | **str**|  | 
 **fields** | **str**| 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id | [optional] 
 **lookup_field** | **str**| 指定查询字段，内容为 lookup_value 所属字段, 例如: username | [optional] 
 **include_disabled** | **bool**| 是否包含已软删除的数据 | [optional] 

### Return type

[**Profile**](Profile.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_profiles_read**
> Profile v2_profiles_read(lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)



获取详细信息

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.ProfilesApi()
lookup_value = 'lookup_value_example' # str | 
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_response = api_instance.v2_profiles_read(lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProfilesApi->v2_profiles_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lookup_value** | **str**|  | 
 **fields** | **str**| 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id | [optional] 
 **lookup_field** | **str**| 指定查询字段，内容为 lookup_value 所属字段, 例如: username | [optional] 
 **include_disabled** | **bool**| 是否包含已软删除的数据 | [optional] 

### Return type

[**Profile**](Profile.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_profiles_restoration**
> Empty v2_profiles_restoration(body, lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)



软删除对象恢复

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.ProfilesApi()
body = NULL # object | 
lookup_value = 'lookup_value_example' # str | 
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_response = api_instance.v2_profiles_restoration(body, lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProfilesApi->v2_profiles_restoration: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | 
 **lookup_value** | **str**|  | 
 **fields** | **str**| 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id | [optional] 
 **lookup_field** | **str**| 指定查询字段，内容为 lookup_value 所属字段, 例如: username | [optional] 
 **include_disabled** | **bool**| 是否包含已软删除的数据 | [optional] 

### Return type

[**Empty**](Empty.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_profiles_update**
> Profile v2_profiles_update(body, lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)



更新用户

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.ProfilesApi()
body = bkuser_sdk.UpdateProfile() # UpdateProfile | 
lookup_value = 'lookup_value_example' # str | 
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_response = api_instance.v2_profiles_update(body, lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProfilesApi->v2_profiles_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**UpdateProfile**](UpdateProfile.md)|  | 
 **lookup_value** | **str**|  | 
 **fields** | **str**| 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id | [optional] 
 **lookup_field** | **str**| 指定查询字段，内容为 lookup_value 所属字段, 例如: username | [optional] 
 **include_disabled** | **bool**| 是否包含已软删除的数据 | [optional] 

### Return type

[**Profile**](Profile.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_retrieve_by_token**
> Profile v2_retrieve_by_token(token, lookup_field=lookup_field, ordering=ordering, page=page, page_size=page_size)



通过 Token 获取用户 通过有效的 token 获取用户信息

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.ProfilesApi()
token = 'token_example' # str | 
lookup_field = 'lookup_field_example' # str | A search term. (optional)
ordering = 'ordering_example' # str | Which field to use when ordering the results. (optional)
page = 56 # int | A page number within the paginated result set. (optional)
page_size = 56 # int | Number of results to return per page. (optional)

try:
    api_response = api_instance.v2_retrieve_by_token(token, lookup_field=lookup_field, ordering=ordering, page=page, page_size=page_size)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProfilesApi->v2_retrieve_by_token: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**|  | 
 **lookup_field** | **str**| A search term. | [optional] 
 **ordering** | **str**| Which field to use when ordering the results. | [optional] 
 **page** | **int**| A page number within the paginated result set. | [optional] 
 **page_size** | **int**| Number of results to return per page. | [optional] 

### Return type

[**Profile**](Profile.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

