from log_analyser.components.analysis.log_tokeniser import LogTokeniser

# LOG TO DATABASE
class LogDatabaseAnalyser():
    # VARIABLES
    ## References
    log_tokeniser: LogTokeniser
    ## States
    filters: tuple = ()

    def __init__(self):
        self.log_tokeniser = LogTokeniser()
    
    def get_frequent_logs_tokenised(self, log_analyser) -> None:
        self.log_tokeniser.get_frequent_logs_tokenised(log_analyser)

    def get_log_type_frequencies(self, log_analyser) -> tuple:
        try:
            frequencies: tuple = log_analyser.get_log_type_frequencies(self.filters)
            if frequencies is None:
                raise Exception("Error: Unable to retrieve log type frequencies.")
            return frequencies
        except Exception as error:
            raise Exception("An error occurred during analysis:", str(error))

    def analyse(self, log_analyser, filters: tuple = ()) -> tuple:
        self.filters = filters
        self.log_tokeniser.filters = filters
        self.get_frequent_logs_tokenised(log_analyser)
        return self.get_log_type_frequencies(log_analyser)