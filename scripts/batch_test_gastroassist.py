#!/usr/bin/env python
"""
Batch Test Script for GastroAssist

This script evaluates GastroAssist outputs against expected answers using an LLM as a judge.
It processes test cases from a CSV file and generates a comprehensive evaluation report.

Usage:
    python batch_test_gastroassist.py --input-file manual_testing/Question_Answers_GastroAssist.csv --output-file evaluation_results.xlsx

Requirements:
    - pandas
    - openpyxl
    - tqdm
    - groq (or openai if using OpenAI)
    - matplotlib
    - seaborn
"""

import os
import sys
import argparse
import pandas as pd
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path to import app modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# Import GastroAssist components
from app.core.query_processor import QueryProcessor
from app.core.reasoning_agent import ReasoningAgent
from app.core.knowledge_router import KnowledgeRouter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check which LLM service to use (Groq or OpenAI)
LLM_SERVICE = os.getenv("LLM_SERVICE", "groq").lower()

if LLM_SERVICE == "groq":
    try:
        from groq import Groq
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            logger.error("GROQ_API_KEY environment variable is not set")
            raise ValueError("GROQ_API_KEY is required when using Groq")
        llm_client = Groq(api_key=groq_api_key)
        DEFAULT_MODEL = "llama3-70b-8192"
    except ImportError:
        logger.error("Groq package not found. Install with: pip install groq")
        raise
elif LLM_SERVICE == "openai":
    try:
        from openai import OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("OPENAI_API_KEY environment variable is not set")
            raise ValueError("OPENAI_API_KEY is required when using OpenAI")
        llm_client = OpenAI(api_key=openai_api_key)
        DEFAULT_MODEL = "gpt-4"
    except ImportError:
        logger.error("OpenAI package not found. Install with: pip install openai")
        raise
else:
    logger.error(f"Unsupported LLM_SERVICE: {LLM_SERVICE}. Use 'groq' or 'openai'")
    raise ValueError(f"Unsupported LLM_SERVICE: {LLM_SERVICE}")

# Define evaluation criteria
EVAL_CRITERIA = {
    "medical_accuracy": {
        "weight": 0.35,
        "description": "Correctness of medical information and absence of factual errors"
    },
    "relevance": {
        "weight": 0.20,
        "description": "How well the summary addresses the original query"
    },
    "conciseness": {
        "weight": 0.15,
        "description": "Brevity and clarity without unnecessary information"
    },
    "source_usage": {
        "weight": 0.15,
        "description": "Appropriate citation and use of source material"
    },
    "completeness": {
        "weight": 0.15,
        "description": "Coverage of all important aspects from the reference summary"
    }
}

def initialize_gastroassist():
    """
    Initialize GastroAssist components.
    
    Returns:
        Tuple of initialized components
    """
    logger.info("Initializing GastroAssist components...")
    query_processor = QueryProcessor()
    reasoning_agent = ReasoningAgent()
    knowledge_router = KnowledgeRouter()
    
    return query_processor, reasoning_agent, knowledge_router

def process_query(query: str, 
                  query_processor, 
                  reasoning_agent, 
                  knowledge_router) -> Dict[str, Any]:
    """
    Process a query through the GastroAssist pipeline.
    
    Args:
        query: The query to process
        query_processor: The initialized QueryProcessor
        reasoning_agent: The initialized ReasoningAgent
        knowledge_router: The initialized KnowledgeRouter
        
    Returns:
        Dictionary with results
    """
    try:
        processed_query = query_processor.process(query)
        information_needs = reasoning_agent.analyze(processed_query)
        results = knowledge_router.retrieve(information_needs)
        
        # Extract summary from results
        summary = "No summary generated"
        sources = []
        
        for need_key, need_result in results.items():
            if "summarized_response" in need_result and need_result["summarized_response"]:
                if "summary" in need_result["summarized_response"]:
                    summary = need_result["summarized_response"]["summary"]
                if "sources" in need_result["summarized_response"]:
                    sources = need_result["summarized_response"]["sources"]
                break
        
        return {
            "query": query,
            "summary": summary,
            "sources": sources,
            "full_results": results
        }
    except Exception as e:
        logger.error(f"Error processing query '{query}': {str(e)}")
        return {
            "query": query,
            "summary": f"Error: {str(e)}",
            "sources": [],
            "error": str(e)
        }

