import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from src.training.engine import EarlyStopping, train_epoch, train_model, validate_epoch


class DummyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc(x)


def test_train_and_validate_epoch():
    device = torch.device("cpu")
    model = DummyModel()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    x = torch.randn(16, 10)
    y = torch.randint(0, 2, (16,))
    loader = DataLoader(TensorDataset(x, y), batch_size=4)

    train_loss = train_epoch(model, loader, criterion, optimizer, device)
    assert isinstance(train_loss, float) and train_loss > 0.0

    val_loss, y_true, y_pred, y_probs = validate_epoch(model, loader, criterion, device)
    assert isinstance(val_loss, float)
    assert len(y_true) == 16 and len(y_pred) == 16 and len(y_probs) == 16


def test_early_stopping_step():
    model = DummyModel()
    stopper = EarlyStopping(patience=2)

    assert not stopper.step(0.5, model)
    assert stopper.counter == 0

    assert not stopper.step(0.6, model)
    assert stopper.counter == 1

    assert stopper.step(0.7, model)
    assert stopper.counter == 2


def test_train_model_loop():
    device = torch.device("cpu")
    model = DummyModel()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    x_train, y_train = torch.randn(20, 10), torch.randint(0, 2, (20,))
    x_val, y_val = torch.randn(10, 10), torch.randint(0, 2, (10,))
    train_loader = DataLoader(TensorDataset(x_train, y_train), batch_size=5)
    val_loader = DataLoader(TensorDataset(x_val, y_val), batch_size=5)

    fitted_model, history, duration = train_model(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        criterion=criterion,
        optimizer=optimizer,
        epochs=3,
        device=device,
        early_stopping_patience=2,
    )
    assert duration > 0.0
    assert "train_loss" in history
    assert "val_f1_score" in history
    assert isinstance(fitted_model, nn.Module)
