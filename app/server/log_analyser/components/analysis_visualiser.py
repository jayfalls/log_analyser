from matplotlib import pyplot
from numpy import array


# HELPER FUNCTIONS
def organise_two_dimensional_array(two_dimensional_list: list) -> array:
    x_list: list = []
    y_list: list[int] = []
    for line in two_dimensional_list:
        x_list.append(line[0])
        y_list.append(line[1])
    return array([x_list, y_list])
    
class AnalysisVisualiser():
    @staticmethod
    def visualise_bar_graph(xy_array: tuple, shuffle: bool = False) -> None:
        working_array: array
        if shuffle:
            working_array = organise_two_dimensional_array(xy_array)
        else:
            working_array = xy_array[:]
        pyplot.bar(working_array[0], working_array[1])
        pyplot.show()