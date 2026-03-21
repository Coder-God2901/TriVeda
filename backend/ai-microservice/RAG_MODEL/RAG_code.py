import json
import numpy as np
import pickle
import os
import requests
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import time
import re
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"

class UnifiedAyurvedicRAGBot:
    """Unified RAG Bot combining herbs database + PubMed research"""
    
    def __init__(self, herbs_file="herbs.json", pubmed_file="pubmed_data/pubmed_for_rag.json"):
        print(" Initializing UNIFIED Ayurvedic RAG Bot with Llama 3.2...")
        print("="*70)
        
        self.herbs_file = herbs_file
        self.pubmed_file = pubmed_file
        
        
        self.herbs_data = []
        self.pubmed_data = []
        self.all_documents = [] 
        self.all_metadata = []   
        self.embeddings = None
        
        self._check_ollama()
        
        print(" Loading embedding model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        os.makedirs("./knowledge_base", exist_ok=True)
        self._load_or_create_embeddings()
        
        
        self._print_stats()
    
    def _check_ollama(self):
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                available = any(MODEL_NAME in model.get('name', '') for model in models)
                if available:
                    print(f" Llama 3.2 is available")
                else:
                    print(f" Llama 3.2 not found. Run: ollama pull llama3.2")
            else:
                print(f" Ollama not running. Start with: ollama serve")
        except:
            print(f" Cannot connect to Ollama. Make sure it's running.")
    
    def _load_or_create_embeddings(self):
        """Load existing embeddings or create new ones"""
        embeddings_path = "./knowledge_base/unified_embeddings.npy"
        docs_path = "./knowledge_base/unified_documents.pkl"
        meta_path = "./knowledge_base/unified_metadata.pkl"
        
        if (os.path.exists(embeddings_path) and 
            os.path.exists(docs_path) and 
            os.path.exists(meta_path)):
            print(" Loading existing unified embeddings...")
            self.embeddings = np.load(embeddings_path)
            with open(docs_path, 'rb') as f:
                self.all_documents = pickle.load(f)
            with open(meta_path, 'rb') as f:
                self.all_metadata = pickle.load(f)
            print(f" Loaded {len(self.all_documents)} documents")
        else:
            print(" Creating new unified embeddings...")
            self._create_unified_embeddings()
    
    def _create_unified_embeddings(self):
        """Create embeddings from both herb and PubMed sources"""
        
        
        print("\n Loading herb database...")
        try:
            with open(self.herbs_file, 'r', encoding='utf-8') as f:
                self.herbs_data = json.load(f)
            print(f"    Loaded {len(self.herbs_data)} herbs")
        except Exception as e:
            print(f"    Error loading herbs: {e}")
            self.herbs_data = []
        
        
        print("\n Loading PubMed research articles...")
        try:
            with open(self.pubmed_file, 'r', encoding='utf-8') as f:
                self.pubmed_data = json.load(f)
            print(f"    Loaded {len(self.pubmed_data)} PubMed articles")
        except Exception as e:
            print(f"    Error loading PubMed data: {e}")
            self.pubmed_data = []
        
        
        print("\n🔨 Creating herb documents...")
        for i, herb in enumerate(self.herbs_data):
            doc_text, metadata = self._create_herb_document(herb, i)
            self.all_documents.append(doc_text)
            self.all_metadata.append(metadata)
        
        
        print("🔨 Creating PubMed research documents...")
        for i, article in enumerate(self.pubmed_data):
            doc_text, metadata = self._create_pubmed_document(article, i)
            self.all_documents.append(doc_text)
            self.all_metadata.append(metadata)
        
        print(f"\n Total documents created: {len(self.all_documents)}")
        print(f"   • Herbs: {len(self.herbs_data)}")
        print(f"   • Research articles: {len(self.pubmed_data)}")
        
        
        if self.all_documents:
            print(f"\n Generating embeddings for {len(self.all_documents)} documents...")
            self.embeddings = self.embedder.encode(
                self.all_documents, 
                show_progress_bar=True,
                batch_size=32
            )
            
            
            print(" Saving to disk...")
            np.save("./knowledge_base/unified_embeddings.npy", self.embeddings)
            with open("./knowledge_base/unified_documents.pkl", 'wb') as f:
                pickle.dump(self.all_documents, f)
            with open("./knowledge_base/unified_metadata.pkl", 'wb') as f:
                pickle.dump(self.all_metadata, f)
            
            print(f" Created unified knowledge base with {len(self.all_documents)} documents")
        else:
            print(" No documents to embed!")
    
    def _create_herb_document(self, herb: Dict, index: int) -> tuple:
        """Create document from herb data"""
        name = herb.get('name', 'Unknown')
        preview = herb.get('preview', '')
        pacify = herb.get('pacify', [])
        aggravate = herb.get('aggravate', [])
        
        
        conditions = []
        condition_keywords = {
            'urinary': ['urinary', 'dysuria', 'cystitis', 'UTI', 'bladder', 'kidney'],
            'digestive': ['digest', 'stomach', 'gut', 'acidity', 'appetite'],
            'respiratory': ['respiratory', 'cough', 'cold', 'asthma', 'bronchitis'],
            'skin': ['skin', 'rash', 'eczema', 'psoriasis', 'acne'],
            'pain': ['pain', 'inflammation', 'arthritis', 'joint'],
            'fever': ['fever', 'jvara', 'temperature'],
            'mental': ['stress', 'anxiety', 'mental', 'nervous', 'brain']
        }
        
        for category, keywords in condition_keywords.items():
            if any(keyword in preview.lower() for keyword in keywords):
                conditions.extend(keywords)
        
        
        doc_text = f"""
[SOURCE: HERB DATABASE]
Herb/Formula: {name}
Primary Indications: {preview}

Ayurvedic Properties:
- Pacifies Doshas: {', '.join(pacify) if pacify else 'N/A'}
- Aggravates Doshas: {', '.join(aggravate) if aggravate else 'N/A'}

Related Conditions: {', '.join(set(conditions)) if conditions else 'General wellness'}

Keywords: {name} ayurveda herb {' '.join(pacify)} {' '.join(aggravate)} {' '.join(conditions)}
"""
        
        metadata = {
            'type': 'herb',
            'name': name,
            'indications': preview,
            'pacify': pacify,
            'aggravate': aggravate,
            'index': index
        }
        
        return doc_text, metadata
    
    def _create_pubmed_document(self, article: Dict, index: int) -> tuple:
        """Create document from PubMed article"""
        
        if isinstance(article, dict) and 'text' in article:
            
            doc_text = article.get('text', '')
            metadata = article.get('metadata', {})
            metadata['type'] = 'research'
            return doc_text, metadata
        else:
            
            title = article.get('title', 'No title')
            abstract = article.get('abstract', 'No abstract')
            journal = article.get('journal', 'Unknown')
            year = article.get('year', 'No year')
            authors = article.get('authors', 'Unknown')
            mesh = article.get('mesh_terms', '')
            keyword = article.get('search_keyword', '')
            
            doc_text = f"""
[SOURCE: PUBMED RESEARCH]
TITLE: {title}
AUTHORS: {authors}
JOURNAL: {journal} ({year})
PMID: {article.get('pmid', 'N/A')}

ABSTRACT:
{abstract}

MESH TERMS: {mesh}
SEARCH KEYWORD: {keyword}
"""
            
            metadata = {
                'type': 'research',
                'title': title,
                'journal': journal,
                'year': year,
                'pmid': article.get('pmid'),
                'search_keyword': keyword,
                'mesh_terms': mesh
            }
            
            return doc_text, metadata
    
    def _expand_query(self, question: str) -> List[str]:
        """Expand query with related terms"""
        question_lower = question.lower()
        
        
        condition_map = {
            'urinary': ['urinary', 'bladder', 'kidney', 'dysuria', 'cystitis', 'UTI', 'mutra'],
            'digestion': ['digest', 'stomach', 'gut', 'indigestion', 'appetite', 'amlapitta'],
            'respiratory': ['respiratory', 'lung', 'breath', 'cough', 'cold', 'asthma', 'shwasa'],
            'pain': ['pain', 'inflammation', 'shoola', 'arthritis', 'joint', 'vedana'],
            'skin': ['skin', 'rash', 'eczema', 'psoriasis', 'acne', 'kushtha'],
            'fever': ['fever', 'jvara', 'temperature', 'jwara'],
            'vata': ['vata', 'vata dosha', 'vata imbalance', 'vata disorder'],
            'pitta': ['pitta', 'pitta dosha', 'pitta imbalance', 'pitta disorder'],
            'kapha': ['kapha', 'kapha dosha', 'kapha imbalance', 'kapha disorder']
        }
        
        
        expanded_queries = [question]
        
        for category, terms in condition_map.items():
            if any(term in question_lower for term in terms[:2]):
                expanded_queries.append(' '.join(terms))
        
        
        ayurvedic_terms = ['ayurveda', 'ayurvedic', 'herb', 'formulation', 'treatment']
        if any(term in question_lower for term in ayurvedic_terms):
            expanded_queries.append(question + ' ayurveda herb')
        
        return list(set(expanded_queries))
    
    def _hybrid_search(self, question: str, top_k: int = 10) -> List[Dict]:
        """Perform hybrid search"""
        all_scores = []
        queries = self._expand_query(question)
        
        for q in queries:
            q_embedding = self.embedder.encode([q])
            similarities = np.dot(self.embeddings, q_embedding.T).flatten()
            
            for idx, score in enumerate(similarities):
                all_scores.append({'idx': idx, 'score': score})
        
        
        herb_scores = {}
        for item in all_scores:
            idx = item['idx']
            score = item['score']
            if idx not in herb_scores or score > herb_scores[idx]:
                herb_scores[idx] = score
        
        
        sorted_results = sorted(herb_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, score in sorted_results[:top_k]:
            if idx < len(self.all_metadata):
                results.append({
                    'idx': idx,
                    'score': score,
                    'metadata': self.all_metadata[idx]
                })
        
        return results
    
    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Query the unified knowledge base"""
        if self.embeddings is None or len(self.all_documents) == 0:
            return self._empty_response()
        
        start_time = time.time()
        
        print(f"  🔍 Searching unified database for: '{question}'")
        search_results = self._hybrid_search(question, top_k=top_k*2)
        
        
        herb_sources = []
        research_sources = []
        retrieved_docs = []
        
        for result in search_results:
            idx = result['idx']
            score = result['score']
            metadata = result['metadata']
            
            if idx < len(self.all_documents):
                retrieved_docs.append(self.all_documents[idx])
                
                source_info = {
                    'relevance': score,
                    'score': score,
                    'text': self.all_documents[idx][:300] + "..."
                }
                
                if metadata.get('type') == 'herb':
                    source_info.update({
                        'type': 'herb',
                        'name': metadata.get('name', 'Unknown'),
                        'indications': metadata.get('indications', '')
                    })
                    herb_sources.append(source_info)
                else:
                    source_info.update({
                        'type': 'research',
                        'title': metadata.get('title', 'Research Article'),
                        'journal': metadata.get('journal', ''),
                        'year': metadata.get('year', '')
                    })
                    research_sources.append(source_info)
        
        
        context = "\n\n---\n\n".join(retrieved_docs[:3])
        
        
        enhanced_prompt = f"""You are an expert Ayurvedic consultant. Based ONLY on the provided context, answer the question using both herb database information and research articles.

Context (Ayurvedic herbs AND research articles):
{context}

Question: {question}

Instructions:
1. Use information from BOTH herbs and research if available
2. Clearly indicate whether information comes from traditional herb knowledge or modern research
3. List specific herbs/formulations with their indications
4. Cite research findings when relevant
5. If the context doesn't contain relevant information, say so

Answer:"""
        
        answer = self._generate_with_llama(enhanced_prompt)
        
        
        all_scores = [r['score'] for r in search_results[:top_k]]
        confidence = float(np.mean(all_scores)) if all_scores else 0.0
        
        return {
            "answer": answer,
            "herb_sources": herb_sources[:3],
            "research_sources": research_sources[:3],
            "total_sources": len(herb_sources) + len(research_sources),
            "confidence": confidence,
            "processing_time": time.time() - start_time
        }
    
    def _generate_with_llama(self, prompt: str) -> str:
        """Generate answer using Llama 3.2"""
        try:
            response = requests.post(OLLAMA_URL, json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1,
                "max_tokens": 1024
            })
            
            if response.status_code == 200:
                return response.json().get('response', '').strip()
            else:
                return "Error generating response."
        except Exception as e:
            print(f"  Error calling Ollama: {e}")
            return "Error connecting to language model."
    
    def _empty_response(self) -> Dict[str, Any]:
        """Return empty response"""
        return {
            "answer": "No knowledge base loaded. Please check your data files.",
            "herb_sources": [],
            "research_sources": [],
            "total_sources": 0,
            "confidence": 0.0,
            "processing_time": 0.0
        }
    
    def _print_stats(self):
        """Print knowledge base statistics"""
        print("\n" + "="*70)
        print(" KNOWLEDGE BASE STATISTICS")
        print("="*70)
        print(f"• Herbs/Formulations: {len(self.herbs_data)}")
        print(f"• Research Articles: {len(self.pubmed_data)}")
        print(f"• Total Documents: {len(self.all_documents)}")
        print(f"• Embedding Dimension: {self.embeddings.shape[1] if self.embeddings is not None else 'N/A'}")
        print("="*70)




if __name__ == "__main__":
    print("\n" + "="*80)
    print("   UNIFIED AYURVEDIC KNOWLEDGE BASE - HERBS + RESEARCH")
    print("="*80)
    
    
    bot = UnifiedAyurvedicRAGBot(
        herbs_file="herbs.json",
        pubmed_file="pubmed_data/pubmed_for_rag.json"
    )
    
    print("\n   Example questions:")
    print("     • What herbs help urinary tract disorders?")
    print("     • What does research say about Ashwagandha?")
    print("     • Herbs for Vata imbalance with research evidence")
    print("     • Compare traditional and modern views on Triphala")
    print("="*80)
    
    while True:
        print("\n Your question (or 'quit' to exit):")
        q = input("> ").strip()
        if q.lower() in ['quit', 'exit', 'q']:
            break
        if q:
            print("\n Processing...")
            result = bot.query(q)
            
            print(f"\n Answer (confidence: {result['confidence']:.1%}):")
            print("-" * 80)
            print(result['answer'])
            
            if result['herb_sources'] or result['research_sources']:
                print("\n Sources used:")
                
                if result['herb_sources']:
                    print("\n   HERB DATABASE:")
                    for i, source in enumerate(result['herb_sources'], 1):
                        print(f"    {i}. {source.get('name', 'Unknown')} (relevance: {source['relevance']:.1%})")
                        if source.get('indications'):
                            print(f"       {source['indications']}")
                
                if result['research_sources']:
                    print("\n   RESEARCH ARTICLES:")
                    for i, source in enumerate(result['research_sources'], 1):
                        print(f"    {i}. {source.get('title', 'Article')[:80]}...")
                        print(f"       {source.get('journal', '')} ({source.get('year', '')})")
                
                print(f"\n   Total sources: {result['total_sources']}")
            
            print(f"\n  Processing time: {result['processing_time']:.2f}s")