from pathlib import Path

from src.evaluation.plots import (
    plot_confusion_matrix,
    plot_loss_accuracy,
    plot_multi_confusion_matrices,
)


def test_plot_confusion_matrix(tmp_path: Path) -> None:
    """Uji penyimpanan plot confusion matrix biner."""
    save_path = tmp_path / "cm.png"
    result = plot_confusion_matrix([0, 1, 1, 0], [0, 1, 0, 0], save_path=save_path)
    assert result == save_path
    assert save_path.is_file()


def test_plot_loss_accuracy(tmp_path: Path) -> None:
    """Uji penyimpanan plot kurva loss dan akurasi."""
    save_path = tmp_path / "loss_acc.png"
    epochs = [1, 2, 3]
    train_loss = [0.8, 0.5, 0.3]
    val_loss = [0.9, 0.6, 0.4]
    val_acc = [0.5, 0.7, 0.85]
    result = plot_loss_accuracy(epochs, train_loss, val_loss, val_acc, save_path=save_path)
    assert result == save_path
    assert save_path.is_file()


def test_plot_multi_confusion_matrices(tmp_path: Path) -> None:
    """Uji penyimpanan plot multi confusion matrix."""
    save_path = tmp_path / "multi_cm.png"
    data = {
        "circle": ([0, 1, 1], [0, 1, 1]),
        "meander": ([0, 1, 0], [0, 0, 0]),
    }
    result = plot_multi_confusion_matrices(data, save_path=save_path)
    assert result == save_path
    assert save_path.is_file()
