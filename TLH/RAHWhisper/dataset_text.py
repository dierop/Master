import re

import torch

from utils import read_file


class TextTokenizer:
    def __init__(self, path: str):
        self.vocab = self._get_vocab(path)
        self.word2idx = {word: idx + 15 for idx, word in enumerate(self.vocab)}
        self.word2idx["<unk>"] = 0
        self.word2idx["<pad>"] = 1
        self.word2idx["<sos>"] = 2
        self.word2idx["<eos>"] = 3
        self.word2idx["/"] = 4
        for i in range(10):
            self.word2idx[str(i)] = 5 + i
        self.idx2word = {idx: word for word, idx in self.word2idx.items()}

    def _get_vocab(self, path: str):
        """
        Get the vocabulary from the text file ignoring the first word (a date) of each line.
        """
        vocab = set()
        text, date = read_file(path)
        for data in text:
            d = data.split()[1:]
            vocab.update(d)
        return vocab

    def _split_date(self, x):
        """
        Split the by character and taking it as the first word.
        As in the inoput data the first word is a date. And the output is only one date.
        """
        return list(x.split()[0])

    def encode(self, x, seq_len=-1):
        x = ["<sos>"] + self._split_date(x) + x.split()[1:] + ["<eos>"]
        x = [self.word2idx.get(w, self.word2idx.get("<unk>")) for w in x]
        if seq_len > len(x):
            x = x + [self.word2idx["<pad>"]] * (seq_len - len(x))
        return torch.tensor(x)

    def decode(self, x):
        if isinstance(x, torch.Tensor):
            x = x.tolist()
        x = " ".join([self.idx2word[i] for i in x])
        x = x.replace("<sos>", "").replace("<eos>", "").replace("<pad>", "")
        match = re.match(r"([\d\s/]+)?\s*(.+)?", x)
        date_with_spaces, prompt = match.groups()
        date_str = re.sub(r"\s", "", date_with_spaces)  # Remove spaces from the date\
        if prompt is None:
            x = f"{date_str}"
        else:
            x = f"{date_str} {prompt}"
        return x.strip()


class TextDataset(torch.utils.data.Dataset):
    def __init__(self, path: str, tokenizer: TextTokenizer, seq_len: int = 24):
        super().__init__()
        self.seq_len = seq_len
        self.promts, self.dates = read_file(path)
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.promts)

    def __getitem__(self, idx):
        x = self.promts[idx]
        y = self.dates[idx]
        return self.tokenizer.encode(x, self.seq_len), self.tokenizer.encode(
            y, self.seq_len
        )
