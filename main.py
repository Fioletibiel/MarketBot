from utils import *


if __name__ == '__main__':

    # history = load_data(range=10)
    # kurs = history['kurs']
    # data = history['data']
    # zmiana = history['zmiana']
    #
    # mean = count_mean(kurs)
    # print("mean: ", mean)
    # median = count_median(kurs)
    # print("median: ", median)
    #
    # frequency = count_frequency(kurs)
    # print("frequency: ", frequency)
    # print("reversed frequencies: ", reverse_frequencies(frequency))
    # print("last encounter: ", kurs[-1])

    interpolation_range = 1000
    funcs = [count_mean, count_median, count_percentail_gt, count_percentail_lt, count_is_gt_mean, count_is_lt_mean, count_is_gt_median, count_is_lt_median]
    paths = 'history.csv'

    prepare_data_table(funcs, 0, 100, interpolation_range, paths)
