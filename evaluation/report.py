"""
evaluation/report.py
Generate summary reports for model performance metrics.
"""
import os
from datetime import datetime

def format_metrics_table(eval_results):
    """Format evaluation results as a readable table"""
    report = []
    report.append("\n" + "="*90)
    report.append("MODEL PERFORMANCE METRICS SUMMARY")
    report.append("="*90)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    for var in ['temperature', 'precipitation']:
        if var not in eval_results:
            continue
        
        report.append(f"\n{'─'*90}")
        report.append(f"Variable: {var.upper()}")
        report.append(f"{'─'*90}")
        
        individual_models = eval_results[var].get('individual_models', {})
        
        # Header row
        report.append(f"{'Model':<15} {'R² Score':<15} {'RMSE':<15} {'MAE':<15}")
        report.append(f"{'-'*15} {'-'*15} {'-'*15} {'-'*15}")
        
        # Data rows
        for model_name in individual_models:
            metrics = individual_models[model_name]
            r2 = metrics.get('R2', 0)
            rmse = metrics.get('RMSE', 0)
            mae = metrics.get('MAE', 0)
            
            # Use [*] instead of ★ for better compatibility
            marker = "[*]" if model_name == "STACKED" else "   "
            report.append(f"{marker} {model_name:<12} {r2:>14.6f} {rmse:>14.6f} {mae:>14.6f}")
        
        # Summary statistics
        report.append("")
        r2_scores = [individual_models[m].get('R2', 0) for m in individual_models]
        rmse_values = [individual_models[m].get('RMSE', 0) for m in individual_models]
        mae_values = [individual_models[m].get('MAE', 0) for m in individual_models]
        
        report.append(f"Best R² Score: {max(r2_scores):.6f}")
        report.append(f"Lowest RMSE:   {min(rmse_values):.6f}")
        report.append(f"Lowest MAE:    {min(mae_values):.6f}")
        
        # Stacked model performance
        if "STACKED" in individual_models:
            stacked = individual_models["STACKED"]
            report.append(f"\nStacked Model Performance:")
            report.append(f"  R² Score: {stacked.get('R2', 0):.6f}")
            report.append(f"  RMSE:     {stacked.get('RMSE', 0):.6f}")
            report.append(f"  MAE:      {stacked.get('MAE', 0):.6f}")
    
    report.append("\n" + "="*90)
    report.append("Legend:")
    report.append("  [*] = Stacked Ensemble Model")
    report.append("  R² Score: Coefficient of determination (closer to 1.0 is better)")
    report.append("  RMSE: Root Mean Squared Error (lower is better)")
    report.append("  MAE: Mean Absolute Error (lower is better)")
    report.append("="*90 + "\n")
    
    return "\n".join(report)

def save_report(eval_results, output_file="model_performance_report.txt"):
    """Save report to file"""
    report_text = format_metrics_table(eval_results)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    return report_text

def print_report(eval_results):
    """Print report to console"""
    report_text = format_metrics_table(eval_results)
    # Use errors='replace' to handle encoding issues
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    print(report_text, file=sys.stdout)