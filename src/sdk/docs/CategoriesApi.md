# bkuser_sdk.CategoriesApi

All URIs are relative to *http://localhost:8000/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_categories_create**](CategoriesApi.md#v2_categories_create) | **POST** /api/v2/categories/ | 
[**v2_categories_delete**](CategoriesApi.md#v2_categories_delete) | **DELETE** /api/v2/categories/{lookup_value}/ | 
[**v2_categories_import_data_file**](CategoriesApi.md#v2_categories_import_data_file) | **POST** /api/v2/categories/{lookup_value}/import/ | 
[**v2_categories_list**](CategoriesApi.md#v2_categories_list) | **GET** /api/v2/categories/ | 
[**v2_categories_list_metas**](CategoriesApi.md#v2_categories_list_metas) | **GET** /api/v2/categories_metas/ | 
[**v2_categories_partial_update**](CategoriesApi.md#v2_categories_partial_update) | **PATCH** /api/v2/categories/{lookup_value}/ | 
[**v2_categories_read**](CategoriesApi.md#v2_categories_read) | **GET** /api/v2/categories/{lookup_value}/ | 
[**v2_categories_restoration**](CategoriesApi.md#v2_categories_restoration) | **POST** /api/v2/categories/{lookup_value}/restoration/ | 
[**v2_categories_sync**](CategoriesApi.md#v2_categories_sync) | **POST** /api/v2/categories/{lookup_value}/sync/ | 
[**v2_categories_test_connection**](CategoriesApi.md#v2_categories_test_connection) | **POST** /api/v2/categories/{lookup_value}/test_connection/ | 
[**v2_categories_test_fetch_data**](CategoriesApi.md#v2_categories_test_fetch_data) | **POST** /api/v2/categories/{lookup_value}/test_fetch_data/ | 
[**v2_categories_update**](CategoriesApi.md#v2_categories_update) | **PUT** /api/v2/categories/{lookup_value}/ | 

# **v2_categories_create**
> Category v2_categories_create(body)



创建用户目录

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.CategoriesApi()
body = bkuser_sdk.CreateCategory() # CreateCategory | 

try:
    api_response = api_instance.v2_categories_create(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CategoriesApi->v2_categories_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CreateCategory**](CreateCategory.md)|  | 

### Return type

[**Category**](Category.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_categories_delete**
> v2_categories_delete(lookup_value)



删除用户目录

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.CategoriesApi()
lookup_value = 'lookup_value_example' # str | 

try:
    api_instance.v2_categories_delete(lookup_value)
except ApiException as e:
    print("Exception when calling CategoriesApi->v2_categories_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lookup_value** | **str**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_categories_import_data_file**
> Empty v2_categories_import_data_file(raw_data_file, lookup_value)



向本地目录导入数据文件

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.CategoriesApi()
raw_data_file = 'raw_data_file_example' # file | 
lookup_value = 'lookup_value_example' # str | 

try:
    api_response = api_instance.v2_categories_import_data_file(raw_data_file, lookup_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CategoriesApi->v2_categories_import_data_file: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **raw_data_file** | **file**|  | 
 **lookup_value** | **str**|  | 

### Return type

[**Empty**](Empty.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data, application/x-www-form-urlencoded
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_categories_list**
> object v2_categories_list(ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, exact_lookups=exact_lookups, fuzzy_lookups=fuzzy_lookups, wildcard_search=wildcard_search, wildcard_search_fields=wildcard_search_fields, best_match=best_match, time_field=time_field, since=since, until=until, include_disabled=include_disabled)



获取对象列表

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.CategoriesApi()
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
    api_response = api_instance.v2_categories_list(ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, exact_lookups=exact_lookups, fuzzy_lookups=fuzzy_lookups, wildcard_search=wildcard_search, wildcard_search_fields=wildcard_search_fields, best_match=best_match, time_field=time_field, since=since, until=until, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CategoriesApi->v2_categories_list: %s\n" % e)
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

# **v2_categories_list_metas**
> list[CategoryMetaSLZ] v2_categories_list_metas(lookup_field=lookup_field, ordering=ordering, page=page, page_size=page_size)



列表展示所有目录类型基本信息

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.CategoriesApi()
lookup_field = 'lookup_field_example' # str | A search term. (optional)
ordering = 'ordering_example' # str | Which field to use when ordering the results. (optional)
page = 56 # int | A page number within the paginated result set. (optional)
page_size = 56 # int | Number of results to return per page. (optional)

try:
    api_response = api_instance.v2_categories_list_metas(lookup_field=lookup_field, ordering=ordering, page=page, page_size=page_size)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CategoriesApi->v2_categories_list_metas: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lookup_field** | **str**| A search term. | [optional] 
 **ordering** | **str**| Which field to use when ordering the results. | [optional] 
 **page** | **int**| A page number within the paginated result set. | [optional] 
 **page_size** | **int**| Number of results to return per page. | [optional] 

### Return type

[**list[CategoryMetaSLZ]**](CategoryMetaSLZ.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_categories_partial_update**
> Category v2_categories_partial_update(body, lookup_value)



### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.CategoriesApi()
body = bkuser_sdk.Category() # Category | 
lookup_value = 'lookup_value_example' # str | 

try:
    api_response = api_instance.v2_categories_partial_update(body, lookup_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CategoriesApi->v2_categories_partial_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Category**](Category.md)|  | 
 **lookup_value** | **str**|  | 

### Return type

[**Category**](Category.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_categories_read**
> Category v2_categories_read(lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)



获取详细信息

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.CategoriesApi()
lookup_value = 'lookup_value_example' # str | 
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_response = api_instance.v2_categories_read(lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CategoriesApi->v2_categories_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lookup_value** | **str**|  | 
 **fields** | **str**| 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id | [optional] 
 **lookup_field** | **str**| 指定查询字段，内容为 lookup_value 所属字段, 例如: username | [optional] 
 **include_disabled** | **bool**| 是否包含已软删除的数据 | [optional] 

### Return type

[**Category**](Category.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_categories_restoration**
> Empty v2_categories_restoration(body, lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)



软删除对象恢复

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.CategoriesApi()
body = NULL # object | 
lookup_value = 'lookup_value_example' # str | 
fields = 'fields_example' # str | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id (optional)
lookup_field = 'lookup_field_example' # str | 指定查询字段，内容为 lookup_value 所属字段, 例如: username (optional)
include_disabled = true # bool | 是否包含已软删除的数据 (optional)

try:
    api_response = api_instance.v2_categories_restoration(body, lookup_value, fields=fields, lookup_field=lookup_field, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CategoriesApi->v2_categories_restoration: %s\n" % e)
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

# **v2_categories_sync**
> CategorySyncResponseSLZ v2_categories_sync(body, lookup_value)



同步目录

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.CategoriesApi()
body = bkuser_sdk.CategorySync() # CategorySync | 
lookup_value = 'lookup_value_example' # str | 

try:
    api_response = api_instance.v2_categories_sync(body, lookup_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CategoriesApi->v2_categories_sync: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CategorySync**](CategorySync.md)|  | 
 **lookup_value** | **str**|  | 

### Return type

[**CategorySyncResponseSLZ**](CategorySyncResponseSLZ.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_categories_test_connection**
> Empty v2_categories_test_connection(body, lookup_value)



测试连接

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.CategoriesApi()
body = bkuser_sdk.CategoryTestConnection() # CategoryTestConnection | 
lookup_value = 'lookup_value_example' # str | 

try:
    api_response = api_instance.v2_categories_test_connection(body, lookup_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CategoriesApi->v2_categories_test_connection: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CategoryTestConnection**](CategoryTestConnection.md)|  | 
 **lookup_value** | **str**|  | 

### Return type

[**Empty**](Empty.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_categories_test_fetch_data**
> Empty v2_categories_test_fetch_data(body, lookup_value)



测试获取数据

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.CategoriesApi()
body = bkuser_sdk.CategoryTestFetchData() # CategoryTestFetchData | 
lookup_value = 'lookup_value_example' # str | 

try:
    api_response = api_instance.v2_categories_test_fetch_data(body, lookup_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CategoriesApi->v2_categories_test_fetch_data: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CategoryTestFetchData**](CategoryTestFetchData.md)|  | 
 **lookup_value** | **str**|  | 

### Return type

[**Empty**](Empty.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_categories_update**
> Category v2_categories_update(body, lookup_value)



更新用户目录

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.CategoriesApi()
body = bkuser_sdk.Category() # Category | 
lookup_value = 'lookup_value_example' # str | 

try:
    api_response = api_instance.v2_categories_update(body, lookup_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CategoriesApi->v2_categories_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Category**](Category.md)|  | 
 **lookup_value** | **str**|  | 

### Return type

[**Category**](Category.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

