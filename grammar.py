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
        ("<drop_table>", opts(prob=0.10)),
        ("<insert_stmt>", opts(prob=0.20)),
        ("<select_stmt>", opts(prob=0.125)),
        ("<alter_table>", opts(prob=0.125)),
        ("<delete_stmt>", opts(prob=0.05)),
        ("<explain_plan>", opts(prob=0.05, pre=lambda: md.pre_explain_plan())),
        ("<create_view>", opts(prob=0.003, post=lambda *args: md.post_create_view(args))),
        ("<drop_view>", opts(prob=0.001)),
        ("<create_index>", opts(prob=0.02)),
        ("<drop_index>", opts(prob=0.02)),
        ("<create_savepoint>", opts(prob=0.01)),
        ("<release_savepoint>", opts(prob=0.005)),
        ("<reindex_stmt>", opts(prob=0.005)),
        ("<vacuum_stmt>", opts(prob=0.002)),
        ("<update_stmt>", opts(prob=0.10)),
        ("<create_trigger>", opts(prob=0.01)),
        ("<drop_trigger>", opts(prob=0.005)),
    ],
    "<vacuum_stmt>": ["VACUUM main;"]
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
    "<column_constraint>": [("", opts(prob=0.85)), "PRIMARY KEY", ("NOT NULL", opts(prob=0.05)), ("UNIQUE", opts(prob=0.05))],
}
grammar.update(create_table_grammar)

drop_table_grammar = {
    "<drop_table>": ["DROP TABLE <if_exist> <drop_table_name>;"],
    "<drop_table_name>": [("<table_name>", opts(pre=lambda: md.get_delete_table_name(0.999)))],
}
grammar.update(drop_table_grammar)

insert_stmt_grammar = {
    "<insert_stmt>": [("INSERT <insert_failure> INTO <table_and_columns> VALUES(<column_values>);", opts(order=[1,2,3]))],
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
    "<alter_table>": ["<alter_table_1>", ("<alter_table_1><drop_table_views>", opts(order=[1,2],prob=0.98))],
    "<alter_table_1>": [("ALTER TABLE <existing_table_name> <alter_action>;", opts(order=[1,2]))],

    "<alter_action>": ["<rename_table>", "<rename_column>", "<add_column>", "<drop_column>"],
    "<rename_table>": ["RENAME TO <rename_table_name>"],
    "<rename_table_name>": [("<table_name>", opts(post=lambda *args: md.post_rename_table(args[0])))],
    "<rename_column>": [("RENAME COLUMN <string> TO <table_name>", opts(post=lambda *args: md.rename_column_name(args[1])))],
    "<add_column>": [("ADD <just_column> <alter_col_def>")],
    
    "<alter_col_def>": [("<table_column_def>", opts(post=lambda *args: md.post_add_column(*args)))],
    "<drop_column>": ["DROP <just_column> <drop_col_name>"],
    "<drop_col_name>": [("column; string not used", opts(pre=lambda:md.drop_col_name()))],
    "<just_column>": ["", "COLUMN"],

    "<drop_table_views>": [("string; not used", opts(pre=lambda: md.drop_table_views()))],
}
grammar.update(alter_table_grammar)

delete_stmt_grammar = {
    "<delete_stmt>": ["DELETE FROM <existing_table_name>;"],
}
grammar.update(delete_stmt_grammar)

explain_plan_grammar = {
    "<explain_plan>": ["EXPLAIN <query_plan> <stmt_to_explain>"],
    "<query_plan>": ["", "QUERY PLAN"],
    "<stmt_to_explain>": ["<create_table>", "<drop_table>", "<insert_stmt>", "<select_stmt>", "<alter_table>", "<delete_stmt>", "<create_view>", "<drop_view>", "<create_index>", "<drop_index>"],
    
}
grammar.update(explain_plan_grammar)

create_view_grammar = {
    "<create_view>": ["CREATE VIEW <if_not_exist> <view_name> AS <select_stmt>;"],
    "<view_name>": [("<string>", opts(post=lambda *args: md.post_view_name(*args)))],
}
grammar.update(create_view_grammar)

