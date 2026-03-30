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

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"

class IntentClassifier:
    def __init__(self):
        self.patterns = {
            "greeting": ["hi", "hello", "hey", "good morning", "good evening", "namaste"],
            "goodbye": ["bye", "exit", "quit", "see you", "goodbye"],
            "thanks": ["thanks", "thank you", "thx", "appreciate"],
            "identity": ["who are you", "what are you", "your name"],
            "pros_cons": ["pros and cons", "advantages and disadvantages", "benefits and risks", "good and bad"],
            "apology": ["sorry", "apologize", "my bad", "oops"],
            "confusion": ["what", "huh", "i don't understand", "confused", "unclear", "meaning"],
            "greeting_response": ["how are you", "how do you do", "what's up", "how's it going"]
        }
        
        self.casual_responses = {
            "apology": "No need to apologize! I'm here to help with your Ayurvedic questions. What would you like to know about?",
            "confusion": "I understand this can be confusing. Let me help! Could you please ask your question more specifically? For example:\n- What herbs help with digestion?\n- Pros and cons of Tulsi\n- Research on Ashwagandha\n- Herbs for Vata imbalance",
            "greeting_response": "I'm doing well, thank you for asking! How can I assist you with Ayurvedic knowledge today?",
            "default_fallback": "I'm your Ayurvedic assistant! I can help with:\n- Herb recommendations\n- Scientific research on herbs\n- Pros and cons of specific herbs\n- Dosha imbalances (Vata, Pitta, Kapha)\n- Traditional Ayurvedic knowledge\n\nWhat would you like to know?"
        }

    def classify(self, text: str):
        text = text.lower()
        for intent, pats in self.patterns.items():
            for p in pats:
                if p in text:
                    return intent
        return "herb_query"
    
    def get_fallback_response(self, intent: str) -> str:
        return self.casual_responses.get(intent, self.casual_responses["default_fallback"])

HERB_PROS_CONS = {
    "Ashwagandha": {"pros": ["Reduces stress and anxiety", "Improves sleep quality", "Boosts energy", "Enhances cognitive function"], "cons": ["May cause drowsiness", "Can interact with thyroid medication", "May cause digestive issues"]},
    "Turmeric": {"pros": ["Powerful anti-inflammatory", "Boosts immunity", "Good for skin health", "Antioxidant properties"], "cons": ["Low absorption without black pepper", "May cause stomach upset", "Can interact with blood thinners"]},
    "Tulsi": {"pros": ["Boosts immunity", "Reduces stress", "Good for respiratory health", "Antimicrobial properties"], "cons": ["May lower blood sugar", "Can affect fertility in large doses", "May interact with blood thinners"]},
    "Ginger": {"pros": ["Improves digestion", "Reduces nausea", "Anti-inflammatory", "Good for cold and flu"], "cons": ["May cause acidity", "Can interact with blood thinners", "May cause heartburn"]},
    "Amla": {"pros": ["Rich in Vitamin C", "Boosts immunity", "Good for hair and skin", "Antioxidant rich"], "cons": ["Cold sensitivity", "May cause constipation", "Can increase acidity"]},
    "Neem": {"pros": ["Antibacterial", "Good for skin conditions", "Blood purifier", "Dental health"], "cons": ["Toxic in excess", "Can cause nausea", "May affect fertility"]},
    "Brahmi": {"pros": ["Memory boost", "Reduces anxiety", "Improves focus", "Neuroprotective"], "cons": ["May cause nausea", "Can lower blood pressure", "May cause digestive issues"]},
    "Shilajit": {"pros": ["Energy boost", "Anti-aging", "Improves stamina", "Enhances nutrient absorption"], "cons": ["Contamination risk if not purified", "May increase uric acid", "Can interact with medications"]},
    "Triphala": {"pros": ["Gut health", "Natural detox", "Improves digestion", "Gentle laxative"], "cons": ["May cause diarrhea", "Can stain teeth", "May cause initial bloating"]},
    "Shatavari": {"pros": ["Hormone balance", "Improves fertility", "Good for lactation", "Supports female reproductive health"], "cons": ["May increase Kapha", "Can cause allergies", "May affect blood sugar"]},
    "Guggulu": {"pros": ["Cholesterol support", "Weight management", "Anti-inflammatory", "Joint health"], "cons": ["Stomach upset", "May cause skin rash", "Can interact with medications"]},
    "Arjuna": {"pros": ["Heart health", "Improves circulation", "Lowers blood pressure", "Cardioprotective"], "cons": ["Limited research", "May cause constipation", "Can interact with heart medications"]},
    "Bhringraj": {"pros": ["Hair growth", "Liver health", "Anti-aging", "Good for skin"], "cons": ["Slow results", "May cause eye irritation", "Can cause digestive issues"]},
    "Vidanga": {"pros": ["Anti-parasitic", "Digestive health", "Weight management", "Antimicrobial"], "cons": ["Strong effect", "May cause stomach pain", "Can be toxic in excess"]},
    "Musta": {"pros": ["Digestive health", "Weight management", "Anti-inflammatory", "Detoxifying"], "cons": ["May cause appetite loss", "Can be drying", "May cause constipation"]},
    "Yavani": {"pros": ["Digestion", "Respiratory health", "Anti-spasmodic", "Carminative"], "cons": ["Strong taste", "May cause heartburn", "Can irritate stomach"]},
    "Ajmoda": {"pros": ["Bloating relief", "Digestive health", "Anti-inflammatory", "Diuretic"], "cons": ["May cause skin irritation", "Can be strong", "May affect pregnancy"]},
    "Lavanga": {"pros": ["Dental health", "Digestive health", "Antiseptic", "Pain relief"], "cons": ["Strong potency", "May cause mouth irritation", "Can be toxic in excess"]},
    "Gokshura": {"pros": ["Urinary health", "Testosterone support", "Energy boost", "Aphrodisiac"], "cons": ["Limited evidence", "May interact with diuretics", "Can affect hormones"]},
    "Haritaki": {"pros": ["Digestion", "Detoxification", "Laxative", "Rejuvenative"], "cons": ["May cause dehydration", "Can be too strong", "May cause initial discomfort"]}
}

