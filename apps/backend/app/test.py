 class Column: 
    def __init__(self, name: str, data: List[int]):
        self.name = name
        self.data = data

    def get_data(self) -> List[int]:
        return self.data

class DataWarehouseTable: 
    def __init__(self, name: str, columns: List[Column]):
        self.name = name
        self.columns = Dict[str, Column] = {column.name : column for column in columns}

        def get_column(self, name: str) -> Column: 
            if name not in self.columns: 
                raise ValueError(f"No column found with the name: {name}")
            return self.columns[name]

class DataWarehouse:
    def __init__(self, tables: List[DataWarehouseTable]):
        self.tables = Dict[str, DataWarehouseTable] = {table.name : table for table in tables}

        def get_table(self, name: str) -> DataWarehouseTable: 
            if name not in self.tables: 
                raise ValueError(f"No table found with the name: {name}")
            return self.tables[name]
        
        
    ### Assessment code 
    ### helper functions allowed, do not change the folllowing input or return types 

class SigmaTable: 
    def __init__(
        self, 
        name: str, 
        base_table_name: str, 
        get_data_warehouse: Callable[[], DataWarehouse]
    ): 
        self.name = name 
        self.base_table_name = base_table_name
        self.get_data_warehouse = get_data_warehouse
        # TODO extend this definition

        def set_sum_col(self, col_name: str, left_col_name: str, right_col_name: str):
            pass
        
        def set_diff_col(self, col_name: str, left_col_name: str, right_col_name: str):
            pass
        
        def get_column(self, col_name: str) -> Column:
            pass

        def get_all_columns(self) -> Dict[str, Column]:
            pass

        def set_max_summary(self, summary_name: str, col_name: str):
            pass

        def set_min_summary(self, summary_name:str, col_name:str):
            pass
        
        def get_summaries(self) -> Dict[str, int]:
            pass

        ### Testing code 
        # These functions are called when 'PRINT_ONLY'  is set to true in the test code 
        def make_test_table() -> SigmaTable:
            col1 = Column(name="col1", data=[1,2,3])
            col2 = Column(name="col2", data=[4,5,6])
            col3 = Column(name="col3", data=[7,8])
            table = DataWarehouseTable(name="test_table", columns=[col1, col2, col3])
            warehouse = DataWarehouse(tables=[table])
            sigma_table = SigmaTable(name="test_table", base_table_name="test_table", get_data_warehouse=lambda: warehouse)