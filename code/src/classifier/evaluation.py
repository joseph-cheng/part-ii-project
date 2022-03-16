import metrics.metric_calculator as metric_calculator
import matplotlib.pyplot as plt
import numpy as np
import util
import os
import os.path
import itertools
import transformations.noise as noise
import transformations.reverb as reverb

TRANSFORMS = [
        noise.Noise("../../res/noise/room.wav", level=1.0),
        reverb.Reverb("../../res/irs/studio.wav")
]

data_dir = "../../res/data"

class Performance:
    def __init__(self, performer, piece, performance_number, audio, path):
        """
        performer: identifier representing a performer
        piece: name of piece
        performance: number representing which performance it was
        audio: an Audio object of the performance, we don't read this in straight from path in case we apply a transform
        path: path to the original audio source
        """
        self.performer = performer
        self.piece = piece
        self.performance_number = performance_number
        self.audio = audio
        self.path = path


    def __repr__(self):
        return f"Performer: {self.performer}, Piece: {self.piece}, Performance: {self.performance_number}"


# cache of audios already found in get_files, maps (path, transforms) tuples to audio objects
# need this or we recreate the Audio objects on each call of evaluate_metrics, losing caching
AUDIO_CACHE = {}

def get_files(data_dir, transforms=[]):
    """
    processes file names in a directory according to the filename format i use: "participant_{participant number}_{piece name}_{performance number}.wav"

    data_dir: path to the directory containing the performance files
    transforms: list of Transformations to apply to each audio file, defaults to []

    returns: a dictionary indexed by piece name, participant number, then performance number, containing Performance objects.
    """
    files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    # nested dictionary of Performances, indexed by piece (name), then performer (number), then performance (number)
    file_dict = {}

    for filename in files:
        # string processing based on format of filenames
        filename_l = filename.split("_")
        participant_number = int(filename_l[1])
        piece_name = filename_l[2]
        performance_number = int(filename_l[3][0])
        full_path = os.path.join(data_dir, filename)

        audio = AUDIO_CACHE.get((full_path, tuple(transforms)))
        if audio == None:
            # read the audio data
            audio = util.read_audio(full_path)
            # apply transforms repeatedly
            for transform in transforms:
                audio = transform.apply(audio)

            AUDIO_CACHE[full_path, tuple(transforms)] = audio

        performance = Performance(participant_number, piece_name, performance_number, audio, full_path)

        # enter default values, maybe use defaultdict? probs doesn't matter
        if piece_name not in file_dict:
            file_dict[piece_name] = {}
        if participant_number not in file_dict[piece_name]:
            file_dict[piece_name][participant_number] = {}
        file_dict[piece_name][participant_number][performance_number] = performance

    return file_dict

def evaluate_metrics(data_dir, metrics, transforms=[]):
    """
    Evaluates a set of metrics on all of the files in a directory

    data_dir: string of path to data directory
    metrics: list of MetricCalculators
    transforms: list of Transformations that are applied to each performance audio, defaults to []

    returns: float from 0-1 representing percentage of trials guessed correctly
    """
    print(f"Evaluating metrics: {metrics}")
    print(f"Using transforms: {transforms}")

    files = get_files(data_dir, transforms=transforms)

    total_trials = 0
    total_correct = 0

    # need to choose each performance once to be our 'unknown' performance
    arbitrary_piece = list(files.keys())[0]
    # assuming 2 performances from each performer
    performances_per_piece = len(files[arbitrary_piece]) * 2

    # for each target performance, run our system
    for piece in files:
        for performance_num in range(1, performances_per_piece+1):
            chosen_performance = None
            other_performances = []
            print(performance_num)
            for performer in files[piece]:
                for performance in files[piece][performer]:
                    # this relies on the fact that performer and performance are just numbers and sensibly named
                    print(performer, performance)
                    if (performer-1)*2 + performance == performance_num:
                        chosen_performance = files[piece][performer][performance]
                    else:
                        other_performances.append(files[piece][performer][performance])

            print(f"Using {chosen_performance}...")
            similarity, detected_performance_audio = metric_calculator.get_most_similar(chosen_performance.audio, [p.audio for p in other_performances], metrics)

            detected_performance = None

            # find matching Performance for detected_performance_path
            for performance in other_performances:
                if performance.audio == detected_performance_audio:
                    detected_performance = performance
                    break

            if detected_performance.performer == chosen_performance.performer and detected_performance.piece == chosen_performance.piece:
                total_correct += 1
                print(f"Correctly detected:\n{chosen_performance}\nas\n{detected_performance}")
            else:
                print(f"Incorrectly detected:\n{chosen_performance}\nas\n{detected_performance}")

            total_trials += 1


    return total_correct/total_trials


if __name__ == "__main__":
    """
    noise_levels = np.linspace(0.0, 40.0, 20)
    peak_metrics = []
    median_metrics = []
    for noise_level in noise_levels:
        noise_transform = noise.Noise("../../res/noise/room.wav", level=noise_level)
        metric_results = {}

        metric_combinations = itertools.chain.from_iterable(itertools.combinations(metric_calculator.METRICS, i) for i in range(1, len(metric_calculator.METRICS)+1))
        metric_combinations = [(metric_calculator.METRICS[1],)]
        for metric_combination in metric_combinations:
            metric_results[metric_combination] = evaluate_metrics(data_dir, metric_combination)

        peak_metrics.append(max(metric_results.values()))
        median_metrics.append(np.median(list(metric_results.values())))
        print(metric_results)

    plt.plot(noise_levels, peak_metrics, label="Peak metric performance")
    plt.plot(noise_levels, median_metrics, label="Median metric performance")
    plt.legend()
    plt.show()
    """
    metric_results = {}

    metric_combinations = itertools.chain.from_iterable(itertools.combinations(metric_calculator.METRICS, i) for i in range(1, len(metric_calculator.METRICS)+1))
    for metric_combination in metric_combinations:
        metric_results[metric_combination] = evaluate_metrics(data_dir, metric_combination)

    print(metric_results)












