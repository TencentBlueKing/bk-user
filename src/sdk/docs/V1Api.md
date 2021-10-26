# bkuser_sdk.V1Api

All URIs are relative to *http://localhost:8000/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_login_login**](V1Api.md#v1_login_login) | **POST** /api/v1/login/check/ | 
[**v1_login_profile_batch_query**](V1Api.md#v1_login_profile_batch_query) | **POST** /api/v1/login/profile/query/ | 
[**v1_login_upsert**](V1Api.md#v1_login_upsert) | **POST** /api/v1/login/profile/ | 

# **v1_login_login**
> Profile v1_login_login(body)



登录信息校验

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.V1Api()
body = bkuser_sdk.ProfileLogin() # ProfileLogin | 

try:
    api_response = api_instance.v1_login_login(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling V1Api->v1_login_login: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ProfileLogin**](ProfileLogin.md)|  | 

### Return type

[**Profile**](Profile.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_login_profile_batch_query**
> LoginBatchQuery v1_login_profile_batch_query(body)



登陆均为兼容代码

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.V1Api()
body = bkuser_sdk.LoginBatchQuery() # LoginBatchQuery | 

try:
    api_response = api_instance.v1_login_profile_batch_query(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling V1Api->v1_login_profile_batch_query: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**LoginBatchQuery**](LoginBatchQuery.md)|  | 

### Return type

[**LoginBatchQuery**](LoginBatchQuery.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_login_upsert**
> LoginUpsert v1_login_upsert(body)



登陆均为兼容代码

### Example
```python
from __future__ import print_function
import time
import bkuser_sdk
from bkuser_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = bkuser_sdk.V1Api()
body = bkuser_sdk.LoginUpsert() # LoginUpsert | 

try:
    api_response = api_instance.v1_login_upsert(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling V1Api->v1_login_upsert: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**LoginUpsert**](LoginUpsert.md)|  | 

### Return type

[**LoginUpsert**](LoginUpsert.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

