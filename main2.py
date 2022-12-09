# distributed version

# 50 tame kangaroo (clients)
# 50 wild kangaroo (clients)

# server receives pairs from clients
# if server finds wild pair that matched tame pair - extract answer

# client
# starting point, type (tame/wild), walk(),jump()

# client:
import queue
import threading
import multiprocessing
import random
import math
import time

g = 21744646143243216057020228551156208752703942887207308868664445275548674736620508732925764357515199547303283870847514971207187185912917434889899462163342116463504651187567271577773370136574456671482796328194698430314464307239426297609039182878000113673163760381575629928593038563536234958563213385495445541911168414741250494418615704883548296728080545795859843320405072472266753448906714605637308642468422898558630812487636188819677130134963833040948411243908028200183454403067866539747291394732970142401544187137624428138444276721310399530477238861596789940953323090393313600101710523922727140772179016720953265564666
p = 21847359589888208475506724917162265063571401985325370367631361781114029653025956815157605328190411141044160689815741319381196532979871500038979862309158738250945118554961626824152307536605872616502884288878062467052777605227846709781850614792748458838951342204812601838112937805371782600380106020522884406452823818824455683982042882928183431194593189171431066371138510252979648513553078762584596147427456837289623008879364829477705183636149304120998948654278133874026711188494311770883514889363351380064520413459602696141353949407971810071848354127868725934057811052285511726070951954828625761984797831079801857828431
h = 2379943664994463434447180799986543062713483099464815442605819358024518874205912039079297734838557301077499485690715187242732637166621861199722810552790750351063910501376656279916109818380142480153541630024844375987866909360327482454547879833328229210199064615160934199590056906292770813436916890557374599901608776771002737638288892742464424376302165637115904125111643815237390808049788607647462153922322177386615212924778476029834861337534317344050414511899408665633738083462745720713477559240135989896733710248600757926137849819921071458210373753356840504150106675895043640641251817448597517740418989043930823670446
w = pow(2, 50, p)
n = 1024

prng = random.randint(1, 2**32)
random.seed(prng)

class KangarooClient(threading.Thread):
    communication_dict: dict[str, queue.Queue] = {} # id -> client

    def __init__(self, uuid, x0, exp0,parent_msg_channel: queue.Queue, kangaroo_type, mean_step_size):
        super(threading.Thread, self).__init__()
        self.x0 = x0
        self.exp0 = exp0
        self.type = kangaroo_type

        self.mean_step_size = mean_step_size
        self.uuid = uuid
        self.cmd_q = queue.Queue()
        self.parent_msg_channel = parent_msg_channel

        KangarooClient.communication_dict[self.uuid] = self.cmd_q

    def walk(self,x_i, a_i):
        a_i = (s_map(x_i, n) + a_i)
        x_i = (x_i*pow(g, s_map(x_i, n), p)) % p
        return x_i, a_i

    def run(self):
        while True:
            #child_pid  = os.getpid()
            #child_name = mp.current_process().name
            #print("[childs][%s#%s] run.." % (child_name, child_pid))   
            x_i, a_i = self.walk(self.x0, self.exp0)
            self.parent_msg_channel.put_nowait({'x_i': x_i, 'a_i': a_i, 'type': self.type, 'id': self.uuid })
            if not self.cmd_q.empty():
                msg = self.cmd_q.get_nowait()
                if msg == "terminate":
                    KangarooClient.communication_dict.pop(self.uuid) # clear dict as best practice
                    return
                if msg == "jump":
                    u = random.randint(1, 2*self.mean_step_size)
                    self.x_i = x_i * pow(g, u, p)
                    self.a_i = a_i + u

def s_map(x, n):
    random.seed(prng*x)
    return random.randint(0, n)

def get_cpu_cores():
    max_cpu_cores = 128
    min_cpu_cores = 1
    cpu_cores = multiprocessing.cpu_count()
    if cpu_cores > max_cpu_cores:
        cpu_cores = max_cpu_cores
    if cpu_cores < min_cpu_cores:  
        cpu_cores = min_cpu_cores
    if (cpu_cores%2) and cpu_cores!=1:
        cpu_cores -= 1
        print("[i] number cpu_cores must be even!")

    print('[cpu] %s cores available (min=%s; max=%s)' % (cpu_cores, min_cpu_cores, max_cpu_cores))

    return (cpu_cores, max_cpu_cores, min_cpu_cores)

def server():
    parent_msg_channel = queue.Queue()

    (cpu_cores, _, _) = get_cpu_cores()
    mean_step_size = cpu_cores*math.sqrt(w)/4

    for i in range(cpu_cores/2):
        a_i = w//2 + i*math.floor(mean_step_size)
        t = KangarooClient("tame"+str(i), pow(g, a_i, p), a_i, parent_msg_channel, "tame", mean_step_size)
        t.start()
    
    for j in range(cpu_cores/2):
        a_i = j*math.floor(mean_step_size)
        t = KangarooClient("wild"+str(j + cpu_cores), pow(g, a_i, p), a_i, parent_msg_channel, "wild", mean_step_size)
        t.start()
    
    tame_lookup = {}
    wild_lookup = {}

    time_delay = 0.05/cpu_cores
    while True:
        time.sleep(time_delay)
        
        if not parent_msg_channel.empty():
            msg  = parent_msg_channel.get_nowait()
            client_type = msg['type']
            client_a_i = msg['a_i']
            client_x_i = msg['x_i']
            client_id = msg['id']
            client_msg_channel = KangarooClient.communication_dict[client_id]

            if found_tame := tame_lookup.get(client_x_i) is not None:
                if client_type == "tame":
                    client_msg_channel.put_nowait("jump")
                else:
                    client_msg_channel.put_nowait("terminate")
                    result = (client_a_i-found_tame) % p
                    print("result: " + result + " from client " + client_id)
                    return result
            if found_wild := wild_lookup.get(client_x_i) is not None:
                if client_type == "wild":
                    client_msg_channel.put_nowait("jump")
                else:
                    client_msg_channel.put_nowait("terminate")
                    result = (found_wild-client_a_i) % p
                    print("result: " + result + " from client " + client_id)
                    return result


server()
