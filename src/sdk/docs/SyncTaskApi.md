# bkuser_sdk.SyncTaskApi

All URIs are relative to *http://localhost:8000/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_sync_task_list**](SyncTaskApi.md#v2_sync_task_list) | **GET** /api/v2/sync_task/ | 
[**v2_sync_task_show_logs**](SyncTaskApi.md#v2_sync_task_show_logs) | **GET** /api/v2/sync_task/{id}/logs | 

# **v2_sync_task_list**
> list[SyncTask] v2_sync_task_list()



### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.SyncTaskApi()

try:
    api_response = api_instance.v2_sync_task_list()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SyncTaskApi->v2_sync_task_list: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[SyncTask]**](SyncTask.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_sync_task_show_logs**
> list[SyncTaskProcess] v2_sync_task_show_logs(id)



### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.SyncTaskApi()
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | A UUID string identifying this sync task.

try:
    api_response = api_instance.v2_sync_task_show_logs(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SyncTaskApi->v2_sync_task_show_logs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)| A UUID string identifying this sync task. | 

### Return type

[**list[SyncTaskProcess]**](SyncTaskProcess.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

