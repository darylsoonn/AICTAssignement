import matplotlib.pyplot as plt
import networkx as nx
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

model = BayesianNetwork([
    ('TimeOfDay', 'Daylight'),
    ('Daylight', 'Weather'),
    ('Street', 'HistoricalCongestion'),
    ('TimeOfDay', 'HistoricalCongestion'),
    ('HistoricalCongestion', 'CurrentCongestion'),
    ('Weather', 'CurrentCongestion')
])

cpd_time_of_day = TabularCPD(
    variable='TimeOfDay', variable_card=3,
    values=[[0.2], [0.3], [0.5]],  
    state_names={'TimeOfDay': ['Morning', 'Afternoon', 'Evening']}
)

cpd_daylight = TabularCPD(
    variable='Daylight', variable_card=2,
    values=[[0.8, 1.0, 0.0], [0.2, 0.0, 1.0]], 
    evidence=['TimeOfDay'], evidence_card=[3],
    state_names={'Daylight': ['Yes', 'No'], 'TimeOfDay': ['Morning', 'Afternoon', 'Evening']}
)

cpd_weather = TabularCPD(
    variable='Weather', variable_card=4,
    values=[[0.0, 0.2], [0.1, 0.3], [0.3, 0.4], [0.6, 0.1]],  
    evidence=['Daylight'], evidence_card=[2],
    state_names={'Weather': ['Sunny', 'Rainy', 'Foggy', 'Cloudy'], 'Daylight': ['Yes', 'No']}
)

cpd_street = TabularCPD(
    variable='Street', variable_card=3,
    values=[[0.5], [0.3], [0.2]],  
    state_names={'Street': ['Orchard Road', 'Choa Chu Kang Road', 'Marina Bay']}
)

cpd_historical = TabularCPD(
    variable='HistoricalCongestion',
    variable_card=3,
    values=[
        [0.9, 0.7, 0.5, 0.8, 0.6, 0.4, 0.7, 0.5, 0.3], 
        [0.1, 0.2, 0.3, 0.2, 0.3, 0.4, 0.2, 0.3, 0.4],
        [0.0, 0.1, 0.2, 0.0, 0.1, 0.2, 0.1, 0.2, 0.3]
    ],
    evidence=['TimeOfDay', 'Street'],
    evidence_card=[3, 3],
    state_names={
        'HistoricalCongestion': ['Low', 'Medium', 'High'],
        'TimeOfDay': ['Morning', 'Afternoon', 'Evening'],
        'Street': ['Orchard Road', 'Choa Chu Kang Road', 'Marina Bay']
    }
)

cpd_current = TabularCPD(
    variable='CurrentCongestion', variable_card=3,
    values=[
        [0.1, 0.2, 0.3, 0.4, 0.2, 0.3, 0.4, 0.5, 0.3, 0.4, 0.5, 0.6],
        [0.3, 0.3, 0.3, 0.3, 0.4, 0.4, 0.3, 0.3, 0.4, 0.3, 0.3, 0.3],
        [0.6, 0.5, 0.4, 0.3, 0.4, 0.3, 0.3, 0.2, 0.3, 0.3, 0.2, 0.1]
    ],
    evidence=['Weather', 'HistoricalCongestion'],
    evidence_card=[4, 3],
    state_names={
        'CurrentCongestion': ['Low', 'Medium', 'High'],
        'Weather': ['Sunny', 'Rainy', 'Foggy', 'Cloudy'],
        'HistoricalCongestion': ['Low', 'Medium', 'High']
    }
)

model.add_cpds(cpd_time_of_day, cpd_daylight, cpd_weather, cpd_street, cpd_historical, cpd_current)

if not model.check_model():
    raise ValueError("The Bayesian Network model is invalid.")

inference = VariableElimination(model)

def query_and_visualize(time_of_day, street, weather):
    time_of_day_map = {'Morning': 'Morning', 'Afternoon': 'Afternoon', 'Evening': 'Evening'}
    street_map = {'Orchard Road': 'Orchard Road', 'Choa Chu Kang Road': 'Choa Chu Kang Road', 'Marina Bay': 'Marina Bay'}
    weather_map = {'Sunny': 'Sunny', 'Rainy': 'Rainy', 'Foggy': 'Foggy', 'Cloudy': 'Cloudy'}

    if time_of_day not in time_of_day_map:
        raise ValueError("Invalid time of day. Please enter 'Morning', 'Afternoon', or 'Evening'.")
    if street not in street_map:
        raise ValueError("Invalid street. Please enter 'Orchard Road', 'Choa Chu Kang Road', or 'Marina Bay'.")
    if weather not in weather_map:
        raise ValueError("Invalid weather. Please enter 'Sunny', 'Rainy', 'Foggy', or 'Cloudy'.")

    query_result = inference.query(
        variables=['CurrentCongestion'],
        evidence={
            'TimeOfDay': time_of_day,
            'Street': street,
            'Weather': weather
        }
    )
    
    print(f"\nPredicted Current Congestion for {street}, {weather} in the {time_of_day}:")
    print(query_result)

    labels = query_result.state_names['CurrentCongestion']
    congestion_levels = query_result.values.flatten()

    plt.figure(figsize=(8, 5))
    plt.bar(labels, congestion_levels, color=["green", "orange", "red"], alpha=0.7)
    plt.xlabel("Congestion Levels", fontsize=12)
    plt.ylabel("Probability", fontsize=12)
    plt.title(f"Predicted Congestion Probabilities for {street}, {weather} in the {time_of_day}", fontsize=14)
    plt.ylim(0, 1) 
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()

street_input = input("Enter the street (Orchard Road, Choa Chu Kang Road, Marina Bay): ")
weather_input = input("Enter the weather (Sunny, Rainy, Foggy, Cloudy): ")
time_of_day_input = input("Enter the time of day (Morning, Afternoon, Evening): ")

query_and_visualize(time_of_day_input, street_input, weather_input)

def draw_bayesian_network(model):
    G = nx.DiGraph()
    G.add_edges_from(model.edges())

    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 8))
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=2000,
        node_color="skyblue",
        font_size=12,
        font_weight='bold',
        edge_color="gray",
        arrows=True,
        arrowsize=20,
    )
    plt.title("Bayesian Network Structure", fontsize=14)
    plt.show()

draw_bayesian_network(model)
