import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, ConfusionMatrixDisplay, silhouette_score)
import warnings, os
warnings.filterwarnings('ignore')
os.chdir(os.path.dirname(os.path.abspath(__file__)))

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('husl')

# ── LOAD & CLEAN ──────────────────────────────────────────────────────────────
df_raw = pd.read_csv('Datasets/Estate_Agent.csv', sep=';')
df_raw.columns = df_raw.columns.str.strip()
df_raw['Parking'] = pd.to_numeric(df_raw['Parking'], errors='coerce')

df = df_raw.copy().drop_duplicates()
for col in df.select_dtypes(include=[np.number]).columns:
    if df[col].isnull().sum() > 0:
        df[col] = df[col].fillna(df[col].median())

Q1, Q3 = df['House_Price'].quantile(0.25), df['House_Price'].quantile(0.75)
IQR = Q3 - Q1
lo, hi = Q1 - 1.5*IQR, Q3 + 1.5*IQR
n_outliers = ((df['House_Price'] < lo) | (df['House_Price'] > hi)).sum()
df = df[(df['House_Price'] >= lo) & (df['House_Price'] <= hi)]
print(f"Clean dataset: {df.shape}, outliers removed: {n_outliers}")
print(f"Price range: {df['House_Price'].min():,.0f} to {df['House_Price'].max():,.0f}")
print(f"Price mean: {df['House_Price'].mean():,.0f}, skewness: {df['House_Price'].skew():.3f}")

target_col   = 'House_Price'
rating_col   = 'Rating'
feature_cols = ['House_Area','Build','No_of_Bathrooms','No_of_Bedrooms',
                'Garage_Area','Living_Space','Parking']

corr_price = df.corr()[target_col].abs().drop(target_col).sort_values(ascending=False)
top2 = corr_price.index[:2].tolist()
top4 = corr_price.index[:4].tolist()
print(f"Top correlations with price: {corr_price.round(3).to_dict()}")

# ── A2 OUTLIER PLOT ───────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 4))
axes[0].boxplot(df_raw['House_Price'].dropna())
axes[0].set_title('House_Price BEFORE Outlier Removal'); axes[0].set_ylabel('Price (GBP)')
axes[1].boxplot(df['House_Price'].dropna())
axes[1].set_title('House_Price AFTER Outlier Removal'); axes[1].set_ylabel('Price (GBP)')
plt.tight_layout(); plt.savefig('png/A2_outlier_boxplot.png', dpi=150, bbox_inches='tight'); plt.close()

# ── A3.1 Price distribution ───────────────────────────────────────────────────
price_data = df[target_col].dropna()
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].hist(price_data, bins=30, color='steelblue', edgecolor='white')
axes[0].set_title('A3.1a - Price Histogram'); axes[0].set_xlabel('Price (GBP)'); axes[0].set_ylabel('Frequency')
stats.probplot(price_data, plot=axes[1])
axes[1].set_title('A3.1b - Price Q-Q Plot (Normality Check)')
plt.tight_layout(); plt.savefig('png/A3_price_distribution.png', dpi=150, bbox_inches='tight'); plt.close()

# ── A3.2 Feature histograms ───────────────────────────────────────────────────
n_cols = 3; n_rows = max(1, (len(feature_cols) + n_cols - 1) // n_cols)
palette = sns.color_palette('husl', len(feature_cols))
fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, n_rows * 4))
axes = axes.flatten()
for i, col in enumerate(feature_cols):
    axes[i].hist(df[col].dropna(), bins=20, color=palette[i], edgecolor='white', alpha=0.85)
    axes[i].set_title(col); axes[i].set_xlabel(col); axes[i].set_ylabel('Count')
for j in range(len(feature_cols), len(axes)):
    axes[j].set_visible(False)
fig.suptitle('A3.2 - Feature Distributions', fontsize=13, y=1.01)
plt.tight_layout(); plt.savefig('png/A3_feature_distributions.png', dpi=150, bbox_inches='tight'); plt.close()

# ── A3.3 Scatter plots ────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for ax, feat, col in zip(axes, top2, ['steelblue', 'darkorange']):
    data = df[[feat, target_col]].dropna()
    ax.scatter(data[feat], data[target_col], alpha=0.45, s=18, color=col)
    m, b = np.polyfit(data[feat], data[target_col], 1)
    xr = np.linspace(data[feat].min(), data[feat].max(), 100)
    ax.plot(xr, m*xr + b, 'r--', lw=2, label='Trend')
    ax.set_title(f'{feat} vs {target_col}'); ax.set_xlabel(feat); ax.set_ylabel('Price'); ax.legend()
plt.tight_layout(); plt.savefig('png/A3_scatter_price.png', dpi=150, bbox_inches='tight'); plt.close()

