# 🤡 LC:Linguistica computacional

Source code for LC subject. The main focus are the usage of NLP techniques: POS, WSD, HMM, ETC.
There is also a small project for sentiment analysis using Bert type models over a small group tweets.

## ⚙️ Installation & Setup

To install it you just need to run the following command in an environment with Python
3.10 or higher with [poetry](https://python-poetry.org/docs/#installation) installed:

`poetry install`

Finally, in order to run the static code analysis checks you should use the following
set of commands once installed:

```
poetry run ruff --fix .
poetry run black .
```


## 💻 Projects

__EJ1__:

- Lab0.ipynb: Notebook for basic python used for the other projectss
- Lab1.ipynb: Notebook with tokenizer based on regex.

__EJ2__:

- ejercicio2.ipynb: Notebook with POS tagging using HMM and TNT

__EJ3__:

- ejercicio3.ipynb: Notebook for create and evaluate a chunker
- conlleval.py: downloaded from [sighsmile/conlleval](https://github.com/sighsmile/conlleval) as the pypi version doesn't work as documented. __Warning__: Not a nice project :S

__EJ4__:

- lab4.ipynb: Notebook with word sense disambiguation using lexicon similarity and Word2Vec embeddings.

__Project__:
__TODO__