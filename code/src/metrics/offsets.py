import tempo
import util


def note_offset_metric(audio, tempo_variation=None):
    """
    Calculates the note onset offset metric by using the tempo variation metric

    audio: an Audio object containing the signal to calculate the metric for
    tempo_variation: the first order difference of beat times, so the distance between subsequent beats. can be precalculated since we will likely calculate this metric at another point

    returns: a 2D array of distances between expected beat times and actual note onsets, along with the strength of the onset
    """
    if tempo_variation == None:
        tempo_variation = tempo.calculate_tempo_variation(audio)

    # TODO: memoise
    onset_function = calculate_onset_func(audio)

    moving_average_window = 4
    tempo_variation_average = moving_average(tempo_variation, moving_average_window)

    # basically, take the moving average tempo, and search for the nearest highest onset value in a small window around the expected beat time based on the moving average tempo
    current_loc = 0
    onset_window_search_size = 0.2
    ret = np.zeros((len(tempo_variation_average), 2))
    for i, inter_onset_interval in enumerate(tempo_variation_average):
        current_loc += inter_onset_interval
        onset_loc, onset_strength = get_best_nearest_onset(onset_function, current_loc, onset_window_search_size)
        ret[i][0] = onset_loc
        ret[i][1] = onset_stength

    return ret



def get_best_nearest_onset(onset_function, expected_beat_time, window_size):
    """
    Gets the distance from the expected beat time of the highest onset value in a small window around the expected beat time

    onset_function: an OnsetFunction object containing the onsets of the signal we are searching
    expected_beat_time: time in seconds of the expected beat time
    window_size: size in seconds of the window to search for the note onset

    returns: a tuple where the first element is the distance from the expected beat time to the best onset in the window, and the second element is the strength of this onset
    """

    window_size = onset_function.time_to_windows(window_size)
    min_window = onset_function.time_to_windows(expected_beat_time) - window_size
    max_window = min_window + 2 * window_size

    best_window = -1
    best_onset_value = np.NINF
    for window in range(min_window, max_window + 1):
        if onset_function.index_window(window) > best_onset_value:
            best_window = window
            best_onset_value = onset_function.index_window(window)

    onset_location = onset_function.windows_to_time(best_window)
    return (onset_location, best_onset_value)
