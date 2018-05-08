from perifericos.Rx_Tx.Motherboard import motherboard

class modulo_rx_tx():
    
    Conj_Motherboards=[]

    def __init__(self):
        #for i in range(0,7):
        self.Conj_Motherboards.append(motherboard(0))
        if self.Conj_Motherboards[-1].empty() == True:
            del self.Conj_Motherboards[-1]
    
    def __del__(self):
        del self.Conj_Motherboards[0]

    def instances_to_webdict(self):
        conj_dict={}
    #for i in range(0,7):
        conj_dict['Board_0']=self.Conj_Motherboards[0].instances_to_webdict()
        return conj_dict
    
    def webdict_to_instance(self,request):
        for item in request:
            if request[item] != '-1':
                dic_break=item.split()
                self.Conj_Motherboards[0].set_gain_rx(dic_break[2],request[item])
    
    def set_gain_rx(self,board,modulo,gain):
        self.Conj_Motherboards[0].set_gain_rx(modulo,gain)
    
    #def webdict_to_instances
        
        
