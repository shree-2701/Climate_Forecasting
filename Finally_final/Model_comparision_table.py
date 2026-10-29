results = pd.DataFrame({
    "Model": ["RF", "XGB", "LGBM", "CAT", "GB", "Stacked"],
    "RMSE_Rain": rain_rmse_list,
    "MAE_Rain": rain_mae_list,
    "R2_Rain": rain_r2_list,
    "RMSE_Temp": temp_rmse_list,
    "MAE_Temp": temp_mae_list,
    "R2_Temp": temp_r2_list
})

results.to_csv("model_comparison_table.csv", index=False)
print(results)