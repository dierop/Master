# ✨ RFA: Reconocimiento de Formas y Aprendizaje Automático

Source code for RFA subject.

The main focus are the usage of [Keras](https://keras.io/).

The project is developed over a dataset for [Diabetic Retinopathy](Rami/Diabetic_Retinopathy_Preprocessed_Dataset_256x256) based on one from Kaggle but preprocessed.

>[!Note]
> The fifth notebook is the main focus of the subject.

>[!Warning]
> The notebooks are prepared to be run over Google Colab. Some dependencies will be missing if you run it on local.

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

- __1Basic__: First notebook with a small MLP and some analysis over the architecture using keras tunner.
- __2Hyperparameters__: Second notebook with an analysis of the Learning rate and batch size using keras tunner.
- __3ReduceLR__: Third notebook with an analysis of the usage of early stopping and reduce learning rate using keras tunner.
- __4CNN__: Fourth notebook with a small CNN and an analysis on the LR using keras tunner.
- **5TL_FT_DA**: Fifth notebook doing transfer learning, fine tunning and data augmentation. 