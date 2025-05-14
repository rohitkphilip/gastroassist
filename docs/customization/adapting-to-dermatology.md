# Adapting to Dermatology: Domain-Specific Implementation Guide

This guide provides comprehensive instructions for adapting the GastroAssist system to create DermaAssist, a specialized QA system for dermatology.

## Overview

Converting GastroAssist to serve dermatology involves several key modifications:

1. Updating medical knowledge dictionaries
2. Adjusting search parameters for dermatology sources
3. Modifying prompts for dermatology expertise
4. Creating dermatology-specific test cases
5. Updating frontend components
6. Extending functionality for dermatology-specific features

The changes preserve the core architecture while tailoring the system to dermatology needs.

## Core Code Changes

### 1. Reasoning Agent Modification

**File**: `app/core/reasoning_agent.py`

Replace gastroenterology-specific medical dictionaries with dermatology-focused terms:

```python
class ReasoningAgent:
    """
    Analyzes queries and determines information needs with enhanced medical reasoning
    for the Tavily Search → Tavily Extract → LLM Summarizer pipeline
    """
    
    def __init__(self):
        """Initialize the reasoning agent"""
        # Load environment variables from .env file
        load_dotenv()
        
        # Medical term dictionaries for concept recognition
        self.derm_conditions = [
            "acne", "actinic keratosis", "alopecia", "atopic dermatitis", "basal cell carcinoma",
            "cellulitis", "dermatitis", "eczema", "hidradenitis suppurativa", "impetigo", 
            "keloid", "lichen planus", "melanoma", "melasma", "molluscum contagiosum", 
            "pemphigus", "psoriasis", "rosacea", "scabies", "seborrheic dermatitis", 
            "squamous cell carcinoma", "tinea", "urticaria", "vitiligo", "warts"
        ]
        
        self.derm_procedures = [
            "biopsy", "cryotherapy", "curettage", "dermatoscopy", "electrodesiccation",
            "excision", "laser therapy", "mohs surgery", "patch testing", "phototherapy",
            "punch biopsy", "shave biopsy", "skin grafting", "wood's lamp examination"
        ]
        
        self.medications = [
            "adapalene", "antibiotics", "antifungals", "antihistamines", "benzoyl peroxide",
            "biologics", "corticosteroids", "finasteride", "isotretinoin", "methotrexate",
            "minoxidil", "retinoids", "tacrolimus", "tazarotene", "tretinoin"
        ]
```

Update the analyze method to recognize dermatology queries:

```python
def analyze(self, processed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Analyze a processed query to determine information needs for dermatology
    
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
    
    # Check if query contains dermatology conditions
    derm_conditions_found = [term for term in self.derm_conditions if term in query_lower]
    
    # Check if query contains dermatology procedures
    derm_procedures_found = [term for term in self.derm_procedures if term in query_lower]
    
    # Check if query contains medications
    medications_found = [med for med in self.medications if med in query_lower]
    
    # Check for question types
    is_treatment_query = any(term in query_lower for term in ["treatment", "manage", "therapy", "cure", "how to treat"])
    is_diagnosis_query = any(term in query_lower for term in ["diagnose", "test", "signs", "symptoms", "how to diagnose"])
    is_screening_query = any(term in query_lower for term in ["screen", "prevent", "risk", "when to get", "how often"])
    is_medication_query = any(term in query_lower for term in ["drug", "medication", "dose", "side effect", "interaction"])
    is_guideline_query = any(term in query_lower for term in ["guideline", "recommendation", "consensus", "protocol", "standard"])
    
    # Determine primary query type and build specialized queries
    if derm_conditions_found:
        condition = derm_conditions_found[0]  # Use the first condition found
        
        if is_treatment_query:
            information_needs.append({
                "type": "medical",
                "query": f"current treatment guidelines for {condition} in dermatology",
                "priority": 1.0
            })
        elif is_diagnosis_query:
            information_needs.append({
                "type": "medical",
                "query": f"diagnosis approach for {condition} in dermatology",
                "priority": 1.0
            })
        elif is_medication_query:
            information_needs.append({
                "type": "medical",
                "query": f"medications for {condition} dermatology evidence-based",
                "priority": 1.0
            })
        elif is_guideline_query:
            information_needs.append({
                "type": "medical",
                "query": f"latest clinical guidelines for {condition} dermatology",
                "priority": 1.0
            })
        else:
            information_needs.append({
                "type": "medical",
                "query": f"{condition} dermatology clinical overview",
                "priority": 1.0
            })
    
    # If we haven't identified any specific needs, use the original query
    if not information_needs:
        # Add medical context to the query
        information_needs.append({
            "type": "medical",
            "query": f"dermatology {query_text} evidence-based",
            "priority": 1.0
        })
    
    # Always add the original query as a backup with lower priority
    information_needs.append({
        "type": "medical",
        "query": query_text,
        "priority": 0.8
    })
    
    return information_needs
```

