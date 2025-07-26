# WorkItemResponse


## Fields

| Field                                                  | Type                                                   | Required                                               | Description                                            |
| ------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------ |
| `id`                                                   | *str*                                                  | :heavy_check_mark:                                     | N/A                                                    |
| `organization_id`                                      | *str*                                                  | :heavy_check_mark:                                     | N/A                                                    |
| `collection_id`                                        | *Nullable[str]*                                        | :heavy_check_mark:                                     | N/A                                                    |
| `title`                                                | *str*                                                  | :heavy_check_mark:                                     | N/A                                                    |
| `description`                                          | *Nullable[str]*                                        | :heavy_check_mark:                                     | N/A                                                    |
| `status`                                               | *str*                                                  | :heavy_check_mark:                                     | N/A                                                    |
| `priority`                                             | *str*                                                  | :heavy_check_mark:                                     | N/A                                                    |
| `estimated_total_hours`                                | *float*                                                | :heavy_check_mark:                                     | N/A                                                    |
| `ccr_hours_required`                                   | Dict[str, *float*]                                     | :heavy_check_mark:                                     | N/A                                                    |
| `estimated_sales_price`                                | *Nullable[float]*                                      | :heavy_check_mark:                                     | N/A                                                    |
| `estimated_variable_cost`                              | *Nullable[float]*                                      | :heavy_check_mark:                                     | N/A                                                    |
| `throughput`                                           | *float*                                                | :heavy_check_mark:                                     | N/A                                                    |
| `tasks`                                                | List[[models.TaskResponse](../models/taskresponse.md)] | :heavy_check_mark:                                     | N/A                                                    |
| `progress_percentage`                                  | *float*                                                | :heavy_check_mark:                                     | N/A                                                    |
| `responsible_user_id`                                  | *Nullable[str]*                                        | :heavy_check_mark:                                     | N/A                                                    |
| `url`                                                  | *Nullable[str]*                                        | :heavy_check_mark:                                     | N/A                                                    |
| `created_date`                                         | *str*                                                  | :heavy_check_mark:                                     | N/A                                                    |
| `updated_date`                                         | *str*                                                  | :heavy_check_mark:                                     | N/A                                                    |