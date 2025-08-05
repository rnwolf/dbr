# DBR

A Drum Buffer and Rope Application based on ToC approaches shared by [Peter Thorby](https://www.linkedin.com/in/peter-thorby-3379169/) from [ViAGO International Limited](https://viagointernational.com/) at the [TOCICO](https://www.tocico.org/) conference in Germany 2024.


# Devlopement guides

## Use Google Gemini

Open Terminal and navigate to `~/worksapce/dbr` directory

Open Gemini-cli and specify that AI is allowed to run commands in the backend and frontend directories with

`gemini --include-directories "C:\Users\rnwol\workspace\dbr\dbr_mvp\backend" "C:\Users\rnwol\workspace\dbr\dbr_mvp\frontend"`


## Use marked tests to focus AI on specific functionlaity to work on

Open Terminal and navigate to `~/worksapce/dbrdbr_mvp/frontend` directory


```
uv sync
uv run pytest .\tests_bdd\step_definitions\test_collection_steps.py -m investigate
```

Capture test output to log file with:
--log-file=/path/to/log/file.
Specify the logging level for the log file by passing --log-file-level=INFO


### For a given set BDD scrnarios

`cd .\dbr_mvp\frontend\; uv run pytest tests_bdd/step_definitions/test_collection_steps.py > tmp-pytest-output.txt`
