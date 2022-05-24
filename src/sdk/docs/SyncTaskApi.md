# bkuser_sdk.SyncTaskApi

All URIs are relative to *http://localhost:8004/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_sync_task_list**](SyncTaskApi.md#v2_sync_task_list) | **GET** /api/v2/sync_task/ |
[**v2_sync_task_show_logs**](SyncTaskApi.md#v2_sync_task_show_logs) | **GET** /api/v2/sync_task/{lookup_value}/logs |

# **v2_sync_task_list**
> object v2_sync_task_list(ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, exact_lookups=exact_lookups, fuzzy_lookups=fuzzy_lookups, wildcard_search=wildcard_search, wildcard_search_fields=wildcard_search_fields, best_match=best_match, time_field=time_field, since=since, until=until, include_disabled=include_disabled)



获取对象列表

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.SyncTaskApi()
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
    api_response = api_instance.v2_sync_task_list(ordering=ordering, page=page, page_size=page_size, fields=fields, lookup_field=lookup_field, exact_lookups=exact_lookups, fuzzy_lookups=fuzzy_lookups, wildcard_search=wildcard_search, wildcard_search_fields=wildcard_search_fields, best_match=best_match, time_field=time_field, since=since, until=until, include_disabled=include_disabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SyncTaskApi->v2_sync_task_list: %s\n" % e)
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

# **v2_sync_task_show_logs**
> list[SyncTaskProcess] v2_sync_task_show_logs(lookup_value)



### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.SyncTaskApi()
lookup_value = 'lookup_value_example' # str |

try:
    api_response = api_instance.v2_sync_task_show_logs(lookup_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SyncTaskApi->v2_sync_task_show_logs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lookup_value** | **str**|  |

### Return type

[**list[SyncTaskProcess]**](SyncTaskProcess.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
