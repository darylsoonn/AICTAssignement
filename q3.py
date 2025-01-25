import matplotlib.pyplot as plt
import networkx as nx
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

model = BayesianNetwork([
    ('TimeOfDay', 'Daylight'),
    ('Daylight', 'Weather'),
    ('Weather', 'CurrentCongestion'),
    ('TimeOfDay', 'HistoricalCongestion'),
    ('HistoricalCongestion', 'CurrentCongestion')
])

cpd_time_of_day = TabularCPD(
    variable='TimeOfDay',
    variable_card=3,
    values=[[0.4], [0.4], [0.2]],
    state_names={'TimeOfDay': ['Morning', 'Afternoon', 'Evening']}
)

cpd_daylight = TabularCPD(
    variable='Daylight',
    variable_card=2,
    values=[
        [0.8, 1.0, 0.0],  
        [0.2, 0.0, 1.0]  
    ],
    evidence=['TimeOfDay'],
    evidence_card=[3],
    state_names={'Daylight': ['Yes', 'No'], 'TimeOfDay': ['Morning', 'Afternoon', 'Evening']}
)

cpd_weather = TabularCPD(
    variable='Weather',
    variable_card=4,
    values=[
        [0.7, 0.0], 
        [0.2, 0.4], 
        [0.1, 0.3], 
        [0.0, 0.3],  
    ],
    evidence=['Daylight'],
    evidence_card=[2],
    state_names={'Weather': ['Sunny', 'Rainy', 'Foggy', 'Cloudy'], 'Daylight': ['Yes', 'No']}
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
        [0.8, 0.6, 0.4, 0.7, 0.5, 0.2, 0.6, 0.4, 0.1, 0.3, 0.5, 0.2],  
        [0.15, 0.3, 0.4, 0.2, 0.3, 0.4, 0.3, 0.4, 0.3, 0.5, 0.4, 0.6], 
        [0.05, 0.1, 0.2, 0.1, 0.2, 0.4, 0.1, 0.2, 0.6, 0.2, 0.1, 0.2]  
    ],
    evidence=['Weather', 'HistoricalCongestion'],
    evidence_card=[4, 3],
    state_names={'CurrentCongestion': ['Low', 'Medium', 'High'], 
                 'Weather': ['Sunny', 'Rainy', 'Foggy', 'Cloudy'], 
                 'HistoricalCongestion': ['Low', 'Medium', 'High']}
)

model.add_cpds(cpd_time_of_day, cpd_daylight, cpd_weather, cpd_historical, cpd_current)

if not model.check_model():
    raise ValueError("The Bayesian Network model is invalid.")

inference = VariableElimination(model)

def query_and_visualize():
    print("Enter the following details:")
    time_of_day = input("Time of Day (Morning, Afternoon, Evening): ").capitalize()
    valid_time_of_day = ['Morning', 'Afternoon', 'Evening']
    if time_of_day not in valid_time_of_day:
        print("Invalid input for time of day.")
        return
    
    daylight = 'Yes' if time_of_day in ['Morning', 'Afternoon'] else 'No'
    weather = input(f"Weather (Sunny, Rainy, Foggy, Cloudy) [Daylight: {daylight}]: ").capitalize()
    valid_weather = ['Sunny', 'Rainy', 'Foggy', 'Cloudy']
    if weather not in valid_weather or (daylight == 'No' and weather == 'Sunny'):
        print("Invalid weather input based on daylight.")
        return

    query_result = inference.query(
        variables=['CurrentCongestion'],
        evidence={'TimeOfDay': time_of_day, 'Weather': weather}
    )
    
    print("\nPredicted Current Congestion:")
    print(query_result)

    labels = query_result.state_names['CurrentCongestion']
    congestion_levels = query_result.values.flatten()

    plt.figure(figsize=(8, 5))
    plt.bar(labels, congestion_levels, color=["green", "orange", "red"], alpha=0.7)
    plt.xlabel("Congestion Levels", fontsize=12)
    plt.ylabel("Probability", fontsize=12)
    plt.title("Predicted Congestion Probabilities", fontsize=14)
    plt.ylim(0, 1) 
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()

    G = nx.DiGraph() 
    for edge in model.edges():
        G.add_edge(edge[0], edge[1])

    pos = nx.spring_layout(G) 
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=12, font_weight='bold', edge_color="gray")
    plt.title("Bayesian Network Structure")
    plt.show()

query_and_visualize()
