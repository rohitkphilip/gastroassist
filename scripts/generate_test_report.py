import os
import json
from pathlib import Path
import pandas as pd
from datetime import datetime

def generate_test_report():
    """
    Generates a summary report from the manual test results
    """
    # Define paths
    results_dir = Path("manual_testing/results")
    
    if not results_dir.exists():
        print("Results directory not found.")
        return
    
    # Find all result files
    result_files = list(results_dir.glob("results_*.json"))
    
    if not result_files:
        print("No result files found in results directory.")
        return
    
    # Get the most recent result file
    latest_result_file = max(result_files, key=os.path.getmtime)
    print(f"Generating report for: {latest_result_file}")
    
    # Load results
    with open(latest_result_file, "r", encoding="utf-8") as f:
        results = json.load(f)
    
    # Prepare report data
    report_data = []
    for i, result in enumerate(results, 1):
        question = result["question"]
        
        if "error" in result:
            status = "Error"
            answer = result["error"]
            confidence = None
            sources_count = None
        else:
            status = "Success"
            response = result["response"]
            answer = response.get("answer", "No answer provided")
            confidence = response.get("confidence_score", None)
            sources = response.get("sources", [])
            sources_count = len(sources)
        
        report_data.append({
            "Question #": i,
            "Question": question[:100] + "..." if len(question) > 100 else question,
            "Status": status,
            "Answer Length": len(answer) if isinstance(answer, str) else 0,
            "Confidence": confidence,
            "Sources Count": sources_count
        })
    
    # Create DataFrame
    df = pd.DataFrame(report_data)
    
    # Calculate statistics
    success_rate = (df["Status"] == "Success").mean() * 100
    avg_confidence = df[df["Confidence"].notnull()]["Confidence"].mean() * 100
    avg_answer_length = df["Answer Length"].mean()
    avg_sources = df[df["Sources Count"].notnull()]["Sources Count"].mean()
    
    # Generate report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_file = results_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"GastroAssist Manual Testing Report\n")
        f.write(f"Generated: {timestamp}\n")
        f.write(f"Test File: {latest_result_file.name}\n\n")
        
        f.write(f"Summary Statistics:\n")
        f.write(f"- Total Questions: {len(results)}\n")
        f.write(f"- Success Rate: {success_rate:.1f}%\n")
        f.write(f"- Average Confidence: {avg_confidence:.1f}%\n")
        f.write(f"- Average Answer Length: {avg_answer_length:.1f} characters\n")
        f.write(f"- Average Sources Count: {avg_sources:.1f}\n\n")
        
        f.write("Question Details:\n")
        for i, row in df.iterrows():
            f.write(f"\n{row['Question #']}. {row['Question']}\n")
            f.write(f"   Status: {row['Status']}\n")
            if row['Status'] == 'Success':
                f.write(f"   Confidence: {row['Confidence']*100:.1f}%\n" if pd.notnull(row['Confidence']) else "   Confidence: N/A\n")
                f.write(f"   Sources: {row['Sources Count']}\n" if pd.notnull(row['Sources Count']) else "   Sources: N/A\n")
    
    print(f"Report generated: {report_file}")
    
    # Also save as CSV for further analysis
    csv_file = results_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(csv_file, index=False)
    print(f"CSV report saved: {csv_file}")

if __name__ == "__main__":
    generate_test_report()