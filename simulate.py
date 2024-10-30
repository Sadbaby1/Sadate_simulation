# Mechanic shop Simulation : the can not afford losing more customers

# goal: Reduice the average wait time for a costumer
# (from the time they arrive att the shop , get register and they
# leave the shop after  repair to 50 minutes), and to reduice the lost of customers

# step it take before  the reparation process starts
#  Arrive att the repair shop
#  get in line to register they arrival and get a ticket (registration)
# Wait for an available mechanics to begin the reparation
# Repair : time for the actual reparation process : short or long depending on the folt
# Repair finished
#  Resources (2 mechanics and a waiter )
#  Jobs :  customers arrive randomly
import simpy
import random
import matplotlib.pyplot as plt


# -----> data collection
wait_times = []      # List to store customer wait times (repair + registration) (WT)
customers_loss = 0      # number of the customers loss due long to wait times
customers_served = 0    # number of customers successfully serves
service_time = 50       # Target max time for registration + repair in minutes ( our goal)
CQ =0  # customer Queue : store all customer that visited the shop
LRQ = 0 #  store the number of customer lost att the registration
MQ = 0  # store  the  numbers of customers att the Mechanic queue
LMQ = 0 # store  the  numbers of customers lost Mechanic step
CS = 0 #  store  the  numbers of customers serve by the mechanic
CSR = 0 # Customer serve att by the waiter
lost_att_registration = []  # list of costumer Lost att the Registration(LR)
lost_att_mechanic_request = []  # time it take to lose  costumer Lost att  Mechanic Request( LMReq)
LR_by_day = [] # store average number of customers lost att the regsitration by day(8 hours)
LMReq_by_day = [] # store average number of customers lost att mechanic request by day(8 hours)
Av_Time_M_by_day = []  # average time to lose a customer att mechanic request
CQ_by_day = [] #coustemer que by  day list
CSR_by_day=[] #  coustemer seveer by the waiter by day list
CS_by_day = [] # number of mechanic serve by day
MQ_by_day = [] # queue length att the mechanic request
WT_by_day = [] # average waite time by day

# -----> resources and other simulation constant
waiter = 1      # worker that welcome the customers and register them
# random arrival_rate : Average between 30 to 45 min
num_mechanics = 3       # list available mechanics i n the repair shop
SIM_TIME = (8 * 60)   # 8 hours per day

class Shop:  # represent the car repair shop
    def __init__(self, env, num_mechanics, waiter):
        self.env = env
        self.mechanics = simpy.Resource(env, num_mechanics)
        self.waiter = simpy.Resource(env, waiter)

    def purchase_registration(self):
        # estimation of the time it tack to  register a costumer
        yield self.env.timeout(random.randint(1, 5))

    def repair(self):
        # estimated reparation time 30 min -50 min
        yield self.env.timeout(random.randint(20, 50))

# customer arrival
def customer_arrivals(env, shop):
    while True:
        # Customer arrives every 10-20 minutes
        yield env.timeout(random.randint(10, 20))
        env.process(customer(env, f"Customer-{env.now}", shop))

def customer(env, name, shop):  #  Customer process
    global customers_served,customers_loss, CQ, LRQ, CSR, MQ, LMQ , CS

    arrival_time = env.now
    print(f'  customer_id {name} arrive att the Shop  {env.now:.2f}.')
    # Wait for an available waiter for registration
    with shop.waiter.request() as request:
        print(f'  customer_id {name} request a to be register  {env.now:.2f}.')
        CQ += 1
        wait_for_registration = yield request | env.timeout(5)  # Max 5 min for registration wait
        if request not in wait_for_registration:
            LRQ += 1
            #time_after_registration = env.now - arrival_time
            lost_att_registration.append(LRQ)
            print(f' lost of customer_id {name} att {env.now:.2f} after waiting 5 minutes without been registered.')
            return

        # Register customer
        yield env.process(shop.purchase_registration())
        print(f'  customer_id {name}  successfully registered att  {env.now:.2f}.')
        CSR += 1
        # After registration, proceed to mechanic queue
        print(f'Customer_id {name} is now waiting for a mechanic at {env.now:.2f}.')
        MQ += 1
    # Wait for an available mechanic for repair
    with shop.mechanics.request() as request:
        print(f'  customer_id {name} start waiting for a mechanic  {env.now:.2f}.')
        wait_t = random.randint(0, 30)
        wait_for_repair = yield request | env.timeout(wait_t)  # Max 30 minutes wait for a mechanic
        if request not in wait_for_repair:
            LMQ += 1
            time_after_mechanic_request = env.now - arrival_time
            lost_att_mechanic_request.append(time_after_mechanic_request) #  #### ??????
            print(f' lost of customer_id {name} att {env.now:.2f}. after waiting 1h for a mechanic to be available')
            return

        # Get the car repaired
        yield env.process(shop.repair())
        total_time = env.now - arrival_time
        wait_times.append(total_time)
        print(f'  customer_id {name} satisfied, they are now leaving the shop at {env.now:.2f}.')

    # Record waiting time




