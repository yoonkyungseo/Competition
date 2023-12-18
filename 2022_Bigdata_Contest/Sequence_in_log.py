import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from tqdm import tqdm
import pickle

def run_df():
    loan = pd.read_csv('loan_result.csv')
    log = pd.read_csv('log_data.csv')
    user = pd.read_csv('user_spec.csv')
    id_in_loan = np.load('id_in_loan.npy')
    id_in_loan = pd.Series(id_in_loan)
    id_in_loan = id_in_loan.rename('id_in_loan')
    user = pd.concat([user,id_in_loan],axis=1)
    return loan, log, user

def create_dt():
    log['timestamp'] = pd.to_datetime(log['timestamp'])
    user['insert_time'] = pd.to_datetime(user['insert_time'])
    loan['loanapply_insert_time'] = pd.to_datetime(loan['loanapply_insert_time'])
    user['month'] = user['insert_time'].dt.month
    log['month'] = log['timestamp'].dt.month
    log['day'] = log.timestamp.dt.day
    log['hour'] = pd.to_datetime(log['timestamp']).dt.hour
    
def user_seq(loan,log,user):
    user_list_log = log.user_id.unique()
    log = log.sort_values(by = 'timestamp')
    log_mini = log[['user_id','event','timestamp','month','day','hour']]
    user_sq = dict()
    idx_val = 0
    for i in tqdm(user_list_log):
        mini_data = log_mini.query('user_id == @i')
        time_list = []
        for j in range(mini_data.shape[0]):
            val = str(list(mini_data.iloc[j,-3 : ].values))
            time_list.append(val)
        # mini_data.query('month == @val[0]')
        time_list = set(time_list)
        user_list = [[] for i in range(len(time_list))]
        idx = 0
        tracker = []
        for z in range(mini_data.shape[0]):
            if z == 0 :
                user_list[idx].append([mini_data['event'].values[z],mini_data['timestamp'].values[z]])
                tracker.append(mini_data['hour'].values[z])
            else:
                if mini_data['hour'].values[z] != tracker[z-1]:
                    if (mini_data['timestamp'].values[z] - mini_data['timestamp'].values[z-1]).astype(int) > 300:
                        idx +=1
                        user_list[idx].append([mini_data['event'].values[z],mini_data['timestamp'].values[z]])
                        tracker.append(mini_data['hour'].values[z])
                    else:
                        user_list[idx].append([mini_data['event'].values[z],mini_data['timestamp'].values[z]])
                        tracker.append(mini_data['hour'].values[z])
                else:
                    user_list[idx].append([mini_data['event'].values[z],mini_data['timestamp'].values[z]])
                    tracker.append(mini_data['hour'].values[z])
        idx_val+=1
        user_sq[i] = user_list
        if idx_val <5:
            print('example :', user_sq[i])
        elif idx_val == 5:
            with open('user1.pickle','wb') as fw:
                pickle.dump(user_sq, fw)
            file = 'user1.pickle'
            with open(file, 'rb') as f:
                data = pickle.load(f)
            print('Pickle_RESULT',data)
        else:
            pass
                
    return user_sq

def add_app_id(user_sq):
    min_list = list(user_sq.keys())
    app_result = []
    for i in tqdm(min_list):
        mini_data = user.query('user_id == @i')[['application_id','label','insert_time']]
        for tracker,seq in enumerate(user_sq[i]): # 한 유저의 모든 시퀀스 
            # seq 는 한 유저 하나의 시퀀스를 의미한다.
            for idx in range(mini_data.shape[0]): # 해당 유저의 user 데이터
                if len(seq) ==0 :
                    pass
                elif abs(mini_data.iloc[idx,-1] - pd.to_datetime(seq[-1][-1])).days <= 1:
                    if abs(mini_data.iloc[idx,-1] - seq[-1][-1]).seconds <= 300:
                        user_sq[i][tracker].append([mini_data.iloc[idx,0],mini_data.iloc[idx,-1]])
                        pass
                else:
                    pass
    return user_sq

def there_in(x):
    loan_app_list = user.query('id_in_loan == 1').application_id.unique()
    if x in loan_app_list:
        if (loan.loc[(loan['application_id'] == x)]['is_applied'] == 1).sum() >=1:
            return 2
        elif (loan.loc[(loan['application_id'] == x)]['is_applied'] == 0).sum() == 0:
            return 1
        else:
            return 4
    else:
        return 0
if __name__ == "__main__":
    loan, log, user = run_df()
    create_dt()
    user_sq = user_seq(loan,log,user)
    with open('user.pickle','wb') as fw:
        pickle.dump(user_sq, fw)
   # user['label'] = user.application_id.apply(lambda x : there_in(x))
    print(user.columns)
    user_sq1 = add_app_id(user_sq)
    with open('user_f.pickle','wb') as fw:
        pickle.dump(user_sq1, fw)
    