import sys

sys.path.append('/opt/python')

EXT_DIR = '/opt/duckdb_extensions'
EXTENSIONS = ['mssql', 'postgres', 'mysql', 'httpfs']


def _connect():
    import duckdb
    return duckdb.connect(config={
        'extension_directory': EXT_DIR,
        'autoinstall_known_extensions': False,
        'autoload_known_extensions': False,
    })


def test_duckdb_import():
    import duckdb
    assert duckdb.__version__


def test_extensions_load_offline():
    con = _connect()
    for ext in EXTENSIONS:
        con.execute(f'LOAD {ext}')
    loaded = {
        r[0] for r in con.execute(
            'SELECT extension_name FROM duckdb_extensions() WHERE loaded'
        ).fetchall()
    }
    assert set(EXTENSIONS) <= loaded
