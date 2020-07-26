"""

 if you are able to query data quickly (or cache it, if cached state is meaningful)
 below StateMachine logic demonstrate how you can determine/track the state using pandas

 workflow
 
 a->b->c0...cn->z->done
 
 assume a is done when col 0 > .5
 assume b is done when col 1 > .5
 assume c is done when col 2 to 8 > .5
 assume z is done when col 9 < .5

"""
import time
import numpy as np
import pandas as pd

undetermined = 'undetermined'
pending_a = 'pending_a'
pending_b = 'pending_b'
pending_c = 'pending_c'
pending_z = 'pending_z'
done = 'done'

# random data
def query_raw_data(project_id):
    sample_size = np.random.randint(3000,30000,1)[0]
    df = pd.DataFrame(np.random.rand(sample_size,10))
    df['id']=list(df.index)
    return df

class StateMachine(object):
    
    def __init__(self,project_id):
        self.project_id = project_id
        
    def _set_raw_df(self):
        # this method preps raw data for one sample or multilpe samples.
        self.raw_df = query_raw_data(self.project_id)
        self.id_df = self.raw_df[['id']]
        
    def _transform_a(self):
        def is_done(x):
            if x > .5:
                return True
            else:
                return False

        df = self.raw_df.copy(deep=True)
        df = df[['id',0]]
        df['is_done'] = df[0].map(is_done)
        
        cols = ['id']
        df = pd.merge(self.id_df,df,how='left',on=cols)
        df.is_done.fillna(False, inplace=True)
        df = df.rename(columns={"is_done": "a_done"})
        df = df.rename(columns={0: "a_detail"})
        return df
    
    def _transform_b(self):
        def is_done(x):
            if x > .5:
                return True
            else:
                return False

        df = self.raw_df.copy(deep=True)
        df = df[['id',1]]
        df['is_done'] = df[1].map(is_done)
        
        cols = ['id']
        df = pd.merge(self.id_df,df,how='left',on=cols)
        df.is_done.fillna(False, inplace=True)
        df = df.rename(columns={"is_done": "b_done"})
        df = df.rename(columns={1: "b_detail"})
        return df

    def _transform_c(self):
        def is_done(x):
            val = np.sum([x[y] for y in np.arange(2,8)])
            if val > 4:
                return True
            else:
                return False
            
        df = self.raw_df.copy(deep=True)
        df = df[['id',2,3,4,5,6,7,8]]
        df['is_done'] = df.apply(lambda x: is_done(x),axis=1)
        
        cols = ['id']
        df = pd.merge(self.id_df,df,how='left',on=cols)
        df.is_done.fillna(False, inplace=True)
        df = df.rename(columns={"is_done": "c_done"})
        df = df.rename(columns={2: "c_detail"})
        df = df[['id','c_done','c_detail']]
        return df

    def _transform_z(self):
        def is_done(x):
            if x < .5:
                return True
            else:
                return False

        df = self.raw_df.copy(deep=True)
        df = df[['id',9]]
        df['is_done'] = df[9].map(is_done)
        
        cols = ['id']
        df = pd.merge(self.id_df,df,how='left',on=cols)
        df.is_done.fillna(False, inplace=True)
        df = df.rename(columns={"is_done": "z_done"})
        df = df.rename(columns={9: "z_detail"})
        return df

    @classmethod
    def STATES(cls): # in this order.. DAG
        return [
            undetermined,
            pending_a,
            pending_b,
            pending_c,
            pending_z,
            done,
        ]

    # state machine
    @staticmethod
    def _determine_state(x):
        if x.a_done is False:
            return pending_a
        elif x.b_done is False:
            return pending_b
        elif x.c_done is False:
            return pending_c
        elif x.z_done is False:
            return pending_z
        elif x.z_done is True:
            return done        
        else:
            return undetermined

    def set_state(self):

        self._set_raw_df()
        
        df = self.raw_df.copy(deep=True)
        cols = ['id']
        
        a_df = self._transform_a()
        df = pd.merge(df,a_df,how='left',on=cols)
        b_df = self._transform_b()
        df = pd.merge(df,b_df,how='left',on=cols)
        c_df = self._transform_c()
        df = pd.merge(df,c_df,how='left',on=cols)
        z_df = self._transform_z()
        df = pd.merge(df,z_df,how='left',on=cols)
        df['state']=df.apply(lambda x: self._determine_state(x),axis=1)
        
        self.summary_dict = dict(
            case_count=len(df.groupby('id')),
        )
        
        self.state_df = df
        
def get_state_summary(project_id):
    start_time = time.time()
    project_id = -1
    rs = StateMachine(project_id)
    rs.set_state()

    end_time = time.time()    
    print('time to compute: {:1.3f} sec'.format(end_time-start_time))

    summary_dict = {}
    for state in rs.STATES():
        summary_dict.update({state:np.sum(rs.state_df.state == state)})

    summary_dict.update(rs.summary_dict)

    return summary_dict, rs.state_df


if __name__ == "__main__":

    summary_dict, rs.state_df = get_state_summary(1)
    mylist = []
    for k,v in summary_dict.items():
        mylist.append({'name':k,'value':v})
        
    pd.DataFrame(mylist) # make it pretty