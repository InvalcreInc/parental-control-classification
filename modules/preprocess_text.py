import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')


def preprocess_text(text: str) -> str:
    '''
    Preprocesses the given text by converting it to lowercase, removing special characters, removing extra whitespaces, and removing stopwords.
    '''
    stop_words = set(stopwords.words('english'))
    text = text.lower()

    # Remove special characters (keeping punctuation like !, ?, etc.)
    text = re.sub(r'[^\w\s!?.,;]', '', text)

    # Remove extra whitespaces and strip leading/trailing spaces
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove stopwords
    text = ' '.join([word for word in text.split()
                     if word not in stop_words])
    return text


if __name__ == "__main__":
    text = "Hello, how are you? This is a sample text."
    print(preprocess_text(text))
