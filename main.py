"""
Main pipeline for climate forecasting: data loading, preprocessing, feature engineering, modeling, evaluation, visualization.
"""

import os
from preprocessing import preprocess
from features import run as create_features
from models import train_models, stack_models
from evaluation import evaluate
from evaluation.bias_correction import run as bias_correction_run
from evaluation import report
from visualization import plot_results

def main():
    # 1. Data Preprocessing
    print("Step 1: Preprocessing data...")
    data = preprocess.run()

    # 2. Feature Engineering
    print("Step 2: Engineering features...")
    features, targets, full_df = create_features(data)

    # 3. Modeling
    print("Step 3: Training models...")
    rf_models, _ = train_models(features, targets)
    stacked_models = stack_models(rf_models, (features, targets))

    # 4. Evaluation
    print("Step 4: Evaluating models...")
    eval_results, eval_df = evaluate.run(stacked_models, features, targets, full_df)

    # Log numeric outputs
    log_path = os.path.join(os.getcwd(), "numeric_output.log")
    with open(log_path, "w") as log_file:
        log_file.write("Evaluation Results:\n")
        for var in eval_results:
            log_file.write(f"{var} Overall Metrics: {eval_results[var]['overall']}\n")
            log_file.write(f"{var} Season-wise Metrics: {eval_results[var]['season_wise']}\n")

    # 5. Bias Correction
    print("Step 5: Applying bias correction...")
    corrected_results = bias_correction_run(eval_results, full_df, targets)

    # Log bias-corrected outputs
    with open(log_path, "a") as log_file:
        log_file.write("\nBias-Corrected Results:\n")
        for var in ['temperature', 'precipitation']:
            if f"{var}_corrected" in corrected_results.columns:
                log_file.write(f"{var} Bias-Corrected Values: {corrected_results[f'{var}_corrected'].values}\n")

    # 6. Generate Performance Report
    print("\nStep 6: Generating performance report...")
    report_text = report.save_report(eval_results, "model_performance_report.txt")
    report.print_report(eval_results)

    # 7. Visualization - Merge corrected results with full_df for complete data
    print("\nStep 7: Creating visualizations...")
    # Ensure we have all necessary columns in one dataframe
    viz_df = full_df.copy()
    # Add predictions from eval_df
    for col in eval_df.columns:
        if col not in viz_df.columns:
            viz_df[col] = eval_df[col]
    # Add corrected values
    for col in corrected_results.columns:
        if col.endswith('_corrected'):
            viz_df[col] = corrected_results[col]
    
    # Use last 20 days only for clear visualization
    viz_data = viz_df.iloc[-20:]
    plot_results.run(eval_results, viz_data, full_df, targets)
    
    print("\n✓ Pipeline completed successfully!")
    print(f"  - Performance report saved to: model_performance_report.txt")
    print(f"  - Visualizations saved to: visualization/")

if __name__ == "__main__":
    main()
