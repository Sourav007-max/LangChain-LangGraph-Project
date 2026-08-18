"""
=============================================================================
  PHASE 10 — RAG INTEGRATION
  AI Hiring Co-Pilot: Multi-Agent Recruitment Platform using LangGraph
=============================================================================

RAG = Retrieval Augmented Generation

In our platform, RAG enables:
  1. Semantic resume search (find "ML engineers" even if resume says "AI developer")
  2. Similar candidate search ("find someone like our best hire, Jane")
  3. Skill normalization ("React.js" = "ReactJS" = "React")
  4. Historical performance matching (find candidates similar to past hires)
=============================================================================
"""

import os
import json
import uuid
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# LESSON: HOW EMBEDDINGS WORK
# ─────────────────────────────────────────────────────────────────────────────
"""
TEXT EMBEDDING:
────────────────
Text → [numbers] = a point in high-dimensional space

  "Python developer"    → [0.23, -0.87, 0.14, ...]  (1536 numbers)
  "Software engineer"   → [0.21, -0.85, 0.16, ...]  (1536 numbers)
  "Chef"                → [0.78,  0.32, -0.91, ...]  (1536 numbers)

"Python developer" and "Software engineer" are CLOSE in this space.
"Chef" is FAR AWAY.

This is SEMANTIC similarity — meaning-based, not keyword-based!

┌─────────────────────────────────────────────────────────────────────┐
│                  2D Visualization of Embeddings                     │
│                                                                     │
│  high tech        ●Python Dev                                       │
│  experience     ●ML Engineer   ●Software Architect                  │
│                   ●Backend Dev                                      │
│                                                                     │
│                                                                     │
│  cooking skills                              ●Chef                  │
│                                         ●Baker ●Sous Chef           │
│                                                                     │
│  ─────────────────────────────────────────────────────────────────  │
│               low experience           high experience              │
└─────────────────────────────────────────────────────────────────────┘

WHY THIS MATTERS:
  JD says "Python developer"
  Resume says "Software engineer with ML background"
  
  Keyword search → NO MATCH ❌
  Semantic search → HIGH MATCH ✅ (they're close in embedding space)
"""

# ─────────────────────────────────────────────────────────────────────────────
# EMBEDDING MANAGER — Central class for all embedding operations
# ─────────────────────────────────────────────────────────────────────────────

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from pinecone import Pinecone, ServerlessSpec


class EmbeddingManager:
    """
    Manages text embeddings for the hiring platform.
    
    Uses OpenAI text-embedding-3-small:
      - 1536 dimensions
      - Best price/performance ratio
      - $0.02 per 1M tokens (very cheap)
    """
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def embed_resume(self, resume_data: dict) -> list[float]:
        """
        Create an embedding for a parsed resume.
        We concatenate the most important fields for best semantic representation.
        """
        # Craft the text to embed — capture the ESSENCE of the candidate
        embed_text = f"""
        Name: {resume_data.get('full_name', '')}
        Current Role: {resume_data.get('current_title', '')}
        Years of Experience: {resume_data.get('total_experience_years', 0)}
        Skills: {', '.join(resume_data.get('skills', []))}
        Education: {' '.join([
            f"{edu.get('degree', '')} in {edu.get('field', '')} from {edu.get('institution', '')}"
            for edu in resume_data.get('education', [])
        ])}
        Work History: {' '.join([
            f"{exp.get('title', '')} at {exp.get('company', '')}"
            for exp in resume_data.get('work_experience', [])[:3]
        ])}
        """
        
        return self.embeddings.embed_query(embed_text.strip())
    
    def embed_job_description(self, jd_text: str, requirements: dict) -> list[float]:
        """Create an embedding for a job description."""
        embed_text = f"""
        Job Requirements:
        {jd_text[:1000]}
        
        Required Skills: {', '.join(requirements.get('required_skills', []))}
        Experience Required: {requirements.get('min_experience_years', 0)} years
        Nice to Have: {', '.join(requirements.get('nice_to_have_skills', []))}
        """
        return self.embeddings.embed_query(embed_text.strip())
    
    def embed_text(self, text: str) -> list[float]:
        """Generic text embedding."""
        return self.embeddings.embed_query(text)


# ─────────────────────────────────────────────────────────────────────────────
# PINECONE VECTOR STORE — Production vector database
# ─────────────────────────────────────────────────────────────────────────────

