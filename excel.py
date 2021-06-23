import pandas as pd
import xlrd

class excel():
    def __init__(self,data):
        self.data=data
    @classmethod
    def xls(cls,dir,*args,**kwargs):
        data=pd.read_excel(dir,*args,**kwargs)
        return cls(data)
    
    @classmethod
    def xlsx(cls,dir,*args,**kwargs):
        data=pd.read_excel(dir,*args,**kwargs)
        return cls(data)

    @classmethod
    def csv(cls,dir,*args,**kwargs):
        data=pd.read_csv(dir,encoding="latin1",*args,**kwargs)
        return cls(data)