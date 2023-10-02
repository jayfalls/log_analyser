# LOG TO DATABASE
class LogDatabaseAnalyser():
    def analyse(self, log_analyser, filters: tuple = ()) -> tuple:
        try:
            frequencies = log_analyser.get_log_type_frequencies(filters)
            if frequencies is None:
                raise Exception("Error: Unable to retrieve log type frequencies.")
            return frequencies
        except Exception as error:
            raise Exception("An error occurred during analysis:", str(error))