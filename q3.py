import matplotlib.pyplot as plt
import networkx as nx
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

# Define the Bayesian Network structure
model = BayesianNetwork([
    ('TimeOfDay', 'HistoricalCongestion'),
    ('Street', 'HistoricalCongestion'),
    ('Weather', 'CurrentCongestion'),
    ('HistoricalCongestion', 'CurrentCongestion')
])

# Define Conditional Probability Distributions (CPDs)
cpd_time_of_day = TabularCPD(
    variable='TimeOfDay', variable_card=3,
    values=[[0.4], [0.4], [0.2]],  # Morning more likely than evening
    state_names={'TimeOfDay': ['Morning', 'Afternoon', 'Evening']}
)

cpd_street = TabularCPD(
    variable='Street', variable_card=3,
    values=[[0.5], [0.3], [0.2]],
    state_names={'Street': ['Orchard Road', 'Choa Chu Kang Road', 'Marina Bay']}
)

cpd_weather = TabularCPD(
    variable='Weather', variable_card=4,
    values=[[0.4], [0.3], [0.2], [0.1]],  # More likely to be sunny
    state_names={'Weather': ['Sunny', 'Rainy', 'Foggy', 'Cloudy']}
)

cpd_historical = TabularCPD(
    variable='HistoricalCongestion',
    variable_card=3,
    values=[
        [0.3, 0.2, 0.1, 0.4, 0.3, 0.2, 0.5, 0.4, 0.3],  # Low congestion
        [0.4, 0.5, 0.4, 0.3, 0.4, 0.5, 0.3, 0.3, 0.4],  # Medium congestion
        [0.3, 0.3, 0.5, 0.3, 0.3, 0.3, 0.2, 0.3, 0.3]   # High congestion
    ],
    evidence=['TimeOfDay', 'Street'], evidence_card=[3, 3],
    state_names={'HistoricalCongestion': ['Low', 'Medium', 'High'], 'TimeOfDay': ['Morning', 'Afternoon', 'Evening'], 'Street': ['Orchard Road', 'Choa Chu Kang Road', 'Marina Bay']}
)

cpd_current = TabularCPD(
    variable='CurrentCongestion', variable_card=3,
    values=[
        [0.1, 0.2, 0.1, 0.3, 0.2, 0.1, 0.4, 0.3, 0.2, 0.2, 0.3, 0.2],  # Low congestion
        [0.3, 0.4, 0.3, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.3, 0.3, 0.4],  # Medium congestion
        [0.6, 0.4, 0.6, 0.3, 0.4, 0.5, 0.2, 0.3, 0.4, 0.5, 0.4, 0.4]   # High congestion
    ],
    evidence=['Weather', 'HistoricalCongestion'], evidence_card=[4, 3],
    state_names={'CurrentCongestion': ['Low', 'Medium', 'High'], 'Weather': ['Sunny', 'Rainy', 'Foggy', 'Cloudy'], 'HistoricalCongestion': ['Low', 'Medium', 'High']}
)

model.add_cpds(cpd_time_of_day, cpd_street, cpd_weather, cpd_historical, cpd_current)

if not model.check_model():
    raise ValueError("The Bayesian Network model is invalid.")

inference = VariableElimination(model)

def query_and_visualize():
    while True:
        street = input("Enter the street (Orchard Road, Choa Chu Kang Road, Marina Bay): ")
        weather = input("Enter the weather (Sunny, Rainy, Foggy, Cloudy): ")
        time_of_day = input("Enter the time of day (Morning, Afternoon, Evening): ")
        
        if street not in ['Orchard Road', 'Choa Chu Kang Road', 'Marina Bay'] or \
           weather not in ['Sunny', 'Rainy', 'Foggy', 'Cloudy'] or \
           time_of_day not in ['Morning', 'Afternoon', 'Evening']:
            print("Invalid input. Please enter values exactly as shown.")
            continue
        
        query_result = inference.query(
            variables=['CurrentCongestion'],
            evidence={'Street': street, 'Weather': weather, 'TimeOfDay': time_of_day}
        )

        print(f"\nPredicted Current Congestion for {street}, {weather} in the {time_of_day}:")
        print(query_result)

        labels = query_result.state_names['CurrentCongestion']
        congestion_levels = query_result.values.flatten()

        plt.figure(figsize=(8, 5))
        plt.bar(labels, congestion_levels, color=["green", "orange", "red"], alpha=0.7)
        plt.xlabel("Congestion Levels")
        plt.ylabel("Probability")
        plt.title(f"Congestion Prediction: {street}, {weather}, {time_of_day}")
        plt.ylim(0, 1)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.show()

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
    plt.title("Bayesian Network Structure")
    plt.show()

query_and_visualize()
draw_bayesian_network(model)
