import os
import json
import argparse
from pathlib import Path
from datetime import datetime

def extract_summaries_and_sources(results_file=None):
    """
    Extracts summaries and sources from manual testing results JSON file
    
    Args:
        results_file: Optional path to specific results file. If None, uses most recent.
    """
    # Define paths
    results_dir = Path("manual_testing/results")
    extracts_dir = Path("manual_testing/extracts")
    
    # Create extracts directory if it doesn't exist
    extracts_dir.mkdir(exist_ok=True)
    
    # Find the results file to process
    if results_file:
        result_file_path = Path(results_file)
        if not result_file_path.exists():
            print(f"Error: File {results_file} not found.")
            return
    else:
        # Find all result files
        result_files = list(results_dir.glob("results_*.json"))
        if not result_files:
            print("No result files found in results directory.")
            return
        
        # Get the most recent result file
        result_file_path = max(result_files, key=os.path.getmtime)
    
    print(f"Extracting summaries from: {result_file_path}")
    
    # Load results
    with open(result_file_path, "r", encoding="utf-8") as f:
        results = json.load(f)
    
    # Create timestamp for output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = extracts_dir / f"summaries_{timestamp}.md"
    
    # Extract summaries and sources
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# GastroAssist Test Summaries\n\n")
        f.write(f"Source file: {result_file_path.name}\n")
        f.write(f"Extraction date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for i, result in enumerate(results, 1):
            question = result["question"]
            f.write(f"## Question {i}: {question}\n\n")
            
            if "error" in result:
                f.write(f"**ERROR**: {result['error']}\n\n")
                continue
            
            # Check for direct API response format
            if "result" in result.get("response", {}):
                # Handle /api/query/direct response format
                response_data = result["response"]["result"]
                
                # Find the first need with a summarized response
                summary = None
                sources = []
                confidence = None
                summarized = None
                
                for need_key, need_data in response_data.items():
                    if "summarized_response" in need_data:
                        summarized = need_data["summarized_response"]
                        summary = summarized.get("summary", "")
                        sources = summarized.get("sources", [])
                        confidence = summarized.get("confidence_score")
                        break
                
                if summary:
                    f.write(f"### Answer\n\n{summary}\n\n")
                else:
                    f.write("### Answer\n\nNo answer provided\n\n")
                
                # Extract confidence score if available
                if summarized and "confidence_score" in summarized:
                    confidence = summarized.get("confidence_score")
                    if confidence is not None:
                        f.write(f"**Confidence Score**: {confidence*100:.1f}%\n\n")
                
                # Extract sources
                if sources:
                    f.write(f"### Sources ({len(sources)})\n\n")
                    for j, source in enumerate(sources, 1):
                        title = source.get("title", "Untitled")
                        url = source.get("url", "")
                        
                        f.write(f"**Source {j}**: {title}\n")
                        if url:
                            f.write(f"- URL: {url}\n")
                        f.write("\n")
            else:
                # Handle standard /api/query response format
                response = result.get("response", {})
                
                # Extract answer
                answer = response.get("answer", "No answer provided")
                f.write(f"### Answer\n\n{answer}\n\n")
                
                # Extract confidence score
                confidence = response.get("confidence_score")
                if confidence is not None:
                    f.write(f"**Confidence Score**: {confidence*100:.1f}%\n\n")
                
                # Extract sources
                sources = response.get("sources", [])
                if sources:
                    f.write(f"### Sources ({len(sources)})\n\n")
                    for j, source in enumerate(sources, 1):
                        title = source.get("title", "Untitled")
                        url = source.get("url", "")
                        snippet = source.get("snippet", "")
                        confidence = source.get("confidence", None)
                        
                        f.write(f"**Source {j}**: {title}\n")
                        if url:
                            f.write(f"- URL: {url}\n")
                        if confidence is not None:
                            f.write(f"- Confidence: {confidence*100:.1f}%\n")
                        if snippet:
                            f.write(f"- Snippet: {snippet[:200]}...\n" if len(snippet) > 200 else f"- Snippet: {snippet}\n")
                        f.write("\n")
            
            # Add separator between questions
            f.write("\n---\n\n")
    
    print(f"Summaries extracted to: {output_file}")
    
    # Also create a JSON file with just the summaries and sources
    json_output_file = extracts_dir / f"summaries_{timestamp}.json"
    
    extracted_data = []
    for i, result in enumerate(results, 1):
        question = result["question"]
        
        if "error" in result:
            extracted_data.append({
                "question_number": i,
                "question": question,
                "error": result["error"]
            })
            continue
        
        # Initialize variables
        answer = ""
        confidence = None
        sources = []
        
        # Check for direct API response format
        if "result" in result.get("response", {}):
            # Handle /api/query/direct response format
            response_data = result["response"]["result"]
            
            # Find the first need with a summarized response
            for need_key, need_data in response_data.items():
                if "summarized_response" in need_data:
                    summarized = need_data["summarized_response"]
                    answer = summarized.get("summary", "")
                    sources = summarized.get("sources", [])
                    confidence = summarized.get("confidence_score")
                    break
        else:
            # Handle standard /api/query response format
            response = result.get("response", {})
            answer = response.get("answer", "")
            confidence = response.get("confidence_score")
            sources = response.get("sources", [])
        
        extracted_data.append({
            "question_number": i,
            "question": question,
            "answer": answer,
            "confidence_score": confidence,
            "sources": sources
        })
    
    with open(json_output_file, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
    
    print(f"JSON summaries extracted to: {json_output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract summaries and sources from manual testing results")
    parser.add_argument("--file", help="Path to specific results file to process")
    args = parser.parse_args()
    
    extract_summaries_and_sources(args.file)

