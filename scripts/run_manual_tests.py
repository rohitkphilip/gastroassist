import os
import json
import requests
import time
from datetime import datetime
from pathlib import Path

def run_manual_tests():
    """
    Reads test questions from manual_testing directory,
    calls the backend service, and saves the responses
    """
    # Define paths
    manual_testing_dir = Path("manual_testing")
    results_dir = manual_testing_dir / "results"
    
    # Create results directory if it doesn't exist
    results_dir.mkdir(exist_ok=True)
    
    # Find all question files
    question_files = list(manual_testing_dir.glob("questions*.txt"))
    
    if not question_files:
        print("No question files found in manual_testing directory.")
        return
    
    # Backend API endpoint
    api_url = "http://localhost:8000/api/query/direct"
    
    # Process each question file
    for question_file in question_files:
        print(f"Processing file: {question_file}")
        
        # Create a timestamp for the results file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"results_{question_file.stem}_{timestamp}.json"
        
        # Read questions from file
        with open(question_file, "r", encoding="utf-8") as f:
            questions = [line.strip() for line in f if line.strip()]
        
        # Process each question
        results = []
        for i, question in enumerate(questions, 1):
            print(f"Processing question {i}/{len(questions)}: {question[:50]}...")
            
            # Prepare request payload
            payload = {
                "text": question,
                "user_id": "test-user",
                "context": {}  # Add empty context object
            }
            
            try:
                # Call backend API
                response = requests.post(api_url, json=payload)
                response.raise_for_status()
                
                # Get response data
                response_data = response.json()
                
                # Add to results
                results.append({
                    "question": question,
                    "response": response_data,
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                })
                
                print(f"  ✓ Success (status: {response.status_code})")
                
                # Add a small delay to avoid overwhelming the server
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                error_message = str(e)
                try:
                    error_detail = response.json() if 'response' in locals() else None
                except:
                    error_detail = None
                
                results.append({
                    "question": question,
                    "error": error_message,
                    "error_detail": error_detail,
                    "status_code": response.status_code if 'response' in locals() else None,
                    "timestamp": datetime.now().isoformat()
                })
                
                print(f"  ✗ Error: {error_message}")
                
                # Add a small delay before the next request
                time.sleep(2)
        
        # Save results to file
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to: {results_file}")

if __name__ == "__main__":
    run_manual_tests()
