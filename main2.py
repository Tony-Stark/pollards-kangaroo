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
g = 21744646143243216057020228551156208752703942887207308868664445275548674736620508732925764357515199547303283870847514971207187185912917434889899462163342116463504651187567271577773370136574456671482796328194698430314464307239426297609039182878000113673163760381575629928593038563536234958563213385495445541911168414741250494418615704883548296728080545795859843320405072472266753448906714605637308642468422898558630812487636188819677130134963833040948411243908028200183454403067866539747291394732970142401544187137624428138444276721310399530477238861596789940953323090393313600101710523922727140772179016720953265564666
p = 21847359589888208475506724917162265063571401985325370367631361781114029653025956815157605328190411141044160689815741319381196532979871500038979862309158738250945118554961626824152307536605872616502884288878062467052777605227846709781850614792748458838951342204812601838112937805371782600380106020522884406452823818824455683982042882928183431194593189171431066371138510252979648513553078762584596147427456837289623008879364829477705183636149304120998948654278133874026711188494311770883514889363351380064520413459602696141353949407971810071848354127868725934057811052285511726070951954828625761984797831079801857828431
h = 2379943664994463434447180799986543062713483099464815442605819358024518874205912039079297734838557301077499485690715187242732637166621861199722810552790750351063910501376656279916109818380142480153541630024844375987866909360327482454547879833328229210199064615160934199590056906292770813436916890557374599901608776771002737638288892742464424376302165637115904125111643815237390808049788607647462153922322177386615212924778476029834861337534317344050414511899408665633738083462745720713477559240135989896733710248600757926137849819921071458210373753356840504150106675895043640641251817448597517740418989043930823670446
w = pow(2, 50, p)
n = 1024
n_p = multiprocessing.cpu_count()
m = n_p*math.sqrt(w)/4

prng = random.randint(1, 2**32)
random.seed(prng)

class KangarooClient(threading.Thread):
    def __init__(self, uuid, x0, exp0, kangaroo_type):
        super(threading.Thread, self).__init__()
        self.x0 = x0
        self.exp0 = exp0
        self.type = kangaroo_type

        self.uuid = uuid
        self.cmd_q = queue.Queue()
        self.terminate = threading.Event()
        self.jump = threading.Event()

    def run(self):
        while True:
            x_i, a_i = walk(self.x0, self.exp0)
            self.cmd_q.put((
                x_i,
                a_i, 
                self.type
            ))
            if self.terminate.is_set():
                return
            if self.jump.is_set():
                self.jump.clear() #unset the jump
                u = random.randint(1, 2*m)
                self.x_i = x_i * pow(g, u, p)
                self.a_i = a_i + u



'''
def kill_service(uuid):
    job = 1
    Client.cmd_queues[uuid].put(job)
    #handle clean up

if __name__ == "__main__":
    for uuid in ['123', '234', '345']:
        t = Client(uuid)
        t.start()

    kill_service('123')
'''


def s_map(x, n):
    random.seed(prng*x)
    return random.randint(0, n)


def server():
    queues = {}
    for i in range(n_p/2):
        a_i = w//2 + i*math.floor(m)
        t = KangarooClient(i, pow(g, a_i, p), a_i, "tame")
        t.start()
        queues[i] = t
    for j in range(n_p/2):
        a_i = j*math.floor(m)
        t = KangarooClient(j + n_p, pow(g, a_i, p), a_i, "wild")
        t.start()
        queues[j + n_p] = t
    tame_lookup = {}
    wild_lookup = {}
    while True:
        for i in queues
        client_response = client.response()
        if found_tame := tame_lookup.get(client_response[0]) is not None:
            if client_response[2] == "tame":
                client_response.jump()
            else:
                clients_all.terminate()
                return (client_response[1]-found_tame) % p
        if found_wild := wild_lookup.get(client_response[0]) is not None:
            if client_response[2] == "wild":
                client_response.jump()
            else:
                clients_all.terminate()
                return (found_wild-client_response[1]) % p
    pass

'''
def client(x0, exp0, kangaroo_type):
    terminate_signal = False
    while not terminate_signal:
        x_i, a_i = walk(x0, exp0)
        send(x_i, a_i, kangaroo_type)
        recv = server.response()
        if recv == "jump":
            u = random.randint(1, 2*m)
            x_i = x_i * pow(g, u, p)
            a_i = a_i + u
'''

def walk(x_i, a_i):
    a_i = (s_map(x_i, n) + a_i)
    x_i = (x_i*pow(g, s_map(x_i, n), p)) % p
    return x_i, a_i