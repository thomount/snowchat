class Sym:  # 股票
    def __init__(self, name, start_price, qty):
        self.name = name
        self.price = start_price
        self.qty = qty  # 上市时全部原价出售
class News: # 消息
    def __init__(self, level, weight, sym_pool):
        self.level = level
        self.weight = weight
        self.sym = {}
        #pick up some syms from sym_pool
        pass

class Order: # 订单
    def __init__(self, _id, flag, sym, px, qty, owner):
        self.id = _id
        self.flag = flag
        self.sym = sym
        self.px = px
        self.qty = qty
        self.owner = owner
        
class Trade: # 交易
    def __init__(self, oa, ob, sym, px, qty):
        self.oa = oa
        self.ob = ob
        self.sym = sym
        self.px = px
        self.qty = qty




class User: # 股民
    def __init__(self, name):
        self.name = name
        self.money = 0
        self.order_pool = []
        self.sym_pool = {}
    def add_order(self, flag, px, qty):
        pass
    def cancel_order(self, order)
        pass
    def make_trade(self, trade):
        pass
    
initial_money = [10 ** 6, 10 **4, 10 ** 6, 10 ** 8]
class AI_User: # 模拟股民
    def __init__(self, _type, name):
        super().__init__(self, name)
        self.type = _type
        self.money = initial_money[self.type]
class RL_User: # 玩家
    def __init__(self, 0, name):
        super().__init__(self, name)
        self.type = 0
        self.money = initial_money[self.type]


class Env: #交易系统
    pass