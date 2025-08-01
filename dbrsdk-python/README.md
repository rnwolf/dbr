# dbrsdk

Developer-friendly & type-safe Python SDK specifically catered to leverage *dbrsdk* API.

<div align="left">
    <a href="https://www.speakeasy.com/?utm_source=dbrsdk&utm_campaign=python"><img src="https://custom-icon-badges.demolab.com/badge/-Built%20By%20Speakeasy-212015?style=for-the-badge&logoColor=FBE331&logo=speakeasy&labelColor=545454" /></a>
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg" style="width: 100px; height: 28px;" />
    </a>
</div>


<br /><br />
> [!IMPORTANT]
> This SDK is not yet ready for production use. To complete setup please follow the steps outlined in your [workspace](https://app.speakeasy.com/org/throughput-focus/dbr). Delete this section before > publishing to a package manager.

<!-- Start Summary [summary] -->
## Summary

DBR Buffer Management System API: API for managing Collections, Work Items, and Schedules within a Drum Buffer Rope (DBR) system
<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents
<!-- $toc-max-depth=2 -->
* [dbrsdk](#dbrsdk)
  * [SDK Installation](#sdk-installation)
  * [IDE Support](#ide-support)
  * [SDK Example Usage](#sdk-example-usage)
  * [Authentication](#authentication)
  * [Available Resources and Operations](#available-resources-and-operations)
  * [Retries](#retries)
  * [Error Handling](#error-handling)
  * [Server Selection](#server-selection)
  * [Custom HTTP Client](#custom-http-client)
  * [Resource Management](#resource-management)
  * [Debugging](#debugging)
* [Development](#development)
  * [Maturity](#maturity)
  * [Contributions](#contributions)

<!-- End Table of Contents [toc] -->

<!-- Start SDK Installation [installation] -->
## SDK Installation

> [!TIP]
> To finish publishing your SDK to PyPI you must [run your first generation action](https://www.speakeasy.com/docs/github-setup#step-by-step-guide).


> [!NOTE]
> **Python version upgrade policy**
>
> Once a Python version reaches its [official end of life date](https://devguide.python.org/versions/), a 3-month grace period is provided for users to upgrade. Following this grace period, the minimum python version supported in the SDK will be updated.

The SDK can be installed with either *pip* or *poetry* package managers.

### PIP

*PIP* is the default package installer for Python, enabling easy installation and management of packages from PyPI via the command line.

```bash
pip install git+<UNSET>.git
```

### Poetry

*Poetry* is a modern tool that simplifies dependency management and package publishing by using a single `pyproject.toml` file to handle project metadata and dependencies.

```bash
poetry add git+<UNSET>.git
```

### Shell and script usage with `uv`

You can use this SDK in a Python shell with [uv](https://docs.astral.sh/uv/) and the `uvx` command that comes with it like so:

```shell
uvx --from dbrsdk python
```

It's also possible to write a standalone Python script without needing to set up a whole project like so:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "dbrsdk",
# ]
# ///

from dbrsdk import Dbrsdk

sdk = Dbrsdk(
  # SDK arguments
)

# Rest of script here...
```

Once that is saved to a file, you can run it with `uv run script.py` where
`script.py` can be replaced with the actual file name.
<!-- End SDK Installation [installation] -->

<!-- Start IDE Support [idesupport] -->
## IDE Support

### PyCharm

Generally, the SDK will work well with most IDEs out of the box. However, when using PyCharm, you can enjoy much better integration with Pydantic by installing an additional plugin.

- [PyCharm Pydantic Plugin](https://docs.pydantic.dev/latest/integrations/pycharm/)
<!-- End IDE Support [idesupport] -->

<!-- Start SDK Example Usage [usage] -->
## SDK Example Usage

### Example

```python
# Synchronous Example
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.work_items.list(organization_id="<id>")

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asychronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
from dbrsdk import Dbrsdk
import os

async def main():

    async with Dbrsdk(
        http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
    ) as d_client:

        res = await d_client.work_items.list_async(organization_id="<id>")

        # Handle response
        print(res)

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->

<!-- Start Authentication [security] -->
## Authentication

### Per-Client Security Schemes

This SDK supports the following security scheme globally:

| Name          | Type | Scheme      | Environment Variable |
| ------------- | ---- | ----------- | -------------------- |
| `http_bearer` | http | HTTP Bearer | `DBRSDK_HTTP_BEARER` |

To authenticate with the API the `http_bearer` parameter must be set when initializing the SDK client instance. For example:
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.work_items.list(organization_id="<id>")

    # Handle response
    print(res)

```
<!-- End Authentication [security] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

<details open>
<summary>Available methods</summary>

### [api_health](docs/sdks/apihealth/README.md)

* [get](docs/sdks/apihealth/README.md#get) - Api Health Check

### [authentication](docs/sdks/authentication/README.md)

* [login](docs/sdks/authentication/README.md#login) - Login
* [get_current_user_info](docs/sdks/authentication/README.md#get_current_user_info) - Get Current User Info
* [logout](docs/sdks/authentication/README.md#logout) - Logout


### [health](docs/sdks/health/README.md)

* [get](docs/sdks/health/README.md#get) - Health Check

### [memberships](docs/sdks/memberships/README.md)

* [get](docs/sdks/memberships/README.md#get) - Get Memberships
* [create](docs/sdks/memberships/README.md#create) - Create Membership
* [get_membership](docs/sdks/memberships/README.md#get_membership) - Get Membership
* [update_membership](docs/sdks/memberships/README.md#update_membership) - Update Membership
* [delete](docs/sdks/memberships/README.md#delete) - Delete Membership

### [organizations](docs/sdks/organizations/README.md)

* [get](docs/sdks/organizations/README.md#get) - Get Organizations
* [create](docs/sdks/organizations/README.md#create) - Create Organization
* [get_by_id](docs/sdks/organizations/README.md#get_by_id) - Get Organization
* [update](docs/sdks/organizations/README.md#update) - Update Organization
* [delete](docs/sdks/organizations/README.md#delete) - Delete Organization

### [root](docs/sdks/root/README.md)

* [get](docs/sdks/root/README.md#get) - Read Root

### [schedules](docs/sdks/schedules/README.md)

* [list](docs/sdks/schedules/README.md#list) - Get Schedules
* [create](docs/sdks/schedules/README.md#create) - Create Schedule
* [get](docs/sdks/schedules/README.md#get) - Get Schedule
* [update](docs/sdks/schedules/README.md#update) - Update Schedule
* [delete](docs/sdks/schedules/README.md#delete) - Delete Schedule
* [get_board_analytics](docs/sdks/schedules/README.md#get_board_analytics) - Get Board Analytics

#### [schedules.analytics](docs/sdks/analytics/README.md)

* [get](docs/sdks/analytics/README.md#get) - Get Schedule Analytics

### [system](docs/sdks/system/README.md)

* [advance_time_unit](docs/sdks/system/README.md#advance_time_unit) - Advance Time Unit
* [get_time](docs/sdks/system/README.md#get_time) - Get Current Time
* [set_time](docs/sdks/system/README.md#set_time) - Set System Time

### [users](docs/sdks/users/README.md)

* [get](docs/sdks/users/README.md#get) - Get Users
* [create](docs/sdks/users/README.md#create) - Create User
* [get_by_id](docs/sdks/users/README.md#get_by_id) - Get User
* [update](docs/sdks/users/README.md#update) - Update User
* [delete](docs/sdks/users/README.md#delete) - Delete User

### [work_items](docs/sdks/workitems/README.md)

* [list](docs/sdks/workitems/README.md#list) - Get Work Items
* [create](docs/sdks/workitems/README.md#create) - Create Work Item
* [get](docs/sdks/workitems/README.md#get) - Get Work Item
* [update](docs/sdks/workitems/README.md#update) - Update Work Item
* [delete](docs/sdks/workitems/README.md#delete) - Delete Work Item
* [update_task](docs/sdks/workitems/README.md#update_task) - Update Work Item Task

</details>
<!-- End Available Resources and Operations [operations] -->

<!-- Start Retries [retries] -->
## Retries

Some of the endpoints in this SDK support retries. If you use the SDK without any configuration, it will fall back to the default retry strategy provided by the API. However, the default retry strategy can be overridden on a per-operation basis, or across the entire SDK.

To change the default retry strategy for a single API call, simply provide a `RetryConfig` object to the call:
```python
from dbrsdk import Dbrsdk
from dbrsdk.utils import BackoffStrategy, RetryConfig
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.work_items.list(organization_id="<id>",
        RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False))

    # Handle response
    print(res)

```

If you'd like to override the default retry strategy for all operations that support retries, you can use the `retry_config` optional parameter when initializing the SDK:
```python
from dbrsdk import Dbrsdk
from dbrsdk.utils import BackoffStrategy, RetryConfig
import os


with Dbrsdk(
    retry_config=RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False),
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.work_items.list(organization_id="<id>")

    # Handle response
    print(res)

```
<!-- End Retries [retries] -->

<!-- Start Error Handling [errors] -->
## Error Handling

[`DbrsdkError`](./src/dbrsdk/errors/dbrsdkerror.py) is the base class for all HTTP error responses. It has the following properties:

| Property           | Type             | Description                                                                             |
| ------------------ | ---------------- | --------------------------------------------------------------------------------------- |
| `err.message`      | `str`            | Error message                                                                           |
| `err.status_code`  | `int`            | HTTP response status code eg `404`                                                      |
| `err.headers`      | `httpx.Headers`  | HTTP response headers                                                                   |
| `err.body`         | `str`            | HTTP body. Can be empty string if no body is returned.                                  |
| `err.raw_response` | `httpx.Response` | Raw HTTP response                                                                       |
| `err.data`         |                  | Optional. Some errors may contain structured data. [See Error Classes](#error-classes). |

### Example
```python
from dbrsdk import Dbrsdk, errors
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:
    res = None
    try:

        res = d_client.work_items.list(organization_id="<id>")

        # Handle response
        print(res)


    except errors.DbrsdkError as e:
        # The base class for HTTP error responses
        print(e.message)
        print(e.status_code)
        print(e.body)
        print(e.headers)
        print(e.raw_response)

        # Depending on the method different errors may be thrown
        if isinstance(e, errors.BadRequestError):
            print(e.data.message)  # Optional[str]
            print(e.data.additional_properties)  # Optional[Dict[str, Any]]
```

### Error Classes
**Primary errors:**
* [`DbrsdkError`](./src/dbrsdk/errors/dbrsdkerror.py): The base class for HTTP error responses.
  * [`HTTPValidationError`](./src/dbrsdk/errors/httpvalidationerror.py): Validation Error. Status code `422`. *

<details><summary>Less common errors (9)</summary>

<br />

**Network errors:**
* [`httpx.RequestError`](https://www.python-httpx.org/exceptions/#httpx.RequestError): Base class for request errors.
    * [`httpx.ConnectError`](https://www.python-httpx.org/exceptions/#httpx.ConnectError): HTTP client was unable to make a request to a server.
    * [`httpx.TimeoutException`](https://www.python-httpx.org/exceptions/#httpx.TimeoutException): HTTP request timed out.


**Inherit from [`DbrsdkError`](./src/dbrsdk/errors/dbrsdkerror.py)**:
* [`BadRequestError`](./src/dbrsdk/errors/badrequesterror.py): Invalid request. Applicable to 22 of 37 methods.*
* [`UnauthorizedError`](./src/dbrsdk/errors/unauthorizederror.py): Permission denied or not authenticated. Applicable to 22 of 37 methods.*
* [`NotFoundError`](./src/dbrsdk/errors/notfounderror.py): Not found. Status code `404`. Applicable to 22 of 37 methods.*
* [`RateLimitedError`](./src/dbrsdk/errors/ratelimitederror.py): Rate limit exceeded. Status code `429`. Applicable to 22 of 37 methods.*
* [`ResponseValidationError`](./src/dbrsdk/errors/responsevalidationerror.py): Type mismatch between the response data and the expected Pydantic model. Provides access to the Pydantic validation error via the `cause` attribute.

</details>

\* Check [the method documentation](#available-resources-and-operations) to see if the error is applicable.
<!-- End Error Handling [errors] -->

<!-- Start Server Selection [server] -->
## Server Selection

### Override Server URL Per-Client

The default server can be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    server_url="http://127.0.0.1:8000",
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.work_items.list(organization_id="<id>")

    # Handle response
    print(res)

```
<!-- End Server Selection [server] -->

<!-- Start Custom HTTP Client [http-client] -->
## Custom HTTP Client

The Python SDK makes API calls using the [httpx](https://www.python-httpx.org/) HTTP library.  In order to provide a convenient way to configure timeouts, cookies, proxies, custom headers, and other low-level configuration, you can initialize the SDK client with your own HTTP client instance.
Depending on whether you are using the sync or async version of the SDK, you can pass an instance of `HttpClient` or `AsyncHttpClient` respectively, which are Protocol's ensuring that the client has the necessary methods to make API calls.
This allows you to wrap the client with your own custom logic, such as adding custom headers, logging, or error handling, or you can just pass an instance of `httpx.Client` or `httpx.AsyncClient` directly.

For example, you could specify a header for every request that this sdk makes as follows:
```python
from dbrsdk import Dbrsdk
import httpx

http_client = httpx.Client(headers={"x-custom-header": "someValue"})
s = Dbrsdk(client=http_client)
```

or you could wrap the client with your own custom logic:
```python
from dbrsdk import Dbrsdk
from dbrsdk.httpclient import AsyncHttpClient
import httpx

class CustomClient(AsyncHttpClient):
    client: AsyncHttpClient

    def __init__(self, client: AsyncHttpClient):
        self.client = client

    async def send(
        self,
        request: httpx.Request,
        *,
        stream: bool = False,
        auth: Union[
            httpx._types.AuthTypes, httpx._client.UseClientDefault, None
        ] = httpx.USE_CLIENT_DEFAULT,
        follow_redirects: Union[
            bool, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        request.headers["Client-Level-Header"] = "added by client"

        return await self.client.send(
            request, stream=stream, auth=auth, follow_redirects=follow_redirects
        )

    def build_request(
        self,
        method: str,
        url: httpx._types.URLTypes,
        *,
        content: Optional[httpx._types.RequestContent] = None,
        data: Optional[httpx._types.RequestData] = None,
        files: Optional[httpx._types.RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[httpx._types.QueryParamTypes] = None,
        headers: Optional[httpx._types.HeaderTypes] = None,
        cookies: Optional[httpx._types.CookieTypes] = None,
        timeout: Union[
            httpx._types.TimeoutTypes, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
        extensions: Optional[httpx._types.RequestExtensions] = None,
    ) -> httpx.Request:
        return self.client.build_request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            extensions=extensions,
        )

s = Dbrsdk(async_client=CustomClient(httpx.AsyncClient()))
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Resource Management [resource-management] -->
## Resource Management

The `Dbrsdk` class implements the context manager protocol and registers a finalizer function to close the underlying sync and async HTTPX clients it uses under the hood. This will close HTTP connections, release memory and free up other resources held by the SDK. In short-lived Python programs and notebooks that make a few SDK method calls, resource management may not be a concern. However, in longer-lived programs, it is beneficial to create a single SDK instance via a [context manager][context-manager] and reuse it across the application.

[context-manager]: https://docs.python.org/3/reference/datamodel.html#context-managers

```python
from dbrsdk import Dbrsdk
import os
def main():

    with Dbrsdk(
        http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
    ) as d_client:
        # Rest of application here...


# Or when using async:
async def amain():

    async with Dbrsdk(
        http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
    ) as d_client:
        # Rest of application here...
```
<!-- End Resource Management [resource-management] -->

<!-- Start Debugging [debug] -->
## Debugging

You can setup your SDK to emit debug logs for SDK requests and responses.

You can pass your own logger class directly into your SDK.
```python
from dbrsdk import Dbrsdk
import logging

logging.basicConfig(level=logging.DEBUG)
s = Dbrsdk(debug_logger=logging.getLogger("dbrsdk"))
```

You can also enable a default debug logger by setting an environment variable `DBRSDK_DEBUG` to true.
<!-- End Debugging [debug] -->

<!-- Placeholder for Future Speakeasy SDK Sections -->

# Development

## Maturity

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning usage
to a specific package version. This way, you can install the same version each time without breaking changes unless you are intentionally
looking for the latest version.

## Contributions

While we value open-source contributions to this SDK, this library is generated programmatically. Any manual changes added to internal files will be overwritten on the next generation. 
We look forward to hearing your feedback. Feel free to open a PR or an issue with a proof of concept and we'll do our best to include it in a future release. 

### SDK Created by [Speakeasy](https://www.speakeasy.com/?utm_source=dbrsdk&utm_campaign=python)
