import json
import numpy as np
import pickle
import os
import requests
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional, Tuple
import time
import re
from datetime import datetime
import faiss
from collections import defaultdict

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"

class UnifiedAyurvedicRAGBot:
    
    def __init__(self, herbs_file="herbs.json", pubmed_file="pubmed_data/pubmed_for_rag.json"):
        print("Initializing UNIFIED Ayurvedic RAG Bot...")
        print("="*70)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.herbs_file = os.path.join(script_dir, herbs_file) if not os.path.isabs(herbs_file) else herbs_file
        self.pubmed_file = os.path.join(script_dir, pubmed_file) if not os.path.isabs(pubmed_file) else pubmed_file
        
        self.herbs_data = []
        self.pubmed_data = []
        self.all_documents = []
        self.all_metadata = []
        self.embeddings = None
        self.faiss_index = None
        
        self.query_cache = {}
        
        self._check_ollama()
        
        print("Loading embedding model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        os.makedirs("./knowledge_base", exist_ok=True)
        
        self._load_or_create_embeddings()
        
        self._build_faiss_index()
        
        self._print_stats()
    
    def _check_ollama(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available = any(MODEL_NAME in model.get('name', '') for model in models)
                if available:
                    print(f"Ollama with {MODEL_NAME} is available")
                else:
                    print(f"Model {MODEL_NAME} not found. Run: ollama pull {MODEL_NAME}")
            else:
                print("Ollama not running. Start with: ollama serve")
        except:
            print("Cannot connect to Ollama. Make sure it's running.")
    
    def _load_or_create_embeddings(self):
        embeddings_path = "./knowledge_base/unified_embeddings.npy"
        docs_path = "./knowledge_base/unified_documents.pkl"
        meta_path = "./knowledge_base/unified_metadata.pkl"
        
        if (os.path.exists(embeddings_path) and 
            os.path.exists(docs_path) and 
            os.path.exists(meta_path)):
            print("Loading existing unified embeddings...")
            self.embeddings = np.load(embeddings_path)
            with open(docs_path, 'rb') as f:
                self.all_documents = pickle.load(f)
            with open(meta_path, 'rb') as f:
                self.all_metadata = pickle.load(f)
            print(f"Loaded {len(self.all_documents)} documents")
        else:
            print("Creating new unified embeddings...")
            self._create_unified_embeddings()
    
    def _create_unified_embeddings(self):
        
        print("\nLoading herb database...")
        try:
            with open(self.herbs_file, 'r', encoding='utf-8') as f:
                self.herbs_data = json.load(f)
            print(f"Loaded {len(self.herbs_data)} herbs")
        except Exception as e:
            print(f"Error loading herbs: {e}")
            self.herbs_data = []
        
        print("\nLoading PubMed research articles...")
        try:
            with open(self.pubmed_file, 'r', encoding='utf-8') as f:
                self.pubmed_data = json.load(f)
            print(f"Loaded {len(self.pubmed_data)} PubMed articles")
        except Exception as e:
            print(f"Error loading PubMed data: {e}")
            self.pubmed_data = []
        
        print("\nCreating herb documents...")
        for i, herb in enumerate(self.herbs_data):
            doc_text, metadata = self._create_herb_document(herb, i)
            self.all_documents.append(doc_text)
            self.all_metadata.append(metadata)
        
        print("Creating PubMed research documents...")
        for i, article in enumerate(self.pubmed_data):
            doc_text, metadata = self._create_pubmed_document(article, i)
            self.all_documents.append(doc_text)
            self.all_metadata.append(metadata)
        
        print(f"\nTotal documents created: {len(self.all_documents)}")
        print(f"Herbs: {len(self.herbs_data)}")
        print(f"Research articles: {len(self.pubmed_data)}")
        
        if self.all_documents:
            print(f"\nGenerating embeddings for {len(self.all_documents)} documents...")
            self.embeddings = self.embedder.encode(
                self.all_documents, 
                show_progress_bar=True,
                batch_size=32,
                convert_to_numpy=True
            )
            
            print("Saving to disk...")
            np.save("./knowledge_base/unified_embeddings.npy", self.embeddings)
            with open("./knowledge_base/unified_documents.pkl", 'wb') as f:
                pickle.dump(self.all_documents, f)
            with open("./knowledge_base/unified_metadata.pkl", 'wb') as f:
                pickle.dump(self.all_metadata, f)
            
            print(f"Created unified knowledge base with {len(self.all_documents)} documents")
        else:
            print("No documents to embed!")
    
    def _create_herb_document(self, herb: Dict, index: int) -> Tuple[str, Dict]:
        name = herb.get('name', 'Unknown')
        preview = herb.get('preview', '')
        pacify = herb.get('pacify', [])
        aggravate = herb.get('aggravate', [])
        
        doc_text = f"""Herb: {name}
Description: {preview}
Doshas: {', '.join(pacify)}"""
        
        metadata = {
            'type': 'herb',
            'name': name,
            'indications': preview,
            'pacify': pacify,
            'aggravate': aggravate,
            'index': index
        }
        
        return doc_text, metadata
    
    def _create_pubmed_document(self, article: Dict, index: int) -> Tuple[str, Dict]:
        
        if isinstance(article, dict) and 'text' in article:
            doc_text = article.get('text', '')
            metadata = article.get('metadata', {})
            metadata['type'] = 'research'
            return doc_text, metadata
        
        title = article.get('title', 'No title')
        abstract = article.get('abstract', 'No abstract')
        journal = article.get('journal', 'Unknown')
        year = article.get('year', 'No year')
        authors = article.get('authors', 'Unknown')
        keyword = article.get('search_keyword', '')
        pmid = article.get('pmid', 'N/A')
        
        doc_text = f"""Research: {title}
Abstract: {abstract}
Journal: {journal} ({year})
Keywords: {keyword}
PMID: {pmid}"""
        
        metadata = {
            'type': 'research',
            'title': title,
            'abstract': abstract,
            'journal': journal,
            'year': year,
            'authors': authors,
            'pmid': pmid,
            'search_keyword': keyword
        }
        
        return doc_text, metadata
    
    def _build_faiss_index(self):
        if self.embeddings is not None and len(self.embeddings) > 0:
            print("Building FAISS index...")
            dimension = self.embeddings.shape[1]
            
            self.embeddings = self.embeddings.astype('float32')
            faiss.normalize_L2(self.embeddings)
            
            self.faiss_index = faiss.IndexFlatIP(dimension)
            self.faiss_index.add(self.embeddings)
            
            print(f"FAISS index built with {self.faiss_index.ntotal} vectors")
    
    def _get_query_embedding(self, query: str) -> np.ndarray:
        if query not in self.query_cache:
            embedding = self.embedder.encode([query], convert_to_numpy=True)
            faiss.normalize_L2(embedding)
            self.query_cache[query] = embedding
        return self.query_cache[query]
    
    def _hybrid_search(self, question: str, top_k: int = 10) -> List[Dict]:
        if self.faiss_index is None:
            return []
        
        q_embedding = self._get_query_embedding(question)
        
        distances, indices = self.faiss_index.search(q_embedding, top_k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.all_metadata):
                results.append({
                    'idx': idx,
                    'score': float(distance),
                    'metadata': self.all_metadata[idx]
                })
        
        return results
    
    def _generate_fallback_answer(self, question: str, herb_sources: List[Dict], research_sources: List[Dict] = None) -> str:
        
        if research_sources is None:
            research_sources = []
        
        is_research_question = any(word in question.lower() for word in ['research', 'study', 'studies', 'evidence', 'scientific', 'say about'])
        
        parts = []
        
        if is_research_question and research_sources:
            parts.append("Research Findings:")
            parts.append("")
            for i, r in enumerate(research_sources[:3], 1):
                title = r.get('title', 'Research Article')
                journal = r.get('journal', '')
                year = r.get('year', '')
                abstract = r.get('abstract', '')
                
                parts.append(f"{i}. {title}")
                if journal and year:
                    parts.append(f"   {journal} ({year})")
                if abstract and abstract != 'No abstract':
                    abstract_text = abstract[:350] + "..." if len(abstract) > 350 else abstract
                    parts.append(f"   {abstract_text}")
                parts.append("")
        
        if herb_sources:
            if is_research_question and research_sources:
                parts.append("Traditional Ayurvedic Knowledge:")
                parts.append("")
            elif not is_research_question:
                parts.append("Ayurvedic Herbs for Your Condition:")
                parts.append("")
            
            for i, h in enumerate(herb_sources[:5], 1):
                name = h.get('name', 'Herb')
                indications = h.get('indications', 'Traditional Ayurvedic herb')
                parts.append(f"{i}. {name}")
                parts.append(f"   {indications}")
                parts.append("")
        
        if not herb_sources and not research_sources:
            return "I couldn't find specific information about this in the database. Please consult an Ayurvedic practitioner for personalized advice."
        
        parts.append("---")
        parts.append("Please consult an Ayurvedic practitioner before using any herbs or formulations.")
        
        return "\n".join(parts)
    
    def _generate_with_llama(self, prompt: str) -> str:
        try:
            response = requests.post(
                OLLAMA_URL, 
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.1,
                    "max_tokens": 500
                },
                timeout=45
            )
            
            if response.status_code == 200:
                return response.json().get('response', '').strip()
            else:
                return ""
        except requests.exceptions.Timeout:
            print("LLM timeout, using fallback...")
            return ""
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return ""
    
    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        if self.faiss_index is None or len(self.all_documents) == 0:
            return self._empty_response()
        
        start_time = time.time()
        
        print(f"Searching for: '{question[:50]}...'")
        
        search_results = self._hybrid_search(question, top_k=top_k * 2)
        
        herb_sources = []
        research_sources = []
        
        for result in search_results:
            idx = result['idx']
            score = result['score']
            metadata = result['metadata']
            
            if idx < len(self.all_documents):
                source_info = {
                    'relevance': score,
                    'score': score
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
                        'abstract': metadata.get('abstract', ''),
                        'journal': metadata.get('journal', ''),
                        'year': metadata.get('year', ''),
                        'authors': metadata.get('authors', '')
                    })
                    research_sources.append(source_info)
        
        seen_titles = set()
        unique_research = []
        for r in research_sources:
            title = r.get('title', '')
            if title not in seen_titles:
                seen_titles.add(title)
                unique_research.append(r)
        research_sources = unique_research
        
        herb_sources.sort(key=lambda x: x['relevance'], reverse=True)
        research_sources.sort(key=lambda x: x['relevance'], reverse=True)
        
        answer = self._generate_fallback_answer(question, herb_sources, research_sources)
        
        all_scores = [r['relevance'] for r in herb_sources[:top_k]] + [r['relevance'] for r in research_sources[:top_k]]
        confidence = float(np.mean(all_scores)) if all_scores else 0.0
        
        return {
            "answer": answer,
            "herb_sources": herb_sources[:5],
            "research_sources": research_sources[:3],
            "total_sources": len(herb_sources) + len(research_sources),
            "confidence": confidence,
            "processing_time": time.time() - start_time
        }
    
    def _empty_response(self) -> Dict[str, Any]:
        return {
            "answer": "No knowledge base loaded. Please check your data files.",
            "herb_sources": [],
            "research_sources": [],
            "total_sources": 0,
            "confidence": 0.0,
            "processing_time": 0.0
        }
    
    def _print_stats(self):
        print("\n" + "="*70)
        print("KNOWLEDGE BASE STATISTICS")
        print("="*70)
        print(f"Herbs/Formulations: {len(self.herbs_data)}")
        print(f"Research Articles: {len(self.pubmed_data)}")
        print(f"Total Documents: {len(self.all_documents)}")
        print(f"Embedding Dimension: {self.embeddings.shape[1] if self.embeddings is not None else 'N/A'}")
        print(f"FAISS Index: {'Built' if self.faiss_index else 'Not built'}")
        print(f"Model: {MODEL_NAME}")
        print("="*70)


