import openai
import numpy as np
from chatagent.agents.agent_db import agents_registry

client = openai.OpenAI()

def get_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return np.array(response.data[0].embedding)

agent_names = [agent['name'] for agent in agents_registry]
agent_descriptions = [agent['description'] for agent in agents_registry]
agent_embeddings = np.array([get_embedding(desc) for desc in agent_descriptions])

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_relevant_agents(query, top_k=None, threshold=None):
    if top_k is None and threshold is None:
        top_k = 3
    query_embedding = get_embedding(query)
    cos_scores = np.array([cosine_similarity(emb, query_embedding) for emb in agent_embeddings])
    if threshold is not None:
        mask = cos_scores >= threshold
        filtered_indices = np.argsort(cos_scores[mask])[::-1]
        relevant_indices = np.where(mask)[0][filtered_indices]
    else:
        relevant_indices = np.argsort(cos_scores)[::-1]
    if top_k is not None:
        relevant_indices = relevant_indices[:top_k]
    return [{"name": agent_names[i], "description": agent_descriptions[i]} for i in relevant_indices]

if __name__ == "__main__":
    user_query = "I need to send an email about AI jobs"
    res1 = get_relevant_agents(user_query, top_k=2)
    print("Top 2:", res1)
    res2 = get_relevant_agents(user_query, threshold=0.5)
    print("Above 0.5:", res2)
    res3 = get_relevant_agents(user_query, top_k=3, threshold=0.4)
    print("Top 3 above 0.4:", res3)
    res4 = get_relevant_agents(user_query)
    print("Default:", res4)
