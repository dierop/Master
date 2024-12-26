import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from tqdm import tqdm


class MNIST_dataset(Dataset):

    partition: str
    data: torchvision.datasets.MNIST
    da_train_transform: transforms.Compose
    transform: transforms.Compose

    def __init__(self, partition="train", da_transform=None):

        print("\nLoading MNIST ", partition, " Dataset...")
        self.partition = partition
        if self.partition == "train":
            self.data = torchvision.datasets.MNIST(".data/", train=True, download=True)
        else:
            self.data = torchvision.datasets.MNIST(".data/", train=False, download=True)
        print("\tTotal Len.: ", len(self.data), "\n", 50 * "-")
        self.da_train_transform = da_transform

        self.transform = transforms.Compose(
            [
                transforms.ToTensor(),
            ]
        )

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):

        # Image
        image = self.data[idx][0]

        if self.partition == "train" and self.da_train_transform:
            image = self.da_train_transform(image)
        else:
            image = self.transform(image)
        # care! net expect a 784 size vector and our dataset
        # provide 1x28x28 (channels, height, width) -> Reshape!
        image = image.view(-1)

        # Label
        label = torch.tensor(self.data[idx][1])
        label = F.one_hot(label, num_classes=10).float()

        return {"idx": idx, "img": image, "label": label}


class MNIST_trainer:
    net: torch.nn.Module
    train_dataloader: DataLoader
    test_dataloader: DataLoader
    optimizer: optim.Optimizer
    criterion: nn.CrossEntropyLoss
    epochs: int
    device: str
    model_path: str

    def __init__(
        self,
        net: torch.nn.Module,
        train_dataloader: DataLoader,
        test_dataloader: DataLoader,
        optimizer: optim,
        criterion: nn.CrossEntropyLoss,
        epochs: int,
        device: str,
        scheduler: optim.lr_scheduler = None,
        model_path: str = "models/best_model.pt",
    ):
        self.net = net
        self.train_dataloader = train_dataloader
        self.test_dataloader = test_dataloader
        self.optimizer = optimizer
        self.criterion = criterion
        self.epochs = epochs
        self.device = device
        self.scheduler = scheduler
        self.model_path = model_path

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
                    labels = torch.argmax(labels, dim=1)
                    pred = torch.argmax(outputs, dim=1)
                    train_correct += pred.eq(labels).sum().item()

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
                        labels = torch.argmax(labels, dim=1)
                        pred = torch.argmax(outputs, dim=1)

                        test_correct += pred.eq(labels).sum().item()

            test_loss /= len(self.test_dataloader.dataset)
            if self.scheduler is not None:
                self.scheduler.step(test_loss)
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
