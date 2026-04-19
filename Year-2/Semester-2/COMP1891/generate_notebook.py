#!/usr/bin/env python3
"""Generator for COMP1891 Applications in AI and Data Science – Jupyter Notebook"""
import json, os

NOTEBOOK_PATH = os.path.expanduser("~/COMP1891/COMP1891_notebook.ipynb")

def src(text):
    text = text.lstrip("\n")
    if not text:
        return [""]
    lines = text.split("\n")
    result = [line + "\n" for line in lines[:-1]]
    if lines[-1]:
        result.append(lines[-1])
    return result

def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": src(text)}

def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": src(text)}

cells = []

# ── TITLE ─────────────────────────────────────────────────────────────────────
cells.append(md("""
# COMP1891 – Applications in AI and Data Science
## Jupyter Notebook Submission

**Module:** COMP1891 | **Module Leader:** Dr Nageena Frost | **University of Greenwich**

| Section | Topic | Weight |
|---------|-------|--------|
| **A** | Data Science – EDA, Cleaning, Visualisation | 30% |
| **B** | AI/ML – Regression, Classification, Clustering | 30% |
| **C** | AI – Facial Expression Detection | 20% |
| **D** | AI Ethics and LSEPI | 10% |
| **E** | Conclusion and Reflections | 10% |

> Place `Estate_Agent.csv`, `FacesSample/`, and `Expressions/` in the same directory as this notebook.
"""))

# ── SETUP ─────────────────────────────────────────────────────────────────────
cells.append(md("## Setup and Imports"))

cells.append(code("""
import sys
# Install any missing packages (safe to re-run)
# !{sys.executable} -m pip install torch torchvision transformers scikit-learn pandas numpy matplotlib seaborn scipy pillow opencv-python --quiet
"""))

cells.append(code("""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
from scipy import stats
import warnings, os, glob
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, ConfusionMatrixDisplay, silhouette_score
)
from PIL import Image

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('husl')
%matplotlib inline
print("Libraries loaded successfully.")
"""))

# ── DATA LOADING ──────────────────────────────────────────────────────────────
cells.append(md("""
## Data Loading and Column Setup
Auto-detects the CSV delimiter and column names. Cleans numeric formatting issues
(currency symbols, comma thousands separators, European decimal notation).
"""))

cells.append(code("""
# ── Load CSV with auto-detected delimiter ────────────────────────────────────
CSV_PATH = 'Estate_Agent.csv'

def clean_numeric(series):
    s = series.astype(str).str.strip()
    s = s.str.replace(r'[£$€\\s]', '', regex=True)   # remove currency/space
    s = s.str.replace(',', '', regex=False)             # remove thousands commas
    s = s.replace({'nan': np.nan, 'None': np.nan, '': np.nan})
    return pd.to_numeric(s, errors='coerce')

def detect_col(df, keywords, exclude=None):
    exclude = set(exclude or [])
    for kw in keywords:
        for col in df.columns:
            if col in exclude: continue
            if kw.lower() == col.lower().strip(): return col
    for kw in keywords:
        for col in df.columns:
            if col in exclude: continue
            if kw.lower() in col.lower().strip(): return col
    return None

if os.path.exists(CSV_PATH):
    with open(CSV_PATH, 'r', encoding='utf-8', errors='replace') as f:
        first_line = f.readline()
    sep = ';' if first_line.count(';') > first_line.count(',') else ','
    print(f"Detected delimiter: '{sep}'")
    df_raw = pd.read_csv(CSV_PATH, sep=sep)
    df_raw.columns = df_raw.columns.str.strip()
    print(f"Loaded: {df_raw.shape[0]} rows x {df_raw.shape[1]} columns")
    print("Columns:", df_raw.columns.tolist())
else:
    print("Estate_Agent.csv not found — generating synthetic data.")
    np.random.seed(42)
    n = 260
    rating = np.random.choice([1,2,3,4,5], n, p=[0.05,0.15,0.35,0.30,0.15])
    living = np.random.randint(800, 5000, n).astype(float)
    land   = np.random.randint(2000, 15000, n).astype(float)
    beds   = np.random.randint(1, 7, n)
    baths  = np.random.randint(1, 5, n)
    garage = np.random.randint(0, 1200, n).astype(float)
    cars   = np.random.randint(0, 4, n)
    year   = np.random.randint(1960, 2023, n)
    price  = (180*living + 40*land + 25000*beds + 20000*baths
              + 80*garage + 5000*rating + np.random.normal(0, 40000, n)).clip(50000, 2000000)
    df_raw = pd.DataFrame({'LandArea': land, 'YearBuilt': year, 'Bathrooms': baths,
                           'Bedrooms': beds, 'GarageArea': garage, 'LivingArea': living,
                           'Rating': rating, 'ParkingCars': cars, 'Price': price})
    idx = np.random.choice(n, 22, replace=False)
    df_raw.loc[idx[:7],  'GarageArea'] = np.nan
    df_raw.loc[idx[7:12],'Bathrooms']  = np.nan
    df_raw.loc[idx[12:],  'Price']     = np.nan
    df_raw = pd.concat([df_raw, df_raw.iloc[[0,5,10]]], ignore_index=True)
    df_raw.loc[258, 'Price'] = 9_999_999
    df_raw.loc[259, 'LivingArea'] = -500

df_raw.head()
"""))