### 2. Knowledge Router Update

**File**: `app/core/knowledge_router.py`

Modify the search_extract_summarize method to prioritize dermatology sources:

```python
def search_extract_summarize(self, query: str, search_type: str = "medical") -> Dict[str, Any]:
    """
    Convenience method to run the full pipeline on a single query
    
    Args:
        query: The search query
        search_type: Type of search to perform (medical or general)
        
    Returns:
        Processed result with summary and sources
    """
    # Add dermatology context to the query if not already present
    if search_type == "medical" and not any(term in query.lower() for term in ["dermatology", "skin", "dermal"]):
        query = f"dermatology {query}"
        
    # Create a single information need
    information_needs = [{
        "type": search_type,
        "query": query
    }]
    
    # Run the full pipeline
    results = self.retrieve(information_needs)
    
    # Return the first result (since we only had one query)
    if results and "need_0" in results:
        return results["need_0"]
    else:
        return {
            "query": query,
            "type": search_type,
            "raw_search_results": [],
            "extracted_contents": [],
            "summarized_response": {
                "summary": "Processing pipeline failed to produce results.",
                "sources": [],
                "error": "Pipeline failure"
            }
        }
```

### 3. Tavily Search Configuration

**File**: `app/knowledge/search_engines/tavily_search.py`

Modify domain filters to prioritize dermatology sources:

```python
def search(self, query: str, search_depth: str = "basic", filter_medical: bool = True) -> List[Dict[str, Any]]:
    """
    Perform a search using the Tavily API
    
    Args:
        query: The search query
        search_depth: Either "basic" or "advanced"
        filter_medical: Whether to filter results to medical content
        
    Returns:
        List of search results
    """
    # Prepare request headers and payload
    # ...
    
    # Add medical filter if requested
    if filter_medical:
        # Add dermatology-specific search parameters
        payload["search_filters"] = {
            "include_domains": [
                "aad.org",                # American Academy of Dermatology
                "dermnetnz.org",          # DermNet NZ
                "skincancer.org",         # Skin Cancer Foundation
                "jaad.org",               # Journal of the American Academy of Dermatology
                "dermatologyadvisor.com", # Dermatology Advisor
                "mdedge.com/dermatology", # MDedge Dermatology
                "nejm.org",               # New England Journal of Medicine
                "jddonline.com",          # Journal of Drugs in Dermatology
                "pubmed.ncbi.nlm.nih.gov",
                "medlineplus.gov",
                "mayoclinic.org"
            ]
        }
    
    # ... rest of the method ...
```

### 4. LLM Summarizer Prompt

**File**: `app/output/llm_summarizer.py`

Update the system prompt and medical prompt template:

```python
def summarize(self, 
              query: str, 
              extracted_contents: List[Dict[str, Any]], 
              max_tokens: int = 500) -> Dict[str, Any]:
    """
    Generate a concise, medically accurate summary from extracted contents
    
    Args:
        query: Original user query
        extracted_contents: List of extracted content dictionaries
        max_tokens: Maximum tokens for the summary response
        
    Returns:
        Dictionary with the summary and metadata
    """
    # ... existing code ...
    
    # Generate the summary using the LLM
    response = self.client.chat.completions.create(
        model=self.model,
        messages=[
            {"role": "system", "content": "You are a dermatology expert assistant providing concise, accurate medical information with proper citations."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.3,
        n=1
    )
    
    # ... rest of the method ...
```

