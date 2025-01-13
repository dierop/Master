import torch


class FeedForward(torch.nn.Module):
    def __init__(self, d_model=512, d_ff=1024, dropout=0.1, **kwargs):
        super().__init__()
        self.ff = torch.nn.Sequential(
            torch.nn.LayerNorm(d_model),
            torch.nn.Linear(d_model, d_ff),
            torch.nn.ReLU(),
            torch.nn.Dropout(dropout),
            torch.nn.Linear(d_ff, d_model),
        )

    def forward(self, x):
        return self.ff(x)


class SelfAttention(torch.nn.Module):
    def __init__(self, d_model, n_heads=8, d_head=64, dropout=0.1, **kwargs):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head = d_head
        self.scale = torch.sqrt(torch.tensor(d_head, dtype=torch.float32))
        self.norm = torch.nn.LayerNorm(d_model)
        self.q_linear = torch.nn.Linear(d_model, d_head * n_heads)
        self.v_linear = torch.nn.Linear(d_model, d_head * n_heads)
        self.k_linear = torch.nn.Linear(d_model, d_head * n_heads)
        self.dropout = torch.nn.Dropout(dropout)
        self.out = torch.nn.Linear(d_head * n_heads, d_model)

    def forward(self, x):
        x = self.norm(x)
        b = x.shape[0]
        q = self.q_linear(x).view(b, -1, self.n_heads, self.d_head)
        k = self.k_linear(x).view(b, -1, self.n_heads, self.d_head)
        v = self.v_linear(x).view(b, -1, self.n_heads, self.d_head)

        scores = torch.einsum("bihd,bjhd->bhij", q, k) / self.scale

        att = scores.softmax(dim=-1)
        att = self.dropout(att)

        out = torch.einsum("bhij,bjhd->bihd", att, v).reshape(
            b, -1, self.n_heads * self.d_head
        )
        out = self.dropout(out)
        out = self.out(out)
        return out


class Encoder(torch.nn.Module):
    def __init__(self, nb_layers=6, **kwargs):
        super().__init__()
        self.seq_len = kwargs["seq_len"]
        self.pos = torch.nn.Parameter(torch.randn(1, self.seq_len, kwargs["d_model"]))
        self.att = torch.nn.ModuleList(
            [SelfAttention(**kwargs) for _ in range(nb_layers)]
        )
        self.ff = torch.nn.ModuleList([FeedForward(**kwargs) for _ in range(nb_layers)])

    def forward(self, x):
        b, t, d = x.shape
        x = x + self.pos[:, :t, :]
        for att, ff in zip(self.att, self.ff):
            x = x + att(x)
            x = x + ff(x)
        return x


class CausalSelfAttention(torch.nn.Module):
    def __init__(self, d_model, n_heads=8, d_head=64, dropout=0.1, **kwargs):
        super().__init__()
        self.seq_len = kwargs["seq_len"]
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head = d_head
        self.scale = torch.sqrt(torch.tensor(d_head, dtype=torch.float32))
        self.norm = torch.nn.LayerNorm(d_model)
        self.q_linear = torch.nn.Linear(d_model, d_head * n_heads)
        self.v_linear = torch.nn.Linear(d_model, d_head * n_heads)
        self.k_linear = torch.nn.Linear(d_model, d_head * n_heads)
        self.dropout = torch.nn.Dropout(dropout)
        self.out = torch.nn.Linear(d_head * n_heads, d_model)

        self.register_buffer(
            "mask",
            torch.tril(torch.ones(self.seq_len, self.seq_len))[None, None, ...] == 0,
        )

    def forward(self, x):
        x = self.norm(x)
        b, n, d = x.shape
        q = self.q_linear(x).view(b, -1, self.n_heads, self.d_head)
        k = self.k_linear(x).view(b, -1, self.n_heads, self.d_head)
        v = self.v_linear(x).view(b, -1, self.n_heads, self.d_head)

        scores = torch.einsum("bihd,bjhd->bhij", q, k) / self.scale

        scores = scores.masked_fill(self.mask[:, :, :n, :n], float("-inf"))
        att = scores.softmax(dim=-1)
        att = self.dropout(att)

        out = torch.einsum("bhij,bjhd->bihd", att, v).reshape(
            b, -1, self.n_heads * self.d_head
        )
        out = self.dropout(out)
        out = self.out(out)
        return out


