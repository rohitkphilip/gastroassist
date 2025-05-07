from typing import Dict, Any, List
import os
from dotenv import load_dotenv
import re

class ReasoningAgent:
    """
    Analyzes queries and determines information needs with enhanced medical reasoning
    for the Tavily Search -> Tavily Extract -> LLM Summarizer pipeline
    """
    
    def __init__(self):
        """Initialize the reasoning agent"""
        # Load environment variables from .env file
        load_dotenv()
        
        # Medical term dictionaries for concept recognition
        self.gi_conditions = [
            "gerd", "acid reflux", "heartburn", "Barrett's esophagus", 
            "esophagitis", "peptic ulcer", "gastritis", "H. pylori", "helicobacter",
            "dyspepsia", "gastroparesis", "ibs", "irritable bowel syndrome", 
            "Crohn's disease", "ulcerative colitis", "ibd", "inflammatory bowel disease",
            "celiac disease", "microscopic colitis", "collagenous colitis", "lymphocytic colitis",
            "diverticulosis", "diverticulitis", "polyps", "colorectal cancer", "colon cancer",
            "rectal cancer", "anal fissure", "hemorrhoids", "fecal incontinence",
            "constipation", "diarrhea", "gi bleeding", "pancreatitis", "gallstones",
            "cholecystitis", "cirrhosis", "hepatitis", "nash", "fatty liver", "jaundice",
            "ascites", "varices", "dysphagia", "odynophagia", "gastroenteritis"
        ]
        
        self.gi_procedures = [
            "endoscopy", "colonoscopy", "sigmoidoscopy", "ercp", "eus", "capsule endoscopy",
            "manometry", "ph monitoring", "breath test", "stool test", "biopsy", "polypectomy",
            "emr", "esd", "band ligation", "sclerotherapy", "paracentesis", "fibroscan",
            "liver biopsy", "gastric emptying study"
        ]
        
        self.medications = [
            "ppi", "proton pump inhibitor", "omeprazole", "esomeprazole", "pantoprazole", 
            "lansoprazole", "dexlansoprazole", "rabeprazole", "h2 blocker", "famotidine", 
            "cimetidine", "ranitidine", "antacid", "sucralfate", "misoprostol", 
            "bismuth", "antibiotic", "metronidazole", "clarithromycin", "amoxicillin",
            "tetracycline", "levofloxacin", "anti-spasmodic", "dicyclomine", "hyoscyamine",
            "antidiarrheal", "loperamide", "diphenoxylate", "fiber supplement", 
            "laxative", "polyethylene glycol", "lactulose", "linaclotide", "lubiprostone",
            "plecanatide", "senna", "bisacodyl", "probiotics", "rifaximin", "mesalamine",
            "sulfasalazine", "balsalazide", "olsalazine", "budesonide", "prednisone",
            "azathioprine", "6-mp", "methotrexate", "infliximab", "adalimumab",
            "vedolizumab", "ustekinumab", "tofacitinib", "ursodiol", "cholestyramine"
        ]
    
    def analyze(self, processed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze a processed query to determine information needs for the enhanced pipeline
        
        Args:
            processed_query: The processed query information
            
        Returns:
            List of information needs with medical context
        """
        query_text = processed_query.get("normalized_text", "")
        if not query_text and "text" in processed_query:
            query_text = processed_query["text"]
        
        # Convert to lowercase for matching
        query_lower = query_text.lower()
        
        # Initial information needs with the original query
        information_needs = []
        
        # Check if query contains GI conditions
        gi_conditions_found = [term for term in self.gi_conditions if term in query_lower]
        
        # Check if query contains GI procedures
        gi_procedures_found = [term for term in self.gi_procedures if term in query_lower]
        
        # Check if query contains medications
        medications_found = [med for med in self.medications if med in query_lower]
        
        # Check for question types
        is_treatment_query = any(term in query_lower for term in ["treatment", "manage", "therapy", "cure", "how to treat"])
        is_diagnosis_query = any(term in query_lower for term in ["diagnose", "test", "signs", "symptoms", "how to diagnose"])
        is_screening_query = any(term in query_lower for term in ["screen", "prevent", "risk", "when to get", "how often"])
        is_medication_query = any(term in query_lower for term in ["drug", "medication", "dose", "side effect", "interaction"])
        is_guideline_query = any(term in query_lower for term in ["guideline", "recommendation", "consensus", "protocol", "standard"])
        
        # Determine primary query type and build specialized queries
        if gi_conditions_found:
            condition = gi_conditions_found[0]  # Use the first condition found
            
            if is_treatment_query:
                information_needs.append({
                    "type": "medical",
                    "query": f"current treatment guidelines for {condition} in gastroenterology",
                    "priority": 1.0
                })
            elif is_diagnosis_query:
                information_needs.append({
                    "type": "medical",
                    "query": f"diagnosis approach for {condition} in gastroenterology",
                    "priority": 1.0
                })
            elif is_medication_query:
                information_needs.append({
                    "type": "medical",
                    "query": f"medications for {condition} gastroenterology evidence-based",
                    "priority": 1.0
                })
            elif is_guideline_query:
                information_needs.append({
                    "type": "medical",
                    "query": f"latest clinical guidelines for {condition} gastroenterology",
                    "priority": 1.0
                })
            else:
                information_needs.append({
                    "type": "medical",
                    "query": f"{condition} gastroenterology clinical overview",
                    "priority": 1.0
                })
        
        elif gi_procedures_found:
            procedure = gi_procedures_found[0]  # Use the first procedure found
            
            information_needs.append({
                "type": "medical",
                "query": f"{procedure} in gastroenterology indications techniques evidence-based",
                "priority": 1.0
            })
        
        elif medications_found:
            medication = medications_found[0]  # Use the first medication found
            
            information_needs.append({
                "type": "medical",
                "query": f"{medication} in gastroenterology uses dosing evidence-based",
                "priority": 1.0
            })
        
        elif is_screening_query:
            # Generic screening query
            information_needs.append({
                "type": "medical",
                "query": f"gastroenterology screening guidelines {query_text}",
                "priority": 1.0
            })
        
        # If we haven't identified any specific needs, use the original query
        if not information_needs:
            # Add medical context to the query
            information_needs.append({
                "type": "medical",
                "query": f"gastroenterology {query_text} evidence-based",
                "priority": 1.0
            })
        
        # Always add the original query as a backup with lower priority
        information_needs.append({
            "type": "medical",
            "query": query_text,
            "priority": 0.8
        })
        
        return information_needs
