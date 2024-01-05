# Implement your grammar here in the `grammar` variable.
# You may define additional functions, e.g. for generators.
# You may not import any other modules written by yourself.
# That is, your entire implementation must be in `grammar.py`
# and `fuzzer.py`.

import string
import string
import random
import copy
import time

from fuzzingbook.GeneratorGrammarFuzzer import opts
from typing import Dict, List

# =======================================================================================================
# ===============================PRAGMAS START===========================================================
# =======================================================================================================

def get_int_between(start, end, prefix=''):
    def get_int():
        return prefix+str(random.randint(start, end))
    return get_int

def get_bool():
    return get_int_between(0,1)

def get_nothing():
    def f():
        return ''
    return f

def get_encoding():
    def encoding():
        return random.choice(["'UTF-8'","'UTF-16'","'UTF-16le'","'UTF-16be'"])
    return encoding

def get_underscore():
    def underscore():
        return '___'
    return underscore

def get_journal_mode():
    def journal_mode():
        return random.choice(['DELETE', 'TRUNCATE', 'PERSIST', 'MEMORY', 'WAL', 'OFF'])
    return journal_mode

def get_locking_mode():
    def locking_mode():
        return random.choice(['NORMAL', 'EXCLUSIVE'])
    return locking_mode


def get_wal_checkpoint():
    def wal_checkpoint():
        return random.choice(['PASSIVE','FULL','RESTART','TRUNCATE'])
    return wal_checkpoint


def wrap_assign_method(equal, fn: callable):
    def wrap_assign_method_inner():
        st = ''
        if equal == '=':
            st+='='
        else:
            st+='('

        st += str(fn())

        if equal == '=':
            pass
        else:
            st+=')'
        return st
    return wrap_assign_method_inner

pragmas_that_need_schemas = ['application_id', 'auto_vacuum', 'cache_size', 'data_version', 'default_cache_size', 'foreign_key_check',
                             'freelist_count', 'incremental_vacuum', 'index_info', 'index_list', 'index_xinfo', 'integrity_check',
                             'journal_mode', 'journal_size_limit', 'locking_mode', 'max_page_count', 'mmap_size', 'page_count', 'quick_check',
                             'secure_delete', 'synchronous', 'table_info']

pragmas = {
    'analysis_limit': wrap_assign_method('=', get_int_between(100,1000)),
    'application_id': wrap_assign_method('=', get_int_between(100,1000)),
    'auto_vacuum': wrap_assign_method('=', get_int_between(0,2)),
    'automatic_index': wrap_assign_method('=', get_int_between(0,2)),
    'busy_timeout': wrap_assign_method('=', get_int_between(1000,3000)),
    'cache_size': wrap_assign_method('=', get_int_between(1500,2500, prefix='-')),
    'cache_spill': wrap_assign_method('=', get_int_between(0,1)),
    'case_sensitive_like': wrap_assign_method('=', get_int_between(0,1)),
    'cell_size_check': wrap_assign_method('=', get_int_between(0,1)),
    'checkpoint_fullfsync': wrap_assign_method('=', get_int_between(0,1)),
    'collation_list': get_nothing(),
    'compile_options': get_nothing(),
    'count_changes': wrap_assign_method('=', get_int_between(0,1)),
    'data_version': get_nothing(),
    'database_list': get_nothing(),
    'defer_foreign_keys': wrap_assign_method('=', get_int_between(0,1)),
    'encoding': wrap_assign_method('=', get_encoding()),
    'foreign_key_check': get_nothing(),
    'foreign_keys': wrap_assign_method('=', get_int_between(0,1)),
    'freelist_count': get_nothing(),
    'full_column_names': get_nothing(),
    'fullfsync': wrap_assign_method('=', get_int_between(0,1)),
    'function_list': get_nothing(),
    'ignore_check_constraints': wrap_assign_method('=', get_int_between(0,1)),
    'incremental_vacuum': wrap_assign_method('()', get_int_between(1,3)),
    'index_info': wrap_assign_method('()', get_underscore()),
    'index_list': wrap_assign_method('()', get_underscore()),
    'index_xinfo': wrap_assign_method('()', get_underscore()),
    'integrity_check': wrap_assign_method('()', get_underscore()),
    'journal_mode': wrap_assign_method('=', get_journal_mode()),
    'legacy_file_format': get_nothing(),
    'journal_size_limit': wrap_assign_method('=', get_int_between(10,30)),
    'locking_mode': wrap_assign_method('=', get_locking_mode()),
    'max_page_count': wrap_assign_method('=', get_int_between(1,300)),
    'mmap_size': wrap_assign_method('=', get_int_between(1,300)),
    'module_list': get_nothing(),
    'optimize': get_nothing(),
    'page_count': get_nothing(),
    'page_size': wrap_assign_method('=', get_int_between(1024,1024)),
    'parser_trace': wrap_assign_method('=', get_int_between(0,1)),
    'pragma_list': get_nothing(),
    'query_only': wrap_assign_method('=', get_int_between(0,1)),
    'quick_check': wrap_assign_method('()', get_underscore()),
    'read_uncommitted': wrap_assign_method('=', get_int_between(0,1)),
    'recursive_triggers': wrap_assign_method('=', get_int_between(0,1)),
    'reverse_unordered_selects': wrap_assign_method('=', get_int_between(0,1)),
    'secure_delete': wrap_assign_method('=', get_int_between(0,1)),
    'shrink_memory': get_nothing(),
    'soft_heap_limit': wrap_assign_method('=', get_int_between(10,50)),
    'stats': get_nothing(),
    'synchronous': wrap_assign_method('=', get_int_between(0,3)),
    'table_info': wrap_assign_method('()', get_underscore()),
    'table_list': wrap_assign_method('()', get_underscore()),
    'table_xinfo': wrap_assign_method('()', get_underscore()),
    'temp_store': wrap_assign_method('=', get_int_between(0,2)),
    'threads': wrap_assign_method('=', get_int_between(1,3)),
    'trusted_schema': wrap_assign_method('=', get_int_between(0,1)),
    'user_version': get_nothing(),
    'wal_autocheckpoint': get_nothing(),
    'wal_checkpoint': wrap_assign_method('()', get_wal_checkpoint()),
    'writable_schema': wrap_assign_method('=', get_int_between(0,1)),
}
# =======================================================================================================
# ===============================PRAGMAS END=============================================================
# =======================================================================================================


