from dates import dates as dt
import pandas as pd
from excel import excel

class leg():
    class rate():
        types = {'f':'Fixed','v':'Variable'}
        def __init__(self,type,curve_name=None,level=None,fwd=False,fwd_period=28):
            if not curve_name is None:
                self.curve=curve_data[curve_name]
            self.level=level
            self.fwd=fwd
            self.fwd_period=fwd_period
            self.type=type
        @classmethod
        def fixed(cls,level):
            return cls('f',level=level)
        @classmethod
        def variable(cls,curve,fwd,fwd_period=28):
            return cls('v',curve_name=curve,fwd=fwd,fwd_period=fwd_period)
        def _get(self,n):
            if n==0 and self.type=="v":
                return 0
            elif self.type=="f":
                return self.level
            else:
                return self.curve[n]
        def value(self,term):
            if self.fwd:
                p=self.fwd_period
                rate_level=((1 + self._get(term+p) * (term+p) / 360) / (1 + self._get(term)* (term) / 360) - 1) * 360 / p
            else:
                rate_level=self._get(term)
            return rate_level
        def df(self,n):
            return 1/(1+self._get(n)*n/360)
    def __init__(self,start_date,rate,dto_rate,freq_num,freq_type,notional,periods,spread=0,notional_exchange=False):
        self.flows=pd.DataFrame(columns=['Start','End','Notional','Rate','Rate+Spread','Interests','DF','Amortization','Cashflow','Cashflow PV'])
        data=self.flows
        fis=dt(start_date)
        fi=dt(fis)
        sd=dt(fis.value)
        for p in range(1,periods+1):
            fi=fis.mod(freq_num*(p-1),period=freq_type)
            ff=fis.mod(freq_num*p,period=freq_type)
            data.loc[p,'Start']=fi.str()
            data.loc[p,'End']=ff.str()
            data.loc[p,'Notional']=notional
            days=(fi.value-sd.value).days
            data.loc[p,'Rate']=rate.value(days)
            data.loc[p,'Rate+Spread']=data.loc[p,'Rate']+spread
            days=(ff.value-fi.value).days
            data.loc[p,'Interests']=data.loc[p,'Rate+Spread']*notional*days/360
            days=(ff.value-sd.value).days
            data.loc[p,'DF']=dto_rate.df(days)
            if notional_exchange and p==periods:
                data.loc[p,"Amortization"]=notional
            else:
                data.loc[p,"Amortization"]=0
            data.loc[p,"Cashflow"]=data.loc[p,'Interests']+data.loc[p,'Amortization']
            data.loc[p,"Cashflow PV"]=data.loc[p,"Cashflow"]*data.loc[p,'DF']
    @classmethod
    def VariableMXN(cls,notional,periods,spread=0):
        sd = dt()
        rate = cls.rate.variable('Descuento_IRS',fwd=True,fwd_period=28)
        return cls(sd,rate,rate,28,'d',notional,periods,spread)
    @classmethod
    def FixedMXN(cls,notional,periods,rate,spread=0):
        sd = dt()
        rate = cls.rate.fixed(rate)
        dto_rate = cls.rate.variable('Descuento_IRS',fwd=True,fwd_period=28)
        return cls(sd,rate,dto_rate,1,'m',notional,periods,spread)
    def pv(self):
        total=0
        if len(self.flows)>0:
            for i in self.flows.iterrows():
                total = i[1]['Cashflow PV'] +total
        return total
    def daystimesDF(self):
        total=0
        for i in self.flows.iterrows():
            fi=dt(i[1]['Start'])
            ff=dt(i[1]['End'])
            total = total + ((ff.value-fi.value).days) / 360 * i[1]['DF']* i[1]['Notional']
        return total
class swap():
    def __init__(self,leg1,leg2):
        self.leg1 = leg1
        self.leg2 = leg2
    def spread(self):
        return (self.leg1.pv() - self.leg2.pv()) / self.leg2.daystimesDF()
class curve():
    def __init__(self,load=True,dir = None):
        self.columns={'Plazo':'Plazo',
        'Descuento Irs':'Descuento_IRS',
        'Yield Bonos':'Yield_Bonos',
        'Cross Currency MID':'CCS_Mid',
        'Libor':'Libor',
        'Cross Currency Swap Udi/TIIE':'CCS_UDI_TIIE',
        'Real IMPTO':'Real_IMPTO',
        'Cetes IMPTO':'Cetes_IMPTO',
        'Cetes Irs':'Cetes_IRS'}
        self.data=pd.DataFrame()
        self.dir=dir
        if load:
            self.load()
    def load(self):
        if dir == None:
            return None
        global curve_data
        curve_data=excel.xls(self.dir,usecols=list(self.columns.keys())).data
        curve_data=curve_data.rename(columns=self.columns)
        curve_data=curve_data.set_index('Plazo')