#  Create an environment and start Running the simulation for 100 days
for day in range(21):
    # Resetting daily counters
    CQ, LRQ, MQ, LMQ, CS, CSR = 0, 0, 0, 0, 0, 0
    env = simpy.Environment()
    shop = Shop(env, num_mechanics, waiter)
    env.process(customer_arrivals(env, shop))
    env.run(until=SIM_TIME)
    # Shop queue
    CQ_by_day.append(CQ)
    # registration
    if len(lost_att_registration) > 0:
        av_CLR_by_day = sum(lost_att_registration) / len(lost_att_registration)
        LR_by_day.append(av_CLR_by_day)
    else:
        LR_by_day.append(0)
    # mechanic
    MQ_by_day.append(MQ)
    if len(lost_att_mechanic_request) > 0:
        av_CLReq_by_day = sum(lost_att_mechanic_request) / len(lost_att_mechanic_request)
        Av_Time_M_by_day.append(av_CLReq_by_day)
    else:
        LMReq_by_day.append(0)

    # Mechanic_lost:
    if LMQ > 0:
        LMReq_by_day.append(LMQ)
    else:
        LMReq_by_day.append(0)

    # average wait tim by day
    if wait_times:
        av_wait_time_by_day = sum(wait_times) / len(wait_times)
        WT_by_day.append(av_wait_time_by_day)
        wait_times.clear()  # <-- Reset wait_times here after recording the daily average
    else:
        WT_by_day.append(0)
    # custer served by day
    CS = CQ - LMQ - LRQ
    CS_by_day.append(CS)

# Final result
# print(f"Que length : {CQ}")
# print(f"Total customers lost att registration: {LRQ}")
# print(f"Total customers lost waiting for mechanic to be available: {LMQ}")
# print(f"Total customers served: {CS}")

print(f"THe Results for 100 days:")
print()
print(f"Que length att registration by day:")
for item in CQ_by_day:
    print(item, end= " ")
print()
print(f"Total customers lost att registration by day:")
for item in LR_by_day:
    print(item, end= " ")
print()
print(f"Que att mechanic:")
for item in MQ_by_day:
    print(item, end=" ")
print()
print(f"Total costumer att mechanic Que lost by day:")
for item in LMReq_by_day:
    print(item, end=" ")
print()
print(f"average wait time before customer lost due to mechanic availability by day:")
for item in Av_Time_M_by_day:
    print(item, end=" ")
print()
print(f"average wait time  by day:")
for item in WT_by_day:
    print(item, end=" ")
print()

print(f"Total customers served by day:")
for item in CS_by_day:
    print(item, end=" ")


# Plotting
from matplotlib.ticker import MaxNLocator

# Days for x-axis
days = list(range(1, 22))

# Plot Queue Length at Registration and Mechanics Queue on the same graph
plt.figure(figsize=(10, 5))
plt.plot(days, CQ_by_day, label='Queue Length at Registration', color='blue')
plt.plot(days, MQ_by_day, label='Mechanics Queue Length', color='orange')
plt.xlabel('Days')
plt.ylabel('Number of Customers')
plt.title('Queue Length at Registration and Mechanics Queue by Day')
plt.xticks(days)  # Set x-axis to show only whole days from 1 to 20
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure integer ticks on x-axis
plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure integer ticks on y-axis
plt.legend()
plt.grid()
plt.show()

# Plot Customer Lost at Registration, Lost at Mechanics, and Served on the same graph
plt.figure(figsize=(10, 5))
plt.plot(days, LR_by_day, label='Customers Lost at Registration', color='red')
plt.plot(days, LMReq_by_day, label='Customers Lost at Mechanics', color='purple')
plt.plot(days, CS_by_day, label='Customers Served', color='green')
plt.xlabel('Days')
plt.ylabel('Number of Customers')
plt.title('Customer Loss and Service Counts by Day')
plt.xticks(days)  # Set x-axis to show only whole days from 1 to 20
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure integer ticks on x-axis
plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure integer ticks on y-axis
plt.legend()
plt.grid()
plt.show()

# Plot Average Wait Time per Day and Target Wait Time on the same graph
plt.figure(figsize=(10, 5))
plt.plot(days, WT_by_day, label='Average Wait Time per Day', color='blue')
plt.axhline(y=service_time, color='orange', linestyle='--', label='Target Wait Time (50 mins)')
plt.xlabel('Days')
plt.ylabel('Wait Time (minutes)')
plt.title('Average Wait Time per Day with Target Wait Time')
plt.xticks(days)  # Set x-axis to show only whole days from 1 to 20
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure integer ticks on x-axis
plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure integer ticks on y-axis
plt.legend()
plt.grid()
plt.show()