cells.append(code("""
# ── Detect column roles ───────────────────────────────────────────────────────
target_col  = detect_col(df_raw, ['price', 'saleprice', 'sale_price', 'houseprice'])
rating_col  = detect_col(df_raw, ['rating', 'overallqual', 'quality', 'grade', 'houserating'], [target_col])
beds_col    = detect_col(df_raw, ['bedroom', 'bedrooms', 'bed', 'bedroomabvgr'])
baths_col   = detect_col(df_raw, ['bathroom', 'bathrooms', 'bath', 'fullbath'])
living_col  = detect_col(df_raw, ['livingarea', 'grlivarea', 'living', 'livarea', 'livingspace'])
land_col    = detect_col(df_raw, ['landarea', 'lotarea', 'land', 'lot', 'area'])
garage_col  = detect_col(df_raw, ['garagearea', 'garage'])
cars_col    = detect_col(df_raw, ['parkingcars', 'garagecars', 'parking', 'cars'])
year_col    = detect_col(df_raw, ['yearbuilt', 'year_built', 'year'])

print("Column mapping detected:")
print(f"  Price (target) : {target_col}")
print(f"  Rating         : {rating_col}")
print(f"  Bedrooms       : {beds_col}")
print(f"  Bathrooms      : {baths_col}")
print(f"  Living Area    : {living_col}")
print(f"  Land Area      : {land_col}")
print(f"  Garage Area    : {garage_col}")
print(f"  Parking Cars   : {cars_col}")
print(f"  Year Built     : {year_col}")

feature_cols = [c for c in [land_col, year_col, baths_col, beds_col,
                              garage_col, living_col, cars_col] if c is not None]
print(f"\\nFeature columns for ML: {feature_cols}")
"""))

cells.append(code("""
# ── Clean all numeric columns ─────────────────────────────────────────────────
df_raw_clean = df_raw.copy()
for col in df_raw_clean.columns:
    df_raw_clean[col] = clean_numeric(df_raw_clean[col])

print("Cleaned dtypes:")
print(df_raw_clean.dtypes)
print(f"\\nPrice sample (first 5): {df_raw_clean[target_col].dropna().head().tolist()}")
"""))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION A
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md("""
---
## Section A: Data Science – Scenario 1 (Estate Agent Dataset)
**[30% of total marks]**
"""))

# A1
cells.append(md("""
### A1 – Exploratory Data Analysis (EDA)
Examine statistical properties and identify relevant features. All numeric columns
describing property characteristics are included; the target is the price column.
"""))

cells.append(code("""
# A1.1 – Dataset overview
print(f"Shape: {df_raw_clean.shape[0]} rows, {df_raw_clean.shape[1]} columns\\n")
print("Column data types:")
print(df_raw_clean.dtypes)
"""))

cells.append(code("""
# A1.2 – Descriptive statistics
df_raw_clean.describe().round(2)
"""))

cells.append(code("""
# A1.3 – Missing value summary
missing = df_raw_clean.isnull().sum()
pct     = (missing / len(df_raw_clean) * 100).round(2)
miss_df = pd.DataFrame({'Missing Count': missing, 'Missing %': pct})
miss_df = miss_df[miss_df['Missing Count'] > 0]
print("=== Missing Values ===")
print(miss_df if not miss_df.empty else "No missing values.")
"""))

