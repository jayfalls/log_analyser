import sqlite3

# LOG TO DATABASE
class Analyser():
    def analyse(self, log_tools) -> tuple:
        frequencies = log_tools.get_log_type_frequencies()
        return frequencies