# Implement your grammar here in the `grammar` variable.
# You may define additional functions, e.g. for generators.
# You may not import any other modules written by yourself.
# That is, your entire implementation must be in `grammar.py`
# and `fuzzer.py`.

import string
from fuzzingbook.GeneratorGrammarFuzzer import opts
from metadata import MetaData

md = MetaData()

grammar = {
    "<start>": [("<stmt>", opts(pre=lambda: md.pre_start(), post=lambda *args: md.post_start(args)))],
    "<stmt>": ["<create_table>"],
    # general_definitions
    # create_table_grammar
}

general_definitions = {
    "<table_name>":[("<string>", opts(pre=lambda: md.hijack_table_name(0.5)))],
    "<string>": ["<letter>", "<letter><string>"],
    "<letter>": [c for c in string.ascii_lowercase[:15]],

    "<if_not_exist>": [("", opts(prob=0.98)), "IF NOT EXISTS "],
    
    "<signed_number>": ["<sign><numeric_literal>"],
    "<sign>": ["+", "-", ""],
    "<numeric_literal>": ["<digit><numeric_literal>", "<digit>"],
    "<digit>": [d for d in string.digits],
}
grammar.update(general_definitions)

create_table_grammar = {
    "<create_table>" : [("CREATE <temp>TABLE <table_name> <if_not_exist>(<table_columns_def>);", opts(post=lambda *args: md.add_created_table(*args)))],
    "<temp>": [ ("", opts(prob=0.95)), "TEMPORARY ", "TEMP "],
    "<table_columns_def>": [("<table_columns_def>,<table_column_def>", opts(prob=0.95)), "<table_column_def>"],
    "<table_column_def>": [("<string> <column_type> <column_constraint>", opts(post=lambda *args: md.add_column(args)))],
    "<column_type>": ["INT", "INTEGER", "TINYINT", "SMALLINT", "MEDIUMINT", "BIGINT", "UNSIGNED", "BIGINT", "INT2", "INT8", "CHARACTER(<signed_number>)", "VARCHAR(<signed_number>)", "VARYING", "CHARACTER(<signed_number>)", "NCHAR(<signed_number>)", "NATIVE", "CHARACTER(<signed_number>)", "NVARCHAR(<signed_number>)", "TEXT", "CLOB", "BLOB", "REAL", "DOUBLE", "DOUBLE", "PRECISION", "FLOAT", "NUMERIC", "DECIMAL(<signed_number>, <signed_number>)", "BOOLEAN", "DATE", "DATETIME"],
    # "<column_modifier>": [("", opts(prob=0.95)), "(<signed_number>)", "(<signed_number>,<signed_number>)"]
    "<column_constraint>": ["", "PRIMARY KEY", "NOT NULL", "UNIQUE"],
}

grammar.update(create_table_grammar)