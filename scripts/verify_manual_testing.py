import os
import sys
import requests
from pathlib import Path

def verify_manual_testing_setup():
    """
    Verifies that the manual testing environment is properly set up
    """
    print("Verifying manual testing setup...")
    
    # Check if manual_testing directory exists
    manual_testing_dir = Path("manual_testing")
    if not manual_testing_dir.exists():
        print("❌ manual_testing directory not found. Creating it now...")
        manual_testing_dir.mkdir(exist_ok=True)
        print("✅ manual_testing directory created.")
    else:
        print("✅ manual_testing directory exists.")
    
    # Check if results directory exists
    results_dir = manual_testing_dir / "results"
    if not results_dir.exists():
        print("❌ results directory not found. Creating it now...")
        results_dir.mkdir(exist_ok=True)
        print("✅ results directory created.")
    else:
        print("✅ results directory exists.")
    
    # Check if question files exist
    question_files = list(manual_testing_dir.glob("questions*.txt"))
    if not question_files:
        print("❌ No question files found. Creating a sample file...")
        sample_file = manual_testing_dir / "questions_sample.txt"
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write("What are the common symptoms of GERD?\n")
            f.write("What is the difference between Crohn's disease and ulcerative colitis?\n")
            f.write("How is celiac disease diagnosed?\n")
            f.write("What are the latest treatments for irritable bowel syndrome?\n")
            f.write("What dietary changes are recommended for patients with diverticulitis?\n")
        print(f"✅ Sample question file created: {sample_file}")
    else:
        print(f"✅ Found {len(question_files)} question file(s):")
        for file in question_files:
            print(f"  - {file.name}")
    
    # Check if backend server is running
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running.")
        else:
            print(f"❌ Backend server returned status code {response.status_code}.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend server is not accessible: {e}")
        print("   Make sure to start the server with: uvicorn app.main:app --reload")
    
    # Check for required Python packages
    try:
        import pandas
        print("✅ pandas package is installed.")
    except ImportError:
        print("❌ pandas package is not installed. Install it with: pip install pandas")
    
    print("\nVerification complete.")
    print("To run manual tests:")
    print("1. Start the backend server (if not running): uvicorn app.main:app --reload")
    print("2. Run the tests: python scripts/run_manual_tests.py")
    print("3. Generate a report: python scripts/generate_test_report.py")

if __name__ == "__main__":
    verify_manual_testing_setup()
