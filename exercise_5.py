import random
import openpyxl


def produce_sample_rtts():

    sample_rtts = [100]

    def next_sample_rtt_main():
        x = random.uniform(0.75, 1.25)
        y = random.uniform(-5, 30)
        return x * sample_rtts[-1] + y

    sample_rtt_funcs = [lambda: 1.75 * sample_rtts[-1],
                        lambda: 0.75 * sample_rtts[-1],
                        lambda: [1.75 * sample_rtts[-1],
                                 0.4 * 1.75 * sample_rtts[-1]],
                        next_sample_rtt_main]
    for i in range(1, 200):
        next_sample_rtt_func = next_sample_rtt_main

        if i >= 19 and (i + 1) % 5 == 0:
            next_sample_rtt_func = random.choice(sample_rtt_funcs)

        rtt_result = next_sample_rtt_func()
        try:
            sample_rtts += [i if i >= 40 else 40 for i in rtt_result]
        except TypeError:
            sample_rtts.append(rtt_result if rtt_result >= 40 else 40)

    return sample_rtts


def compute_timeout_intervals(sample_rtts, a, b):

    estimated_rtts = [40]
    dev_rtts = [0]
    timeout_intervals = [estimated_rtts[0]]

    for sample_rtt in sample_rtts[1:]:
        estimated_rtts.append((1 - a) * estimated_rtts[-1] + a * sample_rtt)

        abs_diff = abs(sample_rtt - estimated_rtts[-1])
        dev_rtts.append((1 - b) * dev_rtts[-1] + b * abs_diff)

        timeout_intervals.append(estimated_rtts[-1] + 4 * dev_rtts[-1])

    return timeout_intervals


def write_result_table(intervals, sample_rtts, sheet=None):
    if not sheet:
        sheet = wb.create_sheet()
    results = [["n", "TimeoutInterval(n-1)", "SampleRTT(n)", "retransmitting"]]
    sheet.append(results[0])
    for i in range(100, 200):
        results.append([i + 1, intervals[i - 1], sample_rtts[i],
                        intervals[i-1] <= sample_rtts[i]])
        sheet.append(results[-1])


if __name__ == "__main__":

    wb = openpyxl.Workbook()
    rtts = produce_sample_rtts()

    a_b_table = [[0.125, 0.125],
                 [0.125, 0.25],
                 [0.125, 0.375],
                 [0.4, 0.25],
                 [0.25, 0.25]]

    ws = wb.active

    for a, b in a_b_table:
        write_result_table(compute_timeout_intervals(rtts, a, b), rtts)

    wb.save("results.xlsx")
