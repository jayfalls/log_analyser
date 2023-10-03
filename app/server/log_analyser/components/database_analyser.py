from numpy import array


# LOG TO DATABASE
class LogDatabaseAnalyser():
    # VARIABLES
    ## References
    # log_analyser | Must be assigned by interface
    ## States
    filters: tuple = ()

    def get_log_type_frequencies(self) -> tuple:
        try:
            frequencies: tuple = self.log_analyser.get_log_type_frequencies(self.filters)
            if frequencies is None:
                raise Exception("Error: Unable to retrieve log type frequencies.")
            return frequencies
        except Exception as error:
            raise Exception("An error occurred during analysis:", str(error))

    def analyse(self, filters: tuple = ()) -> None:
        self.filters = filters
        log_frequencies: tuple = self.get_log_type_frequencies()
        graph_details: tuple = ("Log Type Frequency", "LOG TYPE", "OCCURENCES")
        self.log_analyser.visualise_bar_graph(graph_details, log_frequencies, True)