def main():
    print("\n" + "="*80)
    print("UNIFIED AYURVEDIC KNOWLEDGE BASE")
    print("="*80)
    
    bot = UnifiedAyurvedicRAGBot(
        herbs_file="herbs.json",
        pubmed_file="pubmed_data/pubmed_for_rag.json"
    )
    
    print("\nExample questions:")
    print("  What herbs help urinary tract disorders?")
    print("  What does research say about Ashwagandha?")
    print("  Herbs for Vata imbalance")
    print("  What does scientific evidence say about Turmeric?")
    print("="*80)
    
    while True:
        print("\nYour question (or 'quit' to exit):")
        q = input("> ").strip()
        
        if q.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if not q:
            continue
        
        print("\nProcessing...")
        result = bot.query(q)
        
        print(f"\nAnswer (confidence: {result['confidence']:.1%}):")
        print("-" * 80)
        print(result['answer'])
        
        if result['herb_sources'] or result['research_sources']:
            print("\n" + "=" * 80)
            print("SOURCES & REFERENCES")
            print("=" * 80)
            
            if result['herb_sources']:
                print("\nAYURVEDIC HERB DATABASE")
                print("-" * 60)
                for i, source in enumerate(result['herb_sources'], 1):
                    name = source.get('name', 'Unknown')
                    relevance = source['relevance']
                    print(f"\n{i}. {name} (Match: {relevance:.1%})")
                    if source.get('indications'):
                        print(f"   {source['indications']}")
            
            if result['research_sources']:
                print("\nSCIENTIFIC RESEARCH ARTICLES")
                print("-" * 60)
                for i, source in enumerate(result['research_sources'], 1):
                    title = source.get('title', 'Article')
                    journal = source.get('journal', '')
                    year = source.get('year', '')
                    relevance = source['relevance']
                    
                    print(f"\n{i}. {title}")
                    if journal and year:
                        print(f"   {journal} ({year}) | Relevance: {relevance:.1%}")
                    if source.get('abstract') and source['abstract'] != 'No abstract':
                        abstract = source['abstract']
                        if len(abstract) > 200:
                            abstract = abstract[:200] + "..."
                        print(f"   {abstract}")
            
            print("\n" + "=" * 80)
            print(f"Total sources retrieved: {result['total_sources']}")
        
        print(f"\nProcessing time: {result['processing_time']:.2f}s")


if __name__ == "__main__":
    main()