def read_test_cases(input_file: str) -> pd.DataFrame:
    """
    Read test cases from a CSV file.
    
    Args:
        input_file: Path to the CSV file
        
    Returns:
        DataFrame with test cases
    """
    try:
        # Try different encodings if there are issues
        for encoding in ['utf-8', 'latin1', 'cp1252']:
            try:
                df = pd.read_csv(input_file, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        # Check required columns
        required_columns = ["Question", "Expected_Answer"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            # Try different column names if the expected ones aren't found
            if "Question" in missing_columns and "query" in df.columns:
                df = df.rename(columns={"query": "Question"})
                missing_columns.remove("Question")
            
            if "Expected_Answer" in missing_columns and "reference_summary" in df.columns:
                df = df.rename(columns={"reference_summary": "Expected_Answer"})
                missing_columns.remove("Expected_Answer")
            
            if "Expected_Answer" in missing_columns and "answer" in df.columns:
                df = df.rename(columns={"answer": "Expected_Answer"})
                missing_columns.remove("Expected_Answer")
                
        # Check again for missing columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns in CSV: {missing_columns}")
            logger.info(f"Available columns: {df.columns.tolist()}")
            raise ValueError(f"Input CSV file missing required columns: {missing_columns}")
        
        # Add ID column if not present
        if "ID" not in df.columns:
            df["ID"] = [f"test_{i+1}" for i in range(len(df))]
        
        return df
        
    except Exception as e:
        logger.error(f"Error reading test cases from {input_file}: {str(e)}")
        raise

def create_evaluation_prompt(query: str, 
                             generated_summary: str, 
                             reference_summary: str) -> str:
    """
    Create a prompt for the LLM to evaluate the generated summary against the reference.
    
    Args:
        query: The original gastroenterology query
        generated_summary: The summary produced by GastroAssist
        reference_summary: The reference/expected summary (gold standard)
        
    Returns:
        A structured prompt for the LLM to perform the evaluation
    """
    prompt = """You are an expert gastroenterologist tasked with evaluating AI-generated medical summaries.
You will be provided with:
1. A medical query in the field of gastroenterology
2. A summary generated by an AI system
3. A reference summary (considered the gold standard)

Please evaluate the AI-generated summary on the following criteria:

1. Medical Accuracy (0-10): Correctness of medical information and absence of factual errors
2. Relevance (0-10): How well the summary addresses the original query
3. Conciseness (0-10): Brevity and clarity without unnecessary information
4. Source Usage (0-10): Appropriate citation and use of source material
5. Completeness (0-10): Coverage of all important aspects from the reference summary

For each criterion, provide:
- A score from 0 to 10 (0 = completely inadequate, 10 = perfect)
- A brief explanation of your rating
- For medical accuracy, specifically note any factual errors or omissions

Finally, provide brief qualitative feedback (2-3 sentences) about the overall quality and usefulness of the generated summary for a gastroenterology professional.

Your evaluation should be fair, objective, and focused on clinical utility.

QUERY:
"{query}"

AI-GENERATED SUMMARY:
"{generated_summary}"

REFERENCE SUMMARY:
"{reference_summary}"

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:
{{
  "medical_accuracy": {{
    "score": [0-10],
    "explanation": "your explanation here"
  }},
  "relevance": {{
    "score": [0-10],
    "explanation": "your explanation here"
  }},
  "conciseness": {{
    "score": [0-10],
    "explanation": "your explanation here"
  }},
  "source_usage": {{
    "score": [0-10],
    "explanation": "your explanation here"
  }},
  "completeness": {{
    "score": [0-10],
    "explanation": "your explanation here"
  }},
  "overall_feedback": "your 2-3 sentence overall feedback here"
}}

Return ONLY the JSON object and nothing else.
"""
    return prompt.format(
        query=query,
        generated_summary=generated_summary,
        reference_summary=reference_summary
    )

def evaluate_with_llm(query: str, 
                      generated_summary: str, 
                      reference_summary: str, 
                      model: str = DEFAULT_MODEL, 
                      max_retries: int = 3) -> Dict[str, Any]:
    """
    Evaluate the generated summary using an LLM.
    
    Args:
        query: The original gastroenterology query
        generated_summary: The summary produced by GastroAssist
        reference_summary: The reference/expected summary (gold standard)
        model: The LLM model to use for evaluation
        max_retries: Maximum number of retries in case of API errors
        
    Returns:
        Dictionary containing the evaluation results
    """
    prompt = create_evaluation_prompt(query, generated_summary, reference_summary)
    
    for attempt in range(max_retries):
        try:
            if LLM_SERVICE == "groq":
                response = llm_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert medical evaluator specializing in gastroenterology."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,  # Lower temperature for more consistent evaluations
                    max_tokens=1500
                )
            else:  # OpenAI
                response = llm_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert medical evaluator specializing in gastroenterology."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,  # Lower temperature for more consistent evaluations
                    max_tokens=1500
                )
            
            # Extract the content from the response
            eval_text = response.choices[0].message.content.strip()
            
            # Parse the JSON response
            try:
                eval_results = json.loads(eval_text)
                return eval_results
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse LLM response as JSON (attempt {attempt+1}/{max_retries})")
                logger.debug(f"Raw response: {eval_text}")
                if attempt == max_retries - 1:
                    return {
                        "error": "Failed to parse LLM response as JSON",
                        "raw_response": eval_text
                    }
                    
        except Exception as e:
            logger.warning(f"Error calling LLM API (attempt {attempt+1}/{max_retries}): {str(e)}")
            if attempt == max_retries - 1:
                return {
                    "error": f"API error: {str(e)}",
                    "raw_response": None
                }
            time.sleep(2)  # Wait before retrying
    
    return {"error": "Unknown error in evaluation", "raw_response": None}

