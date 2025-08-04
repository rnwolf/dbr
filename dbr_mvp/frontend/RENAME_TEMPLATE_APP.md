# Renaming the Application

This document details the steps required to rename the application from `tk-template` to a new name. In this example, we will use `frontend` as the new name.

## 1. Update `pyproject.toml`

The first step is to update the project name in the `pyproject.toml` file.

-   **Open** `pyproject.toml`
-   **Find** the line `name = "tk-template"`
-   **Change** it to `name = "frontend"`

## 2. Rename the Source Directory

Next, rename the main application directory within the `src` folder.

```bash
mv src/tk_template src/frontend
```

## 3. Update Import Statements

You can use the following command to find and replace all instances of `tk_template` with `frontend` in both the `src` and `tests` directories:

```bash
find src tests -type f -name "*.py" -exec sed -i 's/tk_template/frontend/g' {} +
```

Alternatively, for PowerShell users:

```powershell
Get-ChildItem -Path src, tests -Recurse -Include *.py | ForEach-Object {
    (Get-Content $_.FullName) -replace 'tk_template', 'frontend' | Set-Content $_.FullName
}
```

This command will update all import statements in the Python files.

## 4. Fix Test Import Paths (Critical)

**Important**: The template had incorrect test imports that need to be fixed. When renaming from `frontend` to your new app name, ensure test files use the correct module paths:

```bash
# If renaming from 'app' to 'frontend', update test @patch decorators
find tests -name "*.py" -exec sed -i 's/"app\./"frontend\./g' {} +
```

For PowerShell users:

```powershell
# Update test patch decorators to use correct module paths
Get-ChildItem -Path tests -Recurse -Include *.py | ForEach-Object {
    (Get-Content $_.FullName) -replace '"app\.', '"frontend.' | Set-Content $_.FullName
}
```

**Note**: Test files use `@patch("module.path.Class")` decorators that must reference the actual module structure, not non-existent `app.*` paths.


## 5. Verify Changes with Tests and Linter

After making the changes, run the test suite to ensure all imports work correctly:

```bash
# Run tests to verify import fixes
python -m pytest tests/ -v
```

## 6. Verify Changes with the Linter

After making the changes, run the linter to ensure that everything is correct and to fix any remaining issues.

First, run the linter with the `--fix` option to automatically correct any errors:

```bash
uv run ruff check . --fix
```

Then, run the linter again to confirm that all issues have been resolved:

```bash
uv run ruff check .
```

After completing these steps, the application will be successfully renamed.
