import argparse
import os
import pickle
import sys
import numpy as np
import torch
from torch.nn import BCELoss
from torch.optim import Adam
from data_loader.dataset import DataSet
from modules.model import GAT
from trainer import train
from utils import debug


if __name__ == '__main__':
    torch.manual_seed(1000)
    np.random.seed(1000)
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, required=True, help='Name of the dataset for experiment.')
    parser.add_argument('--input_dir', type=str, help='Input Directory of the parser',default = '')
    parser.add_argument('--node_tag', type=str, help='Name of the node feature.', default='node_features')
    parser.add_argument('--graph_tag', type=str, help='Name of the graph feature.', default='graph')
    parser.add_argument('--label_tag', type=str, help='Name of the label feature.', default='targets')

    # parser.add_argument('--feature_size', type=int, help='Size of feature vector for each node', default=173)
    parser.add_argument('--feature_size', type=int, help='Size of feature vector for each node', default=100)
    parser.add_argument('--graph_embed_size', type=int, help='Size of the Graph Embedding', default=100)
    parser.add_argument('--batch_size', type=int, help='Batch Size for training', default=128)
    args = parser.parse_args()



    model_dir = os.path.join('models', args.dataset)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    input_dir = args.input_dir
    processed_data_path = os.path.join(input_dir, 'Devign-ffmqem3000.bin')
    if False and os.path.exists(processed_data_path):
        debug('Reading already processed data from %s!' % processed_data_path)
        dataset = pickle.load(open(processed_data_path, 'rb'))
        debug(len(dataset.train_examples), len(dataset.valid_examples), len(dataset.test_examples))
    else:
        # dataset = DataSet(train_src=os.path.join(input_dir, 'train_GNNinput.json'),
        #                   valid_src=os.path.join(input_dir, 'valid_GNNinput.json'),
        #                   test_src=os.path.join(input_dir, 'test_GNNinput.json'),
        #                   batch_size=args.batch_size, n_ident=args.node_tag, g_ident=args.graph_tag,
        #                   l_ident=args.label_tag, inf=False)
        dataset = DataSet(train_src=os.path.join(input_dir, 'Devign-line-ggnn.json'),
                         valid_src=os.path.join(input_dir, 'Devign-line-ggnn.json'),
                         test_src=os.path.join(input_dir, 'Devign-line-ggnn.json'),
                         batch_size=args.batch_size, n_ident=args.node_tag, g_ident=args.graph_tag,
                         l_ident=args.label_tag, inf=False)
        file = open(processed_data_path, 'wb')
        pickle.dump(dataset, file)
        file.close()
        print("feature_size:", dataset.feature_size)
    assert args.feature_size == dataset.feature_size, \
        'Dataset contains different feature vector than argument feature size. ' \
        'Either change the feature vector size in argument, or provide different dataset.'


    # num_steps have default setting
    # model = GAT(input_dim=dataset.feature_size, output_dim=args.graph_embed_size, num_steps=args.num_steps, num_heads=2)
    model = GAT(input_dim=dataset.feature_size, output_dim=args.graph_embed_size, num_heads=2)

    debug('#' * 100)
    loss_function = BCELoss(reduction='sum')
    optim = Adam(model.parameters(), lr=0.001, weight_decay=0.001)
    train(model=model, dataset=dataset, max_steps=3000, dev_every=128,
          loss_function=loss_function, optimizer=optim,
          save_path=model_dir + 'Devign-ffmqem3000', max_patience=10, log_every=None)