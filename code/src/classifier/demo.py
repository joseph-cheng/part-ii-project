import metrics.metric_calculator as metric_calculator
import itertools
import util

if __name__ == "__main__":
    chosen_audio = util.read_audio("../../res/data_demo/participant_1_moonlightsonata_1.wav")

    other_audios = [
            util.read_audio("../../res/data_demo/participant_2_moonlightsonata_1.wav"),
            util.read_audio("../../res/data_demo/participant_1_moonlightsonata_2.wav"),
            ]
















































    metric_combinations = itertools.chain.from_iterable(itertools.combinations(metric_calculator.METRICS, i) for i in range(1, len(metric_calculator.METRICS)+1))
    metric_results = {}
    for metric_comb in metric_combinations:
        similarity, guess = metric_calculator.get_most_similar(chosen_audio, other_audios, metric_comb)

        metric_results[metric_comb] = other_audios.index(guess)

    for metric_comb in metric_results:
        print(f"{str(metric_comb):>45} : {str(metric_results[metric_comb])}")

