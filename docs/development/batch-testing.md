# Batch Testing with LLM Evaluation

This document describes how to use the batch testing script to automatically evaluate GastroAssist's outputs against expected answers using an LLM as a judge.

## Overview

The `batch_test_gastroassist.py` script processes a CSV file containing test cases with both questions and expected answers. It runs each question through the GastroAssist pipeline and then uses an LLM (either Groq LLaMA or OpenAI GPT) to evaluate the generated answers against the expected answers. The evaluation provides detailed metrics on medical accuracy, relevance, conciseness, source usage, and completeness.

## Prerequisites

1. **Install required packages**:
   ```bash
   pip install pandas openpyxl tqdm matplotlib seaborn groq
   # or if using OpenAI instead
   pip install pandas openpyxl tqdm matplotlib seaborn openai
   ```

2. **Set up API key**:
   Add your API key to your `.env` file depending on which LLM service you're using:
   ```
   # Choose one:
   GROQ_API_KEY=your_groq_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Set which service to use
   LLM_SERVICE=groq  # or openai
   ```

3. **Prepare input CSV file**:
   Ensure you have a CSV file with at least the following columns:
   - `Question`: The gastroenterology query
   - `Expected_Answer`: The reference/gold standard answer

## Usage

### Basic Usage

```bash
python scripts/batch_test_gastroassist.py \
  --input-file manual_testing/Question_Answers_GastroAssist.csv \
  --output-dir manual_testing/results \
  --run-gastroassist
```

### Options

- `--input-file`: Path to the CSV file containing test cases (required)
- `--output-dir`: Directory where results will be saved (default: manual_testing/results)
- `--model`: LLM model to use for evaluation (default depends on LLM_SERVICE)
- `--max-tests`: Maximum number of tests to run, useful for debugging
- `--run-gastroassist`: Add this flag to process queries through GastroAssist; omit to skip processing and use pre-existing answers

### Output Files

The script generates several output files with a timestamp:

1. **Excel Report** (`*_evaluation_*.xlsx`):
   - Summary sheet with overall metrics
   - Detailed results sheet with all test cases
   - Individual sheets for each test case with complete evaluation details

2. **JSON Report** (`*_evaluation_*.json`):
   - Complete raw data with all evaluation details
   - Useful for further processing or analysis

3. **Visualization** (`*_evaluation_*.png`):
   - Bar chart of average scores by criterion
   - Histogram of weighted scores
   - Heatmap showing scores across all test cases and criteria

## Test Case Format

The input CSV file should have the following format:

```csv
ID,Question,Expected_Answer
test_1,"What are the clinical features of GERD?","Gastroesophageal reflux disease (GERD) typically presents with heartburn, regurgitation, and chest pain. Other symptoms may include dysphagia, odynophagia, chronic cough, laryngitis, and dental erosions. Complications can include esophagitis, strictures, Barrett's esophagus, and rarely adenocarcinoma."
test_2,"How is H. pylori diagnosed?","H. pylori infection can be diagnosed using invasive methods requiring endoscopy (rapid urease test, histology, culture) or non-invasive methods (urea breath test, stool antigen test, serology). The urea breath test and stool antigen test are preferred for initial diagnosis and confirmation of eradication due to their high sensitivity and specificity."
```

## Evaluation Criteria

The LLM evaluates each answer on five dimensions:

1. **Medical Accuracy (35% weight)**: Correctness of medical information and absence of factual errors
2. **Relevance (20% weight)**: How well the answer addresses the original query
3. **Conciseness (15% weight)**: Brevity and clarity without unnecessary information
4. **Source Usage (15% weight)**: Appropriate citation and use of source material
5. **Completeness (15% weight)**: Coverage of all important aspects from the reference answer

Each dimension receives a score from 0-10, which is then normalized to 0-1 and weighted to calculate the final score.

## Interpreting Results

### Overall Metrics

The summary sheet in the Excel report provides:
- Average weighted score across all test cases
- Average scores for each evaluation criterion
- Highest and lowest scoring test cases

### Individual Test Case Evaluation

Each test case includes:
- Original query and both expected and actual answers
- Scores and explanations for each criterion
- Overall feedback from the LLM evaluator
- Source information used in the answer

### Visualization Analysis

The visualization helps identify:
- Strengths and weaknesses across different evaluation criteria
- Distribution of overall performance
- Individual test cases that need attention

## Best Practices

1. **Representative Test Set**: Include a diverse range of gastroenterology topics in your test set
2. **Consistent Expected Answers**: Ensure reference answers are consistent in style and comprehensiveness
3. **Iterative Testing**: Run batch tests after significant system changes
4. **Result Analysis**: Focus improvements on criteria with lower average scores
5. **Regular Updates**: Keep expected answers up-to-date with the latest medical guidelines

## Troubleshooting

### API Key Issues

If you encounter authentication errors:
1. Verify your API key is correctly set in your `.env` file
2. Check that the `LLM_SERVICE` environment variable matches your API key
3. Ensure your billing information is up to date

### CSV Parsing Issues

If the script fails to read your CSV file:
1. Check the file encoding (UTF-8 is recommended)
2. Ensure column names match expected values
3. Try simplifying the CSV to just the required columns

### Performance Issues

If processing takes too long:
1. Use the `--max-tests` parameter to limit the number of test cases
2. Consider using pre-computed GastroAssist answers by omitting the `--run-gastroassist` flag
3. Run tests in smaller batches

## Integration with CI/CD

You can integrate the batch testing into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow step
- name: Run Batch Testing
  run: |
    python -m pip install -r requirements.txt
    python scripts/batch_test_gastroassist.py \
      --input-file test_cases/regression_tests.csv \
      --output-dir ./test_results \
      --max-tests 5  # Limit for CI/CD to save time
```

## Example Workflow

A typical workflow using the batch test script:

1. Prepare a set of test cases with questions and expected answers
2. Run GastroAssist on these test cases and evaluate the results
3. Identify areas where GastroAssist performs well or needs improvement
4. Make system improvements based on the evaluation
5. Re-run tests to measure the impact of changes
6. Repeat this cycle as part of your development process
