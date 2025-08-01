# Authentication
(*authentication*)

## Overview

### Available Operations

* [login](#login) - Login
* [get_current_user_info](#get_current_user_info) - Get Current User Info
* [logout](#logout) - Logout

## login

Authenticate user and return JWT token

Accepts either username or email address as the username field.

### Example Usage

<!-- UsageSnippet language="python" operationID="login_api_v1_auth_login_post" method="post" path="/api/v1/auth/login" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.authentication.login(username="Felix_Mante", password="3yjgaqeC7UMz5sl")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `username`                                                          | *str*                                                               | :heavy_check_mark:                                                  | Username or email address                                           |
| `password`                                                          | *str*                                                               | :heavy_check_mark:                                                  | User password                                                       |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.LoginResponse](../../models/loginresponse.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.BadRequestError     | 400                        | application/json           |
| errors.UnauthorizedError   | 401, 403                   | application/json           |
| errors.NotFoundError       | 404                        | application/json           |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.RateLimitedError    | 429                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## get_current_user_info

Get current user information

### Example Usage

<!-- UsageSnippet language="python" operationID="get_current_user_info_api_v1_auth_me_get" method="get" path="/api/v1/auth/me" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.authentication.get_current_user_info()

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.DbrAPIAuthUserInfo](../../models/dbrapiauthuserinfo.md)**

### Errors

| Error Type               | Status Code              | Content Type             |
| ------------------------ | ------------------------ | ------------------------ |
| errors.UnauthorizedError | 401, 403                 | application/json         |
| errors.NotFoundError     | 404                      | application/json         |
| errors.BadRequestError   | 400, 422                 | application/json         |
| errors.RateLimitedError  | 429                      | application/json         |
| errors.APIError          | 4XX, 5XX                 | \*/\*                    |

## logout

Logout endpoint (JWT tokens are stateless, so this is mainly for client-side cleanup)

### Example Usage

<!-- UsageSnippet language="python" operationID="logout_api_v1_auth_logout_post" method="post" path="/api/v1/auth/logout" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.authentication.logout()

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[Any](../../models/.md)**

### Errors

| Error Type               | Status Code              | Content Type             |
| ------------------------ | ------------------------ | ------------------------ |
| errors.UnauthorizedError | 401, 403                 | application/json         |
| errors.NotFoundError     | 404                      | application/json         |
| errors.BadRequestError   | 400, 422                 | application/json         |
| errors.RateLimitedError  | 429                      | application/json         |
| errors.APIError          | 4XX, 5XX                 | \*/\*                    |