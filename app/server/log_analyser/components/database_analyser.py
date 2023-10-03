import matplotlib.pyplot as plot
import numpy
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

    def get_sorted_log_types(self) -> dict:
        try:
            sorted_log_types: dict = self.log_analyser.get_sorted_log_types()
            if sorted_log_types is None:
                raise Exception("Error: Unable to retrieve log type frequencies.")
            return sorted_log_types
        except Exception as error:
            raise Exception("An error occurred during analysis:", str(error))

    @staticmethod
    def plot_log_message_frequencies(sorted_log_messages: dict, time_interval_minutes: int):
        # Create an empty DataFrame
        df = pandas.DataFrame(columns=['log_message', 'date', 'time'])

        # Iterate over log types and append results to the DataFrame
        for results in sorted_log_messages.values():
            for result in results:
                df = pandas.concat([df, pandas.DataFrame({'log_message': [result[0]], 'date': [result[1]], 'time': [result[2]]})], ignore_index=True)      
        # Combine date and time columns into a single datetime column
        df['datetime'] = pandas.to_datetime(df['date'] + ' ' + df['time'])
        # Remove the 'date' and 'time' columns
        df.drop(['date', 'time'], axis=1, inplace=True)

        # Set the datetime column as the index
        df.set_index('datetime', inplace=True)

        # Resample the data to the specified time interval and count the occurrences
        resampled = df.resample(str(time_interval_minutes) + 'T').size()
        resampled = resampled.to_frame(name='frequency')
        print(resampled.describe())

        # Plot the frequency of log messages over time
        ax = resampled.plot()

        # Set plot title, x-axis label, and y-axis label
        plot.title('Log Frequency')
        plot.xlabel('Time')
        plot.ylabel('Frequency')

        # Display legend
        plot.legend()

        # Show the plot
        plot.show()


    def analyse(self, filters: tuple = ()) -> None:
        log_frequencies: tuple = self.get_log_type_frequencies()
        graph_details: tuple = ("Log Type Frequency", "LOG TYPE", "OCCURENCES")
        self.log_analyser.visualise_bar_graph(graph_details, log_frequencies, True)
        sorted_log_messages: dict = self.get_sorted_log_types()
        self.plot_log_message_frequencies(sorted_log_messages, 15)