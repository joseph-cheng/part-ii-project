import tempo
import util


def note_offset_metric(audio, tempo_variation=None):
    """
    Calculates the note onset offset metric by using the tempo variation metric

    audio: an Audio object containing the signal to calculate the metric for
    tempo_variation: the first order difference of beat times, so the distance between subsequent beats. can be precalculated since we will likely calculate this metric at another point

    returns: an array of distances between expected beat times and actual note onsets, along with the strength of the onset
    """
    if tempo_variation == None:
        tempo_variation = tempo.calculate_tempo_variation(audio)

    # TODO: memoise
    onset_function = calculate_onset_func(audio)

    moving_average_window = 4
    tempo_variation_average = moving_average(tempo_variation, moving_average_window)

    # basically, take the moving average tempo, and search for the nearest highest onset value in a small window around the expected beat time based on the moving average tempo
    for data


def get_best_nearest_onset(audio, expected_beat_time, window_size):
    """
    Gets the distance from the expected beat time of the highest onset value in a small window around the expected beat time

    audio: an Audio object containing the signal to search for
    expected_beat_time: time in seconds of the expected beat time
    window_size: size in seconds of the window to search for the note onset

    returns:
    """





