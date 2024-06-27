import os

BASE_DIR = os.getcwd()
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'data', 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}
linkedin_domain = (r'https?://(www\.)?linkedin\.com/[^\s<>"]')
github_domain = (r'https?://(www\.)?github\.com/[^\s<>"]')

required_sections = ['PROFILE SUMMARY','ACADEMIC PROFILE','TECHNICAL SKILLS','CERTIFICATIONS','PROJECTS']

basic_informations = ["name", "contact_number", "email", "linkedin_urls", "github_urls"]

data_science_skills = ['queries', 'beautifulsoup', 'ms excel', 'mathematics', 'selenium', 
                       'html', 'analytical skills', 'statsmodels','ai', 'improvement', 
                       'analyze', 'metrics', 'forecasting', 'analytics', 'analytical', 
                       'mysql', 'postgresql', 'database', 'writing', 'excel','regulations', 
                       'algorithms', 'scipy', 'opencv', 'reports',  'eda', 'jupyter', 
                       'presentations', 'modeling', 'audit', 'technical skills', 
                       'schedule', 'nltk', 'iso', 'xgboost', 'segmentation', 'github', 
                       'seaborn', 'keras', 'distribution', 'investigation', 'tableau',
                       'probability', 'analysis', 'r', 'technical', 'programming', 
                       'web scraping', 'research', 'pandas', 'statistical analysis', 
                       'numpy', 'predictive analysis', 'tensorflow', 'hypothesis', 
                       'matplotlib', 'scikit-learn', 'information technology', 
                       'machine learning', 'cloud', 'streamlit', 'mining', 'python', 
                       'data analytics', 'deep learning', 'testing', 'training', 
                       'clustering & classification', 'data analysis', 'engineering', 
                       'data visualization', 'quantitative analysis', 'statistics', 
                       'flask', 'statistical modeling', 'pytorch', 'data mining', 
                       'aws', 'sql']

essential_skills = ["Python", "SQL", "MySQL", "R", "Tableau", "TensorFlow", "NumPy", 
                    "Statsmodels", "PyTorch", "Keras", "OpenCV", "NLTK", "CNN", "ANN",
                    "RNN", "Machine Learning", "Deep Learning", "SciKit Learn", "MS Excel",
                    "Data Visualization", "Power BI", "Data Analysis"]

quality_mapping = {
            'Resume needs significant improvement': 0.15,
            'Resume needs improvement': 0.35,
            'Resume is average': 0.55,
            'Resume is good': 0.75,
            'Resume is very good': 0.90,
            'Resume is excellent': 1,
            'The resume is bad': 1.1
        }