def calculate_weighted_score(eval_results: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
    """
    Calculate a weighted score from the evaluation results.
    
    Args:
        eval_results: Evaluation results from the LLM
        
    Returns:
        Tuple containing (weighted_score, individual_scores)
    """
    scores = {}
    
    # Check if there's an error
    if "error" in eval_results:
        return 0.0, {}
    
    # Calculate scores for each criterion
    for criterion, details in EVAL_CRITERIA.items():
        if criterion in eval_results and "score" in eval_results[criterion]:
            raw_score = eval_results[criterion]["score"]
            # Normalize to 0-1 scale
            normalized_score = raw_score / 10.0
            scores[criterion] = normalized_score
    
    # Calculate weighted score
    weighted_score = sum(
        scores.get(criterion, 0) * details["weight"]
        for criterion, details in EVAL_CRITERIA.items()
    )
    
    return weighted_score, scores

def run_batch_test(test_cases: pd.DataFrame, 
                   query_processor, 
                   reasoning_agent, 
                   knowledge_router,
                   model: str = DEFAULT_MODEL,
                   max_parallel: int = 1) -> List[Dict[str, Any]]:
    """
    Run batch testing on test cases using the GastroAssist pipeline.
    
    Args:
        test_cases: DataFrame with test cases
        query_processor: Initialized QueryProcessor
        reasoning_agent: Initialized ReasoningAgent
        knowledge_router: Initialized KnowledgeRouter
        model: LLM model to use for evaluation
        max_parallel: Maximum parallel requests (not implemented yet)
        
    Returns:
        List of test results
    """
    results = []
    
    for i, row in tqdm(test_cases.iterrows(), total=len(test_cases), desc="Processing test cases"):
        test_id = row.get("ID", f"test_{i+1}")
        query = row["Question"]
        expected_answer = row["Expected_Answer"]
        
        logger.info(f"Processing test case {test_id}: {query}")
        
        # Step 1: Process query through GastroAssist
        gastroassist_result = process_query(query, query_processor, reasoning_agent, knowledge_router)
        generated_summary = gastroassist_result["summary"]
        
        # Step 2: Evaluate using LLM
        eval_result = evaluate_with_llm(
            query=query,
            generated_summary=generated_summary,
            reference_summary=expected_answer,
            model=model
        )
        
        weighted_score, individual_scores = calculate_weighted_score(eval_result)
        
        # Store the results
        result = {
            "id": test_id,
            "query": query,
            "expected_answer": expected_answer,
            "gastroassist_answer": generated_summary,
            "sources": gastroassist_result.get("sources", []),
            "evaluation": eval_result,
            "weighted_score": weighted_score,
            "individual_scores": individual_scores,
            "timestamp": datetime.now().isoformat()
        }
        
        results.append(result)
        logger.info(f"Test case {test_id} completed with score: {weighted_score:.4f}")
        
        # Add a short delay to avoid overwhelming the API
        time.sleep(1)
    
    return results

def generate_excel_report(results: List[Dict[str, Any]], output_file: str) -> None:
    """
    Generate an Excel report from the test results.
    
    Args:
        results: List of test results
        output_file: Path to save the Excel file
    """
    output_path = Path(output_file)
    output_dir = output_path.parent
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a DataFrame with the results
    data = []
    for r in results:
        row = {
            "ID": r["id"],
            "Query": r["query"],
            "Expected Answer": r["expected_answer"],
            "GastroAssist Answer": r["gastroassist_answer"],
            "Weighted Score": r["weighted_score"]
        }
        
        # Add individual scores
        for criterion in EVAL_CRITERIA:
            score = r["individual_scores"].get(criterion, 0)
            row[f"{criterion.replace('_', ' ').title()} Score"] = score
            
            # Add explanations if available
            if "evaluation" in r and criterion in r["evaluation"]:
                explanation = r["evaluation"][criterion].get("explanation", "")
                row[f"{criterion.replace('_', ' ').title()} Explanation"] = explanation
        
        # Add overall feedback
        if "evaluation" in r and "overall_feedback" in r["evaluation"]:
            row["Overall Feedback"] = r["evaluation"]["overall_feedback"]
        
        # Add number of sources
        row["Number of Sources"] = len(r.get("sources", []))
        
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Create a summary sheet
    summary_data = {
        "Metric": ["Total Test Cases", "Average Weighted Score"] + 
                  [f"Average {criterion.replace('_', ' ').title()} Score" for criterion in EVAL_CRITERIA] +
                  ["Highest Scoring Test Case", "Lowest Scoring Test Case"],
        "Value": [
            len(results),
            df["Weighted Score"].mean(),
        ] + 
        [df[f"{criterion.replace('_', ' ').title()} Score"].mean() for criterion in EVAL_CRITERIA] +
        [
            df.loc[df["Weighted Score"].idxmax(), "ID"] if not df.empty else "N/A",
            df.loc[df["Weighted Score"].idxmin(), "ID"] if not df.empty else "N/A"
        ]
    }
    summary_df = pd.DataFrame(summary_data)
    
    # Save to Excel with multiple sheets
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Detailed Results', index=False)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Create a sheet for each test case with complete details
        for i, r in enumerate(results):
            test_id = r["id"]
            test_df = pd.DataFrame([
                {"Field": "Query", "Value": r["query"]},
                {"Field": "Expected Answer", "Value": r["expected_answer"]},
                {"Field": "GastroAssist Answer", "Value": r["gastroassist_answer"]},
                {"Field": "Weighted Score", "Value": r["weighted_score"]}
            ])
            
            # Add individual scores and explanations
            for criterion in EVAL_CRITERIA:
                score = r["individual_scores"].get(criterion, 0)
                explanation = ""
                if "evaluation" in r and criterion in r["evaluation"]:
                    explanation = r["evaluation"][criterion].get("explanation", "")
                
                test_df = pd.concat([test_df, pd.DataFrame([
                    {"Field": f"{criterion.replace('_', ' ').title()} Score", "Value": score},
                    {"Field": f"{criterion.replace('_', ' ').title()} Explanation", "Value": explanation}
                ])])
            
            # Add overall feedback
            if "evaluation" in r and "overall_feedback" in r["evaluation"]:
                test_df = pd.concat([test_df, pd.DataFrame([
                    {"Field": "Overall Feedback", "Value": r["evaluation"]["overall_feedback"]}
                ])])
            
            # Add sources
            for j, source in enumerate(r.get("sources", [])):
                source_str = f"Source {j+1}: {source.get('title', 'Unknown')} - {source.get('url', 'No URL')}"
                test_df = pd.concat([test_df, pd.DataFrame([
                    {"Field": f"Source {j+1}", "Value": source_str}
                ])])
            
            sheet_name = f"Test {i+1} - {test_id}"
            # Excel sheet names have a 31 character limit
            if len(sheet_name) > 31:
                sheet_name = sheet_name[:31]
                
            test_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    logger.info(f"Excel report saved to {output_file}")

def generate_json_report(results: List[Dict[str, Any]], output_file: str) -> None:
    """
    Generate a JSON report from the test results.
    
    Args:
        results: List of test results
        output_file: Path to save the JSON file
    """
    output_path = Path(output_file)
    output_dir = output_path.parent
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"JSON report saved to {output_path}")

