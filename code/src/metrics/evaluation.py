import metric_calculator
import os
import os.path
import itertools

data_dir = "../../res/data"

class Performance:
    def __init__(self, performer, piece, performance_number, path):
        self.performer = performer
        self.piece = piece
        self.performance_number = performance_number
        self.path = path

    def __repr__(self):
        return f"Performer: {self.performer}, Piece: {self.piece}, Performance: {self.performance_number}"

def get_files(data_dir):
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

        performance = Performance(participant_number, piece_name, performance_number, full_path)

        # enter default values, maybe use defaultdict? probs doesn't matter
        if piece_name not in file_dict:
            file_dict[piece_name] = {}
        if participant_number not in file_dict[piece_name]:
            file_dict[piece_name][participant_number] = {}
        file_dict[piece_name][participant_number][performance_number] = performance

    return file_dict

def evaluate_metrics(data_dir, metrics):
    """
    Evaluates a set of metrics on all of the files in a directory

    data_dir: string of path to data directory
    metrics: list of MetricCalculators

    returns: float from 0-1 representing percentage of trials guessed correctly
    """
    print(f"Evaluating metrics: {metrics}")

    files = get_files(data_dir)

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
                    # this relies on the fact that performer and performance are just numbers
                    print(performer, performance)
                    if (performer-1)*2 + performance == performance_num:
                        chosen_performance = files[piece][performer][performance]
                    else:
                        other_performances.append(files[piece][performer][performance])

            print(f"Using {chosen_performance}...")
            similarity, detected_performance_path = metric_calculator.get_most_similar(chosen_performance.path, [p.path for p in other_performances], metrics)

            detected_performance = None

            # find matching Performance for detected_performance_path
            for performance in other_performances:
                if performance.path == detected_performance_path:
                    detected_performance = performance
                    break

            if detected_performance.performer == chosen_performance.performer and detected_performance.piece == chosen_performance.piece:
                total_correct += 1
                print(f"Correctly detected:\n{chosen_performance}\nas\n{detected_performance}")
            else:
                print(f"Incorrectly detected:\n{chosen_performance}\nas\n{detected_performance}")

            total_trials += 1


    return total_correct/total_trials


metric_results = {}

metric_combinations = itertools.chain.from_iterable(itertools.combinations(metric_calculator.METRICS, i) for i in range(1, len(metric_calculator.METRICS)+1))

for metric_combination in metric_combinations:
    metric_results[metric_combination] = evaluate_metrics(data_dir, metric_combination)

print(metric_results)







