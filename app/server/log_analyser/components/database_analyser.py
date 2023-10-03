import pandas


# LOG TO DATABASE
class LogDatabaseAnalyser():
    # VARIABLES
    ## References
    # | log_analyser | Must be assigned by log_analyser interface

    def get_log_type_frequencies(self) -> tuple:
        try:
            frequencies: tuple = self.log_analyser.get_log_type_frequencies()
            if frequencies is None:
                raise Exception("Error: Unable to retrieve log type frequencies.")
            return frequencies
        except Exception as error:
            raise Exception("An error occurred during analysis:", str(error))

    def get_sorted_messages(self) -> tuple:
        try:
            sorted_messages: tuple = self.log_analyser.get_sorted_messages()
            if sorted_messages is None:
                raise Exception("Error: Unable to retrieve log type frequencies.")
            return sorted_messages
        except Exception as error:
            raise Exception("An error occurred during analysis:", str(error))


    @staticmethod
    def get_grouped_messages(sorted_messages: tuple) -> list[list[str]]:
        grouped_messages: list[list[list[str]]] = [[]]
        for index, timedate_message in enumerate(sorted_messages):
            print(grouped_messages)
            does_exist: bool = False
            message: str = timedate_message[0]
            datetime: str = f"{timedate_message[1]} {timedate_message[2]}"
            if index == 0:
                new_group: list = [[message], [datetime]]
                grouped_messages.append(new_group) 
                continue
            for group in grouped_messages:
                if message in group[0][0]:
                    does_exist = True
                    group[0].append(message)
                    group[1].append(datetime)
            if does_exist:
                continue
            new_group: list = [[message], [datetime]]
            grouped_messages.append(new_group)
        return grouped_messages
        
    def get_all_unique_messages_time_series(self) -> tuple:
        try:
            sorted_messages: tuple = self.get_sorted_messages()
            return self.get_grouped_messages(sorted_messages)
        except Exception as error:
            raise Exception("An error occurred during analysis:", str(error))

    def analyse(self, filters: tuple = ()) -> None:
        log_frequencies: tuple = self.get_log_type_frequencies()
        graph_details: tuple = ("Log Type Frequency", "LOG TYPE", "OCCURENCES")
        self.log_analyser.visualise_bar_graph(graph_details, log_frequencies, True)
        messages: list = self.get_all_unique_messages_time_series()
        print(messages)