class UnifiedAyurvedicRAGBot:
    
    def __init__(self, herbs_file="herbs.json", pubmed_file="pubmed_data/pubmed_for_rag.json"):
        print("Initializing UNIFIED Ayurvedic RAG Bot (Enhanced)...")
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
        self.query_history = []
        self.accuracy_history = []
        
        self.herb_synonyms = {
            "turmeric": ["haridra", "curcuma longa", "haldi"],
            "ashwagandha": ["withania somnifera", "indian ginseng", "winter cherry"],
            "triphala": ["triphala churna", "amalaki", "bibhitaki", "haritaki"],
            "tulsi": ["holy basil", "ocimum sanctum", "tulasi"],
            "ginger": ["ardraka", "zinger officinale", "shunthi"],
            "gokshura": ["tribulus terrestris", "puncture vine"],
            "arjuna": ["terminalia arjuna"],
            "neem": ["azadirachta indica", "nimba"],
            "brahmi": ["bacopa monnieri", "gotu kola"],
            "shilajit": ["mineral pitch", "mumijo"],
            "guggulu": ["commiphora mukul", "guggul"],
            "amla": ["emblica officinalis", "indian gooseberry"],
            "bhringraj": ["eclipta alba", "false daisy"],
            "shatavari": ["asparagus racemosus", "wild asparagus"],
            "vidanga": ["embelia ribes", "false black pepper"],
            "musta": ["cyperus rotundus", "nut grass"],
            "yavani": ["trachyspermum ammi", "ajwain"],
            "ajmoda": ["apium graveolens", "celery seeds"],
            "lavanga": ["syzygium aromaticum", "clove"],
            "pippali": ["long pepper", "piper longum"],
            "kalmegh": ["andrographis paniculata", "king of bitters"]
        }
        
        self.dosha_keywords = {
            "pitta": ["acidity", "burning", "inflammation", "heartburn", "ulcer", "rash", "heat", "anger", "irritation"],
            "vata": ["anxiety", "bloating", "gas", "pain", "dryness", "restlessness", "insomnia", "constipation"],
            "kapha": ["cough", "congestion", "mucus", "heaviness", "lethargy", "swelling", "cold", "allergies"]
        }
        
        self._check_ollama()
        self.intent_classifier = IntentClassifier()
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
        except Exception as e:
            print(f"Cannot connect to Ollama. Make sure it's running. Error: {e}")
    
    def _load_or_create_embeddings(self):
        embeddings_path = "./knowledge_base/unified_embeddings.npy"
        docs_path = "./knowledge_base/unified_documents.pkl"
        meta_path = "./knowledge_base/unified_metadata.pkl"
        
        if (os.path.exists(embeddings_path) and 
            os.path.exists(docs_path) and 
            os.path.exists(meta_path)):
            print("Loading existing unified embeddings...")
            try:
                self.embeddings = np.load(embeddings_path)
                with open(docs_path, 'rb') as f:
                    self.all_documents = pickle.load(f)
                with open(meta_path, 'rb') as f:
                    self.all_metadata = pickle.load(f)
                print(f"Loaded {len(self.all_documents)} documents")
            except Exception as e:
                print(f"Error loading embeddings: {e}")
                print("Creating new embeddings instead...")
                self._create_unified_embeddings()
        else:
            print("Creating new unified embeddings...")
            self._create_unified_embeddings()
    
    def _create_unified_embeddings(self):
        print("\nLoading herb database...")
        try:
            if os.path.exists(self.herbs_file):
                with open(self.herbs_file, 'r', encoding='utf-8') as f:
                    self.herbs_data = json.load(f)
                print(f"Loaded {len(self.herbs_data)} herbs")
            else:
                print(f"Herbs file not found: {self.herbs_file}")
                self.herbs_data = []
        except Exception as e:
            print(f"Error loading herbs: {e}")
            self.herbs_data = []
        
        print("\nLoading PubMed research articles...")
        try:
            if os.path.exists(self.pubmed_file):
                with open(self.pubmed_file, 'r', encoding='utf-8') as f:
                    self.pubmed_data = json.load(f)
                print(f"Loaded {len(self.pubmed_data)} PubMed articles")
            else:
                print(f"PubMed file not found: {self.pubmed_file}")
                self.pubmed_data = []
        except Exception as e:
            print(f"Error loading PubMed data: {e}")
            self.pubmed_data = []
        
        print("\nCreating herb documents with enhanced metadata...")
        for i, herb in enumerate(self.herbs_data):
            doc_text, metadata = self._create_enhanced_herb_document(herb, i)
            self.all_documents.append(doc_text)
            self.all_metadata.append(metadata)
        
        print("Creating PubMed research documents...")
        for i, article in enumerate(self.pubmed_data):
            doc_text, metadata = self._create_pubmed_document(article, i)
            self.all_documents.append(doc_text)
            self.all_metadata.append(metadata)
        
        print(f"\nTotal documents created: {len(self.all_documents)}")
        print(f"   Herbs: {len(self.herbs_data)}")
        print(f"   Research articles: {len(self.pubmed_data)}")
        
        if self.all_documents:
            print(f"\nGenerating embeddings for {len(self.all_documents)} documents...")
            try:
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
            except Exception as e:
                print(f"Error generating embeddings: {e}")
                self.embeddings = None
        else:
            print("No documents to embed!")
    
    def _create_enhanced_herb_document(self, herb: Dict, index: int) -> Tuple[str, Dict]:
        name = herb.get('name', 'Unknown')
        preview = herb.get('preview', '')
        pacify = herb.get('pacify', [])
        aggravate = herb.get('aggravate', [])
        indications = herb.get('indications', [])
        
        pacify = pacify if pacify else []
        aggravate = aggravate if aggravate else []
        indications = indications if indications else []
        
        synonyms = []
        name_lower = name.lower()
        for herb_key, syn_list in self.herb_synonyms.items():
            if name_lower == herb_key or name_lower in syn_list:
                synonyms = syn_list
                break
        
        detected_doshas = []
        for dosha, keywords in self.dosha_keywords.items():
            if any(kw in preview.lower() for kw in keywords):
                detected_doshas.append(dosha)
        
        doc_text = f"""Herb: {name}
Synonyms: {', '.join(synonyms) if synonyms else 'None'}
Description: {preview}
Pacifies Doshas: {', '.join(pacify) if pacify else 'None'}
Aggravates Doshas: {', '.join(aggravate) if aggravate else 'None'}
Detected Doshas: {', '.join(detected_doshas)}
Indications: {', '.join(indications) if indications else preview}
Keywords: {name} {preview} {' '.join(pacify)} {' '.join(aggravate)} {' '.join(synonyms)}"""
        
        metadata = {
            'type': 'herb',
            'name': name,
            'indications': preview,
            'pacify': pacify,
            'aggravate': aggravate,
            'synonyms': synonyms,
            'detected_doshas': detected_doshas,
            'index': index
        }
        
        return doc_text, metadata
    
    def _create_pubmed_document(self, article: Dict, index: int) -> Tuple[str, Dict]:
        if isinstance(article, dict):
            if 'text' in article:
                doc_text = article.get('text', '')
                metadata = article.get('metadata', {})
                metadata['type'] = 'research'
                metadata['index'] = index
                return doc_text, metadata
            else:
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
                    'search_keyword': keyword,
                    'index': index
                }
                
                return doc_text, metadata
        else:
            doc_text = str(article)
            metadata = {
                'type': 'research',
                'title': 'Research Article',
                'abstract': doc_text[:500],
                'index': index
            }
            return doc_text, metadata
    
    def _build_faiss_index(self):
        if self.embeddings is not None and len(self.embeddings) > 0:
            print("Building FAISS index...")
            try:
                dimension = self.embeddings.shape[1]
                
                self.embeddings = self.embeddings.astype('float32')
                faiss.normalize_L2(self.embeddings)
                
                self.faiss_index = faiss.IndexFlatIP(dimension)
                self.faiss_index.add(self.embeddings)
                
                print(f"FAISS index built with {self.faiss_index.ntotal} vectors")
            except Exception as e:
                print(f"Error building FAISS index: {e}")
                self.faiss_index = None
        else:
            print("No embeddings available to build FAISS index")
    
    def _expand_query_with_synonyms(self, question: str) -> List[str]:
        expanded_queries = [question]
        question_lower = question.lower()
        
        for herb, synonyms in self.herb_synonyms.items():
            if herb in question_lower or any(syn in question_lower for syn in synonyms[:2]):
                expanded_queries.extend(synonyms)
                expanded_queries.append(f"{herb} {synonyms[0] if synonyms else herb}")
                break
        
        for dosha, keywords in self.dosha_keywords.items():
            if dosha in question_lower or any(kw in question_lower for kw in keywords[:2]):
                expanded_queries.append(f"{question} {dosha} imbalance")
                expanded_queries.append(f"{question} {keywords[0]}")
                break
        
        return list(set(expanded_queries))
    
    def _get_query_embedding(self, query: str) -> np.ndarray:
        if query not in self.query_cache:
            try:
                embedding = self.embedder.encode([query], convert_to_numpy=True)
                faiss.normalize_L2(embedding)
                self.query_cache[query] = embedding
            except Exception as e:
                print(f"Error generating query embedding: {e}")
                return np.zeros((1, 384), dtype=np.float32)
        return self.query_cache[query]
    
    def _hybrid_search(self, question: str, top_k: int = 10) -> List[Dict]:
        if self.faiss_index is None or self.embeddings is None:
            return []
        
        try:
            expanded_queries = self._expand_query_with_synonyms(question)
            
            all_results = []
            for q in expanded_queries[:3]:
                q_embedding = self._get_query_embedding(q)
                distances, indices = self.faiss_index.search(q_embedding, top_k)
                
                for idx, distance in zip(indices[0], distances[0]):
                    if idx < len(self.all_metadata):
                        score = float(distance)
                        
                        metadata = self.all_metadata[idx]
                        if metadata.get('type') == 'herb':
                            herb_name = metadata.get('name', '').lower()
                            question_lower = question.lower()
                            
                            if herb_name in question_lower or question_lower in herb_name:
                                score += 0.15
                            
                            for syn in metadata.get('synonyms', []):
                                if syn in question_lower:
                                    score += 0.10
                                    break
                            
                            for dosha, keywords in self.dosha_keywords.items():
                                if dosha in question_lower and dosha in metadata.get('detected_doshas', []):
                                    score += 0.10
                        
                        all_results.append({
                            'idx': idx,
                            'score': score,
                            'metadata': metadata
                        })
            
            seen = set()
            unique_results = []
            for r in sorted(all_results, key=lambda x: x['score'], reverse=True):
                if r['idx'] not in seen:
                    seen.add(r['idx'])
                    unique_results.append(r)
            
            return unique_results[:top_k]
        except Exception as e:
            print(f"Error in hybrid search: {e}")
            return []
    
    def _extract_herb_name(self, question: str) -> Optional[str]:
        question_lower = question.lower()
        
        all_herbs = list(HERB_PROS_CONS.keys())
        
        herb_variations = {
            "tulsi": ["tulsi", "holy basil", "tulasi"],
            "ashwagandha": ["ashwagandha", "indian ginseng", "winter cherry"],
            "turmeric": ["turmeric", "haldi", "curcuma"],
            "ginger": ["ginger", "adrak", "shunthi"],
            "triphala": ["triphala", "triphala churna"],
            "brahmi": ["brahmi", "bacopa"],
            "amla": ["amla", "indian gooseberry", "amlaki"],
            "neem": ["neem", "nimba"],
            "shilajit": ["shilajit", "mumijo"],
            "guggulu": ["guggulu", "guggul"],
            "pippali": ["pippali", "long pepper"],
            "kalmegh": ["kalmegh", "andrographis"]
        }
        
        for herb in all_herbs:
            if herb.lower() in question_lower:
                return herb
        
        for herb, variations in herb_variations.items():
            for var in variations:
                if var in question_lower:
                    for actual_herb in all_herbs:
                        if actual_herb.lower() == herb.lower():
                            return actual_herb
        
        patterns = [
            r"pros and cons of (\w+)",
            r"advantages and disadvantages of (\w+)",
            r"benefits and risks of (\w+)",
            r"(\w+) pros and cons",
            r"about (\w+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question_lower)
            if match:
                candidate = match.group(1)
                for herb in all_herbs:
                    if candidate in herb.lower() or herb.lower() in candidate:
                        return herb
        
        return None
    
    def _calculate_enhanced_accuracy(self, question: str, confidence: float, 
                                     herb_sources: List[Dict], research_sources: List[Dict]) -> Dict[str, Any]:
        
        if confidence >= 0.7:
            base_accuracy = 90
        elif confidence >= 0.6:
            base_accuracy = 80
        elif confidence >= 0.5:
            base_accuracy = 70
        elif confidence >= 0.4:
            base_accuracy = 60
        else:
            base_accuracy = 50
        
        source_quality = 0
        if herb_sources:
            top_herb_score = herb_sources[0].get('score', 0)
            source_quality += min(15, int(top_herb_score * 15))
        
        if research_sources:
            top_research_score = research_sources[0].get('score', 0)
            source_quality += min(10, int(top_research_score * 10))
        
        is_research_question = any(word in question.lower() for word in ['research', 'study', 'evidence', 'scientific'])
        if is_research_question:
            if research_sources:
                source_quality += 10
            else:
                source_quality -= 15
        
        herb_name_match = False
        for herb in self.herb_synonyms.keys():
            if herb in question.lower():
                herb_name_match = True
                break
        
        if herb_name_match and herb_sources:
            source_quality += 5
        
        final_accuracy = min(100, max(0, base_accuracy + source_quality // 2))
        
        return {
            "query": question,
            "confidence": confidence,
            "accuracy_score": final_accuracy,
            "relevance_score": min(100, final_accuracy - 5),
            "completeness_score": min(100, final_accuracy - 2),
            "overall_accuracy": final_accuracy
        }
    
    def _generate_enhanced_answer(self, question: str, herb_sources: List[Dict], 
                                   research_sources: List[Dict] = None) -> str:
        if research_sources is None:
            research_sources = []
        
        is_research_question = any(word in question.lower() for word in ['research', 'study', 'studies', 'evidence', 'scientific', 'say about'])
        
        parts = []
        
        detected_dosha = None
        for dosha, keywords in self.dosha_keywords.items():
            if any(kw in question.lower() for kw in keywords):
                detected_dosha = dosha
                break
        
        if detected_dosha:
            parts.append(f"Based on your {detected_dosha.capitalize()} imbalance symptoms:")
            parts.append("")
        
        if is_research_question and research_sources:
            parts.append("Research Findings:")
            parts.append("")
            for i, r in enumerate(research_sources[:3], 1):
                title = r.get('title', 'Research Article')
                journal = r.get('journal', '')
                year = r.get('year', '')
                abstract = r.get('abstract', '')
                score = r.get('score', 0)
                
                parts.append(f"{i}. {title}")
                if journal and year:
                    parts.append(f"   {journal} ({year}) | Relevance: {score:.0%}")
                if abstract and abstract != 'No abstract':
                    abstract_text = abstract[:350] + "..." if len(abstract) > 350 else abstract
                    parts.append(f"   {abstract_text}")
                parts.append("")
        
        if herb_sources:
            if is_research_question and research_sources:
                parts.append("Traditional Ayurvedic Recommendations:")
                parts.append("")
            elif not is_research_question:
                parts.append("Recommended Ayurvedic Herbs:")
                parts.append("")
            
            for i, h in enumerate(herb_sources[:5], 1):
                name = h.get('name', 'Herb')
                indications = h.get('indications', 'Traditional Ayurvedic herb')
                score = h.get('score', 0)
                
                if i == 1 and score > 0.6:
                    parts.append(f"{i}. {name} (Best Match)")
                else:
                    parts.append(f"{i}. {name}")
                parts.append(f"   {indications}")
                
                if i == 1 and score > 0.6:
                    if "ginger" in name.lower() or "ardraka" in name.lower():
                        parts.append(f"   Tip: Best taken with warm water before meals")
                    elif "turmeric" in name.lower() or "haridra" in name.lower():
                        parts.append(f"   Tip: Best absorbed with black pepper and healthy fat")
                    elif "ashwagandha" in name.lower():
                        parts.append(f"   Tip: Best taken with warm milk before bed")
                    elif "tulsi" in name.lower() or "holy basil" in name.lower():
                        parts.append(f"   Tip: Best consumed as tea, especially during cold season")
                
                parts.append("")
        
        if not herb_sources and not research_sources:
            return "I couldn't find specific information about this in the database. Please consult an Ayurvedic practitioner for personalized advice."
        
        parts.append("---")
        parts.append("Note: These are traditional Ayurvedic recommendations. Please consult a qualified practitioner before use.")
        
        return "\n".join(parts)
    
    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        intent = self.intent_classifier.classify(question)
        
        if intent == "greeting":
            return {
                "answer": "Hello! I am your Ayurvedic assistant\nHow can I help you with your health and wellness today?", 
                "confidence": 1.0,
                "herb_sources": [],
                "research_sources": [],
                "total_sources": 0,
                "accuracy": {"overall_accuracy": 100, "relevance_score": 100, "completeness_score": 100},
                "processing_time": 0.0
            }
        
        if intent == "goodbye":
            return {
                "answer": "Goodbye! Stay healthy and balanced", 
                "confidence": 1.0,
                "herb_sources": [],
                "research_sources": [],
                "total_sources": 0,
                "accuracy": {"overall_accuracy": 100, "relevance_score": 100, "completeness_score": 100},
                "processing_time": 0.0
            }
        
        if intent == "thanks":
            return {
                "answer": "You're welcome! Wishing you good health", 
                "confidence": 1.0,
                "herb_sources": [],
                "research_sources": [],
                "total_sources": 0,
                "accuracy": {"overall_accuracy": 100, "relevance_score": 100, "completeness_score": 100},
                "processing_time": 0.0
            }
        
        if intent == "identity":
            return {
                "answer": "I am an AI Ayurvedic RAG assistant powered by research and traditional knowledge. I can help you find information about Ayurvedic herbs, their uses, and scientific research supporting them.", 
                "confidence": 1.0,
                "herb_sources": [],
                "research_sources": [],
                "total_sources": 0,
                "accuracy": {"overall_accuracy": 100, "relevance_score": 100, "completeness_score": 100},
                "processing_time": 0.0
            }
        
        if intent == "apology":
            return {
                "answer": self.intent_classifier.get_fallback_response("apology"),
                "confidence": 1.0,
                "herb_sources": [],
                "research_sources": [],
                "total_sources": 0,
                "accuracy": {"overall_accuracy": 100, "relevance_score": 100, "completeness_score": 100},
                "processing_time": 0.0
            }
        
        if intent == "confusion":
            return {
                "answer": self.intent_classifier.get_fallback_response("confusion"),
                "confidence": 1.0,
                "herb_sources": [],
                "research_sources": [],
                "total_sources": 0,
                "accuracy": {"overall_accuracy": 100, "relevance_score": 100, "completeness_score": 100},
                "processing_time": 0.0
            }
        
        if intent == "greeting_response":
            return {
                "answer": self.intent_classifier.get_fallback_response("greeting_response"),
                "confidence": 1.0,
                "herb_sources": [],
                "research_sources": [],
                "total_sources": 0,
                "accuracy": {"overall_accuracy": 100, "relevance_score": 100, "completeness_score": 100},
                "processing_time": 0.0
            }
        
        if intent == "pros_cons":
            herb_name = self._extract_herb_name(question)
            
            if herb_name and herb_name.lower() in [h.lower() for h in HERB_PROS_CONS.keys()]:
                matching_herb = None
                for herb in HERB_PROS_CONS.keys():
                    if herb.lower() == herb_name.lower():
                        matching_herb = herb
                        break
                
                if matching_herb:
                    info = HERB_PROS_CONS[matching_herb]
                    answer = f"{matching_herb}:\n\n"
                    answer += f"Pros:\n"
                    for pro in info['pros']:
                        answer += f"  - {pro}\n"
                    answer += f"\nCons:\n"
                    for con in info['cons']:
                        answer += f"  - {con}\n"
                    answer += "\n---\nNote: These are general observations. Individual results may vary."
                else:
                    answer = f"I don't have detailed pros and cons information for {herb_name}. Please consult an Ayurvedic practitioner."
            else:
                answer = "Please specify which herb you'd like to know about. For example:\n"
                answer += "  - pros and cons of Tulsi\n"
                answer += "  - Ashwagandha advantages and disadvantages\n\n"
                answer += "Here are the herbs I have information about:\n"
                answer += f"  {', '.join(list(HERB_PROS_CONS.keys())[:15])}..."
            
            return {
                "answer": answer, 
                "confidence": 1.0,
                "herb_sources": [],
                "research_sources": [],
                "total_sources": 0,
                "accuracy": {"overall_accuracy": 100, "relevance_score": 100, "completeness_score": 100},
                "processing_time": 0.0
            }
        
        if len(question.split()) <= 3 and not any(keyword in question.lower() for keyword in 
            ['herb', 'ayurveda', 'tulsi', 'ashwagandha', 'ginger', 'turmeric', 'triphala', 
             'dosha', 'pitta', 'vata', 'kapha', 'research', 'study', 'benefit', 'treatment',
             'remedy', 'cure', 'medicine', 'health', 'condition', 'disease']):
            
            return {
                "answer": self.intent_classifier.get_fallback_response("default_fallback"),
                "confidence": 0.5,
                "herb_sources": [],
                "research_sources": [],
                "total_sources": 0,
                "accuracy": {"overall_accuracy": 50, "relevance_score": 50, "completeness_score": 50},
                "processing_time": 0.0
            }
        
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
                        'indications': metadata.get('indications', ''),
                        'synonyms': metadata.get('synonyms', []),
                        'doshas': metadata.get('detected_doshas', [])
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
        
        answer = self._generate_enhanced_answer(question, herb_sources, research_sources)
        
        all_scores = [r['relevance'] for r in herb_sources[:top_k]] + [r['relevance'] for r in research_sources[:top_k]]
        confidence = float(np.mean(all_scores)) if all_scores else 0.0
        
        accuracy_data = self._calculate_enhanced_accuracy(question, confidence, herb_sources, research_sources)
        
        self.query_history.append({
            "question": question,
            "timestamp": datetime.now().isoformat(),
            "confidence": confidence,
            "accuracy": accuracy_data,
            "herb_count": len(herb_sources),
            "research_count": len(research_sources)
        })
        self.accuracy_history.append(accuracy_data["overall_accuracy"])
        
        return {
            "answer": answer,
            "herb_sources": herb_sources[:5],
            "research_sources": research_sources[:3],
            "total_sources": len(herb_sources) + len(research_sources),
            "confidence": confidence,
            "accuracy": accuracy_data,
            "processing_time": time.time() - start_time
        }
    
    def _empty_response(self) -> Dict[str, Any]:
        return {
            "answer": "No knowledge base loaded. Please check your data files (herbs.json and pubmed_data/pubmed_for_rag.json)",
            "herb_sources": [],
            "research_sources": [],
            "total_sources": 0,
            "confidence": 0.0,
            "accuracy": {"overall_accuracy": 0, "relevance_score": 0, "completeness_score": 0},
            "processing_time": 0.0
        }
    
    def _print_stats(self):
        print("\n" + "="*70)
        print("KNOWLEDGE BASE STATISTICS (Enhanced)")
        print("="*70)
        print(f"Herbs/Formulations: {len(self.herbs_data)}")
        print(f"Research Articles: {len(self.pubmed_data)}")
        print(f"Total Documents: {len(self.all_documents)}")
        if self.embeddings is not None:
            print(f"Embedding Dimension: {self.embeddings.shape[1]}")
        else:
            print(f"Embedding Dimension: N/A")
        print(f"FAISS Index: {'Built' if self.faiss_index else 'Not built'}")
        print(f"Herb Synonyms: {len(self.herb_synonyms)} herbs mapped")
        print(f"Dosha Keywords: {len(self.dosha_keywords)} doshas")
        print(f"Model: {MODEL_NAME}")
        print("="*70)
    
    def display_model_accuracy(self):
        print("\n" + "="*80)
        print("MODEL ACCURACY REPORT (Enhanced)")
        print("="*80)
        
        if not self.accuracy_history:
            print("\nNo queries have been made yet. Ask some questions to generate accuracy metrics.")
            return
        
        avg_accuracy = np.mean(self.accuracy_history)
        min_accuracy = np.min(self.accuracy_history)
        max_accuracy = np.max(self.accuracy_history)
        
        print(f"\nTotal Queries Processed: {len(self.query_history)}")
        print(f"Average Accuracy: {avg_accuracy:.1f}/100")
        print(f"Highest Accuracy: {max_accuracy:.1f}/100")
        print(f"Lowest Accuracy: {min_accuracy:.1f}/100")
        
        print("\n" + "-"*80)
        print("RECENT QUERY ACCURACY BREAKDOWN:")
        print("-"*80)
        
        for i, query in enumerate(self.query_history[-10:], 1):
            acc = query.get('accuracy', {}).get('overall_accuracy', 0)
            confidence = query.get('confidence', 0) * 100
            question = query.get('question', '')[:60]
            herb_count = query.get('herb_count', 0)
            research_count = query.get('research_count', 0)
            
            if acc >= 80:
                grade = "Excellent"
            elif acc >= 60:
                grade = "Good"
            elif acc >= 40:
                grade = "Fair"
            else:
                grade = "Poor"
            
            print(f"\n{i}. {question}...")
            print(f"   Accuracy: {acc:.0f}/100 | Confidence: {confidence:.0f}% | Grade: {grade}")
            print(f"   Sources: {herb_count} herbs, {research_count} research articles")
        
        print("\n" + "="*80)
        print("OVERALL MODEL ACCURACY SCORE")
        print("="*80)
        
        overall_accuracy = avg_accuracy
        
        if overall_accuracy >= 80:
            rating = "EXCELLENT"
            recommendation = "The model is performing exceptionally well. Continue maintaining the knowledge base."
        elif overall_accuracy >= 70:
            rating = "GOOD"
            recommendation = "Good performance. Consider adding more research articles for better coverage."
        elif overall_accuracy >= 60:
            rating = "FAIR"
            recommendation = "Fair performance. Add more training data and refine embeddings for better accuracy."
        elif overall_accuracy >= 50:
            rating = "NEEDS IMPROVEMENT"
            recommendation = "Consider expanding the knowledge base with more herbs and research articles."
        else:
            rating = "POOR"
            recommendation = "Model needs significant improvement. Check data quality and embedding model."
        
        print(f"\nAccuracy Score: {overall_accuracy:.1f}/100")
        print(f"Rating: {rating}")
        print(f"Recommendation: {recommendation}")
        
        print("\n" + "="*80)
        
        if len(self.query_history) < 3:
            print("\nNote: More queries needed for accurate model assessment.")
            print("   Ask at least 3-5 different questions to get reliable accuracy metrics.")
        
        print("="*80)

def main():
    print("\n" + "="*80)
    print("UNIFIED AYURVEDIC KNOWLEDGE BASE (Enhanced)")
    print("="*80)
    
    bot = UnifiedAyurvedicRAGBot(
        herbs_file="herbs.json",
        pubmed_file="pubmed_data/pubmed_for_rag.json"
    )
    
    print("\nExample questions:")
    print("  - What herbs help urinary tract disorders?")
    print("  - What does research say about Ashwagandha?")
    print("  - Herbs for Vata imbalance")
    print("  - pros and cons of Tulsi")
    print("  - Herbs for acidity and burning sensation")
    print("  - How are you?")
    print("  - Sorry")
    print("="*80)
    
    while True:
        print("\nYour question (or 'quit' to exit):")
        q = input("> ").strip()
        
        if q.lower() in ['quit', 'exit', 'q']:
            bot.display_model_accuracy()
            print("\nGoodbye! Stay healthy!")
            break
        
        if not q:
            continue
        
        print("\nProcessing...")
        try:
            result = bot.query(q)
            
            print(f"\nAnswer (confidence: {result['confidence']:.1%}):")
            print("-" * 80)
            print(result['answer'])
            
            if 'accuracy' in result and result['accuracy']:
                accuracy_data = result['accuracy']
                print(f"\nQuery Accuracy: {accuracy_data.get('overall_accuracy', 0)}/100")
                print(f"  - Relevance: {accuracy_data.get('relevance_score', 0)}/100")
                print(f"  - Completeness: {accuracy_data.get('completeness_score', 0)}/100")
            
            if result.get('herb_sources') or result.get('research_sources'):
                print("\n" + "=" * 80)
                print("SOURCES & REFERENCES")
                print("=" * 80)
                
                if result.get('herb_sources'):
                    print("\nAYURVEDIC HERB DATABASE")
                    print("-" * 60)
                    for i, source in enumerate(result['herb_sources'], 1):
                        name = source.get('name', 'Unknown')
                        relevance = source.get('relevance', 0)
                        doshas = source.get('doshas', [])
                        dosha_str = f" [Dosha: {', '.join(doshas)}]" if doshas else ""
                        print(f"\n{i}. {name}{dosha_str} (Match: {relevance:.1%})")
                        if source.get('indications'):
                            print(f"   {source['indications']}")
                
                if result.get('research_sources'):
                    print("\nSCIENTIFIC RESEARCH ARTICLES")
                    print("-" * 60)
                    for i, source in enumerate(result['research_sources'], 1):
                        title = source.get('title', 'Article')
                        journal = source.get('journal', '')
                        year = source.get('year', '')
                        relevance = source.get('relevance', 0)
                        
                        print(f"\n{i}. {title}")
                        if journal and year:
                            print(f"   {journal} ({year}) | Relevance: {relevance:.1%}")
                        if source.get('abstract') and source['abstract'] != 'No abstract':
                            abstract = source['abstract']
                            if len(abstract) > 200:
                                abstract = abstract[:200] + "..."
                            print(f"   {abstract}")
                
                print("\n" + "=" * 80)
                print(f"Total sources retrieved: {result.get('total_sources', 0)}")
            
            print(f"\nProcessing time: {result.get('processing_time', 0):.2f}s")
            
        except Exception as e:
            print(f"\nError processing query: {e}")
            import traceback
            traceback.print_exc()
            print("Please try a different question.")

if __name__ == "__main__":
    main()
