# bkuser_sdk.BatchApi

All URIs are relative to *http://localhost:8000/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_batch_departments_multiple_retrieve_profiles**](BatchApi.md#v2_batch_departments_multiple_retrieve_profiles) | **GET** /api/v2/batch/departments/profiles/ | 
[**v2_batch_profiles_delete**](BatchApi.md#v2_batch_profiles_delete) | **DELETE** /api/v2/batch/profiles/ | 
[**v2_batch_profiles_partial_update**](BatchApi.md#v2_batch_profiles_partial_update) | **PATCH** /api/v2/batch/profiles/ | 
[**v2_batch_profiles_read**](BatchApi.md#v2_batch_profiles_read) | **GET** /api/v2/batch/profiles/ | 

# **v2_batch_departments_multiple_retrieve_profiles**
> list[Profile] v2_batch_departments_multiple_retrieve_profiles(department_ids, recursive=recursive)



批量获取组织的用户

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.BatchApi()
department_ids = 'department_ids_example' # str | department id 列表，以 , 分隔
recursive = true # bool |  (optional)

try:
    api_response = api_instance.v2_batch_departments_multiple_retrieve_profiles(department_ids, recursive=recursive)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchApi->v2_batch_departments_multiple_retrieve_profiles: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **department_ids** | **str**| department id 列表，以 , 分隔 | 
 **recursive** | **bool**|  | [optional] 

### Return type

[**list[Profile]**](Profile.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_batch_profiles_delete**
> Empty v2_batch_profiles_delete(body)



批量删除用户

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.BatchApi()
body = [bkuser_sdk.UpdateProfile()] # list[UpdateProfile] | 

try:
    api_response = api_instance.v2_batch_profiles_delete(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchApi->v2_batch_profiles_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**list[UpdateProfile]**](UpdateProfile.md)|  | 

### Return type

[**Empty**](Empty.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_batch_profiles_partial_update**
> list[Profile] v2_batch_profiles_partial_update(body)



批量更新用户

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.BatchApi()
body = [bkuser_sdk.UpdateProfile()] # list[UpdateProfile] | 

try:
    api_response = api_instance.v2_batch_profiles_partial_update(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchApi->v2_batch_profiles_partial_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**list[UpdateProfile]**](UpdateProfile.md)|  | 

### Return type

[**list[Profile]**](Profile.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_batch_profiles_read**
> list[Profile] v2_batch_profiles_read(query_ids)



批量获取用户

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.BatchApi()
query_ids = 'query_ids_example' # str | 查询 id 列表，以 , 分隔

try:
    api_response = api_instance.v2_batch_profiles_read(query_ids)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchApi->v2_batch_profiles_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_ids** | **str**| 查询 id 列表，以 , 分隔 | 

### Return type

[**list[Profile]**](Profile.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

