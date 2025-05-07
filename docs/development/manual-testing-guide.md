# Manual Testing Guide

This document outlines the process for conducting manual testing of the GastroAssist AI system, including test preparation, execution, and analysis.

## Overview

Manual testing allows us to evaluate the system's performance on real-world gastroenterology queries. It helps us assess:

1. **Answer Quality**: Accuracy, completeness, and clinical relevance
2. **Source Quality**: Credibility and relevance of cited sources
3. **Response Time**: System performance under various query complexities
4. **Error Handling**: System behavior with edge cases and unusual queries

## Test Setup

### Prerequisites

- Backend server running locally or in a test environment
- Python 3.11+ installed with required dependencies
- Access to the `manual_testing` directory

### Directory Structure

```
gastroassist/
├── manual_testing/
│   ├── questions_*.txt     # Question files
│   └── results/            # Test results (auto-generated)
│       ├── results_*.json  # Raw test results
│       └── report_*.txt    # Test summary reports
└── scripts/
    ├── run_manual_tests.py       # Script to run tests
    └── generate_test_report.py   # Script to generate reports
```

## Creating Test Questions

1. Create a text file in the `manual_testing` directory with a name following the pattern `questions_*.txt` (e.g., `questions_clinical.txt`, `questions_treatments.txt`)

2. Add one question per line. For example:
   ```
   What is the most likely cause of chronic epigastric pain that improves with meals?
   How does Helicobacter pylori contribute to peptic ulcer disease?
   What are the red flag symptoms in a patient with dyspepsia that warrant urgent endoscopy?
   ```

3. Organize questions by category or complexity to facilitate analysis.

## Running Tests

1. Ensure the backend server is running:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Run the manual tests script:
   ```bash
   python scripts/run_manual_tests.py
   ```

3. The script will:
   - Find all question files in the `manual_testing` directory
   - Send each question to the backend API
   - Save results in the `manual_testing/results` directory
   - Display progress in the console

## Generating Reports

1. After running tests, generate a summary report:
   ```bash
   python scripts/generate_test_report.py
   ```

2. The report includes:
   - Overall success rate
   - Average confidence scores
   - Average answer length
   - Average number of sources
   - Details for each question

## Analyzing Results

### Quantitative Analysis

Review the generated reports to assess:

1. **Success Rate**: Percentage of questions answered without errors
2. **Confidence Scores**: Average confidence reported by the system
3. **Source Count**: Average number of sources cited per answer
4. **Response Time**: Time taken to generate answers

### Qualitative Analysis

For a deeper evaluation, manually review the raw JSON results:

1. **Answer Accuracy**: Verify factual correctness against trusted medical resources
2. **Clinical Relevance**: Assess if answers address the clinical aspects of the question
3. **Source Quality**: Check if cited sources are reputable medical publications
4. **Completeness**: Determine if all aspects of the question are addressed

## Continuous Improvement

Use test results to guide system improvements:

1. **Knowledge Gaps**: Identify topics where answers lack depth or accuracy
2. **Source Enhancement**: Add high-quality sources for frequently queried topics
3. **Query Understanding**: Improve interpretation of complex clinical questions
4. **Response Format**: Refine answer structure for better clinical utility

## Example Test Categories

Consider organizing test questions into these categories:

1. **Diagnostic Questions**: Symptoms, differential diagnoses, diagnostic criteria
2. **Treatment Questions**: Medication options, surgical approaches, treatment guidelines
3. **Pathophysiology Questions**: Disease mechanisms, progression, complications
4. **Epidemiology Questions**: Prevalence, risk factors, population statistics
5. **Procedural Questions**: Endoscopic techniques, preparation, complications
6. **Edge Cases**: Rare conditions, complex comorbidities, unusual presentations

## Best Practices

1. **Regular Testing**: Run manual tests after significant system updates
2. **Diverse Questions**: Include various question types, complexities, and topics
3. **Expert Review**: Have gastroenterology experts review answer quality periodically
4. **Version Control**: Track changes in system performance across versions
5. **Feedback Loop**: Incorporate findings into development priorities

## Troubleshooting

If you encounter issues during testing:

1. **API Connection Errors**: Verify the backend server is running and accessible
2. **Timeout Errors**: Check if complex questions exceed processing time limits
3. **Empty Responses**: Ensure the knowledge base contains relevant information
4. **Format Issues**: Validate that question files use the correct format (one question per line)

For persistent issues, check the application logs or contact the development team.