class ResumeVectorStore:
    """
    Manages resume storage and retrieval in Pinecone.
    
    Each resume is stored as:
    - Vector: 1536-dimensional embedding
    - Metadata: candidate info for filtering and display
    
    WHY PINECONE OVER CHROMADB?
    ───────────────────────────
    ChromaDB: Good for development (local, no setup)
    Pinecone: Production (managed, scalable to millions of vectors)
    
    We'll show BOTH — start with ChromaDB in dev, Pinecone in prod.
    """
    
    def __init__(self, use_pinecone: bool = False):
        self.embedding_manager = EmbeddingManager()
        self.use_pinecone = use_pinecone
        
        if use_pinecone:
            self._init_pinecone()
        else:
            self._init_chromadb()
    
    def _init_pinecone(self):
        """Initialize Pinecone connection."""
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index_name = os.getenv("PINECONE_INDEX_NAME", "hiring-copilot-resumes")
        
        # Create index if it doesn't exist
        if index_name not in [i.name for i in pc.list_indexes()]:
            pc.create_index(
                name=index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print(f"✅ Created Pinecone index: {index_name}")
        
        self.index = pc.Index(index_name)
        print(f"✅ Connected to Pinecone index: {index_name}")
    
    def _init_chromadb(self):
        """Initialize ChromaDB for local development."""
        import chromadb
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(
            name="resumes",
            metadata={"hnsw:space": "cosine"}  # cosine similarity
        )
        print("✅ ChromaDB initialized (local development mode)")
    
    # ─── STORE RESUME ─────────────────────────────────────────────────────
    
    def store_resume(
        self, 
        resume_id: int, 
        candidate_id: int,
        resume_data: dict
    ) -> str:
        """
        Store a parsed resume in the vector database.
        Returns the vector ID for later retrieval.
        """
        vector_id = f"resume_{resume_id}_{uuid.uuid4().hex[:8]}"
        
        # Create the embedding
        embedding = self.embedding_manager.embed_resume(resume_data)
        
        # Metadata for filtering (Pinecone doesn't index vectors alone — metadata is queryable)
        metadata = {
            "resume_id": resume_id,
            "candidate_id": candidate_id,
            "candidate_name": resume_data.get("full_name", "Unknown"),
            "email": resume_data.get("email", ""),
            "current_title": resume_data.get("current_title", ""),
            "experience_years": float(resume_data.get("total_experience_years", 0) or 0),
            "skills": json.dumps(resume_data.get("skills", [])[:20]),  # Pinecone metadata limit
            "education_level": self._get_highest_education(resume_data.get("education", [])),
        }
        
        if self.use_pinecone:
            self.index.upsert(vectors=[(vector_id, embedding, metadata)])
        else:
            self.collection.upsert(
                ids=[vector_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[f"{resume_data.get('full_name')} - {resume_data.get('current_title')}"]
            )
        
        print(f"  ✅ Stored resume vector: {resume_data.get('full_name')} (ID: {vector_id})")
        return vector_id
    
    # ─── SEMANTIC SEARCH ──────────────────────────────────────────────────
    
    def search_similar_candidates(
        self,
        query_text: str,
        top_k: int = 10,
        min_experience_years: Optional[float] = None,
        max_experience_years: Optional[float] = None,
    ) -> list[dict]:
        """
        Find candidates semantically similar to the query.
        
        Example queries:
          "Python developer with FastAPI and AWS experience"
          "Machine learning engineer with PyTorch"
          "Senior backend engineer with team leadership"
        """
        
        query_embedding = self.embedding_manager.embed_text(query_text)
        
        if self.use_pinecone:
            # Build filter dict for Pinecone metadata filtering
            filter_dict = {}
            if min_experience_years:
                filter_dict["experience_years"] = {"$gte": min_experience_years}
            if max_experience_years:
                filter_dict.setdefault("experience_years", {})["$lte"] = max_experience_years
            
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict if filter_dict else None
            )
            
            return [
                {
                    "vector_id": match.id,
                    "similarity_score": round(match.score, 3),
                    **match.metadata
                }
                for match in results.matches
            ]
        else:
            # ChromaDB query
            where_clause = {}
            if min_experience_years:
                where_clause["experience_years"] = {"$gte": min_experience_years}
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause if where_clause else None,
                include=["distances", "metadatas", "documents"]
            )
            
            candidates = []
            for i, metadata in enumerate(results["metadatas"][0]):
                distance = results["distances"][0][i]
                similarity = 1 - distance  # convert distance to similarity
                candidates.append({
                    "vector_id": results["ids"][0][i],
                    "similarity_score": round(similarity, 3),
                    **metadata
                })
            
            return candidates
    
    def search_by_job_description(
        self,
        jd_text: str,
        requirements: dict,
        top_k: int = 20
    ) -> list[dict]:
        """Find best candidates for a specific job description."""
        
        # Create a rich query from JD + requirements
        query_text = f"""
        Looking for: {jd_text[:500]}
        Required skills: {', '.join(requirements.get('required_skills', []))}
        Experience needed: {requirements.get('min_experience_years', 0)}+ years
        """
        
        return self.search_similar_candidates(
            query_text=query_text,
            top_k=top_k,
            min_experience_years=float(requirements.get("min_experience_years", 0) or 0)
        )
    
    def find_similar_to_candidate(self, vector_id: str, top_k: int = 5) -> list[dict]:
        """
        Find candidates similar to a given candidate.
        Use case: "Find me more people like this top candidate."
        """
        if self.use_pinecone:
            # Fetch the candidate's vector
            fetch_result = self.index.fetch(ids=[vector_id])
            if not fetch_result.vectors:
                return []
            
            candidate_vector = fetch_result.vectors[vector_id].values
            
            # Search for similar vectors (excluding the candidate itself)
            results = self.index.query(
                vector=candidate_vector,
                top_k=top_k + 1,
                include_metadata=True
            )
            
            return [
                {"vector_id": m.id, "similarity_score": round(m.score, 3), **m.metadata}
                for m in results.matches
                if m.id != vector_id  # exclude the candidate themselves
            ][:top_k]
        
        return []  # ChromaDB similarity-to-vector search is more complex, simplified here
    
    def _get_highest_education(self, education: list) -> str:
        """Extract highest education level from education list."""
        levels = {"phd": 4, "masters": 3, "bachelors": 2, "associate": 1}
        highest = "other"
        highest_level = 0
        
        for edu in education:
            degree = (edu.get("degree", "") or "").lower()
            for level, score in levels.items():
                if level in degree and score > highest_level:
                    highest = level
                    highest_level = score
        
        return highest


