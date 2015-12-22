import math
import random

def f(improved=False):
    last_time = 0
    cong_win = 10
    mss_sent = 0
    sample_rtts = [100]
    estimated_rtts = [40]
    dev_rtts = [0]
    timeout_intervals = [estimated_rtts[0]]

    results = [["n", "TimeoutInterval(n-1)", "SampleRTT(n)", "retransmitting"]]

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

        should_retransmit = False
        next_sample_rtt_func = next_sample_rtt_main

        if i >= 19 and (i + 1) % 5 == 0:
            next_sample_rtt_func = random.choice(sample_rtt_funcs)

        rtt_result = next_sample_rtt_func()
        try:
            sample_rtts += [i if i >= 40 else 40 for i in rtt_result]
        except TypeError:
            sample_rtts.append(rtt_result if rtt_result >= 40 else 40)


        estimated_rtts.append((1 - a) * estimated_rtts[-1] + a * sample_rtts[-1])

        abs_diff = abs(sample_rtts[-1] - estimated_rtts[-1])
        dev_rtts.append((1 - b) * dev_rtts[-1] + b * abs_diff)

        timeout_intervals.append(estimated_rtts[-1] + 4 * dev_rtts[-1])

        if i >=9:
            if random.random() <= loss_prob(sample_rtts[-1], cong_win):
                should_retransmit = True
                if improved and i - last_time > 5:
                    cong_win -=1
                else:
                    cong_win /= 2
                last_time = i
                #print("boom")
            else:

                if timeout_intervals[i-1] <= sample_rtts[i]:
                    should_retransmit = True
                    cong_win /= 2
                else:
                    should_retransmit = False
                    mss_sent += cong_win
                    cong_win += 1

        results.append([i, timeout_intervals[-1], sample_rtts[-1], should_retransmit])
        #print(cong_win)

    print(mss_sent)

    return results



def loss_prob(sample_rtt, cong_win):
    prob_fragment = 1 - math.exp(- cong_win / 25)
    if sample_rtt < 110:
        return 0.6 * prob_fragment
    return 0.85 * prob_fragment


if __name__ == '__main__':
    a = 0.125
    b = 0.25
    f()
    f(True)
