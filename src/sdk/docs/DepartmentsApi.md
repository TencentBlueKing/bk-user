# bkuser_sdk.DepartmentsApi

All URIs are relative to *http://localhost:8000/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_departments_create**](DepartmentsApi.md#v2_departments_create) | **POST** /api/v2/departments/ | 
[**v2_departments_delete**](DepartmentsApi.md#v2_departments_delete) | **DELETE** /api/v2/departments/{lookup_value}/ | 
[**v2_departments_get_ancestor**](DepartmentsApi.md#v2_departments_get_ancestor) | **GET** /api/v2/departments/{lookup_value}/ancestors/ | 
[**v2_departments_get_children**](DepartmentsApi.md#v2_departments_get_children) | **GET** /api/v2/departments/{lookup_value}/children/ | 
[**v2_departments_list**](DepartmentsApi.md#v2_departments_list) | **GET** /api/v2/departments/ | 
[**v2_departments_partial_update**](DepartmentsApi.md#v2_departments_partial_update) | **PATCH** /api/v2/departments/{lookup_value}/ | 
[**v2_departments_profiles_create**](DepartmentsApi.md#v2_departments_profiles_create) | **POST** /api/v2/departments/{lookup_value}/profiles/ | 
[**v2_departments_profiles_read**](DepartmentsApi.md#v2_departments_profiles_read) | **GET** /api/v2/departments/{lookup_value}/profiles/ | 
[**v2_departments_read**](DepartmentsApi.md#v2_departments_read) | **GET** /api/v2/departments/{lookup_value}/ | 
[**v2_departments_restoration**](DepartmentsApi.md#v2_departments_restoration) | **POST** /api/v2/departments/{lookup_value}/restoration/ | 
[**v2_departments_update**](DepartmentsApi.md#v2_departments_update) | **POST** /api/v2/departments/{lookup_value}/ | 

# **v2_departments_create**
> Department v2_departments_create(body)



创建部门

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.DepartmentsApi()
body = bkuser_sdk.Department() # Department | 

try:
    api_response = api_instance.v2_departments_create(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DepartmentsApi->v2_departments_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Department**](Department.md)|  | 

### Return type

[**Department**](Department.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_departments_delete**
> v2_departments_delete(lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)



删除对象

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.DepartmentsApi()
lookup_value = 'lookup_value_example' # str | 
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_instance.v2_departments_delete(lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)
except ApiException as e:
    print("Exception when calling DepartmentsApi->v2_departments_delete: %s\n" % e)
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

# **v2_departments_get_ancestor**
> object v2_departments_get_ancestor(lookup_value, ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)



获取父级部门

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.DepartmentsApi()
lookup_value = 'lookup_value_example' # str | 
ordering = 'ordering_example' # str | Which field to use when ordering the results. (optional)
page = 56 # int | A page number within the paginated result set. (optional)
page_size = 56 # int | Number of results to return per page. (optional)
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_response = api_instance.v2_departments_get_ancestor(lookup_value, ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DepartmentsApi->v2_departments_get_ancestor: %s\n" % e)
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

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_departments_get_children**
> object v2_departments_get_children(lookup_value, ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)



获取子部门列表

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.DepartmentsApi()
lookup_value = 'lookup_value_example' # str | 
ordering = 'ordering_example' # str | Which field to use when ordering the results. (optional)
page = 56 # int | A page number within the paginated result set. (optional)
page_size = 56 # int | Number of results to return per page. (optional)
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_response = api_instance.v2_departments_get_children(lookup_value, ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DepartmentsApi->v2_departments_get_children: %s\n" % e)
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

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_departments_list**
> object v2_departments_list(ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, exact_lookups=exact_lookups, fuzzy_lookups=fuzzy_lookups, wildcard_search=wildcard_search, wildcard_search_fields=wildcard_search_fields, best_match=best_match, time_field=time_field, since=since, until=until, include_disabled=include_disabled)



获取对象列表

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.DepartmentsApi()
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
    api_response = api_instance.v2_departments_list(ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, exact_lookups=exact_lookups, fuzzy_lookups=fuzzy_lookups, wildcard_search=wildcard_search, wildcard_search_fields=wildcard_search_fields, best_match=best_match, time_field=time_field, since=since, until=until, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DepartmentsApi->v2_departments_list: %s\n" % e)
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

# **v2_departments_partial_update**
> Department v2_departments_partial_update(body, lookup_value)



### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.DepartmentsApi()
body = bkuser_sdk.Department() # Department | 
lookup_value = 'lookup_value_example' # str | 

try:
    api_response = api_instance.v2_departments_partial_update(body, lookup_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DepartmentsApi->v2_departments_partial_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Department**](Department.md)|  | 
 **lookup_value** | **str**|  | 

### Return type

[**Department**](Department.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_departments_profiles_create**
> list[ProfileMinimal] v2_departments_profiles_create(body, lookup_value)



在部门内添加人员

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.DepartmentsApi()
body = bkuser_sdk.DepartmentAddProfiles() # DepartmentAddProfiles | 
lookup_value = 'lookup_value_example' # str | 

try:
    api_response = api_instance.v2_departments_profiles_create(body, lookup_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DepartmentsApi->v2_departments_profiles_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**DepartmentAddProfiles**](DepartmentAddProfiles.md)|  | 
 **lookup_value** | **str**|  | 

### Return type

[**list[ProfileMinimal]**](ProfileMinimal.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_departments_profiles_read**
> object v2_departments_profiles_read(lookup_value, ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled, recursive=recursive, detail=detail, wildcard_search=wildcard_search)



获取部门内的人员

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.DepartmentsApi()
lookup_value = 'lookup_value_example' # str | 
ordering = 'ordering_example' # str | Which field to use when ordering the results. (optional)
page = 56 # int | A page number within the paginated result set. (optional)
page_size = 56 # int | Number of results to return per page. (optional)
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)
recursive = true # bool | 是否递归 (optional)
detail = true # bool | 是否返回全部字段 (optional)
wildcard_search = 'wildcard_search_example' # str | 模糊查找用户的 username & display_name 字段 (optional)

try:
    api_response = api_instance.v2_departments_profiles_read(lookup_value, ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled, recursive=recursive, detail=detail, wildcard_search=wildcard_search)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DepartmentsApi->v2_departments_profiles_read: %s\n" % e)
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
 **recursive** | **bool**| 是否递归 | [optional] 
 **detail** | **bool**| 是否返回全部字段 | [optional] 
 **wildcard_search** | **str**| 模糊查找用户的 username &amp; display_name 字段 | [optional] 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_departments_read**
> DepartmentsWithAncestors v2_departments_read(lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled, with_ancestors=with_ancestors)



### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.DepartmentsApi()
lookup_value = 'lookup_value_example' # str | 
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)
with_ancestors = true # bool |  (optional)

try:
    api_response = api_instance.v2_departments_read(lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled, with_ancestors=with_ancestors)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DepartmentsApi->v2_departments_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lookup_value** | **str**|  | 
 **fields** | **str**| 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id | [optional] 
 **lookup_field** | **str**| 指定查询字段，内容为 lookup_value 所属字段, 例如: username | [optional] 
 **include_disabled** | **bool**| 是否包含已软删除的数据 | [optional] 
 **with_ancestors** | **bool**|  | [optional] 

### Return type

[**DepartmentsWithAncestors**](DepartmentsWithAncestors.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_departments_restoration**
> Empty v2_departments_restoration(body, lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)



软删除对象恢复

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.DepartmentsApi()
body = NULL # object | 
lookup_value = 'lookup_value_example' # str | 
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_response = api_instance.v2_departments_restoration(body, lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DepartmentsApi->v2_departments_restoration: %s\n" % e)
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

# **v2_departments_update**
> Department v2_departments_update(body, lookup_value)



更新部门

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.DepartmentsApi()
body = bkuser_sdk.Department() # Department | 
lookup_value = 'lookup_value_example' # str | 

try:
    api_response = api_instance.v2_departments_update(body, lookup_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DepartmentsApi->v2_departments_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Department**](Department.md)|  | 
 **lookup_value** | **str**|  | 

### Return type

[**Department**](Department.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

