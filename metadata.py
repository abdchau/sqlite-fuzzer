import string
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
