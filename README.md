# TFG_Gender_Bias_Metrics_NLP

This project performs Gender Bias analysis in Spanish sports press using a Word2Vec word embedding.

## Folder Structure

A brief explanation of the folders in this repository:

* **Web scraping**: Contains the code to extract news from the newspapers. There is a different script for each of the newspapers.
* **Analysis**:
  * **Preprocess_pipeline.ipynb**: Script to perform data preprocessing from the scraped data and Word2Vec model construction. 
  * **Nouns**: Contains lists of feminine and masculine nouns to train an SVC classifier for grammatical gender disentanglement.
  * **Test**: Contains analogy tests to analyze the semantic performance of the model.
  * **Metrics**: Contains `main.ipynb` with the main code of the program along with the outputs.

## Getting Started

### Prerequisites

- Python 3.x
- Required libraries: `numpy`, `pandas`, `gensim`, `scikit-learn`, `matplotlib`, `jupyter`,`scipy`, `beautifulsoup`, `spacy`, `pickle`

### Installation

1. Clone the repository.
2. Install the required libraries.

### Usage

1. Run the web scraping scripts to extract news articles from the respective newspapers. Ensure you have the necessary permissions to scrape the data.
2. Use the `preprocess_pipeline.ipynb` to clean, organize, preprocess de scraped data and generate the Word2Vec model.
3. Use the `main.ipynb` notebook in the `Analysis/Metrics` folder to perform the main gender bias analysis and view the outputs.
