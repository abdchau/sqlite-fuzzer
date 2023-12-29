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
    "<stmt>": [
        "<create_table>",
        ("<drop_table>", opts(prob=0.1)),
        ("<insert_stmt>", opts(prob=0.25)),
        ("<select_stmt>", opts(prob=0.15)),
        ("<alter_table>", opts(prob=0.15)),
        ("<delete_stmt>", opts(prob=0.05)),
        ("<explain_plan>", opts(prob=0.05)),
        ("<create_view>", opts(prob=0.05)),
    ],
    # general_definitions
    # create_table_grammar
}

general_definitions = {
    "<existing_table_name>": [("<table_name>", opts(pre=lambda: md.get_existing_table()))],

    "<table_name>": [("<string>", opts(post=lambda *args: md.post_table_name(args)))],
    "<string>": ["<letter>", "<letter><string>"],
    "<letter>": [c for c in string.ascii_lowercase[:15]],

    "<if_exist>": [("", opts(prob=0.98)), "IF EXISTS "],
    "<if_not_exist>": [("", opts(prob=0.98)), "IF NOT EXISTS "],
    
    "<limit_clause>": ["", "LIMIT <signed_number>"],
    # "<order_by_clause>": ["", "ORDER BY <asc_desc>"],
    # "<asc_desc>": ["ASC", "DESC"],

    "<signed_number>": ["<sign><numeric_literal>"],
    "<sign>": ["+", "-", ("", opts(prob=0.95))],
    "<numeric_literal>": ["<digit><numeric_literal>", "<digit>"],
    "<digit>": [d for d in string.digits],
}
grammar.update(general_definitions)

create_table_grammar = {
    "<create_table>" : [("CREATE <temp>TABLE <if_not_exist><create_table_name>(<table_columns_def>);", opts(post=lambda *args: md.add_created_table(*args)))],
    "<create_table_name>": [("<table_name>", opts(pre=lambda: md.hijack_table_name(0.05, 0.3)))],
    "<temp>": [ ("", opts(prob=0.9995)), "TEMPORARY ", "TEMP "],
    "<table_columns_def>": [("<table_columns_def>,<table_column_def>", opts(prob=0.95)), "<table_column_def>"],
    "<table_column_def>": [("<string> <column_type> <column_constraint>", opts(post=lambda *args: md.add_column(args)))],
    "<column_type>": ["INT", "INTEGER", "TINYINT", "SMALLINT", "MEDIUMINT", "BIGINT", "UNSIGNED", "BIGINT", "INT2", "INT8", "CHARACTER(<signed_number>)", "VARCHAR(<signed_number>)", "VARYING", "CHARACTER(<signed_number>)", "NCHAR(<signed_number>)", "NATIVE", "CHARACTER(<signed_number>)", "NVARCHAR(<signed_number>)", "TEXT", "CLOB", "BLOB", "REAL", "DOUBLE", "PRECISION", "FLOAT", "NUMERIC", "DECIMAL(<signed_number>, <signed_number>)", "BOOLEAN", "DATE", "DATETIME"],
    # "<column_modifier>": [("", opts(prob=0.95)), "(<signed_number>)", "(<signed_number>,<signed_number>)"]
    "<column_constraint>": ["", "PRIMARY KEY", "NOT NULL", "UNIQUE"],
}
grammar.update(create_table_grammar)

drop_table_grammar = {
    "<drop_table>": ["DROP TABLE <if_exist> <drop_table_name>;"],
    "<drop_table_name>": [("<table_name>", opts(pre=lambda: md.get_delete_table_name(0.999)))],
}
grammar.update(drop_table_grammar)

insert_stmt_grammar = {
    "<insert_stmt>": [("INSERT <insert_failure> INTO <table_and_columns> VALUES(<column_values>)", opts(order=[1,2,3]))],
    "<insert_failure>": [("", opts(prob=0.95)), "OR <failure>"],
    "<failure>": ["ABORT", "FAIL", "IGNORE", "REPLACE", "ROLLBACK"],
    "<table_and_columns>": [("this string is never used", opts(pre=lambda: md.construct_insert_table_cols()))],
    "<column_values>": [("this string is never used", opts(pre=lambda: md.get_values_for_cols()))],
}
grammar.update(insert_stmt_grammar)

select_stmt_grammar = {
    "<select_stmt>": [("SELECT <select_columns> FROM <select_table_name> <limit_clause>;", opts(order=[1,2,3]))],
    "<select_columns>": [("columns; string not used", opts(pre=lambda: md.get_select_columns()))],
    "<select_table_name>": [("<table_name>",opts(pre=lambda: md.get_select_table()))],
}
grammar.update(select_stmt_grammar)

alter_table_grammar = {
    "<alter_table>": [("ALTER TABLE <existing_table_name> <alter_action>;", opts(order=[1,2]))],
    "<alter_action>": ["<rename_table>", "<rename_column>", "<add_column>", "<drop_column>"],
    "<rename_table>": ["RENAME TO <rename_table_name>"],
    "<rename_table_name>": [("<table_name>", opts(post=lambda *args: md.post_rename_table(args[0])))],
    "<rename_column>": [("RENAME COLUMN <string> TO <table_name>", opts(post=lambda *args: md.rename_column_name(args[1])))],
    "<add_column>": ["ADD <just_column> <table_column_def>"],
    "<drop_column>": ["DROP <just_column> <drop_col_name>"],
    "<drop_col_name>": [("column; string not used", opts(pre=lambda:md.drop_col_name()))],
    "<just_column>": ["", "COLUMN"],
}
grammar.update(alter_table_grammar)

delete_stmt_grammar = {
    "<delete_stmt>": ["DELETE FROM <existing_table_name>;"],
}
grammar.update(delete_stmt_grammar)

explain_plan_grammar = {
    "<explain_plan>": ["EXPLAIN <query_plan> <stmt_to_explain>"],
    "<query_plan>": ["", "QUERY PLAN"],
    "<stmt_to_explain>": ["<create_table>", "<drop_table>", "<insert_stmt>", "<select_stmt>", "<alter_table>", "<delete_stmt>"]
}
grammar.update(explain_plan_grammar)

create_view_grammar = {
    "<create_view>": ["CREATE VIEW <if_not_exist> <table_name> AS <select_stmt>"]
}
grammar.update(create_view_grammar)