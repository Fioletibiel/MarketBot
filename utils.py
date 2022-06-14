import csv
import datetime
import json
import os
from random import randint


def load_data(interpolation_range: int = 1000, path='history.csv') -> dict:
    """

    """
    def str_to_date(date_string):
        return datetime.date.fromisoformat(date_string)

    def interpolate(data_to_interpolate, max_range):   # ta funkcja rozszerza wartości do skali od zera do wybranej.
        response = []
        for d in data_to_interpolate:
            response.append(d - min(data_to_interpolate))
        data_to_interpolate = response
        response = []
        for d in data_to_interpolate:
            response.append(int(d * max_range / max(data_to_interpolate)))
        return response

    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        kurs = []
        data = []
        # zmiana = []
        # try:
        #     kurs.append(float(csv_reader[0]['Kurs']))
        #     data.append(str_to_date(csv_reader[0]['Data']))
        #     # zmiana.append(float(csv_reader[0]['Zmiana']))
        # except Exception:
        #     ...
        for row in csv_reader:
            kurs.append(float(row['Kurs']))
            data.append(str_to_date(row['Data']))
            # zmiana.append(float(row['Zmiana']))
        kurs.reverse()
        data.reverse()
        # zmiana.reverse()

    history = {
        'kurs': interpolate(kurs, interpolation_range),
        'data': data,
        # 'zmiana': zmiana
    }

    return history


def init_data_range(data: list, start: int = 0, end: int = 100) -> list:
    """

    """
    if start == end:
        start = 0
        end = 100
    if start > end:
        temp = start
        start = end
        end = temp
    if end > 100: end = 100
    if start < 0: start = 0
    start = int(start * len(data) / 100)
    end = int(end * len(data) / 100)
    return data[start:end-1]  # ponieważ jest end-1 a nie end to ostatni element data nie jest brany pod uwagę; akurat żeby wziąć go nie na features, ale na predictions


def init_chunk_size(data_len: int, chunks_quantity: int) -> tuple:
    """

    """
    if chunks_quantity < 1: chunks_quantity = 1   # nie można dzielić przez 0, i nie ma sensu dzielić przez minusowe wartości
    if chunks_quantity > data_len: chunks_quantity = data_len
    chunk = int(data_len/chunks_quantity)
    rest = data_len % chunks_quantity
    return chunk, rest


def near_value_cloud(value, percent) -> tuple:
    """
    Dając jakąś wartość liczbową zwraca jej sąsiedztwo z zadanym procentem otoczenia
    """
    if percent < 0: percent = 0
    if percent > 100: percent = 100
    tolerance = int(value * percent / 100)
    return value - tolerance, value + tolerance


#########


def count_mean(data: list, start: int = 0, end: int = 100) -> int:
    """
    oblicza średnią z listy wejściowej, od wybranego miejsca do wybranego, wskazanego poprzez procent całości listy, z którego do którego ma być obliczona
    """
    temp = init_data_range(data, start, end)
    count = 0
    for d in temp:
        count += d
    return int(count/len(temp))


def count_median(data: list, start: int = 0, end: int = 100) -> int:
    """

    """
    def quicksort(data_to_sort):
        if len(data_to_sort) < 2:
            return data_to_sort
        low, same, high = [], [], []
        pivot = data_to_sort[randint(0, len(data_to_sort) - 1)]
        for item in data_to_sort:
            if item < pivot:
                low.append(item)
            elif item == pivot:
                same.append(item)
            elif item > pivot:
                high.append(item)
        return quicksort(low) + same + quicksort(high)
    temp = init_data_range(data, start, end)
    temp = quicksort(temp)
    return temp[int(len(temp)/2)]


def count_percentail_lt(data: list, start: int = 0, end: int = 100) -> list:
    """
    Najpierw trzeba wygenerować kilka punktów, dla których będzie się liczyło percentyl, a potem go dla nich policzyć. Wersja z wartościami mniejszymi od zadanych.
    """
    temp = init_data_range(data, start, end)
    data_len = len(temp)
    results = []
    order_of_magnitude = int("1" + ("0" * (len(str(data_len)) - 1)))
    leap = 10
    while leap < order_of_magnitude:
        count = 0
        for t in temp:
            if t < leap:
                count += 1
        results.append(count)
        leap *= 10
    return results


