from utils import read_file
import torch, torchaudio, glob
import numpy as np
import scipy.signal

class RAHWhisperTokenizer():
    def __init__(self, path: str):
        self.vocab = self._get_vocab(path)
        self.word2idx = {word: idx+4 for idx, word in enumerate(self.vocab)}
        self.word2idx['<unk>'] = 0
        self.word2idx['<pad>'] = 1 
        self.word2idx['<sos>'] = 2
        self.word2idx['<eos>'] = 3
        self.idx2word = {idx: word for word, idx in self.word2idx.items()}

    def _get_vocab(self, path: str):
        vocab = set()
        _, text = read_file(path)
        for data in text:
            vocab.update(data.split())
        return vocab
    
    def encode(self, x, seq_len=-1):
        x = '<sos> ' + x + ' <eos>'
        x = [self.word2idx.get(w,self.word2idx.get('<unk>')) for w in x.split()]
        if seq_len > len(x):
            x = x + [self.word2idx['<pad>']] * (seq_len - len(x))
        return torch.tensor(x)
    
    def decode(self, x):
        if isinstance(x, torch.Tensor):
            x = x.tolist()
        x = ' '.join([self.idx2word[i] for i in x])
        x = x.replace('<sos>', '').replace('<eos>', '').replace('<pad>', '')
        return x.strip()



class RAHWhisperDataset(torch.utils.data.Dataset):
    def __init__(self, path:str,tokenizer: RAHWhisperTokenizer, seq_len:int=16, audio_len = 4*16000, transform=[]):
        super().__init__()
        self.transform = transform
        self.audio_len = audio_len
        self.seq_len = seq_len
        self.files, self.text = read_file(path)
        self.tokenizer = tokenizer
        
    def __len__(self):
        return len(self.files)
    
    def get_all_info(self, idx):
        file = self.files[idx]
        text = self.text[idx]
        x, fs = torchaudio.load(self.files[idx])
        if x.shape[1] < self.audio_len:
            x = torch.nn.functional.pad(x, (0, self.audio_len-x.shape[1]), value=0)
        else:
            x = x[:, :self.audio_len]
        x = x[0]
        if self.transform:
            x = x.numpy()
            for t in self.transform:
                x = t(x)
        return file, text, x, fs, self.tokenizer.encode(text, self.seq_len)
    
    def __getitem__(self, idx):
        _, _, x, _, y = self.get_all_info(idx)
        return x, y
        
    

class NoiseAug(object):
    def __init__(self, noise_dir='noise/musan_small/', prob=0.5):
        self.prob = prob
        self.noises = glob.glob(noise_dir+'/*/*.wav')
        
    def __call__(self, x):
        if np.random.uniform() < self.prob:
            n = torchaudio.load( np.random.choice(self.noises) )[0][0]            
            if len(n) < len(x):
                n = torch.nn.functional.pad(n, (0, len(x)-len(n)), value=0)
            elif len(n) > len(x):
                t0 = np.random.randint(0, len(n) - len(x))
                n = n[t0:t0+len(x)]
            n = n.numpy()
            p_x = x.std()**2
            p_n = n.std()**2
            snr = np.random.uniform(5, 15)
            n = n * np.sqrt(p_x/p_n) * np.power(10, -snr/20)
            x = x + n
        return x
    
class RIRAug(object):
    def __init__(self, rir_dir='noise/RIRS_NOISES_small/simulated_rirs_small/', prob=0.5):
        self.prob = prob
        self.rirs = glob.glob(rir_dir+'/*.wav') 

    def __call__(self, x):
        if np.random.uniform() < self.prob:
            n = len(x)
            rir = torchaudio.load( np.random.choice(self.rirs) )[0][0]
            rir = rir.numpy()
            rir = rir / np.max(np.abs(rir))
            x = scipy.signal.convolve(x, rir)
            t0 = np.argmax(np.abs(rir))
            x = x[t0:t0+n]
        return x


    
