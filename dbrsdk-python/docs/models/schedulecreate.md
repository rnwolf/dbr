# ScheduleCreate


## Fields

| Field                       | Type                        | Required                    | Description                 |
| --------------------------- | --------------------------- | --------------------------- | --------------------------- |
| `organization_id`           | *str*                       | :heavy_check_mark:          | Organization ID             |
| `board_config_id`           | *str*                       | :heavy_check_mark:          | Board configuration ID      |
| `work_item_ids`             | List[*str*]                 | :heavy_check_mark:          | List of work item IDs       |
| `timezone`                  | *Optional[str]*             | :heavy_minus_sign:          | Timezone for schedule dates |