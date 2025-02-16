from neo4j import GraphDatabase
import pandas as pd
import re

# Neo4j Connection Credentials
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "N123456780"

# Connect to Neo4j
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
print("Successfully connected to Neo4j!")

# Load CSV Data
print("Loading the CSV file...")

df = pd.read_csv('DataSet-PlantBio.csv', encoding='ISO-8859-1')
print(f"CSV loaded with {len(df)} rows.")


# Function to Extract Phytochemical Names (Removes Descriptions)
def extract_phytochemicals(text):
    if pd.isna(text):  # Handle NaN values
        return []
    phytochemicals = re.split(r'\n|,', text)  # Split by new line or comma
    phytochemicals = [item.split(":")[0].strip() for item in phytochemicals if ":" in item]  # Extract only names
    return phytochemicals


# Function to Insert Data into Neo4j
def insert_data(tx, plant, phytochemical):
    query = """
    MATCH (p:Plant {name: $plant})
    MERGE (ph:Phytochemical {name: $phytochemical})
    MERGE (p)-[:CONTAINS]->(ph)
    """
    tx.run(query, plant=plant, phytochemical=phytochemical)


# Function to Create Graph Nodes and Relationships
def create_plant_phytochemical_graph(plant_name):
    print(f"Creating graph for plant: {plant_name}...")
    with driver.session() as session:
        print("Creating Plant node in Neo4j...")
        session.run("MERGE (p:Plant {name: $plant_name})", plant_name=plant_name)
        print(f"Plant node for '{plant_name}' created or matched.")

        plant_data = df[df['Plant Name'].str.contains(plant_name, case=False, na=False)]
        print(f"Found {len(plant_data)} entries in CSV for '{plant_name}'.")

        for _, row in plant_data.iterrows():
            phytochemical_text = row['Phytochemicals and their properties for cancer prevention']
            phytochemicals = extract_phytochemicals(phytochemical_text)

            print(f"Extracted Phytochemicals for {plant_name}: {phytochemicals}")

            for phytochemical in phytochemicals:
                session.execute_write(insert_data, plant_name, phytochemical)


# Function to Fetch Graph Data for Visualization
def fetch_graph_data(plant_name):
    print(f"Fetching graph data for plant: {plant_name}...")
    with driver.session() as session:
        query = """
        MATCH (p:Plant {name: $plant_name})-[:CONTAINS]->(ph)
        RETURN ph.name AS phytochemical
        """
        results = session.run(query, plant_name=plant_name)
        phytochemicals = [record["phytochemical"] for record in results]

        print(f"Found {len(phytochemicals)} connections between plant and phytochemicals.")

        nodes = [{"id": i, "label": phytochemical} for i, phytochemical in enumerate(phytochemicals)]
        edges = [{"from": 0, "to": i} for i in range(1, len(phytochemicals) + 1)]

        graph_data = {"nodes": [{"id": 0, "label": plant_name}] + nodes, "edges": edges}
        print(f"Graph Data: {graph_data}")
        return graph_data


if __name__ == "__main__":
    plant_name = "Aloe Vera"
    create_plant_phytochemical_graph(plant_name)
    fetch_graph_data(plant_name)

    driver.close()
