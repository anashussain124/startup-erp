"""
AI Service — Handles RAG logic using OpenAI.
"""
from openai import OpenAI
from config import OPENAI_API_KEY
from sqlalchemy.orm import Session
from models.document import CompanyDocument

from models.document_chunk import DocumentChunk

client = OpenAI(api_key=OPENAI_API_KEY)

def chunk_text(text: str, chunk_size: int = 1500) -> list[str]:
    """Split text into chunks of roughly chunk_size characters."""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def generate_summary(text: str) -> str:
    """Generate a 2-3 sentence summary of the text."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a business analyst. Summarize the following document content in 2 concise sentences."},
                {"role": "user", "content": text[:4000]} # Limit input for summary
            ],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Summary Error: {e}")
        return "Summary unavailable."

def generate_document_insights(text: str) -> dict:
    """Generate key insights and smart analytics from document text."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a business intelligence engine. Extract 3 key bullet points and a list of 'Top Topics' from the text."},
                {"role": "user", "content": text[:5000]}
            ],
            response_format={ "type": "json_object" } # Assuming gpt-3.5-turbo-0125+
        )
        # Fallback if json_object is not supported in the user's region/model version
        import json
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        # Simple fallback
        return {"insights": ["New data uploaded"], "topics": ["General"]}

def generate_actionable_suggestion(context: str, query: str) -> dict:
    """Suggest 1 actionable business step based on a query and its context."""
    try:
        prompt = f"Based on this context: {context}\nAnd this query: {query}\nSuggest one 10-word actionable business advice and a category."
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Provide response in JSON: {'advice': '...', 'category': '...'} "},
                {"role": "user", "content": prompt}
            ]
        )
        import json
        return json.loads(response.choices[0].message.content)
    except:
        return {"advice": "Review your latest reports for trends.", "category": "General"}

def query_ai_with_context(query: str, company_id: str, db: Session) -> str:
    """
    RAG Implementation with Chunked Context: 
    1. Fetch relevant chunks.
    2. Build context.
    3. Query OpenAI.
    """
    # 1. Fetch relevant chunks (Simple keyword search for now)
    # Search for chunks containing query words
    query_words = [w for w in query.split() if len(w) > 3]
    chunks = []
    if query_words:
        # Basic text search on chunks
        chunks = db.query(DocumentChunk).filter(
            DocumentChunk.company_id == company_id,
            DocumentChunk.text_content.ilike(f"%{query_words[0]}%")
        ).limit(5).all()
    
    if not chunks:
        # Fallback to most recent chunks if no keyword match
        chunks = db.query(DocumentChunk).filter(DocumentChunk.company_id == company_id).order_by(DocumentChunk.id.desc()).limit(5).all()

    if not chunks:
        return "No company data available. Please upload some documents first."

    # 2. Build context
    context = "\n\n".join([chunk.text_content for chunk in chunks])
    
    # 3. Query OpenAI
    prompt = f"""
    Context from company documents:
    ---
    {context}
    ---
    User Question: {query}
    
    Answer concisely based ONLY on the context. If not found, say "No relevant data found in documents."
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional business AI analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI Query Error: {e}")
        return "Sorry, I encountered an error."
