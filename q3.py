import random
import pandas as pd
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

model = BayesianNetwork([
    ('Weather', 'CurrentCongestion'),
    ('TimeOfDay', 'HistoricalCongestion'),
    ('HistoricalCongestion', 'CurrentCongestion')
])

cpd_weather = TabularCPD(
    variable='Weather',
    variable_card=3,
    values=[[0.7], [0.2], [0.1]],
    state_names={'Weather': ['Sunny', 'Rainy', 'Foggy']}
)

cpd_time = TabularCPD(
    variable='TimeOfDay',
    variable_card=3,
    values=[[0.4], [0.4], [0.2]],
    state_names={'TimeOfDay': ['Morning', 'Afternoon', 'Evening']}
)

cpd_historical = TabularCPD(
    variable='HistoricalCongestion',
    variable_card=3,
    values=[
        [0.6, 0.3, 0.1],  
        [0.3, 0.4, 0.3],  
        [0.1, 0.3, 0.6]  
    ],
    evidence=['TimeOfDay'],
    evidence_card=[3],
    state_names={'HistoricalCongestion': ['Low', 'Medium', 'High'],
                 'TimeOfDay': ['Morning', 'Afternoon', 'Evening']}
)

cpd_current = TabularCPD(
    variable='CurrentCongestion',
    variable_card=3,
    values=[
        [0.8, 0.6, 0.4, 0.7, 0.5, 0.2, 0.6, 0.4, 0.1],  
        [0.15, 0.3, 0.4, 0.2, 0.3, 0.4, 0.3, 0.4, 0.3], 
        [0.05, 0.1, 0.2, 0.1, 0.2, 0.4, 0.1, 0.2, 0.6]  
    ],
    evidence=['Weather', 'HistoricalCongestion'],
    evidence_card=[3, 3],
    state_names={'CurrentCongestion': ['Low', 'Medium', 'High'],
                 'Weather': ['Sunny', 'Rainy', 'Foggy'],
                 'HistoricalCongestion': ['Low', 'Medium', 'High']}
)

model.add_cpds(cpd_weather, cpd_time, cpd_historical, cpd_current)

if not model.check_model():
    raise ValueError("The Bayesian Network model is invalid.")

inference = VariableElimination(model)

def query_model():
    print("Please enter the following details:")
    weather = input("Weather (Sunny, Rainy, Foggy): ").capitalize()
    time_of_day = input("Time of Day (Morning, Afternoon, Evening): ").capitalize()
    
    valid_weather = ['Sunny', 'Rainy', 'Foggy']
    valid_time_of_day = ['Morning', 'Afternoon', 'Evening']
    
    if weather not in valid_weather or time_of_day not in valid_time_of_day:
        print("\nInvalid input. Please try again with valid values.")
        return

    query_result = inference.query(
        variables=['CurrentCongestion'],
        evidence={'Weather': weather, 'TimeOfDay': time_of_day}
    )
    
    print(f"\nPrediction for {weather} and {time_of_day}:")
    print(query_result)

query_model()
