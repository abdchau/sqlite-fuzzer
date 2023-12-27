from typing import List

class ColumnData:
    def __init__(self, column_name, column_type):
        self.column_name = column_name
        self.column_type = column_type
    
    def __repr__(self) -> str:
        return f"({self.column_name} {self.column_type})"

class TableData:
    def __init__(self):
        self.table_name: str
        self.columns: List[ColumnData] = []

    def set_name(self, name):
        self.table_name = name

    def add_column(self, column):
        self.columns.append(column)

    def __repr__(self) -> str:
        return f"[{self.table_name} {self.columns}]"