import unittest
from covid_charts import charts

class TestChart(unittest.TestCase):
    chart = charts.Chart(timeframe='1W', c_type='geo',
                        region='Bundesrepublik Deutschland', data=['cases', 'deaths'])

    def test_init(self):
        self.assertEqual(self.chart.timeframe, '1W')
        self.assertEqual(self.chart.c_type, 'geo')
        self.assertEqual(self.chart.region, 'Bundesrepublik Deutschland')
        self.assertEqual(self.chart.data, ['cases', 'deaths'])
        self.assertEqual(self.chart.content, 'cases, deaths')

    def test_get_data(self):
        pass

    def test_plot(self):
        pass