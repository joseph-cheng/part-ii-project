import util
import chroma
import dynamics
import offsets
import tempo
import timbre

CHROMA = 2**0
DYNAMICS = 2**1
OFFSETS = 2**2
TEMPO = 2**3
TIMBRE = 2**4

METRIC_FUNCTIONS = {
    CHROMA:   chroma.calculate_chroma_metric,
    DYNAMICS: dynamics.calculate_dynamics_metric,
    OFFSETS:  offsets.calculate_offsets_metric,
    TEMPO:    tempo.calculate_tempo_metric,
    TIMBRE:   timbre.calculate_timbre_metric,
}

SIMILARITY_FUNCTIONS = {
    CHROMA:   chroma.chroma_metric_similarity,
    DYNAMICS: dynamics.dynamics_metric_similarity,
    OFFSETS:  offsets.offsets_metric_similarity,
    TEMPO:    tempo.tempo_metric_similarity,
    TIMBRE:   timbre.timbre_metric_similarity,
}

METRIC_STRINGS = {
    CHROMA:   "CHROMA",
    DYNAMICS: "DYNAMICS",
    OFFSETS:  "OFFSETS",
    TEMPO:    "TEMPO",
    TIMBRE:   "TIMBRE",
}

CACHED_AUDIOS = {}


def calculate_metrics(audio, metric_flags):
    """
    Calculates the chosen metrics for a particular piece of audio

    audio: either a string representing a path to a wavfile, or an Audio object
    metric_flags: binary flags of the metrics to calculate

    returns: a dictionary of the calculated metrics, indexed by metric flag
    """

    calculated_metrics = {}


    if isinstance(audio, str):
        if audio not in CACHED_AUDIOS:
            CACHED_AUDIOS[audio] = util.read_audio(audio)
        audio = CACHED_AUDIOS[audio]

    for metric in METRIC_FUNCTIONS:
        if metric & metric_flags:
            print(f"Calculating {METRIC_STRINGS[metric]} metric...")
            # check if cached
            cached_metric = audio.get_cached_metric(metric)
            if cached_metric is not None:
                calculated_metrics[metric] = cached_metric
            else:
                metric_function = METRIC_FUNCTIONS[metric]
                calculated_metric = metric_function(audio)
                calculated_metrics[metric] = calculated_metric
                audio.cache_metric(metric, calculated_metric)

    return calculated_metrics


def get_most_similar(unknown_audio, other_audios, metric_flags):
    """
    Finds the most similar audio to an unknown audio, using the given metric flags.

    unknown_audio: Audio object, or string representing path, of the audio we want to find the most similar performer to
    other_audios: list of Audio objects, or string representing path, to compare unknown_audio to
    metric_flags: bitmask representing the metrics to use

    returns: a (similarity, Audio) tuple, where similarity is the calculated similarity, and Audio is the most similar Audio object in other_audios
    """

    print("Reading in audio files...")


    # first check if unknown_audio is a string, make it an Audio object if it is
    if isinstance(unknown_audio, str):
        if unknown_audio not in CACHED_AUDIOS:
            CACHED_AUDIOS[unknown_audio] = util.read_audio(unknown_audio)
        unknown_audio = CACHED_AUDIOS[unknown_audio]


    # do the same for the other list, but maintain a different list so we can return a semantically useful value at the end
    other_audios_objs = []
    for other_audio in other_audios:
        if isinstance(other_audio, str):
            if other_audio not in CACHED_AUDIOS:
                CACHED_AUDIOS[other_audio] = util.read_audio(other_audio)
            other_audio = CACHED_AUDIOS[other_audio]
        other_audios_objs.append(other_audio)

    print("Calculating metrics...")

    unknown_audio_metrics = calculate_metrics(unknown_audio, metric_flags)

    other_audios_metrics = []
    for other_audio in other_audios_objs:
        other_audios_metrics.append(
            calculate_metrics(other_audio, metric_flags))

    print("Calculating similarities...")
    similarities = []
    for metrics, other_audio in zip(other_audios_metrics, other_audios_objs):
        similarity_sum = 0
        for metric_enum in metrics:
            metric_value = metrics[metric_enum]
            unknown_audio_metric_value = unknown_audio_metrics[metric_enum]
            similarity_function = SIMILARITY_FUNCTIONS[metric_enum]
            similarity = similarity_function(
                unknown_audio, other_audio, unknown_audio_metric_value, metric_value)
            similarity_sum += similarity

        # now calculate mean similarity and add to our list
        similarities.append(similarity_sum / len(metrics))

    index = similarities.index(max(similarities))


    return (max(similarities), other_audios[index])