Update the medical prompt template:

```python
def _create_medical_prompt(self, query: str, context: str) -> str:
    """
    Create a prompt specifically designed for dermatological summarization
    
    Args:
        query: Original user query
        context: Formatted context from extracted contents
        
    Returns:
        Prompt string
    """
    prompt = f"""
    As a dermatology expert, provide a concise, accurate response to this query:

    QUERY: {query}

    Below are sources from dermatological literature. Use these to formulate your response.

    {context}

    INSTRUCTIONS:
    1. Only include medical facts directly supported by the sources
    2. Be brief and crisp - focus on the most relevant information
    3. Use clear dermatological terminology for healthcare professionals
    4. Cite sources using [SOURCE X] notation after each fact
    5. If sources conflict, present both perspectives
    6. If information is limited, state this clearly
    7. Avoid personal opinions or unsupported recommendations
    8. Use bullet points for readability when appropriate
    9. Keep your response to 3-7 sentences for straightforward queries
    10. Focus on the direct answer to the query

    YOUR RESPONSE:
    """
    return prompt
```

### 5. Main Application Update

**File**: `app/main.py`

Update the API title and documentation:

```python
app = FastAPI(title="DermaAssist AI API")

@app.get("/")
async def root():
    """
    Root endpoint that provides basic API information and health status
    """
    return {
        "name": "DermaAssist AI API",
        "status": "online",
        "version": "0.1.0",
        "documentation": "/docs",
        "health": "ok"
    }
```

### 6. Frontend Components

**File**: `frontend/components/QueryInput.tsx`

Modify query placeholder text:

```jsx
<input
  type="text"
  value={query}
  onChange={(e) => setQuery(e.target.value)}
  placeholder="Ask a dermatology question..."
  className="query-input"
  disabled={isLoading}
/>
```

## Test Data & Evaluation Changes

### 1. Manual Test Questions

Create a new file: `manual_testing/dermatology_questions.txt`

```
What are the clinical features that differentiate melanoma from benign nevi?
What is the first-line treatment for moderate to severe plaque psoriasis?
What are the latest guidelines for managing atopic dermatitis in adults?
What are the recommended treatments for acne in pregnant patients?
What is the appropriate follow-up schedule for patients with history of melanoma?
What are the diagnostic criteria for hidradenitis suppurativa?
What topical treatments are most effective for rosacea?
How should patch testing be performed and interpreted?
What are the current recommendations for skin cancer screening?
What is the differential diagnosis for annular skin lesions?
```

### 2. Test Evaluation Reference Answers

Create a new file: `manual_testing/dermatology_reference_answers.xlsx`

Structure the file with:
- Question ID
- Question text
- Reference answer
- Source citations

### 3. Evaluation Script Updates

Modify the evaluation prompt in `scripts/eval_summarizer.py`:

```python
def create_evaluation_prompt(query: str, generated_summary: str, reference_summary: str) -> str:
    """
    Create a prompt for the LLM to evaluate the generated summary against the reference.
    """
    prompt = """You are an expert dermatologist tasked with evaluating AI-generated medical summaries.
You will be provided with:
1. A medical query in the field of dermatology
2. A summary generated by an AI system
3. A reference summary (considered the gold standard)

Please evaluate the AI-generated summary on the following criteria:

1. Medical Accuracy (0-10): Correctness of dermatological information and absence of factual errors
2. Relevance (0-10): How well the summary addresses the original query
3. Conciseness (0-10): Brevity and clarity without unnecessary information
4. Source Usage (0-10): Appropriate citation and use of source material
5. Completeness (0-10): Coverage of all important aspects from the reference summary

# ... rest of the prompt ...
```

## Configuration Changes

### 1. Environment Variables

Update the .env file with dermatology-specific comments:

```
# DermaAssist AI Configuration
# API Keys for dermatology knowledge retrieval
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key

# Optional: Add specific services for dermatology
# DERM_IMAGE_API_KEY=your_image_analysis_api_key

# Database
DATABASE_URL=sqlite:///./dermaassist.db

# Server
DEBUG=True
```

## Extended Functionality for Dermatology

### 1. Visual Diagnosis Support

