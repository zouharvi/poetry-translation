# MeanPoet

A metric for evaluating poetry translation (**mean**ing & **poet**icness).

Description TODO.

## Installation

Run `pip3 install -r requirements.txt` and makes sure that:

```python3
import nltk
nltk.download('punkt') # tokenization
nltk.download('wordnet') # wordnet corpus
nltk.download('omw-1.4')
nltk.download('averaged_perceptron_tagger') # POS tagging
```

Install `espeak` as well (for the `Poesy` package): `sudo apt install espeak`.