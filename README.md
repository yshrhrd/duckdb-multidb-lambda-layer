# duckdb-multidb-lambda-layer

AWS Lambda Layer (Python) containing `duckdb` and these extensions:

| Extension | Source | Purpose |
|---|---|---|
| `mssql` | community | SQL Server (native TDS) |
| `postgres` | core | PostgreSQL |
| `mysql` | core | MySQL / MariaDB |
| `httpfs` | core | HTTP(S) / S3 file access |
| `aws` | core | AWS credential chain (Lambda IAM role) for S3 |

No ODBC driver, libpq, or libmysqlclient is needed. A SQL Server-only variant is available in [duckdb-mssql-lambda-layer](https://github.com/yshrhrd/duckdb-mssql-lambda-layer).

## Build

```bash
docker buildx build --load --platform linux/amd64 \
  --build-arg PYTHON_VERSION=3.12 -t duckdb-multidb .
docker run --rm -v "$(pwd):/out" duckdb-multidb cp /layer.zip /out/duckdb-multidb-python-3.12-x86_64.zip
```

- `--platform linux/arm64` for arm64 layers.
- `PYTHON_VERSION`: 3.12 – 3.15 (3.15 is experimental until duckdb publishes cp315 wheels and the SAM build image exists; Amazon Linux 2023 based runtimes; 3.11 is Amazon Linux 2 and unsupported by recent duckdb wheels).
- Optional `--build-arg DUCKDB_VERSION=1.4.4` to pin duckdb.

## Release

The GitHub Actions workflow builds all Python/architecture combinations and runs tests.

- Push a tag to build and publish a GitHub Release with all zips attached:

  ```bash
  git tag v1.0.0 && git push origin v1.0.0
  ```

- `workflow_dispatch` (manual run) builds and tests only; zips are kept as workflow artifacts. Run it from a tag ref in the Actions UI to also publish a release.

## Layer contents

```text
/opt/python/                 duckdb Python package
/opt/duckdb_extensions/      pre-installed extensions (offline)
```

## Usage

Lambda's filesystem is read-only except `/tmp`, so point DuckDB at the bundled extensions.

```python
import duckdb

con = duckdb.connect(config={
    "extension_directory": "/opt/duckdb_extensions",
    "home_directory": "/tmp",
    "autoinstall_known_extensions": False,
    "autoload_known_extensions": False,
})
for ext in ("mssql", "postgres", "mysql", "httpfs", "aws"):
    con.execute(f"LOAD {ext}")

con.execute("ATTACH 'host=... user=... password=... dbname=...' AS pg (TYPE postgres)")
con.execute("ATTACH 'host=... user=... password=... database=...' AS my (TYPE mysql)")
con.execute("ATTACH 'Server=host,1433;Database=db;User Id=u;Password=p;Encrypt=yes' AS ms (TYPE mssql)")
con.execute("CREATE SECRET (TYPE s3, PROVIDER credential_chain)")  # uses the Lambda execution role
print(con.execute("SELECT * FROM read_csv('s3://your-bucket/data.csv') LIMIT 5").fetchall())
```

Extensions are built for a specific DuckDB version; rebuild the layer when upgrading duckdb.

## Security

Pin versions, review builds, publish into your own AWS account, and keep credentials in AWS Secrets Manager.

## License

Licensed under the [Apache License 2.0](LICENSE). The build definitions are adapted from [yshrhrd/pyodbc-mssql-lambda-layer-gconv-extra](https://github.com/yshrhrd/pyodbc-mssql-lambda-layer-gconv-extra), which is based on [davidcomerford/pyodbc-mssql-lambda-layer](https://github.com/davidcomerford/pyodbc-mssql-lambda-layer); see [NOTICE](NOTICE). The resulting layer bundles `duckdb` and the extensions above, which are subject to their own licenses.