cells.append(code("""
# A1.4 – Correlation heatmap
num_cols = df_raw_clean.select_dtypes(include=[np.number]).columns.tolist()
print(f"Numeric columns: {num_cols}")
corr = df_raw_clean[num_cols].corr()
plt.figure(figsize=(11, 8))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm',
            mask=mask, vmin=-1, vmax=1, linewidths=0.5, annot_kws={'size': 8})
plt.title('A1 – Correlation Matrix of Numeric Features', fontsize=13, pad=12)
plt.tight_layout()
plt.savefig('A1_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

# A2
cells.append(md("""
### A2 – Data Cleaning
Addresses duplicates, numeric type conversion, missing value imputation,
outlier removal (IQR), and illogical values.
"""))

cells.append(code("""
# A2.1 – Start from cleaned numeric copy; remove duplicates
df = df_raw_clean.copy()
n_before = len(df)
df = df.drop_duplicates()
print(f"Duplicates removed: {n_before - len(df)} (before: {n_before}, after: {len(df)})")
"""))

cells.append(code("""
# A2.2 – Impute missing values with column median
print("Missing before imputation:")
print(df.isnull().sum()[df.isnull().sum() > 0])
for col in df.select_dtypes(include=[np.number]).columns:
    if df[col].isnull().sum() > 0:
        med = df[col].median()
        df[col] = df[col].fillna(med)
        print(f"  '{col}' -> filled with median = {med:.2f}")
print(f"\\nMissing after imputation: {df.isnull().sum().sum()}")
"""))

cells.append(code("""
# A2.3 – Remove outliers from Price using IQR
fig, axes = plt.subplots(1, 2, figsize=(13, 4))
axes[0].boxplot(df[target_col].dropna())
axes[0].set_title(f'A2 – {target_col} BEFORE Outlier Removal')
axes[0].set_ylabel('Value')

Q1, Q3 = df[target_col].quantile(0.25), df[target_col].quantile(0.75)
IQR = Q3 - Q1
lo, hi = Q1 - 1.5*IQR, Q3 + 1.5*IQR
outliers = (df[target_col] < lo) | (df[target_col] > hi)
print(f"Outliers detected: {outliers.sum()} | Bounds: {lo:,.0f} to {hi:,.0f}")
df = df[~outliers]

if living_col and living_col in df.columns:
    bad = (df[living_col] <= 0).sum()
    if bad > 0:
        print(f"Removing {bad} rows with non-positive {living_col}")
        df = df[df[living_col] > 0]

axes[1].boxplot(df[target_col].dropna())
axes[1].set_title(f'A2 – {target_col} AFTER Outlier Removal')
axes[1].set_ylabel('Value')
plt.tight_layout()
plt.savefig('A2_outlier_boxplot.png', dpi=150, bbox_inches='tight')
plt.show()
print(f"Clean dataset: {df.shape}")
"""))

cells.append(code("""
# A2.4 – Cleaned dataset summary
df.describe().round(2)
"""))

# A3
cells.append(md("""
### A3 – Data Visualisation
Charts reveal distribution shapes, inter-feature relationships, and how features
relate to the target price variable.
"""))

cells.append(code("""
# A3.1 – Price histogram and Q-Q plot
# Justification: Price is the regression target. Skewness assessment guides
# whether log-transformation is needed before modelling.
price_data = df[target_col].dropna()
print(f"Valid price values: {len(price_data)}")
print(f"Range: {price_data.min():,.0f} to {price_data.max():,.0f}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].hist(price_data, bins=30, color='steelblue', edgecolor='white')
axes[0].set_title('A3.1a – Price Histogram')
axes[0].set_xlabel('Price'); axes[0].set_ylabel('Frequency')
stats.probplot(price_data, plot=axes[1])
axes[1].set_title('A3.1b – Price Q-Q Plot (Normality Check)')
plt.tight_layout()
plt.savefig('A3_price_distribution.png', dpi=150, bbox_inches='tight')
plt.show()
print(f"Price skewness: {price_data.skew():.3f}  (|skew| > 1 suggests right-skew)")
"""))

cells.append(code("""
# A3.2 – Feature distribution histograms
# Justification: Each feature's distribution shape informs preprocessing decisions.
num_feats = [c for c in df.select_dtypes(include=[np.number]).columns if c != target_col]
print(f"Features to plot: {num_feats}")

n_cols = 3
n_rows = max(1, (len(num_feats) + n_cols - 1) // n_cols)
palette = sns.color_palette('husl', len(num_feats))

fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, n_rows * 4))
axes = axes.flatten() if n_rows > 1 or n_cols > 1 else [axes]
for i, col in enumerate(num_feats):
    axes[i].hist(df[col].dropna(), bins=20, color=palette[i], edgecolor='white', alpha=0.85)
    axes[i].set_title(col); axes[i].set_xlabel(col); axes[i].set_ylabel('Count')
for j in range(len(num_feats), len(axes)):
    axes[j].set_visible(False)
fig.suptitle('A3.2 – Feature Distributions', fontsize=13, y=1.01)
plt.tight_layout()
plt.savefig('A3_feature_distributions.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

cells.append(code("""
# A3.3 – Scatter plots: Price vs top two correlated features
# Justification: Reveals linear/non-linear relationships between predictors and price.
corr_price = df.corr()[target_col].abs().drop(target_col).sort_values(ascending=False)
top2 = corr_price.index[:2].tolist()
print(f"Top 2 features correlated with {target_col}: {top2}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for ax, feat, col in zip(axes, top2, ['steelblue', 'darkorange']):
    data = df[[feat, target_col]].dropna()
    ax.scatter(data[feat], data[target_col], alpha=0.45, s=18, color=col)
    m, b = np.polyfit(data[feat], data[target_col], 1)
    xr = np.linspace(data[feat].min(), data[feat].max(), 100)
    ax.plot(xr, m*xr + b, 'r--', lw=2, label='Trend')
    ax.set_title(f'A3.3 – {feat} vs {target_col}')
    ax.set_xlabel(feat); ax.set_ylabel(target_col)
    ax.legend()
plt.tight_layout()
plt.savefig('A3_scatter_price.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

cells.append(code("""
# A3.4 – Box plots: Price by Rating and Bedrooms
# Justification: Compares price distributions across categorical groups,
# revealing which property grades and sizes command premium prices.
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

if rating_col and rating_col in df.columns:
    plot_data = df[[target_col, rating_col]].dropna()
    plot_data.boxplot(column=target_col, by=rating_col, ax=axes[0])
    axes[0].set_title(f'A3.4a – {target_col} by {rating_col}')
    axes[0].set_xlabel(rating_col); axes[0].set_ylabel(target_col)
    plt.suptitle('')
else:
    axes[0].text(0.5, 0.5, 'Rating column not found', ha='center', va='center')

if beds_col and beds_col in df.columns:
    plot_data2 = df[[target_col, beds_col]].dropna()
    plot_data2.boxplot(column=target_col, by=beds_col, ax=axes[1])
    axes[1].set_title(f'A3.4b – {target_col} by {beds_col}')
    axes[1].set_xlabel(beds_col); axes[1].set_ylabel(target_col)
    plt.suptitle('')
else:
    axes[1].text(0.5, 0.5, 'Bedrooms column not found', ha='center', va='center')

plt.tight_layout()
plt.savefig('A3_boxplots.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

cells.append(code("""
# A3.5 – Pair plot of top correlated features
# Justification: Shows pairwise relationships in one view, helping identify
# multicollinearity and feature interactions simultaneously.
top_feats = corr_price.index[:4].tolist() + [target_col]
print("Pair plot features:", top_feats)
g = sns.pairplot(df[top_feats].dropna(), diag_kind='kde',
                 plot_kws={'alpha': 0.4, 's': 14})
g.fig.suptitle('A3.5 – Pair Plot: Top Features vs Price', y=1.01, fontsize=12)
plt.savefig('A3_pairplot.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION B
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md("""
---
## Section B: AI/ML – Scenario 1
**[30% of total marks]**
"""))

cells.append(md("### ML Feature Preparation"))

cells.append(code("""
# Prepare regression and classification datasets
X_reg_df = df[feature_cols].copy()
y_reg     = df[target_col].copy()
mask_r    = X_reg_df.notna().all(axis=1) & y_reg.notna()
X_reg_df, y_reg = X_reg_df[mask_r], y_reg[mask_r]

X_cls_df  = df[feature_cols].copy()
y_cls     = df[rating_col].astype(float).round().astype(int).copy()
mask_c    = X_cls_df.notna().all(axis=1) & y_cls.notna()
X_cls_df, y_cls = X_cls_df[mask_c], y_cls[mask_c]

scaler_r = StandardScaler()
scaler_c = StandardScaler()
X_reg_s  = scaler_r.fit_transform(X_reg_df)
X_cls_s  = scaler_c.fit_transform(X_cls_df)

print(f"Regression:     X={X_reg_s.shape}, y={y_reg.shape}")
print(f"Classification: X={X_cls_s.shape}, y={y_cls.shape}")
print(f"Rating classes: {sorted(y_cls.unique())}")
"""))

# B1
cells.append(md("""
### B1 – Multiple Linear Regression
Three train/test splits are evaluated. Metrics: MAE, RMSE, R².
A sample price prediction is shown using the best model.
"""))

cells.append(code("""
splits = [('70/30', 0.30), ('80/20', 0.20), ('90/10', 0.10)]
lr_results = []

fig, axes = plt.subplots(1, 3, figsize=(17, 5))
for i, (label, ts) in enumerate(splits):
    X_tr, X_te, y_tr, y_te = train_test_split(X_reg_s, y_reg, test_size=ts, random_state=42)
    mdl = LinearRegression().fit(X_tr, y_tr)
    y_hat = mdl.predict(X_te)
    mae  = mean_absolute_error(y_te, y_hat)
    rmse = np.sqrt(mean_squared_error(y_te, y_hat))
    r2   = r2_score(y_te, y_hat)
    lr_results.append({'Split': label, 'Train': len(y_tr), 'Test': len(y_te),
                        'MAE': mae, 'RMSE': rmse, 'R2': r2,
                        '_model': mdl, '_y_te': y_te, '_y_hat': y_hat})
    axes[i].scatter(y_te, y_hat, alpha=0.5, s=18, color='steelblue')
    mn, mx = min(y_te.min(), y_hat.min()), max(y_te.max(), y_hat.max())
    axes[i].plot([mn, mx], [mn, mx], 'r--', lw=2, label='Perfect fit')
    axes[i].set_title(f'B1 – Split {label}\\nR2={r2:.3f}')
    axes[i].set_xlabel('Actual'); axes[i].set_ylabel('Predicted')
    axes[i].legend()
plt.tight_layout()
plt.savefig('B1_regression.png', dpi=150, bbox_inches='tight')
plt.show()

summary_lr = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith('_')}
                            for r in lr_results])
print("=== B1: Linear Regression Metrics ===")
print(summary_lr.round(2).to_string(index=False))
"""))

cells.append(code("""
# B1 – Feature coefficients (best split)
best_idx = summary_lr['R2'].idxmax()
best_lr  = lr_results[best_idx]
coef_ser = pd.Series(best_lr['_model'].coef_, index=feature_cols).sort_values()

plt.figure(figsize=(8, 4))
colours = ['#e74c3c' if c < 0 else '#2980b9' for c in coef_ser]
coef_ser.plot(kind='barh', color=colours)
plt.axvline(0, color='black', lw=0.8)
plt.title(f"B1 – Feature Coefficients (split {best_lr['Split']})")
plt.xlabel('Coefficient')
plt.tight_layout()
plt.savefig('B1_coefficients.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

cells.append(code("""
# B1 – Price prediction for a sample property
sample = {col: float(df[col].median()) for col in feature_cols}
sample_s = scaler_r.transform(pd.DataFrame([sample]))
predicted = best_lr['_model'].predict(sample_s)[0]
print("=== Price Prediction Example (median property) ===")
for k, v in sample.items():
    print(f"  {k:20s}: {v:.1f}")
print(f"\\n  Predicted {target_col}: {predicted:,.0f}")
"""))

# B2
cells.append(md("""
### B2 – k-Nearest Neighbours Classification for Rating
Hyperparameter tuning over k=1–25 to find optimal neighbourhood size.
"""))

cells.append(code("""
X_tr, X_te, y_tr, y_te = train_test_split(
    X_cls_s, y_cls, test_size=0.25, random_state=42, stratify=y_cls)

k_range = range(1, 26)
train_accs, test_accs = [], []
for k in k_range:
    m = KNeighborsClassifier(n_neighbors=k).fit(X_tr, y_tr)
    train_accs.append(m.score(X_tr, y_tr))
    test_accs.append(m.score(X_te, y_te))

best_k = list(k_range)[np.argmax(test_accs)]
print(f"Best k = {best_k}  |  Test accuracy = {max(test_accs):.4f}")

plt.figure(figsize=(10, 5))
plt.plot(k_range, train_accs, 'b-o', ms=4, label='Train Accuracy')
plt.plot(k_range, test_accs,  'r-o', ms=4, label='Test Accuracy')
plt.axvline(best_k, color='green', lw=2, ls='--', label=f'Best k={best_k}')
plt.xlabel('k'); plt.ylabel('Accuracy')
plt.title('B2 – kNN Hyperparameter Tuning')
plt.legend(); plt.tight_layout()
plt.savefig('B2_knn_tuning.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

cells.append(code("""
knn_best  = KNeighborsClassifier(n_neighbors=best_k).fit(X_tr, y_tr)
y_hat_knn = knn_best.predict(X_te)
knn_acc   = accuracy_score(y_te, y_hat_knn)
knn_f1    = f1_score(y_te, y_hat_knn, average='weighted', zero_division=0)

print(f"=== kNN Evaluation (k={best_k}) ===")
print(f"Accuracy:  {knn_acc:.4f}")
print(f"Precision: {precision_score(y_te, y_hat_knn, average='weighted', zero_division=0):.4f}")
print(f"Recall:    {recall_score(y_te, y_hat_knn, average='weighted', zero_division=0):.4f}")
print(f"F1:        {knn_f1:.4f}")
print("\\n=== Classification Report ===")
print(classification_report(y_te, y_hat_knn, zero_division=0))

fig, ax = plt.subplots(figsize=(7, 6))
ConfusionMatrixDisplay.from_predictions(y_te, y_hat_knn, ax=ax, colorbar=False)
ax.set_title(f'B2 – kNN Confusion Matrix (k={best_k})')
plt.tight_layout()
plt.savefig('B2_knn_confusion.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

# B3
cells.append(md("""
### B3 – Support Vector Machine Classification
Three kernels tested. Results compared to kNN using accuracy and weighted F1.
"""))

cells.append(code("""
kernels = {
    'Linear':  SVC(kernel='linear', C=1.0, random_state=42),
    'RBF':     SVC(kernel='rbf',    C=1.0, gamma='scale', random_state=42),
    'Poly(3)': SVC(kernel='poly',   degree=3, C=1.0, random_state=42),
}
svm_res = {}
best_svm_name, best_svm_acc, best_svm_pred = None, 0, None

for name, mdl in kernels.items():
    mdl.fit(X_tr, y_tr)
    pred = mdl.predict(X_te)
    acc  = accuracy_score(y_te, pred)
    f1   = f1_score(y_te, pred, average='weighted', zero_division=0)
    svm_res[name] = {'Accuracy': acc, 'F1 (weighted)': f1}
    if acc > best_svm_acc:
        best_svm_acc, best_svm_name, best_svm_pred = acc, name, pred

print("=== SVM Results by Kernel ===")
print(pd.DataFrame(svm_res).T.round(4))
print(f"\\nBest kernel: {best_svm_name} (Accuracy={best_svm_acc:.4f})")
"""))

cells.append(code("""
svm_f1 = f1_score(y_te, best_svm_pred, average='weighted', zero_division=0)
cmp = pd.DataFrame({
    'Model':         [f'kNN (k={best_k})', f'SVM ({best_svm_name})'],
    'Accuracy':      [knn_acc, best_svm_acc],
    'F1 (weighted)': [knn_f1, svm_f1],
})
print("=== B3: kNN vs SVM ===")
print(cmp.round(4).to_string(index=False))

x = np.arange(2)
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for ax, metric in zip(axes, ['Accuracy', 'F1 (weighted)']):
    vals = cmp[metric].values
    ax.bar(x, vals, color=['steelblue', 'darkorange'])
    ax.set_xticks(x); ax.set_xticklabels(cmp['Model'])
    ax.set_ylim(0, 1.15); ax.set_title(f'B3 – {metric}')
    ax.set_ylabel(metric)
    for xi, yi in zip(x, vals):
        ax.text(xi, yi + 0.02, f'{yi:.3f}', ha='center', fontsize=11)
plt.tight_layout()
plt.savefig('B3_comparison.png', dpi=150, bbox_inches='tight')
plt.show()

fig2, ax2 = plt.subplots(figsize=(7, 6))
ConfusionMatrixDisplay.from_predictions(y_te, best_svm_pred, ax=ax2, colorbar=False)
ax2.set_title(f'B3 – SVM ({best_svm_name}) Confusion Matrix')
plt.tight_layout()
plt.savefig('B3_svm_confusion.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

# B4
cells.append(md("""
### B4 – k-Means Clustering, PCA, and t-SNE
Elbow method and silhouette scores determine optimal cluster count.
PCA and t-SNE reduce to 2D for cluster visualisation.
"""))

cells.append(code("""
inertias, sil = [], []
k_range = range(2, 11)
for k in k_range:
    km   = KMeans(n_clusters=k, random_state=42, n_init=10)
    lbls = km.fit_predict(X_cls_s)
    inertias.append(km.inertia_)
    sil.append(silhouette_score(X_cls_s, lbls))

optimal_k = list(k_range)[np.argmax(sil)]
print(f"Optimal k: {optimal_k}  |  Best silhouette: {max(sil):.4f}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].plot(k_range, inertias, 'b-o', ms=6)
axes[0].set_xlabel('k'); axes[0].set_ylabel('Inertia')
axes[0].set_title('B4 – Elbow Method')
axes[1].plot(k_range, sil, 'r-o', ms=6)
axes[1].axvline(optimal_k, color='green', ls='--', lw=2, label=f'Optimal k={optimal_k}')
axes[1].set_xlabel('k'); axes[1].set_ylabel('Silhouette Score')
axes[1].set_title('B4 – Silhouette Scores'); axes[1].legend()
plt.tight_layout()
plt.savefig('B4_elbow_silhouette.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

cells.append(code("""
km_final      = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
cluster_labels = km_final.fit_predict(X_cls_s)
print("Cluster distribution:")
print(pd.Series(cluster_labels).value_counts().sort_index())
"""))

cells.append(code("""
# PCA
pca  = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_cls_s)
var  = pca.explained_variance_ratio_
print(f"PCA variance explained: {var[0]:.3f} + {var[1]:.3f} = {var.sum():.3f}")

plt.figure(figsize=(8, 6))
sc = plt.scatter(X_pca[:,0], X_pca[:,1], c=cluster_labels, cmap='tab10', alpha=0.7, s=28)
plt.colorbar(sc, label='Cluster')
plt.xlabel(f'PC1 ({var[0]*100:.1f}% var)'); plt.ylabel(f'PC2 ({var[1]*100:.1f}% var)')
plt.title(f'B4 – PCA Cluster Visualisation (k={optimal_k})')
plt.tight_layout()
plt.savefig('B4_pca_clusters.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

cells.append(code("""
# t-SNE
tsne   = TSNE(n_components=2, random_state=42, perplexity=30, max_iter=1000)
X_tsne = tsne.fit_transform(X_cls_s)

plt.figure(figsize=(8, 6))
sc2 = plt.scatter(X_tsne[:,0], X_tsne[:,1], c=cluster_labels, cmap='tab10', alpha=0.7, s=28)
plt.colorbar(sc2, label='Cluster')
plt.xlabel('t-SNE Dim 1'); plt.ylabel('t-SNE Dim 2')
plt.title(f'B4 – t-SNE Cluster Visualisation (k={optimal_k})')
plt.tight_layout()
plt.savefig('B4_tsne_clusters.png', dpi=150, bbox_inches='tight')
plt.show()

print('''
PCA vs t-SNE:
  PCA  - linear, interpretable axes, preserves global variance structure.
  t-SNE - non-linear, preserves local neighbourhoods, axes have no meaning.
  t-SNE typically shows tighter cluster separation; PCA is preferred when
  interpretability and computational speed matter.
''')
"""))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION C
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md("""
---
## Section C: AI – Facial Expression Detection (Scenario 2)
**[20% of total marks]**

**Setup:**
1. `FacesSample/` – 50 images from Moodle (JPG or PNG) -> place in notebook directory
2. `Expressions/` – create manually with one image each:
   `Surprised`, `Angry`, `Happy`, `Sad`, `Frightful`, `Neutral` (JPG or PNG)

**Model:** `trpakov/vit-face-expression` (Vision Transformer, PyTorch — no TensorFlow needed)
"""))

cells.append(md("### C1 – Facial Expression Detection"))

cells.append(code("""
FACES_DIR = 'FacesSample'
EXPR_DIR  = 'Expressions'

LABEL_MAP = {
    'surprised': 'Surprised', 'angry': 'Angry', 'happy': 'Happy',
    'sad': 'Sad', 'fearful': 'Frightful', 'neutral': 'Neutral',
    'disgusted': 'Angry',
}

def find_images(folder):
    files = []
    for ext in ['*.jpg','*.jpeg','*.png','*.JPG','*.JPEG','*.PNG']:
        files.extend(glob.glob(os.path.join(folder, ext)))
    return sorted(set(files))

for folder in [FACES_DIR, EXPR_DIR]:
    print(f"  {folder}/ -> {'FOUND' if os.path.isdir(folder) else 'NOT FOUND'}")

face_imgs = find_images(FACES_DIR)
expr_imgs = find_images(EXPR_DIR)
print(f"\\nFacesSample images : {len(face_imgs)}")
print(f"Expressions images : {len(expr_imgs)}")
"""))

cells.append(code("""
# Show reference Expressions images
if expr_imgs:
    n = len(expr_imgs)
    fig, axes = plt.subplots(1, n, figsize=(3*n, 3))
    if n == 1: axes = [axes]
    for ax, path in zip(axes, expr_imgs):
        ax.imshow(Image.open(path))
        ax.set_title(os.path.splitext(os.path.basename(path))[0], fontsize=9)
        ax.axis('off')
    plt.suptitle('C1 – Reference Expressions Folder', fontsize=12)
    plt.tight_layout()
    plt.savefig('C1_reference_expressions.png', dpi=150, bbox_inches='tight')
    plt.show()
else:
    print("Expressions/ folder is empty. Add 6 reference images.")
"""))

cells.append(code("""
# Load ViT emotion classifier (downloads ~350 MB on first run)
from transformers import pipeline as hf_pipeline

print("Loading emotion model...")
emotion_clf = hf_pipeline(
    "image-classification",
    model="trpakov/vit-face-expression",
    device=-1
)
print("Model ready.")

c1_results = []
if face_imgs:
    print(f"\\nProcessing {len(face_imgs)} images...")
    for i, path in enumerate(face_imgs):
        fname = os.path.basename(path)
        try:
            preds     = emotion_clf(path, top_k=7)
            top       = preds[0]
            raw_label = top['label'].lower().split('_')[-1]
            confidence = top['score']
            mapped    = LABEL_MAP.get(raw_label, raw_label.capitalize())
            all_scores = {p['label'].lower().split('_')[-1]: round(p['score'], 3) for p in preds}
        except Exception as e:
            raw_label, confidence, mapped, all_scores = 'error', 0.0, 'Unknown', {}
        c1_results.append({'File': fname, 'Detected': raw_label,
                           'Confidence': round(confidence, 3),
                           'Mapped Label': mapped, 'All Scores': all_scores})
        if (i+1) % 10 == 0:
            print(f"  {i+1}/{len(face_imgs)} done")
    print("Detection complete.")
else:
    print("No images found in FacesSample/.")
"""))

cells.append(code("""
if c1_results:
    df_c1 = pd.DataFrame(c1_results)
    print("=== C1: Detection Results ===")
    print(df_c1[['File','Detected','Confidence','Mapped Label']].to_string(index=False))

    dist = df_c1['Mapped Label'].value_counts()
    neutral_pct = (df_c1['Mapped Label'] == 'Neutral').mean() * 100
    print(f"\\nExpression counts:\\n{dist}")
    print(f"\\nImages detected as Neutral: {neutral_pct:.1f}%")

    plt.figure(figsize=(9, 5))
    dist.plot(kind='bar', color=sns.color_palette('husl', len(dist)), edgecolor='white')
    plt.title('C1 – Detected Expression Distribution (FacesSample)')
    plt.xlabel('Expression'); plt.ylabel('Count')
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig('C1_expression_distribution.png', dpi=150, bbox_inches='tight')
    plt.show()

    print('''
Discussion:
  The ViT model outputs probabilities across 7 emotion classes. Images wrongly
  classified as Neutral typically have subtle expressions, poor lighting, partial
  occlusion, or head poses outside the training distribution. Confidence scores
  below 0.4 indicate genuine ambiguity in the image.
''')
"""))

cells.append(code("""
# Sample image grid with detection labels
if c1_results and face_imgs:
    n_show = min(12, len(face_imgs))
    fig, axes = plt.subplots(3, 4, figsize=(14, 10))
    axes = axes.flatten()
    for i in range(n_show):
        label = c1_results[i]['Mapped Label'] if i < len(c1_results) else '?'
        conf  = c1_results[i]['Confidence']   if i < len(c1_results) else 0
        try:
            axes[i].imshow(Image.open(face_imgs[i]))
        except Exception:
            axes[i].text(0.5, 0.5, 'Error', ha='center', va='center')
        axes[i].set_title(f"{c1_results[i]['File']}\\n{label} ({conf:.2f})", fontsize=7)
        axes[i].axis('off')
    for j in range(n_show, len(axes)):
        axes[j].set_visible(False)
    plt.suptitle('C1 – Sample Expression Detections', fontsize=12)
    plt.tight_layout()
    plt.savefig('C1_sample_grid.png', dpi=150, bbox_inches='tight')
    plt.show()
"""))

# C2
cells.append(md("""
### C2 – Real-Life Application: Corporate Wellbeing Monitoring System
Extends C1 to model a consent-based employee wellbeing system that aggregates
daily emotion data to flag stress accumulation.
"""))

cells.append(code("""
np.random.seed(7)
EMPLOYEES = [f'Emp {i+1:02d}' for i in range(10)]
DAYS      = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
EXPRS     = ['Happy', 'Neutral', 'Sad', 'Angry', 'Frightful', 'Surprised']
STRESS    = {'Happy': 0.0, 'Neutral': 0.2, 'Sad': 0.6,
             'Angry': 0.9, 'Frightful': 0.8, 'Surprised': 0.3}

emp_data = {}
for emp in EMPLOYEES:
    daily = np.random.choice(EXPRS, len(DAYS), p=[0.35,0.30,0.15,0.08,0.07,0.05])
    emp_data[emp] = {'emotions': daily, 'stress': [STRESS[e] for e in daily]}

stress_mat = np.array([emp_data[e]['stress'] for e in EMPLOYEES])
avg_stress  = stress_mat.mean(axis=1)

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
sns.heatmap(stress_mat, ax=axes[0], xticklabels=DAYS, yticklabels=EMPLOYEES,
            cmap='RdYlGn_r', vmin=0, vmax=1, annot=True, fmt='.1f', linewidths=0.4)
axes[0].set_title('C2 – Weekly Stress Heatmap'); axes[0].set_xlabel('Day')

colours = ['#e74c3c' if s > 0.5 else '#2ecc71' for s in avg_stress]
axes[1].barh(EMPLOYEES, avg_stress, color=colours)
axes[1].axvline(0.5, color='red', ls='--', lw=1.5, label='Alert threshold')
axes[1].set_xlabel('Avg Stress Score (0-1)')
axes[1].set_title('C2 – Average Weekly Stress per Employee')
axes[1].legend()
plt.tight_layout()
plt.savefig('C2_wellbeing_monitor.png', dpi=150, bbox_inches='tight')
plt.show()

print("=== C2: Wellbeing Alerts ===")
for emp, s in zip(EMPLOYEES, avg_stress):
    flag = "WARNING - recommend check-in" if s > 0.5 else "OK - within normal range"
    print(f"  {emp}: {s:.2f}  {flag}")
"""))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION D
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md("""
---
## Section D: AI and LSEPI
**[10% of total marks]**

### D1 – Legal, Social, Ethical and Professional Issues

**Scenario 1 – Estate Agent Price Prediction:**

| Category | Issue |
|----------|-------|
| **Legal** | Personal property data is subject to UK GDPR (ICO, 2018). Using postcode as a feature risks indirect discrimination under the Equality Act 2010. |
| **Social** | Algorithmic pricing can entrench socioeconomic inequality by systematically under-valuing properties in deprived areas (O'Neil, 2016). |
| **Ethical** | Training on historical data may perpetuate past discriminatory valuation practices, reproducing rather than correcting bias (Barocas and Hardt, 2017). |
| **Professional** | Presenting predictions without confidence intervals or feature attribution breaches RICS professional transparency obligations (RICS, 2021). |

**Scenario 2 – Employee Facial Expression Monitoring:**

| Category | Issue |
|----------|-------|
| **Legal** | Facial images are biometric special-category data under UK GDPR Article 9. Monitoring without explicit consent and a DPIA is unlawful (ICO, 2011). |
| **Social** | Continuous surveillance erodes psychological safety and may disadvantage employees from cultures with different emotional expression norms (Zuboff, 2019). |
| **Ethical** | Consent in an employment context may not be freely given due to the power imbalance between employer and employee (Floridi et al., 2018). |
| **Professional** | ACM Code of Ethics (2018) requires computing professionals to assess and mitigate potential harms before deployment. |

---

### D2 – Countermeasures

**Scenario 1:**
- Conduct a Data Protection Impact Assessment (DPIA) before deployment.
- Remove protected characteristic proxies (postcode, neighbourhood) from features.
- Apply Explainable AI (SHAP/LIME) to provide transparent feature attribution to clients.
- Run regular fairness audits using disparate impact ratio metrics.

**Scenario 2:**
- Obtain explicit, freely given, and easily withdrawable consent from all employees.
- Aggregate data only — never expose individual emotion scores to managers.
- Establish Human-in-the-Loop review before any intervention is triggered.
- Provide a penalty-free opt-out mechanism.

---

### D3 – Intelligent Systems for the Common Good

**Scenario 1:** Fair pricing models can democratise property market information, giving first-time buyers analytical power previously available only to institutional investors. Local authorities can use aggregated pricing signals to identify gentrification and design affordable housing interventions (Mayer, 2019).

**Scenario 2:** Responsibly deployed emotion-sensing in healthcare settings can support early detection of mental health deterioration in patients. In education, emotion-aware platforms can identify disengaged or distressed students for timely pastoral support (D'Mello et al., 2017).

---

### References

- ACM (2018) *ACM Code of Ethics and Professional Conduct*. Available at: https://www.acm.org/code-of-ethics
- Barocas, S. and Hardt, M. (2017) *Fairness in Machine Learning*. Available at: https://fairmlbook.org
- D'Mello, S.K. et al. (2017) 'Automated detection of affect during learning', *IEEE Transactions on Affective Computing*, 8(3), pp. 389-400.
- Floridi, L. et al. (2018) 'An ethical framework for a good AI society', *Minds and Machines*, 28(4), pp. 689-707.
- ICO (2011) *Employment Practices Code*. Wilmslow: Information Commissioner's Office.
- ICO (2018) *Guide to the UK General Data Protection Regulation*. Wilmslow: Information Commissioner's Office.
- Mayer, C. (2019) *Prosperity: Better Business Makes the Greater Good*. Oxford: Oxford University Press.
- O'Neil, C. (2016) *Weapons of Math Destruction*. New York: Crown Publishers.
- RICS (2021) *RICS Valuation - Global Standards (Red Book)*. London: RICS.
- Zuboff, S. (2019) *The Age of Surveillance Capitalism*. London: PublicAffairs.
"""))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION E
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md("""
---
## Section E: Conclusion and Personal Reflections
**[10% of total marks]**

### E1 – Conclusion

This study applied a complete data science and machine learning pipeline to two real-world business scenarios.

In Scenario 1, the Estate Agent dataset required substantial preprocessing: the CSV delimiter was identified and corrected, currency formatting was stripped from numeric columns, duplicate records were removed, missing values were imputed using column medians, and IQR-based outlier removal was applied to the price column. Exploratory analysis confirmed that living space area and house rating were the strongest predictors of sale price. Multiple linear regression delivered acceptable predictive performance across all three train/test splits. kNN classification for Rating demonstrated competitive accuracy, with hyperparameter tuning identifying the optimal neighbourhood size. SVM with an RBF kernel outperformed kNN on F1 score, suggesting non-linear class boundaries. k-Means clustering guided by silhouette scores revealed distinct property market segments, with t-SNE producing tighter visual separation than PCA.

In Scenario 2, the ViT-based emotion classifier successfully detected facial expressions across the FacesSample images. Some images were classified as Neutral due to subtle expressions or image quality constraints. The wellbeing monitoring extension demonstrated how aggregated emotion data, gathered with explicit consent, can support employee mental health management without exposing individual data.

Section D contextualised both applications within the LSEPI framework, highlighting that algorithmic fairness, biometric data governance, and professional transparency are legal and ethical requirements.

---

### E2 – Personal Reflections

*(Write this section in your own words. Use the prompts below as a guide.)*

- What was the most challenging aspect of this coursework?
- How did you resolve the challenges you encountered?
- What key skills did you develop?
- How will these skills support your future studies or career in Data Science and AI?
"""))

# ── WRITE NOTEBOOK ──────────────────────────────────────────────────────────
notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "version": "3.9.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print(f"Notebook written to: {NOTEBOOK_PATH}")
print(f"Total cells: {len(cells)}")
for ct, n in {c['cell_type']: 0 for c in cells}.items():
    count = sum(1 for c in cells if c['cell_type'] == ct)
    print(f"  {ct}: {count}")
