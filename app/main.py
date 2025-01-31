from fastapi import FastAPI, UploadFile, File, HTTPException,Query
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import uvicorn
import google.generativeai as genai
import pandas as pd
import json
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

import urllib.parse
#why ?

# Initialize FastAPI app
app = FastAPI()

# MongoDB connection details
# MongoDB credentials
username = urllib.parse.quote_plus(os.getenv("MONGO_USERNAME"))
password = urllib.parse.quote_plus(os.getenv("MONGO_PASSWORD"))
cluster = os.getenv("MONGO_CLUSTER")
options = os.getenv("MONGO_OPTIONS")

# Construct MongoDB URI
MONGO_URI = f"mongodb+srv://{username}:{password}@{cluster}/{options}"
DB_NAME = "test_db"  # Change this as needed
COLLECTION_NAME = "uploaded_data1"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to frontend URL for security)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
ANTHROPIC_API_KEY=os.getenv("CLAUDE_KEY")
genai.configure(api_key=ANTHROPIC_API_KEY)
# claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

try:
    db.command("ping")  # Check if the database is connected
    connection_status = "Database connected successfully"
except Exception as e:
    connection_status = f"Database connection failed: {str(e)}"

# Function to convert MongoDB ObjectId to string
# def convert_objectid(data):
#     if isinstance(data, list):
#         return [{**doc, "_id": str(doc["_id"])} for doc in data]
#     elif isinstance(data, dict):
#         data["_id"] = str(data["_id"])
#         return data
#     return data    

@app.get("/")
def read_root():
   
    return {"message": "heloo world", "db_status": connection_status}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Read the uploaded Excel file
        df = pd.read_excel(file.file)

        # Handle NaN values by replacing them with None (MongoDB-friendly)
        df = df.where(pd.notna(df), None)

        # Convert DataFrame into desired JSON structure
        json_data = [{"content": row.to_dict()} for _, row in df.iterrows()]

        # Delete all existing documents in the collection
        collection.delete_many({})

        # Store new data in MongoDB and get inserted IDs
        result = collection.insert_many(json_data)
        inserted_docs = collection.find({"_id": {"$in": result.inserted_ids}})
        
        # Convert ObjectId to string and format response
        response_data = [{"id": str(doc["_id"]), "content": doc["content"]} for doc in inserted_docs]

        return {
            "message": "New file uploaded and converted successfully"
            
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    

@app.get("/qa")
def query_rag(question: str = Query(..., title="User Query")):
    """
    Fetch relevant data from MongoDB based on the query and use Google's Gemini to generate an answer.
    """
    print(question)

    # Retrieve relevant documents from MongoDB
    query_result = collection.find({}, {"_id": 0})  # Modify query condition as needed
    documents = list(query_result)

    if not documents:
        return {"error": "No relevant data found in the database."}

    # Convert documents to text
    doc_texts = [str(doc) for doc in documents]

    # Compute TF-IDF similarity
    all_texts = [question] + doc_texts
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Get top relevant documents
    top_n = 5
    top_indices = similarity_scores.argsort()[-top_n:][::-1]
    context_data = [documents[i] for i in top_indices]

    # Prepare prompt for Gemini
    print(context_data)
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(f"Context:\n{context_data}\n\nQuestion: {question}")

    return {"answer": response.text}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)