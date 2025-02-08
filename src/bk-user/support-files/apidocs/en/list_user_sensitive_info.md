### Description

Batch query user's sensitive information

### Parameters

| Name         | Type   | Required | Description                                                                                           |
|--------------|--------|----------|-------------------------------------------------------------------------------------------------------|
| bk_usernames | string | Yes      | Blueking user's unique identifier, multiple identifiers are separated by commas, and the limit is 100 |

### Request Example

```
// URL Query Parameters
bk_usernames=7idwx3b7nzk6xigs,0wngfim3uzhadh1w
```

### Response Example for Status Code 200

```json5
{
  "data": [
    {
      "bk_username": "7idwx3b7nzk6xigs",
      "phone": "17712341234",
      "phone_country_code": "86",
      "email": "zhangsan@qq.com"
    },
    {
      "bk_username": "0wngfim3uzhadh1w",
      "phone": "18712341234",
      "phone_country_code": "86",
      "email": "lisi@qq.com"
    }
  ]
}
```

### Response Parameters Description

| Name               | Type   | Description                       |
|--------------------|--------|-----------------------------------|
| bk_username        | string | Blueking user's unique identifier |
| phone              | string | Phone number                      |
| phone_country_code | string | Phone number area code            |
| email              | string | Email address                     |

### Response Example for Non-200 Status Code

```json5
// status_code = 400
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "Arguments Validation Failed: bk_usernames: This field cannot be empty."
  }
}
```

```json5
// status_code = 400
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "Arguments Validation Failed: bk_usernames: This field must contain at most 100 objects."
  }
}
```