def generate_visualizations(results: List[Dict[str, Any]], output_file: str) -> None:
    """
    Generate visualizations from the test results.
    
    Args:
        results: List of test results
        output_file: Path to save the visualizations
    """
    output_path = Path(output_file)
    output_dir = output_path.parent
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare data
    scores_data = []
    for r in results:
        for criterion, score in r["individual_scores"].items():
            scores_data.append({
                "Test ID": r["id"],
                "Criterion": criterion.replace('_', ' ').title(),
                "Score": score
            })
    
    if not scores_data:
        logger.warning("No score data available for visualization")
        return
        
    scores_df = pd.DataFrame(scores_data)
    
    # Create visualizations
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Average scores by criterion
    plt.subplot(2, 2, 1)
    sns.barplot(x="Criterion", y="Score", data=scores_df)
    plt.title("Average Scores by Criterion")
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0, 1.0)
    
    # Plot 2: Distribution of weighted scores
    plt.subplot(2, 2, 2)
    weighted_scores = [r["weighted_score"] for r in results]
    plt.hist(weighted_scores, bins=10)
    plt.title("Distribution of Weighted Scores")
    plt.xlabel("Score")
    plt.ylabel("Frequency")
    
    # Plot 3: Heatmap of scores
    plt.subplot(2, 1, 2)
    pivot_df = scores_df.pivot_table(values="Score", index="Test ID", columns="Criterion")
    sns.heatmap(pivot_df, annot=True, cmap="YlGnBu", vmin=0, vmax=1)
    plt.title("Score Heatmap by Test Case and Criterion")
    
    plt.tight_layout()
    plt.savefig(output_path)
    logger.info(f"Visualizations saved to {output_path}")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Batch test GastroAssist against expected answers using LLM evaluation.")
    parser.add_argument("--input-file", type=str, required=True, help="Path to the input CSV file with test cases")
    parser.add_argument("--output-dir", type=str, default="manual_testing/results", help="Directory for saving results")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="LLM model for evaluation")
    parser.add_argument("--max-tests", type=int, default=None, help="Maximum number of tests to run (for debugging)")
    parser.add_argument("--run-gastroassist", action="store_true", help="Run queries through GastroAssist (otherwise use precomputed results)")
    
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_arguments()
    
    # Setup output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    base_filename = Path(args.input_file).stem
    output_base = output_dir / f"{base_filename}_evaluation_{timestamp}"
    
    excel_output = f"{output_base}.xlsx"
    json_output = f"{output_base}.json"
    viz_output = f"{output_base}.png"
    
    # Read test cases
    logger.info(f"Reading test cases from {args.input_file}")
    test_cases = read_test_cases(args.input_file)
    
    # Limit number of tests if specified
    if args.max_tests is not None:
        test_cases = test_cases.head(args.max_tests)
        logger.info(f"Limited to {args.max_tests} test cases")
    
    logger.info(f"Loaded {len(test_cases)} test cases")
    
    # Initialize GastroAssist if needed
    if args.run_gastroassist:
        query_processor, reasoning_agent, knowledge_router = initialize_gastroassist()
    else:
        # Use placeholder values since we're not using them
        query_processor, reasoning_agent, knowledge_router = None, None, None
    
    # Run batch tests
    logger.info("Starting batch testing...")
    results = run_batch_test(
        test_cases=test_cases,
        query_processor=query_processor,
        reasoning_agent=reasoning_agent,
        knowledge_router=knowledge_router,
        model=args.model
    )
    
    # Generate reports
    generate_excel_report(results, excel_output)
    generate_json_report(results, json_output)
    generate_visualizations(results, viz_output)
    
    # Print summary
    print("\n" + "="*50)
    print("BATCH TEST SUMMARY")
    print("="*50)
    print(f"Total test cases: {len(results)}")
    
    if results:
        weighted_scores = [r["weighted_score"] for r in results]
        avg_weighted_score = sum(weighted_scores) / len(weighted_scores)
        print(f"Average weighted score: {avg_weighted_score:.4f}")
        
        criterion_scores = {}
        for criterion in EVAL_CRITERIA:
            scores = [r["individual_scores"].get(criterion, 0) for r in results]
            avg_score = sum(scores) / len(scores) if scores else 0
            criterion_scores[criterion] = avg_score
            print(f"Average {criterion.replace('_', ' ')} score: {avg_score:.4f}")
    
    print("\nReports saved to:")
    print(f"- Excel: {excel_output}")
    print(f"- JSON: {json_output}")
    print(f"- Visualization: {viz_output}")
    print("="*50)

if __name__ == "__main__":
    main()