def count_percentail_gt(data: list, start: int = 0, end: int = 100) -> list:
    """
    Najpierw trzeba wygenerować kilka punktów, dla których będzie się liczyło percentyl, a potem go dla nich policzyć. Wersja z wartościami większymi od zadanych.
    """
    temp = init_data_range(data, start, end)
    data_len = len(temp)
    results = []
    order_of_magnitude = int("1" + ("0" * (len(str(data_len)) - 1)))
    leap = 10
    while leap < order_of_magnitude:
        count = 0
        for t in temp:
            if t > leap:
                count += 1
            results.append(count)
        leap *= 10
    return results


def count_is_gt_median(data: list, value:int, start: int = 0, end: int = 100) -> bool:
    """
    Tu jest pomysł, by zastosować pewną strategię inwestycyjną, która sprawdzałaby czy dana wartość jest większa od mediany.
    """
    temp = init_data_range(data, start, end)
    median = count_median(temp, start, end)
    return value > median


def count_is_lt_median(data: list, value:int, start: int = 0, end: int = 100) -> bool:
    """
    Tu jest pomysł, by zastosować pewną strategię inwestycyjną, która sprawdzałaby czy dana wartość jest mniejsza od mediany.
    """
    temp = init_data_range(data, start, end)
    median = count_median(temp, start, end)
    return value < median


def count_is_gt_mean(data: list, value:int, start: int = 0, end: int = 100) -> bool:
    """
    Tu jest pomysł, by zastosować pewną strategię inwestycyjną, która sprawdzałaby czy dana wartość jest większa od średniej.
    """
    temp = init_data_range(data, start, end)
    mean = count_mean(temp, start, end)
    return value > mean


def count_is_lt_mean(data: list, value:int, start: int = 0, end: int = 100) -> bool:
    """
    Tu jest pomysł, by zastosować pewną strategię inwestycyjną, która sprawdzałaby czy dana wartość jest mniejsza od średniej.
    """
    temp = init_data_range(data, start, end)
    mean = count_mean(temp, start, end)
    return value < mean


##########


def generate_is_gt_prediction_data(data: list, value: int, start: int = 0, end: int = 100) -> list:
    """
    Tu jest pomysł, by zastosować pewną strategię inwestycyjną, która sprawdzałaby czy dana wartość jest większa od wartości predykcyjnej.
    Generuje nową listę danych.
    """
    temp = init_data_range(data, start, end)
    return [1 for x in temp if x > value]


def generate_is_lt_prediction_data(data: list, value: int, start: int = 0, end: int = 100) -> list:
    """
    Tu jest pomysł, by zastosować pewną strategię inwestycyjną, która sprawdzałaby czy dana wartość jest mniejsza od wartości predykcyjnej.
    Generuje nową listę danych.
    """
    temp = init_data_range(data, start, end)
    return [1 for x in temp if x<value]


def count_frequency_dict(data: list, start: int = 0, end: int = 100) -> dict:
    """
    Zwraca słownik, gdzie kluczami są kolejne wartości z wybranego przedziału danych wejściowych, a wartości są częstotliwością ich występowania.
    """
    temp = init_data_range(data, start, end)
    numbers = set(temp)
    frequencies_temp = {}
    for n in numbers:
        count = 0
        for t in temp:
            if n == t:
                count += 1
        frequencies_temp[n] = count
    frequencies = {}
    for i in range(len(frequencies_temp)):  # tutaj jeszcze znormalizowuje się zwracany słownik z częstotliwościami, ponieważ są w nim tylko klucze występujących wartości, a niewystępujących trzeba także dodać i wartość wypełnić zerami.
        if i in frequencies_temp:
            frequencies[i] = frequencies_temp[i]
        else:
            frequencies[i] = 0
    return frequencies


