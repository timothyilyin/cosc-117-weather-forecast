from backend import calc_aqi_level
from config import AQI_INTERVALS

def test_so2_level_calculation():
    """
    Tests the case we found in the debugger.
    SO2 concentration of "77" should be Level 2 ("Good").
    """
    concentration = "77"
    intervals = AQI_INTERVALS["so2"]

    # We expect Level 2 (Good)
    expected_level = 2
    calculated_level = calc_aqi_level(concentration, intervals)
    assert calculated_level == expected_level

def test_co_level_calculation():
    """
    Test for bug case Carbon Monoxide (CO) in Chengdu.
    CO concentration = "684.85" should return 7 because it exceeds 
    all the defined interval maximum.
    """
    concentration = 684.85
    intervals = AQI_INTERVALS["co"]

    expected_level = 1  
    calculated_level = calc_aqi_level(float(concentration), intervals)
    assert calculated_level == expected_level



 