keyword_variations = {
        "Python": ["Python", "Python_Language", "Python Programming"],
        "SQL": ["SQL", "SQL_Language", "Structured Query Language"],
        "MySQL": ["MySQL", "MySQL_Database", "My SQL"],
        "Pandas": ["Pandas", "Pandas_Library", "Pandas Data Analysis Library"],
        "R": ["R", "R_Programming", "R Language"],
        "Matplotlib": ["Matplotlib", "Matplotlib_Library", "Matplotlib Plotting Library"],
        "Seaborn": ["Seaborn", "Seaborn_Library", "Seaborn Data Visualization Library"],
        "StatsModel": ["StatsModel", "StatsModel_Library", "StatsModel Statistical Library"],
        "Tableau": ["Tableau", "Tableau_Software", "Tableau Data Visualization"],
        "TensorFlow": ["TensorFlow", "TensorFlow_Library", "TensorFlow Machine Learning Library"],
        "NumPy": ["NumPy", "NumPy_Library", "NumPy Numerical Computing Library"],
        "statsmodels": ["statsmodels", "statsmodels_Library", "statsmodels Statistical Library"],
        "PyTorch": ["PyTorch", "PyTorch_Library", "PyTorch Machine Learning Library"],
        "Keras": ["Keras", "Keras_Library", "Keras Deep Learning Library"],
        "Plotly": ["Plotly", "Plotly_Library", "Plotly Data Visualization Library"],
        "RFM": ["RFM", "RFM_Analysis", "Recency Frequency Monetary Analysis"],
        "ANOVA": ["ANOVA", "ANOVA_Test", "Analysis of Variance"],
        "BeautifulSoup": ["BeautifulSoup", "BeautifulSoup_Library", "BeautifulSoup Web Scraping Library"],
        "Imputation": ["Imputation", "Data_Imputation", "Missing Data Imputation"],
        "Scrappy": ["Scrappy", "Scrappy_Library", "Scrappy Web Scraping Library"],
        "Selenium": ["Selenium", "Selenium_Library", "Selenium WebDriver", "Selenium Automation"],
        "TensorBoard": ["TensorBoard", "TensorBoard_Library", "TensorBoard Visualization Tool"],
        "SciPy": ["SciPy", "SciPy_Library", "SciPy Scientific Computing Library"],
        "OpenCV": ["OpenCV", "OpenCV_Library", "OpenCV Computer Vision Library"],
        "NLTK": ["NLTK", "NLTK_Library", "Natural Language Toolkit"],
        "Hadoop": ["Hadoop", "Hadoop_Framework", "Hadoop Big Data Framework"],
        "Spark": ["Spark", "Spark_Framework", "Apache_Spark", "Spark Big Data Framework"],
        "AdaBoost": ["AdaBoost", "AdaBoost_Algorithm", "Adaptive Boosting"],
        "XGBoost": ["XGBoost", "XGBoost_Algorithm", "Extreme Gradient Boosting"],
        "CNN": ["CNN", "Convolutional Neural Network", "ConvNet", "CNN Algorithm"],
        "ANN": ["ANN", "Artificial Neural Network", "ANN Algorithm"],
        "RNN": ["RNN", "Recurrent Neural Network", "RNN Algorithm"],
        "LSTM": ["LSTM", "Long Short-Term Memory", "LSTM Network", "LSTM Algorithm"],
        "GAN": ["GAN", "Generative Adversarial Network", "GAN Algorithm"],
        "YOLO": ["YOLO", "You Only Look Once", "YOLO Algorithm"],
        "Clustering": ["Clustering", "Clustering_Algorithms", "Data Clustering"],
        "Classification": ["Classification", "Classification_Algorithms", "Data Classification"],
        "Word2Vec": ["Word2Vec", "Word2Vec_Algorithm", "Word2Vec Word Embeddings"],
        "Tf-idf": ["Tf-idf", "Term Frequency-Inverse Document Frequency", "Tf-idf Algorithm"],
        "Tokenization": ["Tokenization", "Text_Tokenization", "Word Tokenization"],
        "Machine Learning": ["Machine Learning", "Machine_Learning", "Machine Learning Algorithms", "Machine_Learning_Algorithms", "ML"],
        "Deep Learning": ["Deep Learning", "Deep_Learning", "Deep Learning Algorithms", "Deep_Learning_Algorithms", "DL"],
        "SciKit Learn": ["SciKit Learn", "SciKit_Learn", "Sci Kit Learn", "SciKit-Learn"],
        "Hugging Face": ["Hugging Face", "Hugging_Face", "Hugging Face", "HuggingFace"],
        "MS Excel": ["MS Excel", "MS_Excel", "MS Excel", "Microsoft_Excel", "Microsoft Excel", "Advance_excel", "advance excel", "Advance_Microsoft_excel", "Advance Microsoft excel"],
        "Data Visualization": ["Data Visualization", "Data_Visualization", "Data Viz"],
        "Power BI": ["Power BI", "Power_BI", "Microsoft_Power_BI", "Microsoft Power BI"],
        "Transfer Learning": ["Transfer Learning", "Transfer_Learning"],
        "Linear Regression": ["Linear Regression", "Linear_Regression"],
        "Logistic Regression": ["Logistic Regression", "Logistic_Regression"],
        "Decision Tree": ["Decision Tree", "Decision_Tree"],
        "Random Forest": ["Random Forest", "Random_Forest"],
        "K-Means Clustering": ["K-Means Clustering", "K_Means_Clustering", "K-Means-Clustering", "K Means Clustering", "K-mean", "k_-mean"],
        "K-Nearest Neighbours": ["K-Nearest Neighbours", "K_Nearest_Neighbours", "K-Nearest-Neighbours", "K Nearest Neighbours", "KNN"],
        "T-test": ["T-test", "T_Test", "T Test"],
        "Z-test": ["Z-test", "Z_Test", "Z Test"],
        "Hypothesis Testing": ["Hypothesis Testing", "Hypothesis_Testing"],
        "Chi-square": ["Chi-square", "Chi_Square", "Chi2"],
        "Normal Distribution": ["Normal Distribution", "Normal_Distribution"],
        "Correlation Analysis": ["Correlation Analysis", "Correlation_Analysis"],
        "Feature Scaling": ["Feature Scaling", "Feature_Scaling"],
        "Dimensionality Reduction": ["Dimensionality Reduction", "Dimensionality_Reduction"],
        "Jupyter Notebook": ["Jupyter Notebook", "Jupyter_Notebook"],
        "Google Colab": ["Google Colab", "Google_Colab"],
        "Data Analysis": ["Data Analysis", "Data_Analysis"],
        "Big Data": ["Big Data", "Big_Data"],
        "Support Vector Machines (SVM)": ["Support Vector Machines (SVM)", "Support_Vector_Machines", "SVM", "Support Vector Machines", "Support_Vector_Machines_SVM"],
        "Natural Language Processing": ["Natural Language Processing", "Natural_Language_Processing", "Natural Language Processing", "NLP"],
        "Artificial Intelligence": ["Artificial Intelligence", "Artificial_Intelligence", "AI"],
        "Naive Bayes": ["Naive Bayes", "Naive_Bayes"],
        "Principal Component Analysis (PCA)": ["Principal Component Analysis (PCA)", "Principal_Component_Analysis", "Principal Component Analysis", "PCA"],
        "Descriptive Statistics": ["Descriptive Statistics", "Descriptive_Statistics"],
        "Inferential Statistics": ["Inferential Statistics", "Inferential_Statistics"],
        "Gradient Boosting Machines (GBM)": ["Gradient Boosting Machines (GBM)", "Gradient_Boosting_Machines", "Gradient Boosting Machines", "GBM"],
        "Association Rule Learning (Apriori)": ["Association Rule Learning (Apriori)", "Association_Rule_Learning", "Association Rule Learning", "Apriori"],
        "Hierarchical Clustering": ["Hierarchical Clustering", "Hierarchical_Clustering"],
        "Image Segmentation": ["Image Segmentation", "Image_Segmentation"],
        "Object Detection": ["Object Detection", "Object_Detection"],
        "Encoder - Decoder": ["Encoder - Decoder", "Encoder_Decoder", "Encoder Decoder"],
        "Word Embedding": ["Word Embedding", "Word_Embedding"],
        "Bag of Words": ["Bag of Words", "Bag_of_Words", "Bag of Words"],
        "Sentiment Analysis": ["Sentiment Analysis", "Sentiment_Analysis"],
        "Predictive Analysis": ["Predictive Analysis", "Predictive_Analysis"],
        "Statistical Modeling": ["Statistical Modeling", "Statistical_Modeling"],
        "Data Preprocessing": ["Data Preprocessing", "Data_Preprocessing"],
        "Model Development": ["Model Development", "Model_Development"],
        "Time Series Analysis": ["Time Series Analysis", "Time_Series_Analysis"],
        "Statistics Fundamentals": ["Statistics Fundamentals", "Statistics_Fundamentals"],
        "Advanced ML": ["Advanced ML", "Advanced_ML", "Advanced Machine Learning", "Advanced_Machine_Learning", "Advanced-ML"],
        "Advanced DL": ["Advanced DL", "Advanced_DL", "Advanced Deep Learning", "Advanced_Deep_Learning", "Advanced-DL"]
    }
