# LoginResponse

Login response model


## Fields

| Field              | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `access_token`     | *str*              | :heavy_check_mark: | JWT access token   |
| `token_type`       | *Optional[str]*    | :heavy_minus_sign: | Token type         |
| `user`             | Dict[str, *Any*]   | :heavy_check_mark: | User information   |