# -*- coding: utf-8 -*-

"""
@Author  : captain
@time    : 18-7-10 下午3:46
@ide     : PyCharm  
"""
from torchtext import data, datasets
import pandas as pd
from config import DefaultConfig
from torchtext.vocab import Vectors
from tqdm import tqdm
from torch.nn import init


# 定义Dataset
class GrandDataset(data.Dataset):
    name = 'Grand Dataset'

    @staticmethod
    def sort_key(ex):
        return len(ex.text)

    def __init__(self, path, text_field, label_field, test=False, **kwargs):
        fields = [('text', text_field), ('label', label_field)]
        examples = []
        csv_data = pd.read_csv(path)
        print('preparing examples...')
        # 可改成data.Example.fromCsv()
        if test:
            for text in tqdm(csv_data['word_seg']):
                examples.append(data.Example.fromlist([text, None], fields))
        else:
            for text, label in tqdm(zip(csv_data['word_seg'], csv_data['class'])):
                examples.append(data.Example.fromlist([text, label-1], fields))
        super(GrandDataset, self).__init__(examples, fields, **kwargs)


def load_data(opt):
    TEXT = data.Field(sequential=True, fix_length=1000)
    LABEL = data.Field(sequential=False, use_vocab=False)

    # load data
    train_path = opt.train_data_path
    val_path = opt.val_data_path
    # 先不加载test dataset
    # test_path = opt.test_data_path

    train = GrandDataset(train_path, text_field=TEXT, label_field=LABEL)
    val = GrandDataset(val_path, text_field=TEXT, label_field=LABEL)
    # test = GrandDataset(test_path, text_field=TEXT, label_field=None, test=True)

    vectors = Vectors(name='emb-100.txt', cache='.vector_cache/')
    # 没有命中的token的初始化方式
    vectors.unk_init = init.xavier_uniform
    # 构建Vocab
    TEXT.build_vocab(train, vectors=vectors)
    # LABEL.build_vocab(train) 

    # 构建Iterator
    # 在 test_iter , sort一定要设置成 False, 要不然会被 torchtext 搞乱样本顺序
    train_iter = data.Iterator(dataset=train, batch_size=opt.batch_size, train=True, repeat=False, device=opt.device)
    val_iter = data.Iterator(dataset=val, batch_size=opt.batch_size, train=False, repeat=False, sort=False, device=opt.device)
    # test_iter = data.Iterator(dataset=test, batch_size=opt.batch_size, train=False, sort=False, device=opt.device)

    return train_iter, val_iter, len(TEXT.vocab), TEXT.vocab.vectors
