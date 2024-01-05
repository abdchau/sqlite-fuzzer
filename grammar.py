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
        ("<insert_stmt>", opts(prob=0.15)),
        ("<select_stmt>", opts(prob=0.175)),
        ("<alter_table>", opts(prob=0.10)),
        ("<delete_stmt>", opts(prob=0.05)),
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
        ("<comment>", opts(prob=0.001)),
        ("<analyze_stmt>", opts(prob=0.003)),
        ("<explain_plan>", opts(prob=0.07, pre=lambda: md.pre_explain_plan())),
        ("<pragma_stmt>", opts(prob=0.08)),
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

    "<literal_value>":["<numeric_literal>", "<string_literal>", "<blob_literal>", "NULL", "TRUE",
                       "FALSE", "CURRENT_TIME", "CURRENT_DATE", "CURRENT_TIMESTAMP"],

    "<signed_number>": ["<sign><numeric_literal>"],
    "<sign>": ["+", "-", ("", opts(prob=0.95))],
    "<numeric_literal>": ["<digit><numeric_literal>", "<digit>"],
    "<digit>": [d for d in string.digits],

    "<blob_literal>": ["X<numeric_literal>"],
    "<string_literal>": ["'<string>'"],

    "<is_null>": ["", "ISNULL"],
    "<notnull>": ["", "NOTNULL"],
    "<not>": ["", "NOT"],
    "<null>": ["", "NULL"],
    # "<is>": ["", "IS"],
    "<distinct>": ["", "DISTINCT"],
    "<distinct_from>": ["", "DISTINCT FROM"],

    "<binary_operator>": ["+", "-", "*", "/", "%"]
}
grammar.update(general_definitions)

expression_grammar = {
    "<expr>": ["<expression> <expr_suffix>"],
    "<expression>": ["<literal_value>", "(<expressions>)", "<expr_table_name><expr_column_name>", "<expr_binary_op>",
                     "<expr_not_distinct>", "<expr_not_between>"],
    "<expressions>": ["<expr>", "<expr>,<expressions>"],

    "<expr_binary_op>": ["<expr> <binary_operator> <expr>"],
    "<expr_not_distinct>": ["<expr> IS <not> <distinct_from> <expr>"],
    "<expr_not_between>": ["<expr> <not> BETWEEN <expr> AND <expr>"],

    "<expr_suffix>": ["<is_null>", "<notnull>", "<not> <null>"],
    "<expr_table_name>": ["", "<existing_table_name>."],
    "<expr_column_name>": ["", "<existing_column_name>"],
    "<existing_column_name>": [("<string>", opts(pre=lambda: md.get_existing_column()))]
}
grammar.update(expression_grammar)

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
    "<table_and_columns>": [("<string>", opts(pre=lambda: md.construct_insert_table_cols()))],
    "<column_values>": [("<string>", opts(pre=lambda: md.get_values_for_cols()))],
}
grammar.update(insert_stmt_grammar)

select_stmt_grammar = {
    "<select_stmt>": [("<select_constant>;", opts(prob=0.001)), ("<select_from_table>;", opts(prob=0.5)), "<select_from_table> <compound_operator> <select_stmt>"],
    "<select_from_table>": [("SELECT <distinct> <select_columns> FROM <select_table_name> <where_clause> <limit_clause>", opts(order=[1,2,3,4,5]))],
    "<compound_operator>": ["UNION", "UNION ALL", "INTERSECT", "EXCEPT"],
    "<select_columns>": [("<string>", opts(pre=lambda: md.get_select_columns()))],
    "<select_table_name>": [("<table_name>",opts(pre=lambda: md.get_select_table()))],
    "<where_clause>": [("", opts(prob=0.8)), "WHERE <expr>"],

    "<select_constant>": ["SELECT <math_expr>"],
    "<math_expr>": ["<func_one>"],# "<func_two>", ("pi()", opts(prob=0.001))],
    "<func_one>": ["<func_one_name>(<signed_number>)"],
    # "<func_two>": ["<func_two_name>(<signed_number>,<signed_number>)"],
    "<func_one_name>": ["abs"], #"acos", "acosh", "asin", "asinh", "atan", "atanh", "ceil", "ceiling", "cos", "cosh", "degrees", "exp", "floor", "ln", "log", "log10", "log2", "radians", "sin", "sinh", "sqrt", "tan", "tanh", "trunc"],
    # "<func_two_name>": ["atan2", "log", "mod", "pow", "power"],
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
    "<drop_col_name>": [("<string>", opts(pre=lambda:md.drop_col_name()))],
    "<just_column>": ["", "COLUMN"],

    "<drop_table_views>": [("<string>", opts(pre=lambda: md.drop_table_views()))],
}
grammar.update(alter_table_grammar)

