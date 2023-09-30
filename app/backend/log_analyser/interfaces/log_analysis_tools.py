import asyncio
from ..components.sql_log import SQL_Log
from ..components.log_to_db import LogToDatabase
from ..components.analyser import Analyser


class LogTools():
    # VARIABLES
    ## References
    log_database: SQL_Log
    extractor: LogToDatabase
    analyser: Analyser
    ## States
    _debug_mode: bool = False
    ### State Changes
    @property
    def debug_mode(self):
        return self._debug_mode
    @debug_mode.setter
    def debug_mode(self, value):
        self._debug_mode = value
        self.log_database.debug_mode = self.debug_mode
        self.log_database.initialise_database()
    
    # OBJECT CREATION & DELETION
    def __init__(self):
        self.log_database = SQL_Log()
        self.extractor = LogToDatabase()
        self.analyser = Analyser()
        
    def __del__(self):
        self.log_database.close_database()
    
    def close_database(self) -> None:
        self.log_database.close_database()

    # INNER FUNCTIONS
    ## Database
    ### Read/Write
    async def add_log_to_database(self, log_path: str) -> None:
        await self.extractor.log_to_database(self.log_database, log_path)

    def commit_to_database(self) -> None:
        self.log_database.commit_to_database()

    def write_line_to_database(self, log_line: dict) -> None:
        self.log_database.write_line_to_database(log_line)
    
    ### Querying
    def get_log_type_frequencies(self) -> tuple:
        return self.log_database.get_log_type_frequencies()
    
    ## Log To Database
    async def log_to_database(self, path_to_log: str) -> None:
        await self.extractor.log_to_database(self, path_to_log)
    
    ## Log Analysis
    def analyse(self) -> tuple:
        return self.analyser.analyse(self)
    
    # OUTER FUNCTIONS
    async def import_logs(self, log_paths: tuple) -> None:
        if len(log_paths) == 0:
            return
        if len(log_paths) == 1:
            await self.log_to_database(log_paths[0])
        else:
            load_tasks: list = []
            for log_path in log_paths:
                task: asyncio.Task = asyncio.create_task(self.log_to_database(log_path))
                load_tasks.append(task)
            await load_tasks[-1]