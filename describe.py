class RecentChangeSignal:
    '''This class is all about the last data point.
    '''
    increase = False
    decrease = False

    # Always positive
    delta = 0

    # Value of previous data pint.
    t_n1_value = 0

    def compute(self, series):
        # Compare t_n to t_(n-1)
        if len(series) < 2:
            return
        t_n = series[-1]['value']
        t_n1 = series[-2]['value']
        if t_n < t_n1:
            self.decrease = True
        elif t_n > t_n1:
            self.increase = True

        diff = abs(t_n - t_n1)
        self.delta = diff
        self.t_n1_value = t_n1

        # TODO(ian): Indicate whether change was small or large.

    def __str__(self):
        return '''RecentChange:
        Increase: %r
        Decrease: %r
        Delta: %f
        ''' % (self.increase, self.decrease, self.delta)

class TrendKeeperSignal:
    lookback_label = ''
    lookback_value = -1

    # Does the last data point keep or reverse the previous trend?
    keeps = False
    reverses = False

    # How does the last data point compare to lookback point?
    lower_than = False
    higher_than = False

    def __init__(self, lookback=2):
        self._lookback = lookback

    def compute(self, series):
        if len(series) < 2:
            return

        self.lookback_label = series[-self._lookback]['label']
        self.lookback_value = series[-self._lookback]['value']

        # Compute lower/higher than lookback
        self.lower_than = self.lookback_value - series[-1]['value'] > 0
        self.higher_than = not self.lower_than

        # Compute trend keeping
        values = [x['value'] for x in series]
        deltas = [values[idx] - values[idx-1] for idx in range(1, len(values))]

        # Start at present and go back in time
        deltas.reverse()
        tn = values[0]
        count = 0
        for idx in range(1, len(deltas)):
            tx = deltas[idx]
            if tx * tn > 0:
                # Numbers are both negative or positive
                self.keeps = True
            else:
                self.keeps = False
                break

            count += 1
            if count > self._lookback:
                break

        self.reverses = not self.keeps

    def __str__(self):
        return '''TrendKeeper (lookback=%d):
        Keeps: %r
        Reverses: %r
        Lower than lookback: %r
        Higher than lookback: %r
        ''' % (self._lookback, self.keeps, self.reverses, self.lower_than, self.higher_than)


class Signals:
    def __init__(self):
        self.recent_change = RecentChangeSignal()
        self.trend_keeper_2 = TrendKeeperSignal(lookback=2)
        self.trend_keeper_3 = TrendKeeperSignal(lookback=3)
        self.trend_keeper_6 = TrendKeeperSignal(lookback=6)
        self.trend_keeper_9 = TrendKeeperSignal(lookback=9)
        self.trend_keeper_12 = TrendKeeperSignal(lookback=12)
        self.trend_keeper_max = None

        self._signal_helpers = [
            self.recent_change,
            self.trend_keeper_2,
            self.trend_keeper_3,
            self.trend_keeper_6,
            self.trend_keeper_9,
            self.trend_keeper_12,
            self.trend_keeper_max,
        ]

    def compute(self, series):
        # Set up dynamic signals
        self.trend_keeper_max = TrendKeeperSignal(lookback=len(series))

        # Compute
        self.recent_change.compute(series)
        self.trend_keeper_2.compute(series)
        self.trend_keeper_3.compute(series)
        self.trend_keeper_6.compute(series)
        self.trend_keeper_9.compute(series)
        self.trend_keeper_12.compute(series)
        self.trend_keeper_max.compute(series)
        # self.overall_trend.compute(series)

    def __str__(self):
        return '\n\n'.join(str(x) for x in self._signal_helpers)

def describe(series, unit='month'):
    signals = Signals()
    signals.compute(series)

    print signals

    t_n = series[-1]
    recent = signals.recent_change
    ret = 'The latest data point in %s was %f.' % (t_n['label'], t_n['value'])
    ret += ' This is a %f %s from the previous value of %f.' % \
            (recent.delta,
             'increase' if recent.increase else 'decrease',
             recent.t_n1_value,)

    trend2 = signals.trend_keeper_2
    if trend2.keeps:
        ret += ' This keeps the trend from %s, which recorded %f' % \
                (trend2.lookback_label,
                 trend2.lookback_value)
    if trend2.reverses:
        ret += ' This reverses the trend from %s, which recorded %f' % \
                (trend2.lookback_label,
                 trend2.lookback_value)

    print ret


describe([
    {
        'label': 'January',
        'value': 2.50,
    },
    {
        'label': 'February',
        'value': 2.74,
    },
    {
        'label': 'March',
        'value': 2.38,
    },
    {
        'label': 'April',
        'value': 2.20,
    },
    {
        'label': 'May',
        'value': 1.87,
    },
    {
        'label': 'June',
        'value': 1.63,
    },
    {
        'label': 'July',
        'value': 1.73,
    },
    {
        'label': 'August',
        'value': 1.94,
    },
    {
        'label': 'September',
        'value': 2.23,
    },
    {
        'label': 'October',
        'value': 2.04,
    },
    {
        'label': 'November',
        'value': 2.20,
    },
    {
        'label': 'December',
        'value': 2.11,
    },
])
