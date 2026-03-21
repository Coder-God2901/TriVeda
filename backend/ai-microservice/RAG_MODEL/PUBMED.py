import requests
from xml.etree import ElementTree
import json
import time
import os
from datetime import datetime
import random

class PubMedScraper:
    """Enhanced PubMed scraper for Ayurveda research articles"""
    
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.results = []
        self.failed_terms = []
        self.stats = {
            "total_searched": 0,
            "total_found": 0,
            "start_time": datetime.now().isoformat(),
            "terms_processed": 0
        }
        
        
        os.makedirs("pubmed_data", exist_ok=True)
    
    def search(self, keyword, max_results=30):
        """Search PubMed using E-utilities API"""
        print(f"\n Searching PubMed for: '{keyword}'")
        
        
        formatted_term = f"ayurveda AND {keyword}"
        
        
        search_url = f"{self.base_url}esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": formatted_term,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance"  
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                id_list = data.get("esearchresult", {}).get("idlist", [])
                count = data.get("esearchresult", {}).get("count", "0")
                
                print(f"    Total available: {count} | Fetching: {len(id_list)}")
                
                if len(id_list) == 0:
                    self.failed_terms.append(keyword)
                    return []
                
                
                articles = []
                for i, pmid in enumerate(id_list):
                    print(f"    Fetching article {i+1}/{len(id_list)} (PMID: {pmid})", end="\r")
                    article = self.fetch_details(pmid, keyword)
                    if article:
                        articles.append(article)
                    time.sleep(0.34)  
                
                print(f"    Found {len(articles)} articles for '{keyword}'")
                return articles
            
            else:
                print(f"    HTTP Error {response.status_code}")
                self.failed_terms.append(keyword)
                return []
                
        except requests.exceptions.Timeout:
            print(f"    Timeout error for '{keyword}'")
            self.failed_terms.append(keyword)
            return []
        except Exception as e:
            print(f"    Error: {e}")
            self.failed_terms.append(keyword)
            return []
    
    def fetch_details(self, pmid, keyword):
        """Fetch article details using efetch"""
        fetch_url = f"{self.base_url}efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml"
        }
        
        try:
            response = requests.get(fetch_url, params=params, timeout=10)
            if response.status_code == 200:
                
                root = ElementTree.fromstring(response.content)
                
                
                article = {
                    "pmid": pmid,
                    "search_keyword": keyword,
                    "title": self.extract_text(root, ".//ArticleTitle"),
                    "abstract": self.extract_text(root, ".//AbstractText"),
                    "journal": self.extract_text(root, ".//Title"),
                    "volume": self.extract_text(root, ".//Volume"),
                    "issue": self.extract_text(root, ".//Issue"),
                    "pages": self.extract_text(root, ".//MedlinePgn"),
                    "year": self.extract_text(root, ".//PubDate/Year"),
                    "month": self.extract_text(root, ".//PubDate/Month"),
                    "day": self.extract_text(root, ".//PubDate/Day"),
                    "authors": self.extract_authors(root),
                    "affiliations": self.extract_affiliations(root),
                    "doi": self.extract_doi(root),
                    "mesh_terms": self.extract_mesh_terms(root),
                    "article_type": self.extract_article_type(root),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                }
                return article
        except Exception as e:
            print(f"    Error fetching {pmid}: {e}")
        
        return None
    
    def extract_text(self, root, xpath):
        """Extract text from XML element"""
        elem = root.find(xpath)
        return elem.text.strip() if elem is not None and elem.text else ""
    
    def extract_authors(self, root):
        """Extract author names"""
        authors = []
        for author in root.findall(".//Author"):
            last = author.find("LastName")
            fore = author.find("ForeName")
            if last is not None and fore is not None:
                authors.append(f"{fore.text} {last.text}")
            elif last is not None:
                authors.append(last.text)
        return ", ".join(authors[:10]) 
    
    def extract_affiliations(self, root):
        """Extract author affiliations"""
        affiliations = []
        for aff in root.findall(".//Affiliation"):
            if aff.text:
                affiliations.append(aff.text)
        return " | ".join(affiliations[:3])  
    
    def extract_doi(self, root):
        """Extract DOI if available"""
        for el in root.findall(".//ELocationID"):
            if el.get("EIdType") == "doi" and el.text:
                return el.text
        return ""
    
    def extract_mesh_terms(self, root):
        """Extract MeSH terms"""
        terms = []
        for mesh in root.findall(".//MeshHeading/DescriptorName"):
            if mesh.text:
                terms.append(mesh.text)
        return ", ".join(terms[:15])  
    
    def extract_article_type(self, root):
        """Extract article type/publication type"""
        types = []
        for pt in root.findall(".//PublicationType"):
            if pt.text:
                types.append(pt.text)
        return ", ".join(types)
    
    def save_to_json(self, filename, data):
        """Save results to JSON"""
        filepath = os.path.join("pubmed_data", filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f" Saved {len(data)} articles to {filepath}")
    
    def save_stats(self):
        """Save statistics"""
        self.stats["end_time"] = datetime.now().isoformat()
        self.stats["total_found"] = len(self.results)
        self.stats["failed_terms"] = self.failed_terms
        
        stats_file = os.path.join("pubmed_data", "scraping_stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2)
        print(f" Stats saved to {stats_file}")
    
    def create_rag_format(self):
        """Convert to RAG-ready format"""
        rag_docs = []
        
        for i, article in enumerate(self.results):
            
            doc_text = f"""
TITLE: {article.get('title', 'No title')}
AUTHORS: {article.get('authors', 'Unknown')}
JOURNAL: {article.get('journal', 'Unknown')} ({article.get('year', 'No year')})
VOLUME: {article.get('volume', 'N/A')} ISSUE: {article.get('issue', 'N/A')} PAGES: {article.get('pages', 'N/A')}
PMID: {article.get('pmid', 'N/A')}
DOI: {article.get('doi', 'N/A')}
ARTICLE TYPE: {article.get('article_type', 'N/A')}

ABSTRACT:
{article.get('abstract', 'No abstract available')}

MESH TERMS:
{article.get('mesh_terms', 'N/A')}

SEARCH KEYWORD: {article.get('search_keyword', '')}
SOURCE: PubMed
"""
            
            rag_docs.append({
                'id': f"pubmed_{article.get('pmid', i)}",
                'text': doc_text,
                'metadata': {
                    'pmid': article.get('pmid'),
                    'title': article.get('title'),
                    'authors': article.get('authors'),
                    'journal': article.get('journal'),
                    'year': article.get('year'),
                    'doi': article.get('doi'),
                    'mesh_terms': article.get('mesh_terms'),
                    'search_keyword': article.get('search_keyword'),
                    'url': article.get('url')
                }
            })
        
        self.save_to_json("pubmed_for_rag.json", rag_docs)
        print(f" Created {len(rag_docs)} RAG-ready documents")
        return rag_docs





AYURVEDIC_TERMS = [
    
    "Amlapitta", "Grahani", "Ajirna", "Atisara", "Vibandha", 
    "Adhmana", "Yakrit Vikara", "Kamala", "Udara Roga", "Gulma", 
    "Arsha", "Udara shoola", "Chhardi", "Trishna", "Aruchi",
    
    
    "Amavata", "Sandhigata Vata", "Vatarakta", "Gridhrasi", "Katigraha",
    "Manyastambha", "Pakshaghata", "Avabahuka", "Apabahukam", "Marmabhighatam",
    "Khanja", "Pangu", "Vishwachi", "Kati Shoola", "Asthi Majja Vikara",
    
    
    "Vatavyadhi", "Ardita", "Akshepaka", "Apasmara", "Kampavata",
    "Unmada", "Chittodvega", "Anidra", "Vishada", "Padasupthi",
    "Sirah shoola", "Ardhavabhedaka", "Suryavarta", "Ananta vata", "Dhatri",
    
    
    "Prameha", "Sthaulya", "Karshya", "Madatyaya", "Hridroga",
    "Uccha Rakta Chapa", "Medoroga", "Madhumeha", "Vatarakta", "Raktapitta",
    
    
    "Tamaka Shwasa", "Kasa", "Rajayakshma", "Peenasa", "Pratishyaya",
    "Hikka", "Shwasa roga", "Urah kshata", "Pinasa", "Kaphaja Kasa",
    "Vataja Kasa", "Pittaja Kasa",
    
    
    "Kushtha", "Sidhma Kushtha", "Vicharchika", "Dadru", "Shvitra",
    "Visarpa", "Mandala Kushtha", "Kitibha", "Vicarcika", "Pama",
    "Charmadala", "Indralupta", "Khalya", "Palitya", "Vyanga",
    
    
    "Jwara", "Vatajwara", "Pittajwara", "Kaphajwara", "Vishamajwara",
    "Dhatrijwara", "Pratishyaya jwara", "Abhinyasa jwara", "Ama jwara", "Punaravartaka jwara",
    
    
    "Abhishyanda", "Timira", "Kacha", "Karnashoola", "Karnanada",
    "Mukhapaka", "Dantashoola", "Netra roga", "Karna roga", "Nasa roga",
    "Shiro roga", "Kantharoga", "Swara bheda", "Gala graha", "Tundikeri",
    
    
    "Mutrakrichra", "Ashmari", "Mutraghata", "Vatashthila", "Mutra krichra",
    "Mutra jwara", "Prameha", "Mutradosha", "Basti vikara", "Vrukka roga",
    "Mutra sanga", "Mutra atisa",
    
    
    "Klaibya", "Vandhyatva", "Shukradushti", "Shukra dosha", "Shukra alpa",
    "Shukra stambha", "Dhvaja bhanga", "Napumsakata",
    
    
    "Artava dushti", "Asrigdara", "Kashtartava", "Shweta pradara", "Yonivyapad",
    "Garbhashaya shotha", "Garbhini chardi", "Sutika roga", "Rajonivritti", "Yoni kanda",
    "Yoni arsha", "Yoni shoola", "Pushpaghni", "Vandhyatva stri", "Garbha srava",
    
    
    "Arbuda", "Granthi", "Mamsarbuda", "Raktarbuda", "Medo arbuda", "Asthi arbuda",
    
    
    "Balashosha", "Balaka graha", "Dantodbheda jwara", "Karshya bala", "Grahami bala",
    "Phakka roga", "Parigarbhika", "Revati graha", "Skanda graha", "Shushka revati",
    
    
    "Amavata", "Vatarakta", "Kushtha", "Shvitra", "Lupus", "SLE", "Rheumatoid", "Psoriasis",
    
    
    "Ayurvedic treatment", "Panchakarma", "Rasayana", "Vajikarana",
    "Dinacharya", "Ritucharya", "Sadvritta", "Achara rasayana",
    
    
    "Diabetes Ayurveda", "Hypertension Ayurveda", "Arthritis Ayurveda",
    "Asthma Ayurveda", "Cancer Ayurveda", "Liver disease Ayurveda",
    "Kidney disease Ayurveda", "Heart disease Ayurveda", "Skin disease Ayurveda",
    "Mental health Ayurveda"
]


ENGLISH_TERMS = [
    
    "Acidity Ayurveda", "IBS Ayurveda", "Indigestion Ayurveda", "Diarrhea Ayurveda", 
    "Constipation Ayurveda", "Flatulence Ayurveda", "Liver disorders Ayurveda", 
    "Jaundice Ayurveda", "Ascites Ayurveda", "Hemorrhoids Ayurveda",
    
    
    "Rheumatoid arthritis Ayurveda", "Osteoarthritis Ayurveda", "Gout Ayurveda", 
    "Sciatica Ayurveda", "Back pain Ayurveda", "Cervical spondylosis Ayurveda", 
    "Paralysis Ayurveda", "Frozen shoulder Ayurveda", "Stroke Ayurveda",
    
    
    "Parkinson Ayurveda", "Epilepsy Ayurveda", "Anxiety Ayurveda", "Insomnia Ayurveda", 
    "Depression Ayurveda", "Migraine Ayurveda", "Headache Ayurveda",
    
    
    "Diabetes Ayurveda", "Obesity Ayurveda", "Hypertension Ayurveda", 
    "High cholesterol Ayurveda", "Metabolic syndrome Ayurveda",
    
    
    "Asthma Ayurveda", "Bronchitis Ayurveda", "Tuberculosis Ayurveda", 
    "Sinusitis Ayurveda", "Cold Ayurveda", "Cough Ayurveda",
    
    
    "Psoriasis Ayurveda", "Eczema Ayurveda", "Ringworm Ayurveda", "Vitiligo Ayurveda", 
    "Herpes Ayurveda", "Acne Ayurveda", "Skin allergy Ayurveda",
    
    
    "UTI Ayurveda", "Kidney stones Ayurveda", "Dysuria Ayurveda", "Urinary retention Ayurveda",
    "BPH Ayurveda", "Prostate Ayurveda",
    
    
    "Infertility Ayurveda", "Erectile dysfunction Ayurveda", "Menstrual disorders Ayurveda",
    "PCOS Ayurveda", "Leukorrhea Ayurveda", "Menorrhagia Ayurveda",
    
    
    "Pregnancy Ayurveda", "Postpartum Ayurveda", "Menopause Ayurveda",
    
    
    "Immunity Ayurveda", "Digestion Ayurveda", "Stress Ayurveda", "Anti-aging Ayurveda"
]


ALL_TERMS = []
seen = set()
for term in AYURVEDIC_TERMS + ENGLISH_TERMS:
    if term.lower() not in seen:
        ALL_TERMS.append(term)
        seen.add(term.lower())

print(f" Loaded {len(ALL_TERMS)} unique search terms")




def main():
    print("\n" + "="*80)
    print("   PUBMED AYURVEDA RESEARCH SCRAPER - ENHANCED VERSION")
    print("="*80)
    print(f"   Total search terms: {len(ALL_TERMS)}")
    print("  ⏱  Estimated time: ~{:.1f} minutes".format(len(ALL_TERMS) * 12 / 60))  
    print("="*80)
    
    scraper = PubMedScraper()
    all_articles = []
    
    
    print("\n  Options:")
    print("  1. Process ALL terms (recommended for final build)")
    print("  2. Process first 20 terms (quick test)")
    print("  3. Process specific category")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    terms_to_process = []
    if choice == "1":
        terms_to_process = ALL_TERMS
    elif choice == "2":
        terms_to_process = ALL_TERMS[:20]
        print(f"    Testing with first 20 terms")
    elif choice == "3":
        print("\nCategories:")
        print("  a. Gastrointestinal")
        print("  b. Musculoskeletal")
        print("  c. Neurological")
        print("  d. Metabolic")
        print("  e. Respiratory")
        print("  f. Skin")
        print("  g. Urinary/Reproductive")
        print("  h. General")
        cat = input("Select category (a-h): ").strip().lower()
        
        category_map = {
            'a': AYURVEDIC_TERMS[:15],  
            'b': AYURVEDIC_TERMS[15:30],  
            'c': AYURVEDIC_TERMS[30:45],  
            'd': AYURVEDIC_TERMS[45:55],  
            'e': AYURVEDIC_TERMS[55:67],  
            'f': AYURVEDIC_TERMS[67:82],  
            'g': AYURVEDIC_TERMS[97:117],  
            'h': ENGLISH_TERMS[-10:]  
        }
        terms_to_process = category_map.get(cat, ALL_TERMS[:20])
    
    print(f"\n Starting scrape of {len(terms_to_process)} terms...")
    
    try:
        for i, term in enumerate(terms_to_process, 1):
            print(f"\n [{i}/{len(terms_to_process)}] Processing: {term}")
            
            articles = scraper.search(term, max_results=15)  
            all_articles.extend(articles)
            
            
            scraper.results = all_articles
            scraper.stats["terms_processed"] = i
            scraper.stats["total_found"] = len(all_articles)
            
            
            if i % 5 == 0:
                scraper.save_to_json(f"pubmed_backup_{i}.json", all_articles)
                print(f"    Backup saved at {i} terms")
            
            
            delay = random.uniform(3, 7)
            print(f"    Waiting {delay:.1f}s before next term...")
            time.sleep(delay)
    
    except KeyboardInterrupt:
        print("\n\n Interrupted by user. Saving partial results...")
    
    finally:
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scraper.save_to_json(f"pubmed_ayurveda_final_{timestamp}.json", all_articles)
        scraper.save_to_json("pubmed_ayurveda_latest.json", all_articles)
        
        
        rag_docs = scraper.create_rag_format()
        
        
        scraper.stats["total_articles"] = len(all_articles)
        scraper.stats["failed_terms"] = scraper.failed_terms
        scraper.save_stats()
        
        print("\n" + "="*80)
        print(f" SCRAPING COMPLETE")
        print("="*80)
        print(f" Final Statistics:")
        print(f"   • Terms processed: {scraper.stats['terms_processed']}")
        print(f"   • Articles found: {len(all_articles)}")
        print(f"   • Failed terms: {len(scraper.failed_terms)}")
        print(f"   • RAG documents created: {len(rag_docs)}")
        print(f"\n Files saved in 'pubmed_data/' folder:")
        print(f"   • pubmed_ayurveda_latest.json - Raw article data")
        print(f"   • pubmed_for_rag.json - RAG-ready format")
        print(f"   • scraping_stats.json - Statistics")
        print("="*80)


if __name__ == "__main__":
    main()