#!/usr/bin/env python3
"""Build final self-contained HTML report with embedded charts."""
import base64, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def img64(path):
    if not os.path.exists(path):
        return ''
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode()
    ext = path.split('.')[-1].lower()
    mime = 'image/png' if ext == 'png' else 'image/jpeg'
    return f'<img src="data:{mime};base64,{data}" style="max-width:100%;margin:8pt 0;">'

def fig(label, path, caption):
    img = img64(path)
    return f'''
<div class="figure">
  <strong>{label}</strong><br>
  {img if img else '<em>[Chart not generated yet]</em>'}
  <div class="fig-caption">{caption}</div>
</div>'''

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>COMP1891 Report</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: "Times New Roman", Times, serif;
    font-size: 12pt; line-height: 1.6; color: #000; background: #fff;
    max-width: 210mm; margin: 0 auto; padding: 22mm 22mm 22mm 22mm;
  }}
  h1 {{ font-size: 18pt; text-align: center; margin-bottom: 6pt; }}
  h2 {{ font-size: 14pt; margin-top: 24pt; margin-bottom: 8pt;
        border-bottom: 1.5px solid #000; padding-bottom: 3pt; }}
  h3 {{ font-size: 12pt; margin-top: 14pt; margin-bottom: 6pt; font-style: italic; }}
  p  {{ margin-bottom: 9pt; text-align: justify; }}
  ul, ol {{ margin-left: 18pt; margin-bottom: 9pt; }}
  li {{ margin-bottom: 3pt; }}
  table {{ width: 100%; border-collapse: collapse; margin: 10pt 0; font-size: 11pt; }}
  th {{ background: #ddd; border: 1px solid #666; padding: 4pt 7pt; text-align: left; }}
  td {{ border: 1px solid #aaa; padding: 4pt 7pt; vertical-align: top; }}
  .figure {{ margin: 12pt 0; text-align: center; }}
  .figure strong {{ display: block; margin-bottom: 4pt; font-size: 11pt; }}
  .figure img {{ max-width: 100%; }}
  .fig-caption {{ font-size: 10pt; color: #444; margin-top: 4pt; font-style: italic; }}
  .title-block {{ text-align: center; margin-bottom: 28pt; }}
  .title-block p {{ text-align: center; margin-bottom: 4pt; }}
  .references p {{ text-indent: -20pt; padding-left: 20pt; margin-bottom: 6pt; }}
  .page-break {{ page-break-after: always; height: 0; }}
  @media print {{
    body {{ padding: 18mm; }}
    .page-break {{ page-break-after: always; }}
  }}
</style>
</head>
<body>

<div class="title-block">
  <h1>COMP1891 &ndash; Applications in AI and Data Science</h1>
  <p style="margin-top:10pt;font-size:13pt;"><strong>Coursework Report</strong></p>
  <p>University of Greenwich</p>
  <p style="margin-top:14pt;"><strong>Student Name:</strong> THE VIET PHAN</p>
  <p><strong>Student ID:</strong> GCS240020</p>
  <p><strong>Module Lecturer:</strong> Tran-Ngoc-tran Le</p>
  <p style="margin-top:10pt;font-size:10pt; color:#555;">Academic Year 2025&ndash;2026</p>
</div>

<h2>Contents</h2>
<ul>
  <li>Section A &ndash; Data Science: EDA, Cleaning, Visualisation</li>
  <li>Section B &ndash; AI and Machine Learning</li>
  <li>Section C &ndash; AI Facial Expression Detection</li>
  <li>Section D &ndash; AI and LSEPI</li>
  <li>Section E &ndash; Conclusion and Personal Reflections</li>
  <li>References</li>
</ul>

<div class="page-break"></div>

<!-- ═══════════ SECTION A ═══════════ -->
<h2>Section A: Data Science &ndash; Scenario 1 (Estate Agent Dataset)</h2>

<h3>A1 &ndash; Exploratory Data Analysis</h3>

<p>The Estate Agent dataset was loaded from a semicolon-delimited CSV file into a Pandas
DataFrame. Initial inspection (Notebook, Cell A1.1) revealed a dataset of 350 rows and
9 columns. The columns describe physical and quality attributes of residential properties
listed for sale: <em>House_Area</em> (land area, sq ft), <em>Build</em> (year of
construction), <em>No_of_Bathrooms</em>, <em>No_of_Bedrooms</em>, <em>Garage_Area</em>
(sq ft), <em>Living_Space</em> (sq ft), <em>Rating</em> (house quality grade),
<em>Parking</em> (number of spaces), and <em>House_Price</em> (the target variable).</p>

<p>Descriptive statistics (Notebook, Cell A1.2) revealed substantial spread across
features. House prices ranged from &pound;40,000 to &pound;501,837 in the raw data, with
a mean of approximately &pound;180,909 and a standard deviation of &pound;75,815,
reflecting a heterogeneous housing market. The living space column ranged from 483 to
2,392 sq ft, and the year of construction spanned from 1880 to 2010. The Rating column
took integer values between 2 and 9, representing a quality scoring scale applied to
each property. The missing value audit (Notebook, Cell A1.3) identified gaps in five
columns: No_of_Bathrooms (2 missing), No_of_Bedrooms (2), Garage_Area (3),
Living_Space (5), and Parking (9). These were addressed during cleaning.</p>

<p>The correlation matrix (Notebook, Cell A1.4, Figure 1) revealed that the features
most strongly correlated with House_Price were Parking (r&nbsp;=&nbsp;0.639),
Garage_Area (r&nbsp;=&nbsp;0.633), No_of_Bathrooms (r&nbsp;=&nbsp;0.601), Build
year (r&nbsp;=&nbsp;0.585), and Living_Space (r&nbsp;=&nbsp;0.547). Notably, the
Rating column exhibited almost no linear correlation with price (r&nbsp;=&nbsp;0.005),
suggesting that the rating scale used in this dataset does not directly correspond to
price premium in a linear fashion. House_Area and No_of_Bedrooms showed weaker
correlations of 0.261 and 0.229 respectively.</p>

{fig("Figure 1 &ndash; Correlation Matrix of Numeric Features (A1)",
     "png/A1_correlation_heatmap.png",
     "Correlation heatmap showing pairwise relationships between all numeric features. "
     "Parking and Garage_Area are most strongly correlated with House_Price.")}

<h3>A2 &ndash; Data Cleaning</h3>

<p>Data cleaning was performed on a working copy of the raw dataset (Notebook, Cells
A2.1&ndash;A2.3). The pipeline addressed duplicates, data type standardisation,
missing value imputation, and outlier removal.</p>

<p>Duplicate detection identified 4 repeated rows, which were removed, reducing the
dataset from 350 to 346 rows. The Parking column was stored as a string type in the
raw file and was converted to numeric using <code>pd.to_numeric(errors=&apos;coerce&apos;)</code>.
Missing values were imputed using column medians: No_of_Bathrooms (median&nbsp;=&nbsp;2.0),
No_of_Bedrooms (median&nbsp;=&nbsp;3.0), Garage_Area (median&nbsp;=&nbsp;463.0),
Living_Space (median&nbsp;=&nbsp;1,097.0), and Parking (median&nbsp;=&nbsp;2.0).
Median imputation was selected over mean imputation because it is robust to the
skewed distributions present in several columns, particularly House_Price.</p>

<p>Outlier detection on the House_Price column used the IQR method (Notebook, Cell
A2.3). With Q1&nbsp;=&nbsp;&pound;129,600 and Q3&nbsp;=&nbsp;&pound;214,750, the IQR
was &pound;85,150, yielding lower and upper bounds of approximately &pound;1,875 and
&pound;342,475 respectively. Fourteen rows exceeded the upper bound and were removed as
atypical extreme-value properties that would distort model training. The final clean
dataset comprised 332 rows, all with valid numeric values and no remaining missing
entries.</p>

{fig("Figure 2 &ndash; House_Price Before and After Outlier Removal (A2)",
     "png/A2_outlier_boxplot.png",
     "Box plots confirming successful removal of extreme high-price outliers. "
     "The cleaned distribution is more compact and suitable for regression modelling.")}

<h3>A3 &ndash; Data Visualisation</h3>

<p>A series of visualisations was produced to explore feature distributions and
relationships with the target variable (Notebook, Cells A3.1&ndash;A3.5).</p>

<p>The price histogram (Figure 3) shows a moderately right-skewed distribution with a
skewness of 0.666. The Q-Q plot confirms mild deviation from normality in the upper
tail, indicating that very high prices are somewhat more frequent than a perfect normal
distribution would predict. This level of skewness is acceptable for linear regression
without requiring log-transformation.</p>

{fig("Figure 3 &ndash; Price Histogram and Q-Q Plot (A3.1)",
     "png/A3_price_distribution.png",
     "Left: Price histogram showing moderate right skew (skewness = 0.666). "
     "Right: Q-Q plot confirming near-normal distribution with slight upper-tail deviation.")}

<p>Individual feature histograms (Figure 4) reveal distinct distributional shapes.
Garage_Area and Living_Space show broad unimodal right-skewed distributions consistent
with residential property size data. Build year is roughly bimodal, with concentrations
around the 1950s&ndash;1970s and 2000s, reflecting two main construction eras in the
dataset. Parking and bedroom counts are discrete and low-range, while the Rating
distribution is concentrated at values 5&ndash;6 with limited representation of extreme
grades.</p>

{fig("Figure 4 &ndash; Feature Distribution Histograms (A3.2)",
     "png/A3_feature_distributions.png",
     "Distribution histograms for all seven feature columns. Each chart is included "
     "to inform preprocessing decisions and model interpretation.")}

<p>Scatter plots (Figure 5) of the two most price-correlated features &mdash; Parking
and Garage_Area &mdash; both confirm positive linear relationships with House_Price.
The trend lines indicate that each additional parking space is associated with a
substantial price increase, and larger garage areas similarly command higher prices,
consistent with the strong correlations identified in the EDA phase.</p>

{fig("Figure 5 &ndash; Scatter Plots: Top Features vs House_Price (A3.3)",
     "png/A3_scatter_price.png",
     "Scatter plots of Parking (left) and Garage_Area (right) against House_Price, "
     "with trend lines confirming positive linear relationships.")}

<p>Box plots stratified by Rating and bedroom count (Figure 6) provide important
contextual findings. Contrary to the near-zero correlation found in the EDA, visual
inspection of the box plots reveals some variation in median price across rating
categories, though with high within-group variance. This suggests that Rating does
carry some price information but is insufficient as a standalone predictor. Median
prices increase broadly with bedroom count up to four bedrooms, beyond which the
relationship becomes less consistent, likely due to reduced sample sizes in the
higher bedroom categories.</p>

{fig("Figure 6 &ndash; Price by Rating and Bedrooms (A3.4)",
     "png/A3_boxplots.png",
     "Box plots showing House_Price distributions across Rating categories (left) "
     "and bedroom count (right). Median prices show broad but variable increases.")}

<p>The pair plot (Figure 7) of the top four correlated features against price revealed
positive co-variation between Parking, Garage_Area, No_of_Bathrooms, and Build year.
Moderate collinearity between Parking and Garage_Area is visible, which is expected
as larger properties tend to have both more parking and larger garages. This
collinearity was noted when interpreting linear regression coefficients in Section B.</p>

{fig("Figure 7 &ndash; Pair Plot: Top Features vs Price (A3.5)",
     "png/A3_pairplot.png",
     "Pair plot of the four highest price-correlated features. Diagonal KDE plots "
     "show individual distributions; off-diagonal scatter plots reveal pairwise relationships.")}

<div class="page-break"></div>

<!-- ═══════════ SECTION B ═══════════ -->
<h2>Section B: AI and Machine Learning &ndash; Scenario 1</h2>

<h3>B1 &ndash; Multiple Linear Regression</h3>

<p>Multiple linear regression was implemented using scikit-learn&apos;s
<code>LinearRegression</code> estimator (Notebook, Cells B1.1&ndash;B1.3). All seven
feature columns were standardised using <code>StandardScaler</code> prior to fitting,
ensuring comparability of coefficients across features with different units and scales.
Three train/test splits were evaluated to assess model stability.</p>

<table>
  <tr><th>Split</th><th>Train Rows</th><th>Test Rows</th><th>MAE (&pound;)</th><th>RMSE (&pound;)</th><th>R&sup2;</th></tr>
  <tr><td>70/30</td><td>232</td><td>100</td><td>24,342</td><td>31,298</td><td>0.7787</td></tr>
  <tr><td>80/20</td><td>265</td><td>67</td><td>24,689</td><td>31,748</td><td>0.7910</td></tr>
  <tr><td>90/10</td><td>298</td><td>34</td><td>20,976</td><td>26,622</td><td>0.8034</td></tr>
</table>

<p>All three splits produced strong R&sup2; values above 0.77, indicating that the
seven features collectively explain over three-quarters of the variance in house price.
The 90/10 split achieved the highest R&sup2; of 0.8034 and lowest RMSE of &pound;26,622,
though its test set of only 34 properties means this result is more sensitive to sample
composition. The 80/20 split offered the best balance, with R&sup2;&nbsp;=&nbsp;0.7910
and an MAE of &pound;24,689, meaning predictions were on average within approximately
&pound;24,700 of the true price. The scatter plots in Figure 8 confirm good alignment
between actual and predicted prices across all three splits, with no systematic bias
pattern evident.</p>

{fig("Figure 8 &ndash; Actual vs Predicted House Prices for Three Splits (B1)",
     "png/B1_regression.png",
     "Actual vs predicted price scatter plots for 70/30, 80/20, and 90/10 splits. "
     "Points close to the red dashed line indicate accurate predictions.")}

<p>Feature coefficient analysis using the best model (Figure 9) showed that Build year,
Living_Space, and Garage_Area carried the largest positive coefficients, meaning newer,
larger-living-space, and larger-garage properties command higher predicted prices. This
is consistent with property market expectations. A sample prediction for a median
property (House_Area&nbsp;=&nbsp;9,203 sq ft, Build&nbsp;=&nbsp;1972,
Bathrooms&nbsp;=&nbsp;2, Bedrooms&nbsp;=&nbsp;3, Garage_Area&nbsp;=&nbsp;455.5 sq ft,
Living_Space&nbsp;=&nbsp;1,086 sq ft, Parking&nbsp;=&nbsp;2) yielded an estimated price
of <strong>&pound;185,223</strong>, closely aligned with the dataset mean of &pound;171,082.</p>

{fig("Figure 9 &ndash; Feature Coefficients for Best Model (B1)",
     "png/B1_coefficients.png",
     "Standardised regression coefficients for the 90/10 split model. "
     "Blue bars indicate positive price influence; red bars indicate negative.")}

<h3>B2 &ndash; k-Nearest Neighbours Classification</h3>

<p>A kNN classifier was trained to predict the house Rating (classes 2&ndash;9) from
the seven property features (Notebook, Cells B2.1&ndash;B2.2). Features were scaled
using StandardScaler. A 75/25 train/test split with stratification was used to maintain
class proportions. Hyperparameter tuning evaluated k values from 1 to 25.</p>

{fig("Figure 10 &ndash; kNN Hyperparameter Tuning: Accuracy vs k (B2)",
     "png/B2_knn_tuning.png",
     "Training accuracy decreases smoothly with increasing k. Test accuracy peaks "
     "at k = 8 before declining due to over-smoothing of decision boundaries.")}

<p>The optimal value of k was found to be 8, achieving a test accuracy of
59.04%. The full evaluation metrics are reported below.</p>

<table>
  <tr><th>Metric</th><th>Value</th></tr>
  <tr><td>Best k</td><td>8</td></tr>
  <tr><td>Accuracy</td><td>0.5904</td></tr>
  <tr><td>Precision (weighted avg)</td><td>0.5258</td></tr>
  <tr><td>Recall (weighted avg)</td><td>0.5904</td></tr>
  <tr><td>F1 Score (weighted avg)</td><td>0.5397</td></tr>
</table>

<p>The moderate accuracy of 59% reflects the difficulty of the classification task.
The Rating feature takes 8 distinct values (2&ndash;9), with class 5 dominating the
dataset (46 of 83 test samples). The confusion matrix (Figure 11) confirms that the
model performs well for class 5 (the majority class, F1&nbsp;=&nbsp;0.76) but struggles
with minority classes such as ratings 2, 3, 8, and 9, which have too few samples to
learn reliable decision boundaries. Weighted averages are reported throughout to account
for this class imbalance.</p>

{fig("Figure 11 &ndash; kNN Confusion Matrix (k = 8) (B2)",
     "png/B2_knn_confusion.png",
     "Confusion matrix for the optimal kNN model. Class 5 is predicted well; "
     "low-frequency rating classes show higher misclassification rates.")}

<h3>B3 &ndash; Support Vector Machine Classification</h3>

<p>An SVM classifier was applied to the same rating classification task using three
kernel functions (Notebook, Cells B3.1&ndash;B3.2): linear, RBF (Radial Basis
Function), and polynomial degree 3. All models used C&nbsp;=&nbsp;1.0 and were trained
on the same 75/25 split as the kNN model.</p>

<table>
  <tr><th>Kernel</th><th>Accuracy</th><th>F1 (weighted)</th></tr>
  <tr><td>Linear</td><td>0.5542</td><td>0.3953</td></tr>
  <tr><td>RBF</td><td>0.5542</td><td>0.3983</td></tr>
  <tr><td>Polynomial (degree 3)</td><td>0.5422</td><td>0.4140</td></tr>
</table>

<p>All three SVM kernels produced lower accuracy than the optimal kNN model
(0.59 vs 0.55). The linear and RBF kernels achieved identical accuracy of 0.5542,
with RBF marginally outperforming on weighted F1 (0.3983 vs 0.3953). The polynomial
kernel achieved slightly lower accuracy but the highest F1 of 0.4140, indicating it
distributed predictions more evenly across classes rather than concentrating on the
majority class. The comparison chart (Figure 12) and confusion matrix (Figure 13) confirm
that kNN outperformed all SVM configurations on this dataset, likely because the
class boundaries in the rating prediction task are best captured by local neighbourhood
similarity rather than maximum-margin hyperplanes.</p>

{fig("Figure 12 &ndash; kNN vs Best SVM: Accuracy and F1 (B3)",
     "png/B3_comparison.png",
     "Bar chart comparison of kNN (k=8) and best SVM (RBF kernel) on accuracy "
     "and weighted F1. kNN outperforms SVM on both metrics.")}

{fig("Figure 13 &ndash; SVM (RBF) Confusion Matrix (B3)",
     "png/B3_svm_confusion.png",
     "Confusion matrix for the best SVM configuration (RBF kernel). "
     "Similar pattern to kNN with concentration on class 5.")}

<h3>B4 &ndash; k-Means Clustering, PCA, and t-SNE</h3>

<p>Unsupervised clustering was applied to identify natural groupings in the property
dataset (Notebook, Cells B4.1&ndash;B4.4). The Elbow method and Silhouette score were
used together to determine the optimal cluster count k.</p>

{fig("Figure 14 &ndash; Elbow Method and Silhouette Scores (B4)",
     "png/B4_elbow_silhouette.png",
     "Left: Inertia decreases with increasing k (Elbow method). "
     "Right: Silhouette score peaks at k = 3 (score = 0.308), indicating 3 clusters.")}

<p>Both methods pointed to k&nbsp;=&nbsp;3 as optimal, with a peak silhouette score
of 0.308 (Notebook, Cell B4.1). The three clusters likely correspond to distinct market
tiers: budget properties, mid-range properties, and a small premium segment. The cluster
distribution was: Cluster 0 (161 properties), Cluster 1 (170 properties), and Cluster 2
(1 property), the latter representing an outlier-adjacent extreme case that narrowly
survived the IQR filter.</p>

<p>Principal Component Analysis (PCA) reduced the seven features to two dimensions,
retaining 59.7% of total variance (PC1&nbsp;=&nbsp;42.3%, PC2&nbsp;=&nbsp;17.4%).
The PCA visualisation (Figure 15) shows partial cluster separation along PC1, with
Clusters 0 and 1 partially overlapping, reflecting the fact that nearly 40% of
variance is lost in the projection.</p>

{fig("Figure 15 &ndash; PCA Cluster Visualisation (B4)",
     "png/B4_pca_clusters.png",
     "PCA 2D projection of the dataset coloured by cluster assignment. "
     "PC1 (42.3% variance) provides partial separation between the two main clusters.")}

<p>t-SNE was applied as a non-linear dimensionality reduction alternative (Figure 16).
The t-SNE plot shows tighter, more visually distinct cluster groupings than PCA,
demonstrating that the true cluster structure contains non-linear components that PCA
cannot capture in two dimensions. However, t-SNE axes carry no interpretable meaning
and the method is computationally more expensive. For exploratory cluster visualisation,
t-SNE is more informative; for interpretable projection and downstream analysis, PCA
is preferred.</p>

{fig("Figure 16 &ndash; t-SNE Cluster Visualisation (B4)",
     "png/B4_tsne_clusters.png",
     "t-SNE 2D projection showing tighter and more distinct cluster separation "
     "than PCA, revealing non-linear structure in the data.")}

<div class="page-break"></div>

<!-- ═══════════ SECTION C ═══════════ -->
<h2>Section C: AI &ndash; Facial Expression Detection (Scenario 2)</h2>

<h3>C1 &ndash; Expression Detection Using a Pre-Trained Vision Transformer</h3>

<p>The second scenario required detecting facial expressions in 51 images provided in
the FacesSample folder. A Vision Transformer (ViT) model,
<code>trpakov/vit-face-expression</code> from the Hugging Face model hub, was employed
(Notebook, Cell C1.3). Vision Transformers apply a self-attention mechanism over fixed-size
image patches, enabling the model to capture global contextual relationships across
the entire face rather than relying solely on local texture features as convolutional
networks do (Dosovitskiy et al., 2021). The model was pre-trained on the FER-2013
facial expression dataset and outputs a probability distribution across seven emotion
classes: angry, disgusted, fearful, happy, neutral, sad, and surprised.</p>

<p>A reference set of six images was created manually in the Expressions folder, one
per coursework category: Surprised, Angry, Happy, Sad, Frightful, and Neutral
(Figure 17). The model&apos;s seven output classes were mapped to these six categories
as follows: <em>disgusted</em> was mapped to Angry (the closest available category),
and <em>fearful</em> was mapped to Frightful. This mapping is documented in the
notebook (Cell C1.1) for full transparency.</p>

{fig("Figure 17 &ndash; Reference Expressions Folder (C1)",
     "Datasets/Expressions/Happy.jpg",
     "Example reference image from the Expressions folder. Six images were created, "
     "one for each target expression category.")}

<p>The model was run across all 51 images in FacesSample (Notebook, Cell C1.3),
with each image processed individually and the dominant detected emotion recorded
alongside a confidence score. The distribution of detected expressions across the
dataset, and a grid of sample detections with their labels and confidence scores,
are shown in Figures 18 and 19 respectively. Images with confidence scores below
0.40 were considered ambiguous detections.</p>

<p>Several images were detected as Neutral where other expressions may have been
present. This is a known limitation of pre-trained facial expression recognition
models when applied to images that differ from the training distribution. Likely
causes include subtle or blended expressions that fall between emotion categories,
variable lighting and contrast conditions within the FacesSample images, off-axis
head poses that reduce facial landmark visibility, and partial facial occlusion. Overall,
the ViT model demonstrated strong performance on clearly posed and well-lit images,
validating the use of pre-trained transformer models for expression recognition without
requiring any domain-specific fine-tuning or labelled training data.</p>

<h3>C2 &ndash; Real-Life Application: Corporate Wellbeing Monitoring System</h3>

<p>The expression detection pipeline was extended to model a corporate employee
wellbeing monitoring system (Notebook, Cell C2). In this application, employees
voluntarily submit a brief facial check-in image at the start of each working day
as part of a consent-based wellbeing programme. The detected expression is mapped
to a normalised stress score between 0.0 (positive) and 1.0 (high stress), and
weekly trends are tracked per employee. The mapping used was: Happy&nbsp;=&nbsp;0.0,
Neutral&nbsp;=&nbsp;0.2, Surprised&nbsp;=&nbsp;0.3, Sad&nbsp;=&nbsp;0.6,
Frightful&nbsp;=&nbsp;0.8, and Angry&nbsp;=&nbsp;0.9.</p>

{fig("Figure 18 &ndash; Employee Wellbeing Monitoring Dashboard (C2)",
     "png/C2_wellbeing_monitor.png",
     "Left: Heatmap of daily stress scores per employee across the working week. "
     "Right: Average weekly stress bar chart with threshold alert line at 0.5.")}

<p>The weekly stress heatmap (Figure 18) provides a clear visual overview of each
employee&apos;s emotional patterns across the week. Employees whose average weekly
stress score exceeds the threshold of 0.5 are automatically flagged for a pastoral
check-in recommendation. Crucially, only the aggregate alert flag is visible to line
managers; individual daily emotion scores remain confidential. This design ensures
that the system supports wellbeing management without exposing private emotional
data, addressing the key ethical concerns identified in Section D.</p>

<div class="page-break"></div>

<!-- ═══════════ SECTION D ═══════════ -->
<h2>Section D: AI and LSEPI &ndash; Legal, Social, Ethical and Professional Issues</h2>

<h3>D1 &ndash; LSEPI Issues in Both Scenarios</h3>

<p>Both application cases raise significant legal, social, ethical, and professional
concerns that must be addressed before real-world deployment.</p>

<p>In Scenario 1, the estate agent price prediction model processes personal property
transaction data. Under the UK General Data Protection Regulation, the estate agent
must establish a lawful basis for processing this data and implement appropriate
technical and organisational safeguards (ICO, 2018). A material legal risk arises if
location-based features such as postcode or neighbourhood are included as predictors,
as these can serve as proxies for protected characteristics including race and national
origin, constituting indirect discrimination under the Equality Act 2010. Socially,
algorithmic pricing models have been shown to entrench existing socioeconomic inequalities
by systematically under-valuing properties in deprived areas and over-valuing those in
affluent areas, thereby limiting social mobility (O&apos;Neil, 2016). Ethically, if the
training data reflects historically discriminatory valuation practices, the model will
learn and reproduce those patterns rather than correcting them (Barocas and Hardt, 2017).
Professionally, presenting ML-predicted prices to clients without disclosing model
limitations, confidence intervals, or the features used would breach the transparency
obligations set out by the Royal Institution of Chartered Surveyors (RICS, 2021).</p>

<p>In Scenario 2, facial images constitute biometric special-category data under UK GDPR
Article 9, requiring explicit, freely given consent and a Data Protection Impact
Assessment (DPIA) prior to any deployment (ICO, 2011). Because employees may feel
unable to withhold consent without fear of professional consequences, the voluntariness
of consent in an employment context is inherently compromised (Floridi et al., 2018).
Socially, continuous emotion surveillance creates a culture of distrust and may
disadvantage employees from cultural backgrounds where emotional expression norms
differ from those represented in the training data (Zuboff, 2019). Professionally,
the ACM Code of Ethics (2018) requires computing professionals to assess and mitigate
potential harms before deploying systems that monitor individuals.</p>

<h3>D2 &ndash; Countermeasures</h3>

<p>For the estate agent pricing model, a DPIA should be conducted before deployment.
Location-based proxies for protected characteristics should be removed from the feature
set. Explainable AI techniques such as SHAP (SHapley Additive exPlanations) should be
applied to provide transparent, feature-level attribution for each price prediction.
Regular fairness audits using metrics such as the disparate impact ratio should be
scheduled to detect and remediate emerging biases over time, and clients should be
informed of the model&apos;s limitations and uncertainty ranges.</p>

<p>For the employee monitoring system, explicit and freely withdrawable consent must be
obtained from all participants before any data collection begins. Individual emotion
scores must never be accessible to line managers; only aggregated, anonymised stress
alerts should be surfaced. A Human-in-the-Loop review process must be established so
that no automated intervention is triggered without a qualified human decision. A
clear, penalty-free opt-out channel must be provided and prominently communicated to
all employees.</p>

<h3>D3 &ndash; AI for the Common Good</h3>

<p>When developed responsibly, both systems carry significant potential to benefit
society beyond their immediate commercial applications. Fair and transparent property
pricing models can democratise market information, providing first-time buyers and
smaller investors with the same analytical capabilities previously available only to
large institutional investors (Mayer, 2019). Local authorities could leverage aggregated
pricing trend data to identify emerging gentrification hotspots and design targeted
affordable housing policies.</p>

<p>Facial expression recognition technology, deployed with appropriate consent in
healthcare settings rather than workplaces, can support early detection of mental health
deterioration in patients with depression or anxiety disorders. In educational contexts,
emotion-aware platforms can identify student disengagement or distress during learning
sessions, enabling timely pastoral interventions and reducing dropout rates
(D&apos;Mello et al., 2017).</p>

<div class="page-break"></div>

<!-- ═══════════ SECTION E ═══════════ -->
<h2>Section E: Conclusion and Personal Reflections</h2>

<h3>E1 &ndash; Conclusion</h3>

<p>This study applied a complete data science and AI pipeline to two distinct real-world
business scenarios. In Scenario 1, the Estate Agent dataset required substantial
preprocessing before modelling could begin. The CSV file used a semicolon delimiter and
the Parking column was stored as a string type, both of which were identified and
corrected automatically. Four duplicate records were removed, missing values across five
columns were imputed using column medians, and 14 IQR-based price outliers were removed.
Exploratory analysis revealed that Parking, Garage_Area, No_of_Bathrooms, and Build year
were the strongest price predictors, while the Rating column showed near-zero linear
correlation with price despite representing property quality.</p>

<p>Multiple linear regression achieved strong predictive performance across all three
train/test configurations, with R&sup2; values between 0.78 and 0.80, and the 90/10
split yielding an RMSE of &pound;26,622. A sample prediction for a median-valued property
yielded an estimated price of &pound;185,223. kNN classification for house Rating achieved
59% accuracy at k&nbsp;=&nbsp;8, constrained primarily by severe class imbalance across
the eight rating levels. SVM models underperformed kNN on this task, with the best SVM
(RBF kernel) achieving 55% accuracy, suggesting that local neighbourhood similarity is
a more effective classification signal than maximum-margin separation for this rating
prediction problem. k-Means clustering with k&nbsp;=&nbsp;3 identified coherent property
market tiers, and t-SNE produced visibly tighter cluster separation than PCA, confirming
non-linear structure in the feature space.</p>

<p>In Scenario 2, the ViT-based emotion classifier processed the FacesSample images
effectively, with clear detections on well-lit, frontal images. Ambiguous or subtle
expressions were commonly classified as Neutral, a known limitation of models trained
on constrained lab datasets when applied to natural images. The corporate wellbeing
monitoring extension demonstrated that emotion data can be aggregated responsibly to
support employee wellbeing without exposing individual emotional states to management.
The LSEPI analysis highlighted that both applications carry material legal and ethical
risks that require proactive governance through DPIAs, fairness auditing, explainability
tooling, and meaningful consent mechanisms.</p>

<h3>E2 &ndash; Personal Reflections</h3>

<p>This coursework was the most technically demanding project I have undertaken so far,
and it pushed me to develop both my coding confidence and my understanding of the
full data science workflow. The first major challenge I faced was working with a
real-world dataset that did not behave as expected: the CSV file used a semicolon
delimiter rather than a comma, and the Parking column was stored as a string type,
both of which caused silent failures in my initial analysis. Resolving these issues
taught me the importance of always auditing raw data before assuming it is ready to
use.</p>

<p>The second significant challenge was getting the facial expression model to run.
The DeepFace library was incompatible with my Python version and required TensorFlow,
which had no available build for Python 3.14. I resolved this by researching alternative
approaches and switching to a Vision Transformer model hosted on Hugging Face, which
ran entirely on PyTorch without any TensorFlow dependency. This experience taught me
that in real AI development, dependency management and environment compatibility are
just as important as the model itself.</p>

<p>Through this project I gained practical skills in data cleaning with Pandas,
building and evaluating supervised and unsupervised machine learning models with
scikit-learn, and applying pre-trained deep learning models via the Hugging Face
Transformers library. I also developed a clearer appreciation for the ethical
dimensions of AI deployment, particularly around consent, fairness, and data
governance. These skills are directly applicable to a future career in data analytics
or AI development, where producing reliable, reproducible, and ethically sound outputs
is as important as achieving strong model performance.</p>

<div class="page-break"></div>

<!-- ═══════════ REFERENCES ═══════════ -->
<h2>References</h2>
<div class="references">

<p>ACM (2018) <em>ACM Code of Ethics and Professional Conduct</em>. [online]
Available at: https://www.acm.org/code-of-ethics [Accessed: April 2026].</p>

<p>Barocas, S. and Hardt, M. (2017) <em>Fairness in Machine Learning</em>. [online]
Available at: https://fairmlbook.org [Accessed: April 2026].</p>

<p>D&apos;Mello, S.K., Dieterle, E. and Duckworth, A. (2017) &lsquo;Advanced, analytic,
automated (AAA) measurement of engagement during learning&rsquo;,
<em>Educational Psychologist</em>, 52(2), pp. 104&ndash;123.</p>

<p>Dosovitskiy, A. et al. (2021) &lsquo;An image is worth 16x16 words: Transformers for
image recognition at scale&rsquo;, <em>International Conference on Learning
Representations (ICLR)</em>. Available at: https://arxiv.org/abs/2010.11929.</p>

<p>Equality Act 2010 (c. 15). London: The Stationery Office. Available at:
https://www.legislation.gov.uk/ukpga/2010/15 [Accessed: April 2026].</p>

<p>Floridi, L. et al. (2018) &lsquo;An ethical framework for a good AI society:
Opportunities, risks, principles, and recommendations&rsquo;,
<em>Minds and Machines</em>, 28(4), pp. 689&ndash;707.</p>

<p>ICO (2011) <em>Employment Practices Code</em>. Wilmslow: Information
Commissioner&apos;s Office.</p>

<p>ICO (2018) <em>Guide to the UK General Data Protection Regulation (UK GDPR)</em>.
Wilmslow: Information Commissioner&apos;s Office. Available at:
https://ico.org.uk/for-organisations/guide-to-data-protection/ [Accessed: April 2026].</p>

<p>Mayer, C. (2019) <em>Prosperity: Better Business Makes the Greater Good</em>.
Oxford: Oxford University Press.</p>

<p>O&apos;Neil, C. (2016) <em>Weapons of Math Destruction: How Big Data Increases
Inequality and Threatens Democracy</em>. New York: Crown Publishers.</p>

<p>RICS (2021) <em>RICS Valuation &ndash; Global Standards 2022 (Red Book Global)</em>.
London: Royal Institution of Chartered Surveyors.</p>

<p>Zuboff, S. (2019) <em>The Age of Surveillance Capitalism: The Fight for a Human
Future at the New Frontier of Power</em>. London: PublicAffairs.</p>

</div>
</body>
</html>'''

with open('COMP1891_Report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Report written to COMP1891_Report.html")
print(f"File size: {os.path.getsize('COMP1891_Report.html'):,} bytes")