# ── A3.4 Box plots ────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
df[[target_col, rating_col]].dropna().boxplot(column=target_col, by=rating_col, ax=axes[0])
axes[0].set_title('Price by Rating'); axes[0].set_xlabel('Rating'); axes[0].set_ylabel('Price'); plt.suptitle('')
df[[target_col, 'No_of_Bedrooms']].dropna().boxplot(column=target_col, by='No_of_Bedrooms', ax=axes[1])
axes[1].set_title('Price by Bedrooms'); axes[1].set_xlabel('No_of_Bedrooms'); axes[1].set_ylabel('Price'); plt.suptitle('')
plt.tight_layout(); plt.savefig('png/A3_boxplots.png', dpi=150, bbox_inches='tight'); plt.close()

# ── A3.5 Pair plot ────────────────────────────────────────────────────────────
pair_feats = top4 + [target_col]
g = sns.pairplot(df[pair_feats].dropna(), diag_kind='kde', plot_kws={'alpha': 0.4, 's': 14})
g.fig.suptitle('A3.5 - Pair Plot: Top Features vs Price', y=1.01, fontsize=12)
plt.savefig('png/A3_pairplot.png', dpi=150, bbox_inches='tight'); plt.close()
print("A3 saved.")

# ── B: PREPARE ML DATA ────────────────────────────────────────────────────────
X = df[feature_cols].copy()
y_reg = df[target_col].copy()
y_cls = df[rating_col].astype(int).copy()
mask = X.notna().all(axis=1)
X, y_reg, y_cls = X[mask], y_reg[mask], y_cls[mask]
scaler = StandardScaler()
X_s = scaler.fit_transform(X)
print(f"ML data: X={X_s.shape}, rating classes={sorted(y_cls.unique())}")

# ── B1: LINEAR REGRESSION ─────────────────────────────────────────────────────
print("\n=== B1: LINEAR REGRESSION ===")
splits = [('70/30', 0.30), ('80/20', 0.20), ('90/10', 0.10)]
lr_results = []
fig, axes = plt.subplots(1, 3, figsize=(17, 5))
for i, (label, ts) in enumerate(splits):
    Xtr, Xte, ytr, yte = train_test_split(X_s, y_reg, test_size=ts, random_state=42)
    mdl = LinearRegression().fit(Xtr, ytr)
    yhat = mdl.predict(Xte)
    mae = mean_absolute_error(yte, yhat)
    rmse = np.sqrt(mean_squared_error(yte, yhat))
    r2 = r2_score(yte, yhat)
    lr_results.append({'Split': label, 'Train': len(ytr), 'Test': len(yte),
                        'MAE': mae, 'RMSE': rmse, 'R2': r2, '_mdl': mdl})
    print(f"  {label}: Train={len(ytr)} Test={len(yte)} MAE={mae:,.0f} RMSE={rmse:,.0f} R2={r2:.4f}")
    axes[i].scatter(yte, yhat, alpha=0.5, s=18, color='steelblue')
    mn, mx = min(yte.min(), yhat.min()), max(yte.max(), yhat.max())
    axes[i].plot([mn, mx], [mn, mx], 'r--', lw=2, label='Perfect fit')
    axes[i].set_title(f'Split {label}\nR2={r2:.3f}'); axes[i].set_xlabel('Actual'); axes[i].set_ylabel('Predicted'); axes[i].legend()
plt.tight_layout(); plt.savefig('png/B1_regression.png', dpi=150, bbox_inches='tight'); plt.close()

best_idx = max(range(len(lr_results)), key=lambda i: lr_results[i]['R2'])
best_lr = lr_results[best_idx]
coef = pd.Series(best_lr['_mdl'].coef_, index=feature_cols).sort_values()
colours = ['#e74c3c' if c < 0 else '#2980b9' for c in coef]
coef.plot(kind='barh', color=colours)
plt.axvline(0, color='black', lw=0.8)
plt.title(f"B1 - Feature Coefficients ({best_lr['Split']})")
plt.xlabel('Coefficient'); plt.tight_layout()
plt.savefig('png/B1_coefficients.png', dpi=150, bbox_inches='tight'); plt.close()

sample = {col: float(df[col].median()) for col in feature_cols}
sample_pred = best_lr['_mdl'].predict(scaler.transform(pd.DataFrame([sample])))[0]
print(f"  Sample prediction (median property): GBP {sample_pred:,.0f}")
print(f"  Sample inputs: {sample}")

# ── B2: kNN ────────────────────────────────────────────────────────────────────
print("\n=== B2: kNN ===")
Xtr, Xte, ytr, yte = train_test_split(X_s, y_cls, test_size=0.25, random_state=42, stratify=y_cls)
k_range = range(1, 26)
train_acc, test_acc = [], []
for k in k_range:
    m = KNeighborsClassifier(n_neighbors=k).fit(Xtr, ytr)
    train_acc.append(m.score(Xtr, ytr)); test_acc.append(m.score(Xte, yte))
