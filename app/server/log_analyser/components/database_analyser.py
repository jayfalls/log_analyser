from numpy import array


# LOG TO DATABASE
class LogDatabaseAnalyser():
    # VARIABLES
    ## States
    filters: tuple = ()

    def get_log_type_frequencies(self, log_analyser) -> tuple:
        try:
            frequencies: tuple = log_analyser.get_log_type_frequencies(self.filters)
            if frequencies is None:
                raise Exception("Error: Unable to retrieve log type frequencies.")
            return frequencies
        except Exception as error:
            raise Exception("An error occurred during analysis:", str(error))

    def analyse(self, log_analyser, filters: tuple = ()) -> None:
        self.filters = filters
        log_frequencies: tuple = self.get_log_type_frequencies(log_analyser)
        log_analyser.visualise_bar_graph(log_frequencies, True)