drop_view_grammar = {
    "<drop_view>": ["DROP VIEW <if_exist> <existing_view_name>;"],
    "<existing_view_name>": [("<view_name>", opts(pre=lambda: md.get_drop_view()))],
}
grammar.update(drop_view_grammar)

create_index_grammar = {
    "<create_index>": [("CREATE <unique> INDEX <if_not_exist> <index_name> ON <existing_table_name>(<indexed_columns>);", opts(order=[1,2,3,4,5]))],
    "<unique>": [("", opts(prob=0.9)), "UNIQUE"],
    "<index_name>": [("<string>", opts(post=lambda *args: md.post_index_name(*args)))],
    "<indexed_columns>": [("<indexed_column>", opts(prob=0.9)), "<indexed_column>,<indexed_columns>"],
    "<indexed_column>": [("string; unused", opts(pre=lambda: md.get_column_to_index()))]
}
grammar.update(create_index_grammar)

drop_index_grammar = {
    "<drop_index>": ["DROP INDEX <if_exist> <existing_index_name>;"],
    "<existing_index_name>": [("<index_name>", opts(pre=lambda: md.get_drop_index()))],
}
grammar.update(drop_index_grammar)

reindex_stmt_grammar = {
    "<reindex_stmt>": ["REINDEX <reindex_name>;"],
    "<reindex_name>": ["<existing_table_name>", "<existing_index_name>"],
}
grammar.update(reindex_stmt_grammar)

save_point_grammar = {
    "<create_savepoint>": ["SAVEPOINT <savepoint_name>;"],
    "<savepoint_name>": [("<string>", opts(post=lambda *args: md.post_savepoint_name(*args)))],

    "<release_savepoint>": ["RELEASE <savepoint> <existing_savepoint_name>;"],
    "<savepoint>": ["", "SAVEPOINT"],
    "<existing_savepoint_name>": [("<savepoint_name>", opts(pre=lambda: md.get_release_savepoint()))],
}
grammar.update(save_point_grammar)

update_stmt_grammar = {
    "<update_stmt>": [("UPDATE <insert_failure> <existing_table_name> SET <set_columns>;", opts(order=[1,2,3]))],
    "<set_columns>": [("<set_column>", opts(prob=0.95)), "<set_column>, <set_column>"],
    "<set_column>": [("string; not used", opts(pre=lambda: md.get_set_column()))]
}
grammar.update(update_stmt_grammar)

create_trigger_grammar = {
    "<create_trigger>":  # existing_table_name MUST expand first
        [("CREATE TRIGGER <if_not_exist> <trigger_name> <when_trigger> <trigger_operation> ON <existing_table_name> " +
          "<for_each_row> BEGIN <crud_stmts> END;",
          opts(order=[2,3,4,5,1,6,7]))],
    "<trigger_name>": [("<string>", opts(post=lambda *args: md.post_trigger_name(*args)))],
    "<when_trigger>": ["", "BEFORE", "AFTER"],#, "INSTEAD OF"],
    "<trigger_operation>": ["DELETE", "INSERT", "UPDATE <of_column>"],
    "<of_column>": ["", "OF <of_col_name>"],
    "<of_col_name>": [("string; not used", opts(pre=lambda: md.get_of_col_name()))],
    "<for_each_row>": ["", "FOR EACH ROW"],
    "<crud_stmts>": ["<crud_stmt>", "<crud_stmt><crud_stmts>"],
    "<crud_stmt>": ["<insert_stmt>", "<select_stmt>", "<delete_stmt>", "<update_stmt>"]
}
grammar.update(create_trigger_grammar)

drop_trigger_grammar = {
    "<drop_trigger>": ["DROP TRIGGER <if_exist> <existing_trigger_name>;"],
    "<existing_trigger_name>": [("<table_name>", opts(pre=lambda: md.get_drop_trigger()))],
}
grammar.update(drop_trigger_grammar)
