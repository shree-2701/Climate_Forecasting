"""
visualization/plot_results.py
Visualization for climate forecasting results.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

def plot_actual_vs_pred(df, var, out_dir):
    plt.figure(figsize=(16, 6))
    
    # Plot lines with distinct colors and thicker lines for visibility
    plt.plot(df['date'], df[var], label='Actual', color='#2E86AB', linewidth=2.5, marker='o', markersize=5, linestyle='-', alpha=0.9)
    
    # Add predictions if available
    if f'{var}_pred' in df.columns:
        plt.plot(df['date'], df[f'{var}_pred'], label='Predicted (Stacked)', color='#A23B72', linewidth=2.5, marker='s', markersize=4, linestyle='--', alpha=0.85)
    
    # Add bias corrected if available
    if f'{var}_corrected' in df.columns:
        plt.plot(df['date'], df[f'{var}_corrected'], label='Bias Corrected', color='#F18F01', linewidth=2.5, marker='^', markersize=4, linestyle='-.', alpha=0.85)
    
    plt.title(f'Actual vs Predicted vs Bias-Corrected: {var.capitalize()}', fontsize=14, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel(f'{var.capitalize()} Value', fontsize=12)
    plt.legend(loc='best', fontsize=11, framealpha=0.95)
    plt.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'{var}_actual_vs_pred.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_waveform_individual_models(df, var, out_dir):
    """Plot waveforms for each individual model"""
    models_to_plot = ['rf', 'xgb', 'lgb', 'cat', 'lstm']
    fig, axes = plt.subplots(len(models_to_plot), 1, figsize=(16, 12))
    
    if len(models_to_plot) == 1:
        axes = [axes]
    
    for idx, model_name in enumerate(models_to_plot):
        pred_col = f'{var}_{model_name}_pred'
        if pred_col not in df.columns:
            continue
        
        ax = axes[idx]
        valid_mask = ~df[pred_col].isna()
        x_data = df.loc[valid_mask, 'date']
        
        ax.plot(x_data, df.loc[valid_mask, var], label='Actual', color='#2E86AB', linewidth=2.5, marker='o', markersize=4, alpha=0.9)
        ax.plot(x_data, df.loc[valid_mask, pred_col], label=f'{model_name.upper()} Predicted', color='#A23B72', linewidth=2.5, marker='s', markersize=3, alpha=0.85, linestyle='--')
        
        ax.set_title(f'{model_name.upper()} Model Waveform: {var.capitalize()}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Date', fontsize=10)
        ax.set_ylabel(f'{var.capitalize()} Value', fontsize=10)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
        ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'{var}_waveform_individual_models.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_all_models_overlay(df, var, out_dir):
    """Plot all models' predictions overlaid on actual values"""
    plt.figure(figsize=(16, 7))
    
    models_to_plot = ['rf', 'xgb', 'lgb', 'cat', 'lstm']
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#06A77D', '#D62828']
    linestyles = ['-', '--', '-.', ':', '-']
    
    # Plot actual
    plt.plot(df['date'], df[var], label='Actual', color='black', linewidth=3, marker='o', markersize=6, zorder=10, alpha=0.9)
    
    # Plot each model
    for idx, model_name in enumerate(models_to_plot):
        pred_col = f'{var}_{model_name}_pred'
        if pred_col not in df.columns:
            continue
        
        valid_mask = ~df[pred_col].isna()
        x_data = df.loc[valid_mask, 'date']
        
        plt.plot(x_data, df.loc[valid_mask, pred_col], label=f'{model_name.upper()}', 
                color=colors[idx], linewidth=2, marker='s', markersize=3, 
                linestyle=linestyles[idx], alpha=0.7)
    
    # Plot stacked
    plt.plot(df['date'], df[f'{var}_pred'], label='STACKED (Ensemble)', 
            color='#FF6B6B', linewidth=2.5, marker='^', markersize=4, linestyle='-', alpha=0.8, zorder=5)
    
    plt.title(f'All Models Waveform Comparison: {var.capitalize()}', fontsize=14, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel(f'{var.capitalize()} Value', fontsize=12)
    plt.legend(loc='best', fontsize=11, framealpha=0.95, ncol=2)
    plt.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'{var}_waveform_all_models_overlay.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_confusion_matrix_discretized(df, var, out_dir):
    """Plot confusion matrices for each model using discretized predictions"""
    models_to_plot = ['rf', 'xgb', 'lgb', 'cat', 'lstm']
    
    # Discretize actual and predicted values into bins
    n_bins = 5
    actual_binned = pd.cut(df[var], bins=n_bins, labels=False)
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    
    plot_idx = 0
    for model_name in models_to_plot:
        pred_col = f'{var}_{model_name}_pred'
        if pred_col not in df.columns:
            continue
        
        valid_mask = ~df[pred_col].isna()
        pred_binned = pd.cut(df.loc[valid_mask, pred_col], bins=n_bins, labels=False)
        actual_binned_valid = actual_binned[valid_mask]
        
        cm = confusion_matrix(actual_binned_valid, pred_binned, labels=[0, 1, 2, 3, 4])
        
        ax = axes[plot_idx]
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax, cbar=True, annot_kws={'size': 10})
        ax.set_title(f'{model_name.upper()} Confusion Matrix\n({var.capitalize()})', fontsize=11, fontweight='bold')
        ax.set_xlabel('Predicted Bin', fontsize=10)
        ax.set_ylabel('Actual Bin', fontsize=10)
        plot_idx += 1
    
    # Plot stacked model
    stacked_pred = df[f'{var}_pred']
    stacked_binned = pd.cut(stacked_pred, bins=n_bins, labels=False)
    cm_stacked = confusion_matrix(actual_binned, stacked_binned, labels=[0, 1, 2, 3, 4])
    
    ax = axes[plot_idx]
    sns.heatmap(cm_stacked, annot=True, fmt='d', cmap='RdYlGn', ax=ax, cbar=True, annot_kws={'size': 10})
    ax.set_title(f'STACKED Confusion Matrix\n({var.capitalize()})', fontsize=11, fontweight='bold')
    ax.set_xlabel('Predicted Bin', fontsize=10)
    ax.set_ylabel('Actual Bin', fontsize=10)
    
    # Hide unused subplots
    for idx in range(plot_idx + 1, len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'{var}_confusion_matrices_discretized.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_model_accuracy_comparison(eval_results, var, out_dir):
    """Plot accuracy metrics comparison across all models"""
    if var not in eval_results:
        return
    
    individual_models = eval_results[var].get('individual_models', {})
    if not individual_models:
        return
    
    models = list(individual_models.keys())
    r2_scores = [individual_models[m].get('R2', 0) for m in models]
    rmse_values = [individual_models[m].get('RMSE', 0) for m in models]
    mae_values = [individual_models[m].get('MAE', 0) for m in models]
    
    # Create subplots
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # R² Score comparison
    colors_r2 = ['#FF6B6B' if m == 'STACKED' else '#4ECDC4' for m in models]
    axes[0].bar(models, r2_scores, color=colors_r2, alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0].set_title(f'R² Score Comparison\n({var.capitalize()})', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('R² Score', fontsize=11)
    axes[0].set_ylim([min(r2_scores) - 0.1, 1.05])
    axes[0].grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(r2_scores):
        axes[0].text(i, v + 0.02, f'{v:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    axes[0].tick_params(axis='x', rotation=45)
    
    # RMSE comparison
    colors_rmse = ['#FF6B6B' if m == 'STACKED' else '#95E1D3' for m in models]
    axes[1].bar(models, rmse_values, color=colors_rmse, alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1].set_title(f'RMSE Comparison (Lower is Better)\n({var.capitalize()})', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('RMSE', fontsize=11)
    axes[1].grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(rmse_values):
        axes[1].text(i, v + max(rmse_values)*0.02, f'{v:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    axes[1].tick_params(axis='x', rotation=45)
    
    # MAE comparison
    colors_mae = ['#FF6B6B' if m == 'STACKED' else '#F38181' for m in models]
    axes[2].bar(models, mae_values, color=colors_mae, alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[2].set_title(f'MAE Comparison (Lower is Better)\n({var.capitalize()})', fontsize=12, fontweight='bold')
    axes[2].set_ylabel('MAE', fontsize=11)
    axes[2].grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(mae_values):
        axes[2].text(i, v + max(mae_values)*0.02, f'{v:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    axes[2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'{var}_model_accuracy_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_model_metrics_table(eval_results, out_dir):
    """Create a summary table of all model metrics"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    
    for var_idx, var in enumerate(['temperature', 'precipitation']):
        if var not in eval_results:
            continue
        
        individual_models = eval_results[var].get('individual_models', {})
        if not individual_models:
            continue
        
        models = list(individual_models.keys())
        r2_scores = [individual_models[m].get('R2', 0) for m in models]
        rmse_values = [individual_models[m].get('RMSE', 0) for m in models]
        mae_values = [individual_models[m].get('MAE', 0) for m in models]
        
        # Create table data
        table_data = []
        for i, model in enumerate(models):
            table_data.append([
                model,
                f'{r2_scores[i]:.4f}',
                f'{rmse_values[i]:.4f}',
                f'{mae_values[i]:.4f}'
            ])
        
        ax = axes[var_idx]
        ax.axis('off')
        
        table = ax.table(
            cellText=table_data,
            colLabels=['Model', 'R² Score', 'RMSE', 'MAE'],
            cellLoc='center',
            loc='center',
            bbox=[0, 0, 1, 1]
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Color header
        for i in range(4):
            table[(0, i)].set_facecolor('#FF6B6B')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Color stacked row
        for i, model in enumerate(models):
            if model == 'STACKED':
                for j in range(4):
                    table[(i+1, j)].set_facecolor('#FFE5E5')
                    table[(i+1, j)].set_text_props(weight='bold')
        
        ax.set_title(f'{var.capitalize()} Model Metrics Summary', fontsize=13, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'model_metrics_summary_table.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_season_error_comparison(df, var, out_dir):
    if 'season' not in df.columns or f'{var}_pred' not in df.columns:
        return
    
    df = df.copy()  # Create a copy to avoid SettingWithCopyWarning
    df['error'] = df[var] - df[f'{var}_pred']
    
    plt.figure(figsize=(12, 6))
    plot_data_before = df[['season', 'error']].dropna()
    
    sns.boxplot(x='season', y='error', data=plot_data_before, color='#E63946', width=0.6, fliersize=5, boxprops=dict(alpha=0.7, linewidth=1.5), whiskerprops=dict(linewidth=1.3), medianprops=dict(color='darkred', linewidth=2))
    
    # Add error_corrected if available
    if f'{var}_corrected' in df.columns:
        df['error_corrected'] = df[var] - df[f'{var}_corrected']
        plot_data_after = df[['season', 'error_corrected']].dropna()
        sns.boxplot(x='season', y='error_corrected', data=plot_data_after, color='#06A77D', width=0.6, fliersize=5, boxprops=dict(alpha=0.7, linewidth=1.5), whiskerprops=dict(linewidth=1.3), medianprops=dict(color='darkgreen', linewidth=2))
        
        # Add legend for the two box colors manually
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor='#E63946', alpha=0.7, label='Error (Before Correction)'),
                           Patch(facecolor='#06A77D', alpha=0.7, label='Error (After Correction)')]
    else:
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor='#E63946', alpha=0.7, label='Error')]
    
    plt.legend(handles=legend_elements, loc='best', fontsize=11)
    
    plt.title(f'Season-wise Error Comparison: {var.capitalize()}', fontsize=14, fontweight='bold')
    plt.xlabel('Season', fontsize=12)
    plt.ylabel('Error Value', fontsize=12)
    plt.grid(True, alpha=0.2, axis='y', linestyle=':')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'{var}_season_error_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_before_after_bias(df, var, out_dir):
    if f'{var}_pred' not in df.columns:
        return
    
    plt.figure(figsize=(14, 6))
    
    # Calculate errors
    error_before = df[var] - df[f'{var}_pred']
    
    plots_to_show = 1
    if f'{var}_corrected' in df.columns:
        error_after = df[var] - df[f'{var}_corrected']
        plots_to_show = 2
    
    # Plot histograms with KDE
    sns.histplot(error_before, color='#D62828', label='Error (Before Correction)', kde=True, stat='density', alpha=0.6, bins=20, linewidth=1.5)
    if plots_to_show == 2:
        sns.histplot(error_after, color='#1D3557', label='Error (After Correction)', kde=True, stat='density', alpha=0.6, bins=20, linewidth=1.5)
    
    plt.title(f'Error Distribution: Before vs After Bias Correction ({var.capitalize()})', fontsize=14, fontweight='bold')
    plt.xlabel('Error Value', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.legend(loc='best', fontsize=11, framealpha=0.95)
    plt.grid(True, alpha=0.3, axis='y', linestyle=':')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'{var}_before_after_bias.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_deviation_lines(df, var, out_dir):
    """Plot deviations/errors as separate lines for clear visualization"""
    if f'{var}_pred' not in df.columns:
        return
    
    plt.figure(figsize=(16, 6))
    
    # Calculate deviations
    deviation_pred = df[var] - df[f'{var}_pred']
    
    # Plot deviation lines
    plt.plot(df['date'], deviation_pred, label='Deviation (Actual - Predicted)', color='#D62828', linewidth=2.5, marker='o', markersize=4, alpha=0.85)
    
    if f'{var}_corrected' in df.columns:
        deviation_corrected = df[var] - df[f'{var}_corrected']
        plt.plot(df['date'], deviation_corrected, label='Deviation (Actual - Bias Corrected)', color='#06A77D', linewidth=2.5, marker='s', markersize=4, alpha=0.85)
    
    plt.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    
    plt.title(f'Model Deviations from Actual Values: {var.capitalize()}', fontsize=14, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Deviation (Actual - Predicted)', fontsize=12)
    plt.legend(loc='best', fontsize=11, framealpha=0.95)
    plt.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'{var}_deviation_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_scatter_with_lines(df, var, out_dir):
    """Scatter plot with connecting lines for detailed deviation visualization"""
    if f'{var}_pred' not in df.columns:
        return
    
    plt.figure(figsize=(16, 6))
    
    # Scatter plots for better visibility
    plt.scatter(df['date'], df[var], label='Actual', color='#2E86AB', s=80, alpha=0.8, edgecolors='navy', linewidth=1.5, zorder=3)
    plt.scatter(df['date'], df[f'{var}_pred'], label='Predicted (Stacked)', color='#A23B72', s=60, alpha=0.75, edgecolors='purple', linewidth=1, marker='s', zorder=2)
    
    # Add connecting lines
    plt.plot(df['date'], df[var], color='#2E86AB', linewidth=1.5, alpha=0.4, zorder=1)
    plt.plot(df['date'], df[f'{var}_pred'], color='#A23B72', linewidth=1.5, alpha=0.3, linestyle='--', zorder=1)
    
    # Add corrected if available
    if f'{var}_corrected' in df.columns:
        plt.scatter(df['date'], df[f'{var}_corrected'], label='Bias Corrected', color='#F18F01', s=60, alpha=0.75, edgecolors='darkorange', linewidth=1, marker='^', zorder=2)
        plt.plot(df['date'], df[f'{var}_corrected'], color='#F18F01', linewidth=1.5, alpha=0.3, linestyle='-.', zorder=1)
    
    plt.title(f'Detailed Comparison with Scatter Points: {var.capitalize()}', fontsize=14, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel(f'{var.capitalize()} Value', fontsize=12)
    plt.legend(loc='best', fontsize=11, framealpha=0.95, scatterpoints=1)
    plt.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'{var}_scatter_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()

def run(eval_results, corrected_df, features, targets, out_dir='visualization'):
    os.makedirs(out_dir, exist_ok=True)
    
    print("Generating visualizations...")
    
    # Generate metrics summary table
    print("  - Creating model metrics summary table...")
    plot_model_metrics_table(eval_results, out_dir)
    
    for var in ['temperature', 'precipitation']:
        print(f"  - Processing {var}...")
        print(f"    - Actual vs Predicted plot...")
        plot_actual_vs_pred(corrected_df, var, out_dir)
        
        print(f"    - Individual model waveforms...")
        plot_waveform_individual_models(corrected_df, var, out_dir)
        
        print(f"    - All models overlay waveform...")
        plot_all_models_overlay(corrected_df, var, out_dir)
        
        print(f"    - Confusion matrices (discretized)...")
        plot_confusion_matrix_discretized(corrected_df, var, out_dir)
        
        print(f"    - Model accuracy comparison...")
        plot_model_accuracy_comparison(eval_results, var, out_dir)
        
        print(f"    - Season-wise error comparison...")
        plot_season_error_comparison(corrected_df, var, out_dir)
        
        print(f"    - Before/after bias correction...")
        plot_before_after_bias(corrected_df, var, out_dir)
        
        print(f"    - Deviation comparison...")
        plot_deviation_lines(corrected_df, var, out_dir)
        
        print(f"    - Scatter plot with lines...")
        plot_scatter_with_lines(corrected_df, var, out_dir)
    
    print(f"✓ All visualizations saved to {out_dir}/")

