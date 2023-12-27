# Implement your grammar here in the `grammar` variable.
# You may define additional functions, e.g. for generators.
# You may not import any other modules written by yourself.
# That is, your entire implementation must be in `grammar.py`
# and `fuzzer.py`.

import string
from fuzzingbook.GeneratorGrammarFuzzer import opts
import random
import copy

class MetaData:
    # global initialization
    def __init__(self) -> None:
        self.created_tables = set()
        self.table_columns = {}        # {table_name: [column_names]}
        self.current_columns = []
        self.current_primary_generated = False

        self.deleted_tables = set()
        self.input_fuzzed = 0

    # initialization for single fuzz generation
    def pre_start(self):
        self.current_primary_generated = False

        # MUST RETURN FALSE
        return False

    # called after each fuzz generation
    def post_start(self, *args):
        self.input_fuzzed += 1

        return args

    def add_created_table(self, *args):
        args = list(args)
        if random.uniform(0, 1) < 0.9:
            for _ in range(0, 3 - len(args[1])):
                args[1] += random.choice(string.ascii_lowercase)
        
        self.created_tables.add(args[1])
        self.table_columns[args[1]] = copy.deepcopy(self.current_columns)
        self.current_columns = []

        if self.input_fuzzed > 9:
            exit()
        return args

    def add_column(self, args):
        self.current_columns.append(args[0])
        return args

    def add_deleted_table(self, table):
        self.deleted_tables.add(table)

    def get_created_table(self, prob):
        if self.created_tables and random.uniform(0, 1) < prob:
            return random.choice(list(self.created_tables))
        else:
            return False

    def get_deleted_table(self, prob):
        if self.deleted_tables and random.uniform(0, 1) < prob:
            return random.choice(list(self.deleted_tables))
        else:
            return False

    def hijack_table_name(self, prob):
        if random.uniform(0, 1) < prob:
            if random.uniform(0, 1) < 0.5:
                return self.get_created_table(1)
            else:
                return self.get_deleted_table(1)
        
    def print_vars(self):
        print(self.created_tables)
        print(self.deleted_tables)

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
    "<table_column_def>": [("<string> <column_type>", opts(post=lambda *args: md.add_column(args)))],
    "<column_type>": ["INT", "INTEGER", "TINYINT", "SMALLINT", "MEDIUMINT", "BIGINT", "UNSIGNED", "BIGINT", "INT2", "INT8", "CHARACTER(<signed_number>)", "VARCHAR(<signed_number>)", "VARYING", "CHARACTER(<signed_number>)", "NCHAR(<signed_number>)", "NATIVE", "CHARACTER(<signed_number>)", "NVARCHAR(<signed_number>)", "TEXT", "CLOB", "BLOB", "REAL", "DOUBLE", "DOUBLE", "PRECISION", "FLOAT", "NUMERIC", "DECIMAL(<signed_number>, <signed_number>)", "BOOLEAN", "DATE", "DATETIME"],
    # "<column_modifier>": [("", opts(prob=0.95)), "(<signed_number>)", "(<signed_number>,<signed_number>)"]
}

grammar.update(create_table_grammar)