import torch
import torchvision
from tqdm import tqdm
import torch.nn.functional as  F
from torch.utils.data import Dataset
from torchvision import transforms


class CIFAR10_dataset(Dataset):

    def __init__(self, partition = "train", transform=transforms.Compose([transforms.ToTensor()])):

        print("\nLoading CIFAR10 ", partition, " Dataset...")
        self.partition = partition
        if self.partition == "train":
            self.data = torchvision.datasets.CIFAR10('.data/', 
                                                     train=True,
                                                     download=True)
        else:
            self.data = torchvision.datasets.CIFAR10('.data/', 
                                                     train=False,
                                                     download=True)
        self.transform = transform
        print("\tTotal Len.: ", len(self.data), "\n", 50*"-")

    
    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):

        # Image
        image = self.data[idx][0]
        # PIL Image to torch tensor
        image_tensor = self.transform(image)

        # Label
        label = torch.tensor(self.data[idx][1])
        label = F.one_hot(label, num_classes=10).float()

        return {"img": image_tensor, "label": label}
    

class CIFAR10_trainer:
    def __init__(self, net, train_dataloader, test_dataloader, optimizer, criterion, epochs=10, lr_scheduler=None, early_stopping=15, batch_size=100):    
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
    
    def train(self, model_path="models/best_model.pt"):

        print("\n---- Start Training ----")
        best_accuracy = 1000
        best_epoch = 0
        for epoch in range(self.epochs):

            # TRAIN NETWORK
            train_loss, train_error = 0, 0
            self.net.train()
            with tqdm(iter(self.train_dataloader), desc="Epoch " + str(epoch), unit="batch") as tepoch:
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
                    labels = torch.argmax(labels, dim=1)
                    pred = torch.argmax(outputs, dim=1)
                    train_error += pred.not_equal(labels).sum().item()

                    # print statistics
                    train_loss += loss.item()

            train_loss /= (len(self.train_dataloader.dataset) / self.batch_size)

            # TEST NETWORK
            test_loss, test_error = 0, 0
            self.net.eval()
            with torch.no_grad():
                with tqdm(iter(self.test_dataloader), desc="Test " + str(epoch), unit="batch") as tepoch:
                    for batch in tepoch:

                        images = batch["img"].to(self.device)
                        labels = batch["label"].to(self.device)

                        # Forward
                        outputs = self.net(images)
                        test_loss += self.criterion(outputs, labels)

                        # one hot -> labels
                        labels = torch.argmax(labels, dim=1)
                        pred = torch.argmax(outputs, dim=1)

                        test_error += pred.not_equal(labels).sum().item()
            
            if self.lr_scheduler:
                self.lr_scheduler.step(test_loss)

            test_loss /= (len(self.test_dataloader.dataset) / self.batch_size)
            test_accuracy = 100. * test_error / len(self.test_dataloader.dataset)

            print("[Epoch {}] Train Loss: {:.6f} - Test Loss: {:.6f} - Train Error: {:.2f}% - Test Error: {:.2f}%".format(
                epoch + 1, train_loss, test_loss, 100. * train_error / len(self.train_dataloader.dataset), test_accuracy
            ))

            if test_accuracy < best_accuracy:
                best_accuracy = test_accuracy
                best_epoch = epoch

                # Save best weights
                torch.save(self.net.state_dict(), model_path)
            if epoch - best_epoch > self.early_stopping:
                print("\nEarly Stopping at epoch ", epoch)
                break

        print("\nBEST TEST ERROR: ", best_accuracy, " in epoch ", best_epoch)