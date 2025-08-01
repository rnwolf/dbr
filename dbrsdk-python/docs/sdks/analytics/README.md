# Analytics
(*schedules.analytics*)

## Overview

### Available Operations

* [get](#get) - Get Schedule Analytics

## get

Get analytics for a specific schedule

### Example Usage

<!-- UsageSnippet language="python" operationID="get_schedule_analytics_api_v1_schedules__schedule_id__analytics_get" method="get" path="/api/v1/schedules/{schedule_id}/analytics" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.schedules.analytics.get(schedule_id="<id>", organization_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `schedule_id`                                                       | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID to scope the request                                |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.ScheduleAnalytics](../../models/scheduleanalytics.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.BadRequestError     | 400                        | application/json           |
| errors.UnauthorizedError   | 401, 403                   | application/json           |
| errors.NotFoundError       | 404                        | application/json           |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.RateLimitedError    | 429                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |