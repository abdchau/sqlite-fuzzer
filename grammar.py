# Implement your grammar here in the `grammar` variable.
# You may define additional functions, e.g. for generators.
# You may not import any other modules written by yourself.
# That is, your entire implementation must be in `grammar.py`
# and `fuzzer.py`.

import string
from fuzzingbook.GeneratorGrammarFuzzer import opts
import random

class MetaData:
    def __init__(self) -> None:
        self.created_tables = set()
        self.deleted_tables = set()

    def add_created_table(self, table, *args):
        self.created_tables.add(table)

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
    "<start>": ["<create_table>"],
    "<create_table>" : [("CREATE TABLE <table_name> (<table_columns_def>);", opts(post=lambda *args: md.add_created_table(*args)))],
    "<table_name>":[("<string>", opts(pre=lambda: md.hijack_table_name(0.5)))],
    "<table_columns_def>": ["<table_column_def>", "<table_columns_def>,<table_column_def>"],
    "<table_column_def>": ["<string> TEXT"],
    "<string>": ["<letter>", ("<letter><string>", opts(prob=0.7))],
    "<letter>": [c for c in string.ascii_letters],
}