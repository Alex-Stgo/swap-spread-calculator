import datetime as dt
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import pandas as pd

class dates():
    def __init__(self,fec=None,form='%d/%m/%Y'):
        if fec is None:
            fec=dt.date.today()
        if type(fec) == str:
            try:
                self.value=dt.datetime.strptime(fec,form)
            except:
                self.value=dt.datetime.strptime(fec,'%d/%m/%y')
            self.value=self.value.date()
        elif type(fec) is dt.datetime:
            self.value=fec.date()
        elif type(fec) is dt.date:
            self.value=fec
        elif type(fec)==pd._libs.tslibs.timestamps.Timestamp:
            self.value=fec.to_pydatetime().date()
        elif type(fec)==dates:
            self.value=fec.value
        else:
            raise Exception("Error in date format")
    def str(self,form='%d/%m/%Y'):
        return dt.datetime.strftime(self.value,form)
    def mod(self,q,period="d",save=False,eom=False,som=False):
        if period=="d":
            f=self.value+relativedelta(days=q)
        elif period=="m":
            f=self.value+relativedelta(months=q)
        elif period=="y":
            f=self.value+relativedelta(years=q)
        if eom:
            f=dt.datetime(f.year,f.month,monthrange(f.year,f.month)[1]).date()
        if som:
            f=dt.datetime(f.year,f.month,1).date()
        if save:
            self.value=f
            return self
        else:
            t=dates()
            t.value=f
            return t
    def dts(self):
        return f"dateserial({self.value.year},{self.value.month},{self.value.day})"
    def dts_or(self):
        return f"TO_DATE('{self.str()}', 'DD-MM-YYYY')"
    def now(self):
        return dt.datetime.today()