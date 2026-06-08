"""
All your implementation code for the bank system simulation goes here.
"""
from collections import defaultdict
import bisect
class Simulation:

    def __init__(self):
        # self.timestamp = defaultdict(list)
        self.balance = defaultdict(int)
        self.spenders = defaultdict(int)

        self.pay_counter = defaultdict(int)
        self.acc_payment = [] # should be deque
        self.personal_payment = {}
        self.history = defaultdict(list) # (timestamp, balance, delta) bisect left 


       
    def create_account(self, timestamp: int, account_id: str) -> bool | None:
        self.process_cashback(timestamp)   
        if account_id in self.balance: return False
        # self.account[account_id].append(timestamp)
        self.balance[account_id] = 0
        self.spenders[account_id] = 0
        self.personal_payment[account_id] = {}
        self.history[account_id].append((timestamp, 0, 0))
        return True


    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self.process_cashback(timestamp)   
        if account_id not in self.balance: return None
        self.balance[account_id] += amount
        self.history[account_id].append((timestamp, self.balance[account_id], amount))
        return self.balance[account_id]

    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        self.process_cashback(timestamp)   
        if source_account_id not in self.balance: return None
        if target_account_id not in self.balance: return None
        if source_account_id == target_account_id: return None

        if self.balance[source_account_id] < amount: 
            # print(f'{self.balance[source_account_id]} less than {amount}')
            return None
        
        self.balance[source_account_id] -= amount
        self.balance[target_account_id] += amount

        self.spenders[source_account_id] += amount
        self.history[source_account_id].append((timestamp, self.balance[source_account_id], -amount))
        self.history[target_account_id].append((timestamp, self.balance[target_account_id], amount))
        # print(f"{source_account_id} has {self.balance[source_account_id]}")
        return self.balance[source_account_id]

    def top_spenders(self, timestamp: int, n: int) -> list[str] | None:
        spender = [(-y,x) for x,y in self.spenders.items()]
        spender.sort()
        return [f'{x}({-y})' for y,x in spender][:n]
        

    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        self.process_cashback(timestamp)     
        if account_id not in self.balance: return None
        if self.balance[account_id] < amount: return None

        self.spenders[account_id] += amount
        self.balance[account_id] -= amount
        self.pay_counter[account_id] += 1

        payment_id = f"payment{self.pay_counter[account_id]}"
        
        if account_id not in self.personal_payment:
            self.personal_payment[account_id] = {}
        self.personal_payment[account_id][payment_id] = "IN_PROGRESS"
        self.acc_payment.append((account_id, payment_id, timestamp + 86400000, amount * 0.02))
        self.history[account_id].append((timestamp, self.balance[account_id], -amount))
        return payment_id

    def process_cashback(self, timestamp):
        while(self.acc_payment):
            account_id, p,t,a = self.acc_payment[0]
            if t > timestamp: 
                return 
            self.acc_payment.pop(0)
            self.personal_payment[account_id][p] = "CASHBACK_RECEIVED"
            self.balance[account_id] += a
            print(account_id, p,t,a, 'adding to history',t, self.balance[account_id], a )
            self.history[account_id].append((t, self.balance[account_id], a))


    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:
        self.process_cashback(timestamp)
        if account_id not in self.balance: return None
        if account_id not in self.personal_payment: return None
        if payment not in self.personal_payment[account_id]: return None
        # # see if payment id does not exist
        # payment_num = int(payment.split('payment')[1])
        # if self.pay_counter[account_id] < payment_num: return None

        return self.personal_payment[account_id][payment]

        
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool | None:
        self.process_cashback(timestamp)
        if account_id_1 == account_id_2: return False
        if account_id_2 not in self.balance or account_id_1 not in self.balance: return False


        # merge cashback
        self.personal_payment[account_id_1].update(self.personal_payment[account_id_2])
        for i in range(len(self.acc_payment)):
            account_id, p,t,a = self.acc_payment[i]
            if account_id == account_id_2:
                self.acc_payment[i] = (account_id_1, p,t,a)

        # merge acc_payment w/ merge sort
        account1_history = self.history[account_id_1]
        account2_history = self.history[account_id_2]

        i , j = 0,0 
        tot = 0
        combines = []
        while(i < len(account1_history) and j < len(account2_history)):
            time1, _, delta1 = account1_history[i]
            time2, _, delta2 = account2_history[j]

            if time1 < time2:
                tot += delta1
                combines.append((time1, tot))
                i+=1
                # combines.append(account1_history[i])
            else:
                tot += delta2
                combines.append((time2, tot))
                j+=1
                # combines.append(account2_history[j])
        
        for ii in range(i, len(account1_history)):
            time1, _, delta1 = account1_history[ii]
            tot += delta1
            combines.append((time1, tot))
            # combines.append(account1_history[ii])
        
        for jj in range(j, len(account2_history)):
            time2, _, delta2 = account2_history[jj]
            tot += delta2
            combines.append((time2, tot))
            # combines.append(account2_history[jj])
        
        self.history[account_id_1] = combines # check if we can just do account1history = combines

        # combine and delete
        self.spenders[account_id_1] += self.spenders[account_id_2]
        self.balance[account_id_1] += self.balance[account_id_2]

        del self.spenders[account_id_2]
        del self.balance[account_id_2]

        del self.pay_counter[account_id_2]
        del self.history[account_id_2]
        del self.personal_payment[account_id_2]


            


    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        print('get balance', time_at)
        self.process_cashback(timestamp)
        if account_id not in self.history: return None
        acc_history = self.history[account_id]

        if time_at > acc_history[-1][0]: return self.balance[account_id]
        idx = bisect.bisect_right(acc_history, (time_at,))
        ti , amt, _ = acc_history[idx]

        # print(acc_history, f'\n getting history at position {idx} ')
        if ti == time_at or idx == 0 : return amt 
        else: return acc_history[idx-1][1]