def count_frequency_list(data: list, start: int = 0, end: int = 100) -> list:
    """
    Zwraca listę z kolejnymi wartościami z wybranego przedziału danych wejściowych i częstotliwością ich występowania.
    """
    frequencies_list = []
    for k, v in count_frequency_dict(data, start, end).items():
        frequencies_list.append(v)
    return frequencies_list


def reverse_frequencies(data: list, start: int = 0, end: int = 100) -> list:    # TODO można rozszerzyć o histogram i rozciągnięcie histogramu
    """
    Odwraca i sortuje listę częstotliwości, czyli najpierw są posortowane częstotliwości występowania, a potem jakie wartości danych wejściowych tym częstotliwościom odpowiadają.
    Zwraca listę wartości, ale w kolejności posortowanych odpowiadających im częstotliwości.
    """
    def quicksort_2d(data_to_sort):
        if len(data_to_sort) < 2:
            return data_to_sort
        low, same, high = [], [], []
        pivot = data_to_sort[randint(0, len(data_to_sort) - 1)][0]
        for k, v in data_to_sort:
            if k < pivot:
                low.append([k, v])
            elif k == pivot:
                same.append([k, v])
            elif k > pivot:
                high.append([k, v])
        return quicksort_2d(low) + same + quicksort_2d(high)
    reversed_frequencies = []
    for key, value in count_frequency_dict(data, start, end).items():
        reversed_frequencies.append([value, key])
    frequencies = quicksort_2d(reversed_frequencies)
    result = []
    for f in frequencies:
        result.append(f[1])
    return result


def generate_changes_data(data: list, start: int = 0, end: int = 100) -> list:
    """

    """
    temp = init_data_range(data, start, end)
    changes = []
    d_old = 0
    for d in temp:
        changes.append(d - d_old)
        d_old = d
    changes[0] = 0  # ponieważ pierwsze będzie niemiarodajne, ponieważ nie ma z czym go porównać, nadam mu zmianę równą 0
    return changes


def generate_percent_changes_data(data: list, start: int = 0, end: int = 100) -> list:
    """

    """
    temp = init_data_range(data, start, end)
    changes = []
    d_old = 1
    for d in temp:
        if d != 0:
            changes.append((d - d_old) * 100 / d_old)
        else:
            changes.append(100) # ponieważ jeżeli poprzednia wartość wynosiła 0, następna jakakolwiek by nie była, procentowo będzie poza zakresem, niech więc równa się 100
        d_old = d
    changes[0] = 0  # ponieważ pierwsze będzie niemiarodajne, ponieważ nie ma z czym go porównać, nadam mu zmianę równą 0
    return changes


def chunk_data(data: list, start = 0, end = 100, chunks_quantity: int = 1, picked_value: str = 'medians') -> list:
    """
    próbkuje dane wejściowe wg zadanej częstotliwości, zmniejszając dokładność / uśredniając dane w zadanych okresach; dzieli len(data) na (nie przez!) ilość próbek wyrażoną przez chunks_quantity
    """
    temp_init = init_data_range(data, start, end)
    data_len_init = len(temp_init)
    chunk, rest = init_chunk_size(data_len_init, chunks_quantity)   # jeżeli chunks_quantity=1 to chunk=data_len, czyli bardzo kiepsko; jeżeli chunks_quantity=2 to chunk=int(data_len/2) czyli są dwie próbki, itd.
    temp = temp_init[rest:]
    data_len = len(temp)
    chunked_data = []
    chunk_count = 0

    if picked_value == 'begginings':
        def count(): chunked_data.append(temp[chunk * (chunk_count - 1)])
    elif picked_value == 'means':
        def count(): chunked_data.append(count_mean(temp[(chunk * (chunk_count - 1)):(chunk * chunk_count)-1]))
    elif picked_value == 'endings':
        def count(): chunked_data.append(temp[chunk * chunk_count - 1])
    else:
        def count(): chunked_data.append(count_median(temp[(chunk * (chunk_count - 1)):(chunk * chunk_count)-1]))

    for i in range(data_len):
        if i < chunk * chunk_count:
            count()
        if i == chunk * chunk_count:
            chunk_count += 1
            count()
    return chunked_data


