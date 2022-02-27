import util
import chroma
import dynamics
import offsets
import tempo
import timbre


METRICS = [
        chroma.ChromaCalculator(),
        dynamics.DynamicsCalculator(),
        offsets.OffsetsCalculator(),
        tempo.TempoCalculator(),
        timbre.TimbreCalculator(),
        ]
           

# we cache audio objects because audio objects contain their own cached information which we don't want to just throw away, better solution would be to cache these in util.py
CACHED_AUDIOS = {}


def calculate_metrics(audio, metrics):
    """
    Calculates the chosen metrics for a particular piece of audio

    audio: either a string representing a path to a wavfile, or an Audio object
    metric_flags: list of MetricCalculators

    returns: a dictionary of the calculated metrics, indexed by MetricCalculator
    """

    calculated_metrics = {}


    if isinstance(audio, str):
        if audio not in CACHED_AUDIOS:
            CACHED_AUDIOS[audio] = util.read_audio(audio)
        audio = CACHED_AUDIOS[audio]

    for metric in metrics:
        print(f"Calculating {metric} metric...")
        # check if cached
        cached_metric = audio.get_cached_metric(metric)
        if cached_metric is not None:
            calculated_metrics[metric] = cached_metric
        else:
            calculated_metric = metric.calculate_metric(audio)
            calculated_metrics[metric] = calculated_metric
            audio.cache_metric(metric, calculated_metric)

    return calculated_metrics


def get_most_similar(unknown_audio, other_audios, metrics):
    """
    Finds the most similar audio to an unknown audio, using the given metric flags.

    unknown_audio: Audio object, or string representing path, of the audio we want to find the most similar performer to
    other_audios: list of Audio objects, or string representing path, to compare unknown_audio to
    metrics: list of MetricCalculators

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

    unknown_audio_metrics = calculate_metrics(unknown_audio, metrics)

    # dict of metrics indexed by audio
    other_audios_metrics = {}
    for other_audio in other_audios_objs:
        other_audios_metrics[other_audio] = calculate_metrics(other_audio, metrics)

    print("Calculating similarities...")
    similarities = []
    
    for other_audio in other_audios_metrics:
        similarity_sum = 0
        metrics = other_audios_metrics[other_audio]
        for metric in metrics:
            metric_value = metrics[metric]
            unknown_audio_metric_value = unknown_audio_metrics[metric]
            similarity = metric.calculate_similarity(
                unknown_audio, other_audio, unknown_audio_metric_value, metric_value)
            similarity_sum += similarity

        # now calculate mean similarity and add to our list
        similarities.append(similarity_sum / len(metrics))

    index = similarities.index(max(similarities))


    return (max(similarities), other_audios[index])


