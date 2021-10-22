# bkuser_sdk.ShortcutsApi

All URIs are relative to *http://localhost:8000/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_shortcuts_departments_list_tops**](ShortcutsApi.md#v2_shortcuts_departments_list_tops) | **GET** /api/v2/shortcuts/departments/tops/ | 

# **v2_shortcuts_departments_list_tops**
> object v2_shortcuts_departments_list_tops(lookup_field=lookup_field, ordering=ordering, page=page, page_size=page_size)



获取最顶层的组织列表[权限中心亲和]

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.ShortcutsApi()
lookup_field = 'lookup_field_example' # str | A search term. (optional)
ordering = 'ordering_example' # str | Which field to use when ordering the results. (optional)
page = 56 # int | A page number within the paginated result set. (optional)
page_size = 56 # int | Number of results to return per page. (optional)

try:
    api_response = api_instance.v2_shortcuts_departments_list_tops(lookup_field=lookup_field, ordering=ordering, page=page, page_size=page_size)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ShortcutsApi->v2_shortcuts_departments_list_tops: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lookup_field** | **str**| A search term. | [optional] 
 **ordering** | **str**| Which field to use when ordering the results. | [optional] 
 **page** | **int**| A page number within the paginated result set. | [optional] 
 **page_size** | **int**| Number of results to return per page. | [optional] 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