def generate_ranges(data: list, start: int = 0, end: int = 100) -> list:
    """
    Ta funkcja generuje listę zakresów [od, do] , np. gdy data_len = 1000, wtedy:
    1) od 0 do 9, od 10 do 19, itd., a także od 0 do 99, od 100 do 199, itd., a także
    2) od 0 do 1000, od 100 do 1000, od 200 do 1000, od 300 do 1000, itd.
    """
    temp = init_data_range(data, start, end)
    data_len = len(temp)
    ranges_list = []

    if data_len <= 100:
        return [[0, data_len - 1]]  # bo mniejszych zbiorów danych nie ma sensu dzielić na jeszcze mniejsze

    order_of_magnitude = int("1" + ("0" * (len(str(data_len)) - 1)))    # oblicza rząd wielkości len(data), czyli jeśli len(data) = 1234 to order_of_magnitude = 1000

    # tutaj generuje się listę zakresów z punktu 1)
    current_leap = 10
    rest = data_len % current_leap
    while current_leap < order_of_magnitude:
        for i in range(rest, data_len)[::current_leap]:
            ranges_list.append([i, i + (current_leap - 1)])
        current_leap *= 10
        rest = data_len % current_leap

    # tutaj generuje się listę zakresów z punktu 2)
    current_leap = 10
    rest = data_len % current_leap
    while current_leap < order_of_magnitude:
        for i in range(rest, data_len)[::current_leap]:
            ranges_list.append([i, data_len])
        current_leap *= 10
        rest = data_len % current_leap

    return ranges_list


def generate_chunk_quantities(data: list, start: int = 0, end: int = 100) -> list:
    """
    Podobnie jak z generate_ranges(data), tylko że generuje listę z różnej wielkości chunkami.
    Generuje od 2 do data_len, przy założeniu, że data_len jest przez tą liczbę podzielna.
    """
    temp = init_data_range(data, start, end)
    data_len = len(temp)
    chunk_quantities_list = []
    for i in range(2, data_len+1):
        if data_len % i == 0:
            chunk_quantities_list.append(i)
    return chunk_quantities_list


def iterate_through_all_chunk_quantities(datas: list, start: int = 0, end: int = 100, chunked_by='medians') -> list:
    """

    """
    list_of_chunked_data_through_all_chunk_quantities = []
    for data in datas:
        chunks_quantities = generate_chunk_quantities(data, start, end)
        for chunks_quantity in chunks_quantities:
            list_of_chunked_data_through_all_chunk_quantities.append(chunk_data(data, start, end, chunks_quantity, picked_value=chunked_by))
    return list_of_chunked_data_through_all_chunk_quantities


def iterate_through_all_ranges(datas: list, start: int = 0, end: int = 100) -> list:
    """

    """
    list_of_cropped_data_through_all_ranges = []
    for data in datas:
        ranges = generate_ranges(data, start, end)
        for r in ranges:
            list_of_cropped_data_through_all_ranges.append(data[r[0]:r[1]])
    return list_of_cropped_data_through_all_ranges


def init_iteration(funcs: list, data: list, start: int = 0, end: int = 100, chunked_by='medians', choice = 1) -> list:
    """

    """
    results = []
    if choice ==1:  # jeśli najpierw robi chunki a potem dla każdego pochunkowania robi ranges
        datas = iterate_through_all_chunk_quantities(iterate_through_all_ranges(datas=data), start, end, chunked_by)
    else:   # jeśli najpierw robi ranges a potem dla każdego range robi chunki
        datas = iterate_through_all_ranges(iterate_through_all_chunk_quantities(datas=data, chunked_by=chunked_by), start, end)
    for d in datas:
        for func in funcs:
            result = func(d)
            if type(result) is list:
                for r in result:
                    results.append(r)
            elif type(result) is dict:
                for k, v in result.items():
                    results.append(v)
            else:
                results.append(result)
    return results


