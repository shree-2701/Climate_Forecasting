# Project Deliverables

- All code is modular and ready to run in VS Code on Windows.
- Place your data (CSV/NetCDF) in the data/ folder.
- Run main.py to execute the full pipeline: preprocessing, feature engineering, model training (Random Forest, boosting, stacking), seasonal bias correction, evaluation, and visualization.
- Results (trained models, evaluation tables, and plots) are saved in models/, evaluation/, and visualization/ folders.
- See README.md for usage instructions.

## Key Outputs
- Trained models: models/
- Forecast results: evaluation/
- Evaluation tables: evaluation/
- Plots: visualization/

## Notes
- All steps are reproducible and academic-style.
- Code is commented for clarity.
- No deep learning is used; Random Forest is always included.
- Results show improvement: Random Forest → Stacked Ensemble → Bias-Corrected Forecast.