For a complete dermatology system, consider adding image handling capabilities:

**Create new file**: `app/core/image_analyzer.py`

```python
class ImageAnalyzer:
    """
    Analyzes dermatological images to support diagnosis
    """
    
    def __init__(self):
        """Initialize the image analyzer"""
        # Load environment variables
        load_dotenv()
        
        # Initialize image analysis services
        # (implementation depends on chosen service)
    
    def analyze(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze a dermatological image
        
        Args:
            image_data: Binary image data
            
        Returns:
            Dictionary with analysis results
        """
        # Implement image analysis logic
        # This could use OpenAI Vision, Google Cloud Vision, or specialized medical APIs
        
        return {
            "possible_conditions": ["condition1", "condition2"],
            "confidence_scores": [0.85, 0.65],
            "recommendations": "Consult with a dermatologist for confirmation."
        }
```

**Update FastAPI endpoint**:

```python
@app.post("/api/analyze-image")
async def analyze_image(image: UploadFile = File(...)):
    """
    Analyze a dermatological image
    """
    # Read the file
    image_data = await image.read()
    
    # Initialize image analyzer
    image_analyzer = ImageAnalyzer()
    
    # Analyze the image
    analysis_result = image_analyzer.analyze(image_data)
    
    return analysis_result
```

### 2. Dermatology-Specific Calculators

**Create new file**: `app/utils/derm_calculators.py`

```python
def calculate_pasi_score(
    head_severity: Dict[str, int],
    trunk_severity: Dict[str, int],
    upper_limbs_severity: Dict[str, int],
    lower_limbs_severity: Dict[str, int]
) -> float:
    """
    Calculate Psoriasis Area and Severity Index (PASI) score
    
    Args:
        head_severity: Dict with erythema, induration, and scaling scores (0-4) and area score (0-6)
        trunk_severity: Dict with erythema, induration, and scaling scores (0-4) and area score (0-6)
        upper_limbs_severity: Dict with erythema, induration, and scaling scores (0-4) and area score (0-6)
        lower_limbs_severity: Dict with erythema, induration, and scaling scores (0-4) and area score (0-6)
        
    Returns:
        PASI score (0-72)
    """
    # Implementation of PASI score calculation
    # ...
    
    return pasi_score
```

## Implementation Strategy

For efficient conversion, follow this sequence:

1. First update the medical knowledge dictionaries in the reasoning agent
2. Modify the search domain filters for dermatology sources
3. Update LLM prompts for dermatology expertise
4. Create new test data and reference answers
5. Update UI text and placeholders
6. Modify documentation
7. Test the full pipeline with dermatology queries

## Required Domain Expertise

To ensure accurate medical information, consult with:

1. **Dermatologists**: For validating conditions, procedures, and terminology lists
2. **Medical Publications**: For creating test cases from authoritative sources
3. **Medical Informatics Experts**: For dermatology-specific search optimization

## Migration Plan

Here's a systematic approach to migrate from GastroAssist to DermaAssist:

1. **Preparation Phase** (1-2 weeks)
   - Fork the GastroAssist repository
   - Rename all instances of "GastroAssist" to "DermaAssist"
   - Update documentation with dermatology focus
   - Compile dermatology dictionaries and reference materials

2. **Core Implementation Phase** (2-3 weeks)
   - Update medical knowledge dictionaries
   - Modify search parameters
   - Adapt LLM prompting
   - Update frontend components

3. **Testing Phase** (1-2 weeks)
   - Create dermatology test cases
   - Run pipeline tests
   - Evaluate system performance
   - Fine-tune based on results

4. **Production Release** (1 week)
   - Final QA testing
   - Documentation finalization
   - Deployment preparation
   - System launch

## Conclusion

Adapting GastroAssist to create DermaAssist involves primarily changing the medical knowledge dictionaries, search parameters, and prompt engineering to focus on dermatology rather than gastroenterology. The robust pipeline architecture (Tavily Search → Tavily Extract → LLM Summarizer) remains effective, but the content and domain expertise shift to dermatology.

For a complete dermatology solution, consider extending the system with image analysis capabilities, as visual examination is central to dermatological diagnosis.