best_k = list(k_range)[np.argmax(test_acc)]
print(f"  Best k={best_k}, test acc={max(test_acc):.4f}")
plt.figure(figsize=(10, 5))
plt.plot(k_range, train_acc, 'b-o', ms=4, label='Train Accuracy')
plt.plot(k_range, test_acc, 'r-o', ms=4, label='Test Accuracy')
plt.axvline(best_k, color='green', lw=2, ls='--', label=f'Best k={best_k}')
plt.xlabel('k'); plt.ylabel('Accuracy'); plt.title('B2 - kNN Hyperparameter Tuning'); plt.legend()
plt.tight_layout(); plt.savefig('png/B2_knn_tuning.png', dpi=150, bbox_inches='tight'); plt.close()

knn = KNeighborsClassifier(n_neighbors=best_k).fit(Xtr, ytr)
yhat_knn = knn.predict(Xte)
knn_acc = accuracy_score(yte, yhat_knn)
knn_prec = precision_score(yte, yhat_knn, average='weighted', zero_division=0)
knn_rec = recall_score(yte, yhat_knn, average='weighted', zero_division=0)
knn_f1 = f1_score(yte, yhat_knn, average='weighted', zero_division=0)
print(f"  Acc={knn_acc:.4f} Prec={knn_prec:.4f} Rec={knn_rec:.4f} F1={knn_f1:.4f}")
print(classification_report(yte, yhat_knn, zero_division=0))
fig, ax = plt.subplots(figsize=(7, 6))
ConfusionMatrixDisplay.from_predictions(yte, yhat_knn, ax=ax, colorbar=False)
ax.set_title(f'B2 - kNN Confusion Matrix (k={best_k})')
plt.tight_layout(); plt.savefig('png/B2_knn_confusion.png', dpi=150, bbox_inches='tight'); plt.close()

# ── B3: SVM ────────────────────────────────────────────────────────────────────
print("\n=== B3: SVM ===")
kernels = {'Linear': SVC(kernel='linear', C=1.0, random_state=42),
           'RBF':    SVC(kernel='rbf', C=1.0, gamma='scale', random_state=42),
           'Poly(3)':SVC(kernel='poly', degree=3, C=1.0, random_state=42)}
svm_res = {}; best_svm_name, best_svm_acc, best_svm_pred = None, 0, None
for name, mdl in kernels.items():
    mdl.fit(Xtr, ytr); pred = mdl.predict(Xte)
    acc = accuracy_score(yte, pred); f1 = f1_score(yte, pred, average='weighted', zero_division=0)
    svm_res[name] = {'Accuracy': acc, 'F1': f1}
    print(f"  {name}: Acc={acc:.4f} F1={f1:.4f}")
    if acc > best_svm_acc:
        best_svm_acc, best_svm_name, best_svm_pred = acc, name, pred
svm_f1 = f1_score(yte, best_svm_pred, average='weighted', zero_division=0)

x = np.arange(2)
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for ax, metric, vals in zip(axes, ['Accuracy', 'F1 (weighted)'], [[knn_acc, best_svm_acc], [knn_f1, svm_f1]]):
    ax.bar(x, vals, color=['steelblue', 'darkorange'])
    ax.set_xticks(x); ax.set_xticklabels([f'kNN (k={best_k})', f'SVM ({best_svm_name})'])
    ax.set_ylim(0, 1.15); ax.set_title(f'B3 - {metric}'); ax.set_ylabel(metric)
    for xi, yi in zip(x, vals): ax.text(xi, yi+0.02, f'{yi:.3f}', ha='center', fontsize=11)
plt.tight_layout(); plt.savefig('png/B3_comparison.png', dpi=150, bbox_inches='tight'); plt.close()
fig2, ax2 = plt.subplots(figsize=(7, 6))
ConfusionMatrixDisplay.from_predictions(yte, best_svm_pred, ax=ax2, colorbar=False)
ax2.set_title(f'B3 - SVM ({best_svm_name}) Confusion Matrix')
plt.tight_layout(); plt.savefig('png/B3_svm_confusion.png', dpi=150, bbox_inches='tight'); plt.close()

# ── B4: CLUSTERING ─────────────────────────────────────────────────────────────
print("\n=== B4: CLUSTERING ===")
inertias, sil = [], []
for k in range(2, 11):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    lbls = km.fit_predict(X_s)
    inertias.append(km.inertia_); sil.append(silhouette_score(X_s, lbls))
