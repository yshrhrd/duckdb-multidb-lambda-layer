import sys

sys.path.append('/opt/python')

EXT_DIR = '/opt/duckdb_extensions'
EXTENSIONS = ['mssql', 'postgres', 'mysql', 'httpfs', 'aws']


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
    # duckdb reports some extensions under their internal names
    loaded = {
        n
        for name, aliases in con.execute(
            'SELECT extension_name, aliases FROM duckdb_extensions() WHERE loaded'
        ).fetchall()
        for n in [name, *aliases]
    }
    assert set(EXTENSIONS) <= loaded
