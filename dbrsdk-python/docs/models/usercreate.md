# UserCreate

Schema for creating a new user


## Fields

| Field              | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `organization_id`  | *str*              | :heavy_check_mark: | Organization ID    |
| `username`         | *str*              | :heavy_check_mark: | Username           |
| `email`            | *str*              | :heavy_check_mark: | Email address      |
| `display_name`     | *str*              | :heavy_check_mark: | Display name       |
| `password`         | *str*              | :heavy_check_mark: | Password           |
| `system_role_id`   | *str*              | :heavy_check_mark: | System role ID     |
| `active_status`    | *Optional[bool]*   | :heavy_minus_sign: | Active status      |