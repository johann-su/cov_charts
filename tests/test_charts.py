import unittest
from covid_charts import charts

class TestChart(unittest.TestCase):
    chart = charts.Chart(timeframe='1W', c_type='geo',
                        region='Bundesrepublik Deutschland', data=['cases'])

    def test_chart(self):
        self.assertEquals(self.chart.timeframe, '1W')
        self.assertEquals(self.chart.c_type, 'geo')
        self.assertEquals(self.chart.region, 'Bundesrepublik Deutschland')
        self.assertEquals(self.chart.data, ['cases'])

    