# ─────────────────────────────────────────────────────────────────────────────
# RAG-ENHANCED CANDIDATE MATCHING AGENT
# ─────────────────────────────────────────────────────────────────────────────

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class RAGCandidateMatcher:
    """
    Enhanced candidate matching using RAG.
    
    FLOW:
    1. JD → embed → search Pinecone → get top 20 semantically similar resumes
    2. Pass top 20 to LLM for detailed scoring (not all 1000!)
    3. LLM produces ranked, explained results
    
    This is MUCH better than passing all resumes to LLM:
    ✅ Cost: only score top 20, not 1000 (50x cheaper)
    ✅ Quality: pre-filtered by semantic similarity
    ✅ Speed: semantic search in milliseconds
    """
    
    def __init__(self):
        self.vector_store = ResumeVectorStore(use_pinecone=False)  # ChromaDB for dev
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    def match_candidates_for_job(
        self,
        jd_text: str,
        requirements: dict,
        top_k: int = 5
    ) -> list[dict]:
        """
        RAG-based matching: semantic search → LLM scoring.
        """
        
        # Step 1: Semantic search to narrow field
        print(f"  [RAG] Semantic search for top {top_k * 4} candidates...")
        semantic_results = self.vector_store.search_by_job_description(
            jd_text=jd_text,
            requirements=requirements,
            top_k=top_k * 4  # get more, then LLM filters
        )
        
        if not semantic_results:
            print("  [RAG] No candidates found in vector store")
            return []
        
        print(f"  [RAG] Found {len(semantic_results)} semantic matches")
        
        # Step 2: LLM detailed scoring on semantic results
        scoring_prompt = ChatPromptTemplate.from_template("""
        You are evaluating candidates retrieved from semantic search against a job description.
        
        Job Requirements:
        {requirements}
        
        Job Description:
        {jd_text}
        
        Candidates (from semantic search):
        {candidates}
        
        For each candidate, provide a detailed score and ranking.
        Return a JSON array sorted by final_score descending:
        [
          {{
            "candidate_name": "...",
            "email": "...",
            "resume_id": <int>,
            "semantic_similarity": <float 0-1>,
            "final_score": <int 0-100>,
            "recommendation": "STRONGLY_RECOMMEND|RECOMMEND|MAYBE|REJECT",
            "key_strengths": ["strength1", "strength2"],
            "skill_gaps": ["gap1"],
            "reasoning": "<2-3 sentences>"
          }}
        ]
        
        Return ONLY valid JSON array.
        """)
        
        from langchain_core.output_parsers import JsonOutputParser
        chain = scoring_prompt | self.llm | JsonOutputParser()
        
        candidates_summary = [
            {
                "candidate_name": r.get("candidate_name"),
                "email": r.get("email"),
                "resume_id": r.get("resume_id"),
                "current_title": r.get("current_title"),
                "experience_years": r.get("experience_years"),
                "skills": json.loads(r.get("skills", "[]")),
                "semantic_similarity": r.get("similarity_score")
            }
            for r in semantic_results
        ]
        
        try:
            scored_candidates = chain.invoke({
                "requirements": json.dumps(requirements, indent=2),
                "jd_text": jd_text[:1000],
                "candidates": json.dumps(candidates_summary, indent=2)
            })
            
            # Return top K
            return scored_candidates[:top_k]
        
        except Exception as e:
            print(f"  ❌ LLM scoring failed: {e}")
            # Fallback: return semantic results with semantic score as final score
            return [
                {
                    "candidate_name": r.get("candidate_name"),
                    "email": r.get("email"),
                    "resume_id": r.get("resume_id"),
                    "final_score": int(r.get("similarity_score", 0) * 100),
                    "semantic_similarity": r.get("similarity_score"),
                    "recommendation": "MAYBE",
                    "reasoning": "LLM scoring failed; ranked by semantic similarity only"
                }
                for r in semantic_results[:top_k]
            ]


