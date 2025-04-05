import torch
import torchvision
from tqdm import tqdm
import torch.nn.functional as  F
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image
import numpy as np


class G_dataset(Dataset):

    def __init__(self, x, y, transform=transforms.Compose([transforms.ToTensor()])):

        self.images = x
        self.labels = y
        self.transform = transform

    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img = Image.fromarray(self.images[idx].astype(np.uint8))  # Convertir a PIL
        label = float(self.labels[idx])
        img = self.transform(img)
        return {"img": img, "label": torch.tensor([label], dtype=torch.float32)}
    
class G_trainer:
    def __init__(self, net, train_dataloader, test_dataloader, optimizer, criterion, epochs=10, lr_scheduler=None, early_stopping=15, batch_size=100, model_path="model.pth"):
        self.model_path = model_path    
        self.net = net
        self.train_dataloader = train_dataloader
        self.test_dataloader = test_dataloader
        self.epochs = epochs
        self.batch_size = batch_size
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.net.to(self.device)
        self.criterion = criterion
        self.optimizer = optimizer
        self.lr_scheduler = lr_scheduler
        self.early_stopping = early_stopping

    
    def train(self):
        # Load model in GPU
        self.net.to(self.device)

        print("\n---- Start Training ----")
        best_accuracy = -1
        best_epoch = 0
        for epoch in range(self.epochs):

            # TRAIN NETWORK
            train_loss, train_correct = 0, 0
            self.net.train()
            with tqdm(
                iter(self.train_dataloader), desc="Epoch " + str(epoch), unit="batch"
            ) as tepoch:
                for batch in tepoch:

                    # Returned values of Dataset Class
                    images = batch["img"].to(self.device)
                    labels = batch["label"].to(self.device)

                    # zero the parameter gradients
                    self.optimizer.zero_grad()

                    # Forward
                    outputs = self.net(images)
                    loss = self.criterion(outputs, labels)
                    

                    # Calculate gradients
                    loss.backward()

                    # Update gradients
                    self.optimizer.step()

                    # one hot -> labels
                    pred = torch.sigmoid(outputs)

                    # Aplicar umbral de 0.5 para convertir a clases binarias
                    pred_labels = (pred > 0.5).float()  # valores: 0.0 o 1.0

                    # Comparar con las etiquetas reales
                    train_correct += pred_labels.eq(labels).sum().item()

                    # print statistics
                    train_loss += loss.item()

            train_loss /= len(self.train_dataloader.dataset)

            # TEST NETWORK
            test_loss, test_correct = 0, 0
            self.net.eval()
            with torch.no_grad():
                with tqdm(
                    iter(self.test_dataloader), desc="Test " + str(epoch), unit="batch"
                ) as tepoch:
                    for batch in tepoch:

                        images = batch["img"].to(self.device)
                        labels = batch["label"].to(self.device)

                        # Forward
                        outputs = self.net(images)
                        test_loss += self.criterion(outputs, labels)

                        # one hot -> labels
                        pred = torch.sigmoid(outputs)

                        # Aplicar umbral de 0.5 para convertir a clases binarias
                        pred_labels = (pred > 0.5).float()  # valores: 0.0 o 1.0

                        test_correct += pred_labels.eq(labels).sum().item()

            test_loss /= len(self.test_dataloader.dataset)
            if self.lr_scheduler is not None:
                self.lr_scheduler.step(test_loss)
                print("\tLR: ", self.optimizer.param_groups[0]["lr"])
            test_accuracy = 100.0 * test_correct / len(self.test_dataloader.dataset)

            print(
                "[Epoch {}] Train Loss: {:.6f} - Test Loss: {:.6f} - Train Accuracy: {:.2f}% - Test Accuracy: {:.2f}%".format(
                    epoch + 1,
                    train_loss,
                    test_loss,
                    100.0 * train_correct / len(self.train_dataloader.dataset),
                    test_accuracy,
                )
            )

            if test_accuracy > best_accuracy:
                best_accuracy = test_accuracy
                best_epoch = epoch

                # Save best weights
                torch.save(self.net.state_dict(), self.model_path)
            
            if epoch - best_epoch > self.early_stopping:
                print("\nEarly Stopping at epoch ", epoch)
                break

        print("\nBEST TEST ACCURACY: ", best_accuracy, " in epoch ", best_epoch)

    def get_model(self):
        # Load best weights
        self.net.load_state_dict(torch.load(self.model_path))

        test_loss, test_correct = 0, 0
        self.net.eval()
        with torch.no_grad():
            with tqdm(
                iter(self.test_dataloader),
                desc="Test " + str(self.epochs - 1),
                unit="batch",
            ) as tepoch:
                for batch in tepoch:

                    images = batch["img"].to(self.device)
                    labels = batch["label"].to(self.device)

                    # Forward
                    outputs = self.net(images)
                    test_loss += self.criterion(outputs, labels)

                    # one hot -> labels
                    labels = torch.argmax(labels, dim=1)
                    pred = torch.argmax(outputs, dim=1)

                    test_correct += pred.eq(labels).sum().item()

            test_loss /= len(self.test_dataloader.dataset)
            test_accuracy = 100.0 * test_correct / len(self.test_dataloader.dataset)
        print("Final best acc: ", test_accuracy)