def init(funcs: list, kurs: list, start:int=0, end:int=100) -> tuple:
    """

    """
    # history = load_data(interpolation_range, path)
    # # data = history['data']  # data służy tylko do synchronizacji różnych wykresów, zmian różnych elementów, ze sobą; do wykorzystania w rozwinięciu MerchantBoy do Merchant i MerchantPrince
    # kurs = history['kurs']

    kurs = kurs

    features_1: list = init_iteration(funcs, data=kurs, start=start, end=end, chunked_by='medians')
    features_2: list = init_iteration(funcs, data=kurs, start=start, end=end, chunked_by='means')
    features_3: list = init_iteration(funcs, data=generate_changes_data(kurs), start=start, end=end, chunked_by='medians')
    features_4: list = init_iteration(funcs, data=generate_percent_changes_data(kurs), start=start, end=end, chunked_by='medians')
    features_5: list = init_iteration(funcs, data=count_frequency_list(kurs), start=start, end=end, chunked_by='medians')
    features_6: list = init_iteration(funcs, data=reverse_frequencies(kurs), start=start, end=end, chunked_by='medians')
    features_7: list = init_iteration(funcs, data=generate_is_gt_prediction_data(data=kurs, value=kurs[-1]), start=start, end=end)
    features_8: list = init_iteration(funcs, data=generate_is_lt_prediction_data(data=kurs, value=kurs[-1]), start=start, end=end)

    features: list = features_1 + features_2 + features_3 + features_4 + features_5 + features_6 + features_7 + features_8
    prediction = kurs[-1]
    return features, prediction


def synchro_data(funcs: list, start:int=0, end:int=100, interpolation_range:int=1000, paths:list=None) -> tuple:
    """

    :param funcs:
    :param data:
    :param start:
    :param end:
    :param interpolation_range:
    :param paths:
    :return:
    """
    kursy = []
    daty = []
    if paths is None:
        paths = ['history.csv']
    for path in paths:
        history = load_data(interpolation_range, path=path)
        kursy.append(history['kurs'])
        daty.append(history['data'])

    # TODO: tutaj dodać synchronizację

    featuress = []
    features, prediction = init(funcs, kursy[0], start, end)
    featuress.append(features)
    for kurs in kursy[1:]:
        features, _ = init(funcs, kurs, start, end)
        featuress.append(features)
    return featuress, prediction

def prepare_data_rows(funcs:list=None, start:int=0, end:int=100, interpolation_range:int=1000, paths:list=None) -> tuple:
    """
    Przygotowuje kilka wierszy features, po jednym dla każdego z plików wejściowych;
    oraz jedną wartość prediction, z pierwszego pliku, dla wszystkich.
    """
    # funcs = [count_mean, count_median, count_percentail_gt, count_percentail_lt, count_is_gt_mean, count_is_lt_mean, count_is_gt_median, count_is_lt_median]
    # start = 0
    # end = 100
    # interpolation_range = 1000
    if funcs is None:
        funcs = [count_mean, count_median, count_percentail_gt, count_percentail_lt, count_is_gt_mean, count_is_lt_mean, count_is_gt_median, count_is_lt_median]
    # features, prediction = init(funcs, start, end, interpolation_range)
    featuress, prediction = synchro_data(funcs, start, end, interpolation_range, paths)
    predictions = [prediction] * len(featuress)
    return featuress, predictions

def prepare_data_table(funcs:list=None, interpolation_range:int=1000, paths:list=None, ranges:list=[0, 100]):
    """
    Skleja wiersze z plików (z różnych danych) i ich wartość prediction, z kolejnymi (z tych samych plików) ale dla innych zakresów, tak żeby można było
    podzielić dane do uczenia.
    Dla jednego prepare_data_rows jest po wierszu dla każdego pliku i dla każdych z nich jedna wartość prediction,
    lecz dla kolejnej iteracji prepare_data_rows będzie już inna wartość prediction.
    :return:
    """
    data_table = []
    for range in ranges:
        featuress, predictions = prepare_data_rows(funcs, range[0], range[1], interpolation_range, paths)
        data_table = data_table + featuress


    with open(os.path.join('./venv/input_file/input_data.json'), 'w') as temp_file:
        json.dump(features, temp_file)
    with open(os.path.join('./venv/input_file/predictions.json'), 'w') as temp_file:
        json.dump(prediction, temp_file)


