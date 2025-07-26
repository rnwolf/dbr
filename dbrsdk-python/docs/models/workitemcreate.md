# WorkItemCreate


## Fields

| Field                                              | Type                                               | Required                                           | Description                                        |
| -------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------- |
| `organization_id`                                  | *str*                                              | :heavy_check_mark:                                 | Organization ID                                    |
| `collection_id`                                    | *OptionalNullable[str]*                            | :heavy_minus_sign:                                 | Collection ID (optional)                           |
| `title`                                            | *str*                                              | :heavy_check_mark:                                 | Work item title                                    |
| `description`                                      | *OptionalNullable[str]*                            | :heavy_minus_sign:                                 | Work item description                              |
| `status`                                           | *OptionalNullable[str]*                            | :heavy_minus_sign:                                 | Work item status                                   |
| `priority`                                         | *OptionalNullable[str]*                            | :heavy_minus_sign:                                 | Work item priority                                 |
| `estimated_total_hours`                            | *float*                                            | :heavy_check_mark:                                 | Estimated total hours                              |
| `ccr_hours_required`                               | Dict[str, *float*]                                 | :heavy_minus_sign:                                 | CCR hours required                                 |
| `estimated_sales_price`                            | *OptionalNullable[float]*                          | :heavy_minus_sign:                                 | Estimated sales price                              |
| `estimated_variable_cost`                          | *OptionalNullable[float]*                          | :heavy_minus_sign:                                 | Estimated variable cost                            |
| `tasks`                                            | List[[models.TaskCreate](../models/taskcreate.md)] | :heavy_minus_sign:                                 | Initial tasks                                      |
| `responsible_user_id`                              | *OptionalNullable[str]*                            | :heavy_minus_sign:                                 | Responsible user ID                                |
| `url`                                              | *OptionalNullable[str]*                            | :heavy_minus_sign:                                 | External URL                                       |