# =======================================================================================================
# =============================TABLE DATA START==========================================================
# =======================================================================================================

class ColumnData:
    def __init__(self, column_name, column_type, constraint):
        self.column_name = column_name
        self.column_type = column_type
        self.is_primary = 'PRIMARY KEY' in constraint
        self.is_nullable = not ('NOT NULL' in constraint)
        self.constraint = constraint
    
    def __repr__(self) -> str:
        return f"({self.column_name} {self.column_type} {self.constraint} {self.is_primary})"

class TableData:
    def __init__(self):
        self.table_name: str = None
        self.columns: List[ColumnData] = []
        self.has_primary_key = False
        self.associated_views = []

    def set_name(self, name):
        self.table_name = name

    def add_column(self, column):
        self.columns.append(column)
        self.has_primary_key = self.has_primary_key or column.is_primary

    def __repr__(self) -> str:
        return f"[{self.table_name} {self.columns}]"

# =======================================================================================================
# ==============================TABLE DATA END===========================================================
# =======================================================================================================

# =======================================================================================================
# ===============================METADATA START==========================================================
# =======================================================================================================

class MetaData:
    # global initialization
    def __init__(self) -> None:
        self.created_tables: Dict[str : TableData] = {}
        self.deleted_tables = set()
        self._created_views = set()
        self._created_indices = set()
        self._created_savepoints = []
        self._created_triggers = []
        self.input_fuzzed = 0

    # initialization for single fuzz generation
    def pre_start(self):
        self.current_table = TableData()
        random.seed(time.time())

        self.is_explain = False
        self._need_schema_for_pragma = False

        # MUST RETURN FALSE
        return False

    # called after each fuzz generation
    def post_start(self, args):
        self.input_fuzzed += 1

        if self.is_explain:
            self.created_tables = copy.deepcopy(self._created_tables_copy)
            self.deleted_tables = copy.deepcopy(self._deleted_tables_copy)
            self._created_views = copy.deepcopy(self._created_views_copy)
            self._created_indices = copy.deepcopy(self._created_indices_copy)
            self._created_savepoints = copy.deepcopy(self._created_savepoints_copy)


        return args[0]
    
    def post_create_view(self, args):
        if self.current_table.table_name:
            self.current_table.associated_views.append(self.new_view)

        return args[0]

    def pre_explain_plan(self):
        self.is_explain = True
        self._created_tables_copy = copy.deepcopy(self.created_tables)
        self._deleted_tables_copy = copy.deepcopy(self.deleted_tables)
        self._created_views_copy = copy.deepcopy(self._created_views)
        self._created_indices_copy = copy.deepcopy(self._created_indices)
        self._created_savepoints_copy = copy.deepcopy(self._created_savepoints)

    def force_string_min_length(self, s, length, prob=1):
        if random.uniform(0, 1) < prob:
            for _ in range(0, length - len(s)):
                s += random.choice(string.ascii_lowercase)
        return s

    def post_table_name(self, args):
        table_name = args[0]
        table_name = self.force_string_min_length(table_name, 3)
        return table_name

    def add_created_table(self, *args):
        args = list(args)
        args[2] = self.force_string_min_length(args[2], 3, prob=0.9)
        
        self.current_table.set_name(args[2])
        if self.current_table.table_name not in self.created_tables.keys():
            self.created_tables[args[2]] = copy.deepcopy(self.current_table)

        return args

    def add_column(self, args):
        """col_name, col_type, col_constraint"""
        args = list(args)
        args[0] = self.force_string_min_length(args[0], 3, prob=0.8)
        if  self.current_table.has_primary_key:
            if 'PRIMARY KEY' in args[2]:
                args[2] = ''
        elif random.uniform(0, 1) < 0.8:
            args[2] = 'PRIMARY KEY'

        col = ColumnData(*args)
        self.current_table.add_column(col)
        return "{} {} {}".format(*args)

    def add_deleted_table(self, table):
        self.deleted_tables.add(table)

    def get_created_table(self, prob):
        if self.created_tables and random.uniform(0, 1) < prob:
            return random.choice(list(self.created_tables.keys()))
        else:
            return False

    def get_deleted_table(self, prob):
        if self.deleted_tables and random.uniform(0, 1) < prob:
            return random.choice(list(self.deleted_tables))
        else:
            return False

    def hijack_table_name(self, prob, created_prob):
        if random.uniform(0, 1) < prob:
            if random.uniform(0, 1) < created_prob:
                return self.get_created_table(1)
            else:
                return self.get_deleted_table(1)
        return False
    
    def construct_insert_table_cols(self):
        if not self.created_tables:
            return ''
        self.current_table: TableData = random.choice(list(self.created_tables.values()))
        col_str = ', '.join([c.column_name for c in self.current_table.columns])
        return f"{self.current_table.table_name}({col_str})"
    
    def get_values_for_cols(self):
        if not self.current_table.table_name:
            return ''

        values = []
        for column in self.current_table.columns:
            value = None
            if column.column_type in ['DOUBLE', 'REAL', 'PRECISION', 'FLOAT']:
                value = random.choice(string.digits)+'.'+random.choice(string.digits)+random.choice(string.digits)
            elif 'CHAR' in column.column_type or 'LOB' in column.column_type:
                value = f"'{''.join([random.choice(string.ascii_letters) for i in range(2)])}'"
            else:
                value = random.choice(string.digits)+random.choice(string.digits)

            values.append(value)

        return ', '.join(values)

    def get_delete_table_name(self, prob):
        if random.uniform(0, 1) > prob or not self.created_tables:
            return False

        self.current_table: TableData = self.created_tables.pop(random.choice(list(self.created_tables.keys())))
        self.deleted_tables.add(self.current_table.table_name)

        return self.current_table.table_name

    def wrap_aggregate(self, col_name):
        agg_funcs = ["avg", "count", "group_concat", "max", "min", "sum", "total"]
        if random.uniform(0, 1) < 0.1:
            return f"{random.choice(agg_funcs)}({col_name})"
        else:
            return col_name

    def get_select_columns(self):
        if not self.created_tables:
            return '*'

        self.current_table: TableData = random.choice(list(self.created_tables.values()))

        num = random.randint(1, max(1, len(self.current_table.columns)))
        return ', '.join([self.wrap_aggregate(c.column_name) for c in self.current_table.columns[:num]]) if len(self.current_table.columns) > 0 else '*'

    def get_select_table(self):
        return self.current_table.table_name if self.current_table.table_name else ''.join([random.choice(string.ascii_lowercase) for i in range(3)])

    def get_existing_table(self):
        if self.created_tables:
            self.current_table: TableData = random.choice(list(self.created_tables.values()))
        return self.current_table.table_name if self.current_table.table_name else ''.join([random.choice(string.ascii_lowercase) for i in range(3)])

    def get_existing_column(self):
        return random.choice(self.current_table.columns).column_name if self.current_table.columns else ''.join([random.choice(string.ascii_lowercase) for i in range(3)])

    def post_rename_table(self, new_name):
        curr_name = self.current_table.table_name
        if curr_name:
            self.current_table.set_name(new_name)
            self.created_tables[new_name] = self.current_table
            del self.created_tables[curr_name]
        return new_name

    def rename_column_name(self, new_name):
        if self.current_table.table_name and len(self.current_table.columns) > 0:
            col = random.choice(self.current_table.columns)
            old_name = col.column_name
            col.column_name = new_name
        else:
            old_name = 'asdf'

        return f"RENAME COLUMN {old_name} TO {new_name}"

    def post_add_column(self, st: str):
        st = st.replace('UNIQUE', '')
        return st

    def drop_col_name(self, primary_prob=0.3, drop=True):
        satisfied = False
        if self.current_table.table_name and len(self.current_table.columns) > 0:
            while not satisfied:
                col = random.choice(self.current_table.columns)
                satisfied = True
                if col.is_primary and random.uniform(0,1) < primary_prob and len(self.current_table.columns) > 1:
                    satisfied = False
        else:
            return 'adsff'

        if drop:
            self.current_table.columns.remove(col)
        return col.column_name

    def drop_table_views(self):
        if not self.current_table.columns:
            return ''

        # chaining commands according to fair use policy: https://cms.cispa.saarland/askbot/fuzzing2324/question/415/project-1-fuzz_one_input-should-generate-only-one-sqlite-command/
        drops = ''.join([f"DROP VIEW {view};" for view in self.current_table.associated_views])
        return drops

    def post_view_name(self, args):
        name = self.post_table_name(args)
        self._created_views.add(name)
        self.new_view = name
        return name

    def get_drop_view(self):
        if self._created_views:
            view = random.choice(list(self._created_views))
            self._created_views.remove(view)
            return view
        return False

    def post_index_name(self, args):
        name = self.post_table_name(args)
        self._created_indices.add(name)
        return name

    def get_column_to_index(self):
        return self.drop_col_name(primary_prob=0.8, drop=False)

    def get_drop_index(self):
        if self._created_indices:
            index = random.choice(list(self._created_indices))
            self._created_indices.remove(index)
            return index
        return False

    def get_existing_index(self):
        if self._created_indices:
            index = random.choice(list(self._created_indices))
            # self._created_indices.remove(index)
            return index
        return 'False'

    def post_savepoint_name(self, args):
        name = self.post_table_name(args)
        self._created_savepoints.append(name)
        return name

    def get_release_savepoint(self):
        if self._created_savepoints:
            idx = random.randint(0, len(self._created_savepoints) - 1)
            savepoint = self._created_savepoints[idx]
            self._created_savepoints = self._created_savepoints[:idx]
            return savepoint
        return False

    def get_set_column(self):
        if not self.current_table.columns:
            return 'asdf=13'
        column = random.choice(self.current_table.columns)
        value = None
        if column.column_type in ['DOUBLE', 'REAL', 'PRECISION', 'FLOAT']:
            value = random.choice(string.digits)+'.'+random.choice(string.digits)+random.choice(string.digits)
        elif 'CHAR' in column.column_type or 'LOB' in column.column_type:
            value = f"'{''.join([random.choice(string.ascii_letters) for i in range(2)])}'"
        else:
            value = random.choice(string.digits)+random.choice(string.digits)

        return f"{column.column_name}={value}"

    def post_trigger_name(self, args):
        name = self.post_table_name(args)
        self._created_triggers.append(name)
        return name

    def get_of_col_name(self):
        return self.drop_col_name(primary_prob=0.8, drop=False)

    def get_drop_trigger(self):
        if self._created_triggers:
            trigger = random.choice(list(self._created_triggers))
            self._created_triggers.remove(trigger)
            return trigger
        return False

    def handle_pragma(self):
        pragma = random.choice(list(pragmas.keys()))
        if pragma in pragmas_that_need_schemas:
            self._need_schema_for_pragma = True

        pragma_str = f"{pragma}"
        if random.uniform(0,1) < 0.8:
            pragma_str += pragmas[pragma]()
            if pragma == 'index_info':
                pragma_str.replace('___', self.get_existing_index())
            elif pragma == 'index_list':
                pragma_str.replace('___', self.get_existing_table())
            elif pragma == 'index_xinfo':
                pragma_str.replace('___', self.get_existing_index())
            elif pragma == 'integrity_check':
                pragma_str.replace('___', self.get_existing_table())
            elif pragma == 'quick_check':
                pragma_str.replace('___', self.get_existing_table())
            elif pragma == 'table_info' or pragma == 'table_list' or pragma == 'table_xinfo':
                pragma_str.replace('___', self.get_existing_table())
            else:
                pass
        return pragma_str
    
    def check_need_schema(self):
        if self._need_schema_for_pragma:
            return 'main.'

# =======================================================================================================
# ================================METADATA END===========================================================
# =======================================================================================================


# =======================================================================================================
# ================================GRAMMAR START==========================================================
# =======================================================================================================

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
    "<delete_stmt>": ["DELETE FROM <existing_table_name> <where_clause>;"],
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

# =======================================================================================================
# =================================GRAMMAR END===========================================================
# =======================================================================================================