class CrossAttention(torch.nn.Module):
    def __init__(self, d_model, n_heads=8, d_head=64, dropout=0.1, **kwargs):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head = d_head
        self.scale = torch.sqrt(torch.tensor(d_head, dtype=torch.float32))
        self.norm1 = torch.nn.LayerNorm(d_model)
        self.norm2 = torch.nn.LayerNorm(d_model)
        self.q_linear = torch.nn.Linear(d_model, d_head * n_heads)
        self.v_linear = torch.nn.Linear(d_model, d_head * n_heads)
        self.k_linear = torch.nn.Linear(d_model, d_head * n_heads)
        self.dropout = torch.nn.Dropout(dropout)
        self.out = torch.nn.Linear(d_head * n_heads, d_model)

    def forward(self, x1, x2):
        x1 = self.norm1(x1)
        x2 = self.norm2(x2)
        b = x1.shape[0]
        q = self.q_linear(x1).view(b, -1, self.n_heads, self.d_head)
        k = self.k_linear(x2).view(b, -1, self.n_heads, self.d_head)
        v = self.v_linear(x2).view(b, -1, self.n_heads, self.d_head)

        scores = torch.einsum("bihd,bjhd->bhij", q, k) / self.scale

        att = scores.softmax(dim=-1)
        att = self.dropout(att)

        out = torch.einsum("bhij,bjhd->bihd", att, v).reshape(
            b, -1, self.n_heads * self.d_head
        )
        out = self.dropout(out)
        out = self.out(out)
        return out, att


class Decoder(torch.nn.Module):
    def __init__(self, nb_layers=6, **kwargs):
        super().__init__()
        self.seq_len = kwargs["seq_len"]
        self.pos = torch.nn.Parameter(torch.randn(1, self.seq_len, kwargs["d_model"]))
        self.att = torch.nn.ModuleList(
            [CausalSelfAttention(**kwargs) for _ in range(nb_layers)]
        )
        self.cross_att = torch.nn.ModuleList(
            [CrossAttention(**kwargs) for _ in range(nb_layers)]
        )
        self.ff = torch.nn.ModuleList([FeedForward(**kwargs) for _ in range(nb_layers)])

    def forward(self, x, enc):
        b, t, d = x.shape
        x = x + self.pos[:, :t, :]
        for att, cross_att, ff in zip(self.att, self.cross_att, self.ff):
            x = x + att(x)
            x = x + cross_att(x, enc)[0]
            x = x + ff(x)
        return x


class TextTransformer(torch.nn.Module):
    def __init__(self, vocab_size=24, **kwargs):
        super().__init__()
        self.vocab_size = vocab_size
        self.seq_len = kwargs["seq_len"]

        self.enc = Encoder(**kwargs)

        self.emb = torch.nn.Embedding(vocab_size, kwargs["d_model"])
        self.dec = Decoder(**kwargs)
        self.out = torch.nn.Linear(kwargs["d_model"], vocab_size)

    def encoder(self, x):
        x = self.emb(x)
        return self.enc(x)

    def decoder(self, y, enc):
        y = self.emb(y)
        dec = self.dec(y, enc)
        return self.out(dec)

    def forward(self, x, y):
        enc = self.encoder(x)
        return self.decoder(y, enc)

    def loss(self, x, y):
        logits = self(x, y[:, :-1])
        target = y[:, 1:]
        loss = torch.nn.functional.cross_entropy(
            logits.reshape(-1, self.vocab_size), target.reshape(-1)
        )
        return loss

    def generate(self, x):
        device = next(self.parameters()).device
        self.eval()
        y = [
            2,
        ]
        with torch.no_grad():
            enc = self.encoder(x.to(device))

            while y[-1] != 3 and len(y) < self.seq_len:
                logits = self.decoder(torch.tensor(y).unsqueeze(0).to(device), enc)
                y.append(logits.argmax(-1)[:, -1].item())

        return y
