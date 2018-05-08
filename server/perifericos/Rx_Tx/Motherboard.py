from perifericos.Rx_Tx.Rx import rx
from perifericos.Rx_Tx.Tx import tx

class motherboard():
    
    Conj_Modulos=[]
    board=0
    def __init__(self,board_number):
        self.board=board_number
        for i in range(0,8):
            self.Conj_Modulos.append(rx(i))
            if i == 0:
                self.Conj_Modulos[-1].reset_mcp23s17()
            type=self.Conj_Modulos[-1].setup_module()
            if type != 2:
                del self.Conj_Modulos[-1]
                if type == 1:
                    self.Conj_Modulos.append(tx(i))
                    type=self.Conj_Modulos[-1].setup_module()
                     
    def __del__(self):
        del self.Conj_Modulos[:]
    
    def instances_to_webdict(self):
        motherboard_dict={}
        for i in range(0,len(self.Conj_Modulos)):
            motherboard_dict['Modulo_'+str(i)]=self.Conj_Modulos[i].instances_to_webdict()
        return motherboard_dict
    
    def set_gain_rx(self,modulo,gain):
        for i in range(0,8):
            if modulo == 'Modulo_'+str(i):
                self.Conj_Modulos[i].update_gain(gain)
                if self.Conj_Modulos[i].setup_module() == 0:
                    print('Gain Update'+modulo+' Sucess')
                else:
                    print('Gain Update'+modulo+' Fail')
        
    
    def empty(self):
        if len(self.Conj_Modulos) == 0:
            return True
        else:
            return False