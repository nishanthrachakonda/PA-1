import argparse
import network
import data
import image
from tqdm import tqdm
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plot

def main(hyperparameters):
    pca = PCA(n_components = hyperparameters.p)
    train_data, train_labels = data.load_data("data/")
    train_data = train_data.reshape(len(train_data), -1)
    test_data, test_labels = data.load_data("data/", train=False)
    test_data = test_data.reshape(len(test_data), -1)
    train_data_pca = pca.fit_transform(train_data)
    test_data_pca = pca.transform(test_data)

    for fold in range(hyperparameters.k_folds):
        train_folds, val_fold = next(data.generate_k_fold_set((train_data_pca, train_labels)))
        net = network.Network(hyperparameters, network.sigmoid, 
                              network.binary_cross_entropy, 1)
        best_val_acc = -1
        train_losses = []
        val_losses = []
        for _ in tqdm(range(hyperparameters.epochs)):
                train_acc, train_loss = 0, 0
                for _ in range(len(train_folds)//hyperparameters.batch_size):
                        train_acc_batch, train_loss_batch = net.train(train_folds)
                        train_acc += train_acc_batch
                        train_loss += train_loss_batch
                train_acc /= len(train_folds)
                train_loss /= len(train_folds)
                val_acc, val_loss = 0, 0
                for _ in range(len(val_fold)/hyperparameters.batch_size):
                        val_acc_batch, val_loss_batch = net.train(val_fold)
                        val_acc += val_acc_batch
                        val_loss += val_loss_batch
                val_acc /= len(val_fold)
                val_loss /= len(val_fold)
                train_losses.append(train_loss)
                val_losses.append(val_loss)
        plot.plot(np.arange(len(train_losses)), train_losses)
        plot.plot(np.arange(len(val_losses)), val_losses)
        plot.show()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'CSE151B PA1')
    parser.add_argument('--batch-size', type = int, default = 1,
            help = 'input batch size for training (default: 1)')
    parser.add_argument('--epochs', type = int, default = 100,
            help = 'number of epochs to train (default: 100)')
    parser.add_argument('--learning-rate', type = float, default = 0.001,
            help = 'learning rate (default: 0.001)')
    parser.add_argument('--z-score', dest = 'normalization', action='store_const', 
            default = data.min_max_normalize, const = data.z_score_normalize,
            help = 'use z-score normalization on the dataset, default is min-max normalization')
    parser.add_argument('--k-folds', type = int, default = 5,
            help = 'number of folds for cross-validation')
    parser.add_argument('--p', type = int, default = 100,
            help = 'number of principal components')

    hyperparameters = parser.parse_args()
    main(hyperparameters)
