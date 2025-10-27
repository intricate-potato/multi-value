# python -m spacy download en_core_web_sm 
# Above command sometimes fails due to network issues.
# So using the following command to download the spaCy model directly.
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
python -m nltk.downloader wordnet
python -m nltk.downloader cmudict