optimal_k = list(range(2, 11))[np.argmax(sil)]
print(f"  Optimal k={optimal_k}, silhouette={max(sil):.4f}")
print(f"  All silhouettes: {[round(s,3) for s in sil]}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].plot(range(2,11), inertias, 'b-o', ms=6); axes[0].set_xlabel('k'); axes[0].set_ylabel('Inertia'); axes[0].set_title('Elbow Method')
axes[1].plot(range(2,11), sil, 'r-o', ms=6)
axes[1].axvline(optimal_k, color='green', ls='--', lw=2, label=f'Optimal k={optimal_k}')
axes[1].set_xlabel('k'); axes[1].set_ylabel('Silhouette Score'); axes[1].set_title('Silhouette Scores'); axes[1].legend()
plt.tight_layout(); plt.savefig('png/B4_elbow_silhouette.png', dpi=150, bbox_inches='tight'); plt.close()

km_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
cluster_labels = km_final.fit_predict(X_s)
print(f"  Cluster distribution: {dict(pd.Series(cluster_labels).value_counts().sort_index())}")

pca = PCA(n_components=2, random_state=42); X_pca = pca.fit_transform(X_s)
var = pca.explained_variance_ratio_
print(f"  PCA variance explained: PC1={var[0]:.3f} PC2={var[1]:.3f} Total={var.sum():.3f}")
plt.figure(figsize=(8, 6))
sc = plt.scatter(X_pca[:,0], X_pca[:,1], c=cluster_labels, cmap='tab10', alpha=0.7, s=28)
plt.colorbar(sc, label='Cluster')
plt.xlabel(f'PC1 ({var[0]*100:.1f}% var)'); plt.ylabel(f'PC2 ({var[1]*100:.1f}% var)')
plt.title(f'B4 - PCA Cluster Visualisation (k={optimal_k})')
plt.tight_layout(); plt.savefig('png/B4_pca_clusters.png', dpi=150, bbox_inches='tight'); plt.close()

tsne = TSNE(n_components=2, random_state=42, perplexity=30, max_iter=1000)
X_tsne = tsne.fit_transform(X_s)
plt.figure(figsize=(8, 6))
sc2 = plt.scatter(X_tsne[:,0], X_tsne[:,1], c=cluster_labels, cmap='tab10', alpha=0.7, s=28)
plt.colorbar(sc2, label='Cluster')
plt.xlabel('t-SNE Dim 1'); plt.ylabel('t-SNE Dim 2')
plt.title(f'B4 - t-SNE Cluster Visualisation (k={optimal_k})')
plt.tight_layout(); plt.savefig('png/B4_tsne_clusters.png', dpi=150, bbox_inches='tight'); plt.close()

print("\nAll charts saved.")

# ── C2 WELLBEING ───────────────────────────────────────────────────────────────
np.random.seed(7)
EMPLOYEES = [f'Emp {i+1:02d}' for i in range(10)]
DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
EXPRS = ['Happy', 'Neutral', 'Sad', 'Angry', 'Frightful', 'Surprised']
STRESS = {'Happy': 0.0, 'Neutral': 0.2, 'Sad': 0.6, 'Angry': 0.9, 'Frightful': 0.8, 'Surprised': 0.3}
emp_data = {}
for emp in EMPLOYEES:
    daily = np.random.choice(EXPRS, len(DAYS), p=[0.35, 0.30, 0.15, 0.08, 0.07, 0.05])
    emp_data[emp] = {'emotions': daily, 'stress': [STRESS[e] for e in daily]}
stress_mat = np.array([emp_data[e]['stress'] for e in EMPLOYEES])
avg_stress = stress_mat.mean(axis=1)
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
sns.heatmap(stress_mat, ax=axes[0], xticklabels=DAYS, yticklabels=EMPLOYEES,
            cmap='RdYlGn_r', vmin=0, vmax=1, annot=True, fmt='.1f', linewidths=0.4)
axes[0].set_title('C2 - Weekly Stress Heatmap'); axes[0].set_xlabel('Day')
colours = ['#e74c3c' if s > 0.5 else '#2ecc71' for s in avg_stress]
axes[1].barh(EMPLOYEES, avg_stress, color=colours)
axes[1].axvline(0.5, color='red', ls='--', lw=1.5, label='Alert threshold')
axes[1].set_xlabel('Avg Stress Score (0-1)'); axes[1].set_title('C2 - Average Weekly Stress'); axes[1].legend()
plt.tight_layout(); plt.savefig('png/C2_wellbeing_monitor.png', dpi=150, bbox_inches='tight'); plt.close()
print("C2 saved.")

# input validation
def validate_dataset(df):
    assert df.shape[0] > 0, "Dataset is empty"
    assert 'House_Price' in df.columns, "Missing target column"
    return True
