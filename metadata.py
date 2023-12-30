import string
import random
import copy
import time

from typing import Dict

from tabledata import TableData, ColumnData

class MetaData:
    # global initialization
    def __init__(self) -> None:
        self.created_tables: Dict[str : TableData] = {}
        self.deleted_tables = set()
        self._created_views = set()
        self._created_indices = set()
        self._created_savepoints = []
        self.input_fuzzed = 0

    # initialization for single fuzz generation
    def pre_start(self):
        self.current_table = TableData()
        random.seed(time.time())

        self.is_explain = False

        # MUST RETURN FALSE
        return False

    # called after each fuzz generation
    def post_start(self, args):
        self.input_fuzzed += 1

        if self.is_explain:
            self.created_tables: copy.deepcopy(self._created_tables_copy)
            self.deleted_tables = copy.deepcopy(self._deleted_tables_copy)
            self._created_views = copy.deepcopy(self._created_views_copy)
            self._created_indices = copy.deepcopy(self._created_indices_copy)
            self._created_savepoints = copy.deepcopy(self._created_savepoints_copy)

        return args[0]
    
    def pre_explain_plan(self):
        self.is_explain = True
        self._created_tables_copy: copy.deepcopy(self.created_tables)
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
        print('TABLE NAME', args)
        # exit()
        table_name = args[0]
        table_name = self.force_string_min_length(table_name, 3)
        return table_name

    def add_created_table(self, *args):
        args = list(args)
        args[2] = self.force_string_min_length(args[2], 3, prob=0.9)
        
        self.current_table.set_name(args[2])
        if self.current_table.table_name not in self.created_tables.keys():
            self.created_tables[args[2]] = copy.deepcopy(self.current_table)

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
    
    def construct_insert_table_cols(self):
        if not self.created_tables:
            return ''
        print(self.created_tables)
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

    def get_select_columns(self):
        if not self.created_tables:
            return '*'

        self.current_table: TableData = random.choice(list(self.created_tables.values()))

        num = random.randint(1, max(1, len(self.current_table.columns)))
        return ', '.join([c.column_name for c in self.current_table.columns[:num]]) if len(self.current_table.columns) > 0 else '*'

    def get_select_table(self):
        return self.current_table.table_name if self.current_table.table_name else ''.join([random.choice(string.ascii_lowercase) for i in range(3)])

    def get_existing_table(self):
        if self.created_tables:
            self.current_table: TableData = random.choice(list(self.created_tables.values()))
        return self.current_table.table_name if self.current_table.table_name else ''.join([random.choice(string.ascii_lowercase) for i in range(3)])

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

    def drop_col_name(self, primary_prob=0.3):
        satisfied = False
        if self.current_table.table_name and len(self.current_table.columns) > 0:
            while not satisfied:
                col = random.choice(self.current_table.columns)
                satisfied = True
                if col.is_primary and random.uniform(0,1) < primary_prob and len(self.current_table.columns) > 1:
                    satisfied = False
        else:
            return 'adsff'

        self.current_table.columns.remove(col)
        return col.column_name

    def post_view_name(self, args):
        name = self.post_table_name(args)
        self._created_views.add(name)
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
        return self.drop_col_name(primary_prob=0.8)

    def get_drop_index(self):
        if self._created_indices:
            index = random.choice(list(self._created_indices))
            self._created_indices.remove(index)
            return index
        return False

    def post_savepoint_name(self, args):
        name = self.post_table_name(args)
        self._created_savepoints.append(name)
        return name

    def get_release_savepoint(self):
        if self._created_savepoints:
            idx = random.randint(0, len(self._created_savepoints) - 1)
            print(self._created_savepoints, idx)
            savepoint = self._created_savepoints[idx]
            self._created_savepoints = self._created_savepoints[:idx]
            return savepoint
        return False

    def print_vars(self):
        print(self.created_tables)
        print(self.deleted_tables)
