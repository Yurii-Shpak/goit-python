from datetime import datetime
from multiprocessing import Pool


def assertion(a, b, c, d, start_time):
    print(
        f'Time spent is {(datetime.now() - start_time).total_seconds()} seconds.')
    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316,
                 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]


def factorize(*number):
    result = []
    for index in range(len(number)):
        result.append([])
        for i in range(number[index]):
            if number[index] % (i + 1) == 0:
                result[index].append(i + 1)
    return tuple(result)


def factorize_process(number):
    result = []
    for i in range(number):
        if number % (i + 1) == 0:
            result.append(i + 1)
    return result


if __name__ == '__main__':

    start_time = datetime.now()
    a, b, c, d = factorize(128, 255, 99999, 10651060)
    assertion(a, b, c, d, start_time)

    start_time = datetime.now()
    with Pool(processes=4) as pool:
        a, b, c, d = tuple(
            pool.map(factorize_process, (128, 255, 99999, 10651060)))
    assertion(a, b, c, d, start_time)
