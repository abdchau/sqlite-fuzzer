from typing import List

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

    def set_name(self, name):
        self.table_name = name

    def add_column(self, column):
        self.columns.append(column)
        self.has_primary_key = self.has_primary_key or column.is_primary

    def __repr__(self) -> str:
        return f"[{self.table_name} {self.columns}]"