delete_stmt_grammar = {
    "<delete_stmt>": ["DELETE FROM <existing_table_name>;"],
}
grammar.update(delete_stmt_grammar)

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
    "<indexed_column>": [("<string>", opts(pre=lambda: md.get_column_to_index()))]
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
    # chaining according to fair usage policy
    "<create_savepoint>": ["SAVEPOINT <savepoint_name>;<release_savepoint>",],
    "<savepoint_name>": [("<string>", opts(post=lambda *args: md.post_savepoint_name(*args)))],

    "<release_savepoint>": ["RELEASE <savepoint> <existing_savepoint_name>;"],
    "<savepoint>": ["", "SAVEPOINT"],
    "<existing_savepoint_name>": [("<savepoint_name>", opts(pre=lambda: md.get_release_savepoint()))],
}
grammar.update(save_point_grammar)

update_stmt_grammar = {
    "<update_stmt>": [("UPDATE <insert_failure> <existing_table_name> SET <set_columns>;", opts(order=[1,2,3]))],
    "<set_columns>": [("<set_column>", opts(prob=0.95)), "<set_column>, <set_column>"],
    "<set_column>": [("<string>", opts(pre=lambda: md.get_set_column()))]
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
    "<of_col_name>": [("<string>", opts(pre=lambda: md.get_of_col_name()))],
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

comment_grammar = {
    "<comment>": ["<c_style_comment>", "<dash_comment>"],
    "<c_style_comment>": ["/*<string*/"],
    "<dash_comment>": ["--<string>\n"]
}
grammar.update(comment_grammar)

analyze_stmt_grammar = {
    "<analyze_stmt>": ["ANALYZE <symbol_to_analyze>;"],
    "<symbol_to_analyze>": [("main", opts(prob=0.1)), "<existing_table_name>", "<existing_index_name>"],
}
grammar.update(analyze_stmt_grammar)

explain_plan_grammar = {
    "<explain_plan>": ["EXPLAIN <query_plan> <stmt_to_explain>"],
    "<query_plan>": ["", "QUERY PLAN"],
    "<stmt_to_explain>": ["<create_table>", "<drop_table>", "<insert_stmt>", "<select_stmt>", "<alter_table>", "<delete_stmt>", "<create_view>", "<drop_view>", "<create_index>", "<drop_index>", "<create_savepoint>", "<release_savepoint>", "<reindex_stmt>", "<vacuum_stmt>", "<update_stmt>", "<create_trigger>", "<drop_trigger>", "<comment>", "<analyze_stmt>"],
    
}
grammar.update(explain_plan_grammar)

pragma_stmt_grammar = {
    "<pragma_stmt>": [("PRAGMA <main_or_temp><pragma_name_and_value>;", opts(order=[2,1]))],
    "<pragma_name_and_value>": [("<string>", opts(pre=lambda: md.handle_pragma()))],
    "<main_or_temp>": [("", opts(pre=lambda: md.check_need_schema(), prob=0.9)), "main.", "temp."],
}
grammar.update(pragma_stmt_grammar)
