
from tqdm import tqdm
from numpy import random
import pandas as pd
from pandas import Series, DataFrame
import numpy as np
import datetime as dt
if __name__ == "__main__":
    data_train = pd.read_csv('tr_feature_woo.csv',encoding='UTF-8')
    data_test = pd.read_csv('te_feature_woo.csv',encoding='UTF-8')##
    dat = data_train['신청서번호'].unique()
    a = data_train.query('신청서번호 in @dat').groupby('신청서번호')['신청서번호'].count()
    a = a.rename('신청수')
    a = a.reset_index()
    mini = data_train[['신청서번호','신청여부']]
    rand_idx = []
    index_rand = []
    z=0
    for j in tqdm(dat):
        rnd_num = []
        df = mini.query('신청서번호 == @j & 신청여부 == 0 ').index
        num = a.query('신청서번호 == @j')['신청수']
        if len(df) != 0:
            if len(df) > num.values[0]:
                if int(num.values[0]*0.85) > 5:
                    rnd_num = list(np.random.choice(len(df), size  =int(num.values[0]*0.85),replace = False))
                elif int(num.values[0]*0.85) > 3:
                    rnd_num = list(np.random.choice(len(df), size  =int(num.values[0]/2),replace = False))
                else:
                    rnd_num = list(np.random.choice(len(df), size  = 1 ,replace = False))
            else:
                rnd_num = [i for i in range(len(df))]
        else:
            rnd_num = [-1234]
        for idx in rnd_num:
            if idx == -1234:
                pass
            else:
                index_rand.append(df[idx])
    with open("index_final.npy", "wb") as fp:   #Pickling
        pickle.dump(index_rand, fp)