# ─────────────────────────────────────────────────────────────────────────────
# CHUNKING STRATEGY FOR LONG RESUMES
# ─────────────────────────────────────────────────────────────────────────────
"""
LESSON: When to chunk documents?
──────────────────────────────────
  Short resumes (1-2 pages): Embed entire resume as ONE vector
  Long resumes (3+ pages):   Chunk by section, embed separately

  Our chunking strategy:
    Section 1: Contact + Summary (high weight)
    Section 2: Work Experience   (high weight)
    Section 3: Skills            (high weight)
    Section 4: Education         (medium weight)
    Section 5: Certifications    (low weight)

  Why different weights?
  A 10-year work experience at Google matters more than
  a 2-day certification course.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_resume_for_embedding(resume_text: str, candidate_id: int) -> list[dict]:
    """
    Chunks a resume into sections for better embedding quality.
    Returns list of chunks with metadata.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,         # characters per chunk
        chunk_overlap=50,       # overlap for context continuity
        separators=["\n\n", "\n", ". ", " "]  # try to split on paragraphs first
    )
    
    chunks = splitter.create_documents(
        texts=[resume_text],
        metadatas=[{"candidate_id": candidate_id, "source": "resume"}]
    )
    
    return [
        {"text": chunk.page_content, "metadata": chunk.metadata}
        for chunk in chunks
    ]


# ─────────────────────────────────────────────────────────────────────────────
# QUICK DEMO — Run this to test RAG
# ─────────────────────────────────────────────────────────────────────────────

def demo_rag_search():
    """Quick demo of RAG search capabilities."""
    
    vector_store = ResumeVectorStore(use_pinecone=False)
    
    # Add sample resumes to vector store
    sample_resumes = [
        {
            "full_name": "John Smith",
            "email": "john@example.com",
            "current_title": "Senior Python Developer",
            "total_experience_years": 7,
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
            "education": [{"degree": "Bachelor's", "field": "Computer Science"}],
            "work_experience": [
                {"title": "Senior Dev", "company": "TechCorp", "years": 4},
                {"title": "Dev", "company": "StartupXYZ", "years": 3}
            ]
        },
        {
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "current_title": "Machine Learning Engineer",
            "total_experience_years": 5,
            "skills": ["Python", "PyTorch", "TensorFlow", "LangChain", "AWS"],
            "education": [{"degree": "Master's", "field": "Computer Science"}],
            "work_experience": [
                {"title": "ML Engineer", "company": "AI Startup", "years": 3},
            ]
        }
    ]
    
    for i, resume in enumerate(sample_resumes, 1):
        vector_store.store_resume(resume_id=i, candidate_id=i, resume_data=resume)
    
    # Search for candidates
    print("\n🔍 Searching for Python developers...")
    results = vector_store.search_similar_candidates(
        query_text="Python developer with cloud experience and API development",
        top_k=5
    )
    
    for result in results:
        print(f"  {result['candidate_name']} — Similarity: {result['similarity_score']:.3f}")
    
    return results


if __name__ == "__main__":
    demo_rag_search()
