import util
import chroma
import dynamics
import offsets
import tempo
import timbre

CHROMA   = 2**0
DYNAMICS = 2**1
OFFSETS  = 2**2
TEMPO    = 2**3
TIMBRE   = 2**4

METRIC_FUNCTIONS = {
        CHROMA:   chroma.calculate_chroma_metric,
        DYNAMICS: dynamics.calculate_dynamics_metric,
        OFFSETS:  offsets.calculate_offsets_metric,
        TEMPO:    tempo.calculate_tempo_metric,
        TIMBRE:   timbre.calculate_timbre_metric,
        }

METRIC_STRINGS = {
        CHROMA:   "CHROMA",
        DYNAMICS: "DYNAMICS",
        OFFSETS:  "OFFSETS",
        TEMPO:    "TEMPO",
        TIMBRE:   "TIMBRE",
        }


def calculate_metrics(audio, metric_flags):
    """
    Calculates the chosen metrics for a particular piece of audio

    audio: either a string representing a path to a wavfile, or an Audio object
    metric_flags: binary flags of the metrics to calculate

    returns: a list of tuples, each containing the metric flag and the calculated metric
    """

    calculated_metrics = []

    if isinstance(audio, str):
        audio = util.read_audio(audio)

    for metric in METRIC_FUNCTIONS:
        if metric & metric_flags:
            print(f"Calculating {METRIC_STRINGS[metric]} metric...")
            metric_function = METRIC_FUNCTIONS[metric]
            calculated_metric = metric_function(audio)
            calculated_metrics.append((metric, calculated_metric))
            print(calculated_metric)

    return calculated_metrics

print(calculate_metrics("/home/joe/Documents/cambridge/ii/part-ii-project/code/res/data/participant_1_prelude_1.wav", OFFSETS ))

