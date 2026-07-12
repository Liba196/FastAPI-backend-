import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Instantiate the client using your API key
client = genai.Client(api_key= os.getenv("GOOGLE_API_KEY"))

# Generate the embedding response
result = client.models.embed_content(
    model="gemini-embedding-001", 
    contents="Retirement pension eligibility requires ten years of contributory service.",
)

# FIX: Validate the list exists and contains items before indexing [0]
if result.embeddings and len(result.embeddings) > 0:
    # 1. Grab the first ContentEmbedding object out of the list wrapper
    embedding_obj = result.embeddings[0] 
    
    # 2. Extract the literal float list from the .values attribute
    if embedding_obj.values:
        vector = embedding_obj.values
        
        print("Vector length:", len(vector))  # Safe for Sized checking
        print("First 5 numbers:", vector[:5])
else:
    print("No embeddings were returned by the API.")




