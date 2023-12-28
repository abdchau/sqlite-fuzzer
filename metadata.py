import string
import random
import copy

from typing import Dict

from tabledata import TableData, ColumnData

class MetaData:
    # global initialization
    def __init__(self) -> None:
        self.created_tables: Dict[str : TableData] = {}
        self.deleted_tables = set()
        self.input_fuzzed = 0

    # initialization for single fuzz generation
    def pre_start(self):
        self.current_table = TableData()

        # MUST RETURN FALSE
        return False

    # called after each fuzz generation
    def post_start(self, args):
        self.input_fuzzed += 1

        return args[0]

    def force_string_min_length(self, s, length, prob=1):
        if random.uniform(0, 1) < prob:
            for _ in range(0, length - len(s)):
                s += random.choice(string.ascii_lowercase)
        return s

    def add_created_table(self, *args):
        args = list(args)
        args[1] = self.force_string_min_length(args[1], 3, prob=0.9)
        
        self.current_table.set_name(args[1])
        if self.current_table.table_name not in self.created_tables.keys():
            self.created_tables[args[1]] = copy.deepcopy(self.current_table)

        # if self.input_fuzzed > 9:
        #     print(self.created_tables)
        #     exit()
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
        
    def print_vars(self):
        print(self.created_tables)
        print(self.deleted_tables)
