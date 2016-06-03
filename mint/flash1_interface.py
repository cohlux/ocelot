'''
machine interface
includes online optimizer, response measurement and other stuff
'''
try:
    import swig.dcs as dcs
except:
    print 'error importing doocs library'
    
import re
from pylab import *

    
    
class FLASH1MachineInterface():
    def __init__(self):
        
        self.debug = False
        
        self.blm_names = ['14L.SMATCH','14R.SMATCH',
                          '1L.UND1', '1R.UND1',
                          '1L.UND2', '1R.UND2', 
                          '1L.UND3', '1R.UND3', 
                          '1L.UND4', '1R.UND4',
                          '1L.UND5', '1R.UND5',
                          '1L.UND6', '1R.UND6',
                          '10SMATCH','3SDUMP']


    def init_corrector_vals(self, correctors):
        vals = [0.0]*len(correctors)#np.zeros(len(correctors))
        for i in range(len(correctors)):
            mag_channel = 'TTF2.MAGNETS/STEERER/' + correctors[i] + '/PS'
            vals[i] = dcs.get_device_val(mag_channel)
        return vals
        

    def get_alarms(self):
        alarm_vals = np.zeros(len(self.blm_names))
        for i in xrange(len(self.blm_names)):
            blm_channel = 'TTF2.DIAG/BLM/'+self.blm_names[i]+'/CH00.TD'
            blm_alarm_ch  = ('TTF2.DIAG/BLM/'+self.blm_names[i]).replace('BLM', 'BLM.ALARM') + '/THRFHI'
            if (self.debug): print 'reading alarm channel', blm_alarm_ch
            alarm_val = dcs.get_device_val(blm_alarm_ch) * 1.25e-3 # alarm thr. in Volts
            if (self.debug): print 'alarm:', alarm_val
    
            h = np.array(dcs.get_device_td(blm_channel))
    
            alarm_vals[i] = np.max( np.abs(h) ) / alarm_val 
            
        return alarm_vals
    
    
    def get_sase(self, detector='gmd_default'):
        
        if detector == 'mcp':
	    # incorrect
	    return dcs.get_device_val('TTF2.DIAG/MCP.HV/MCP.HV1/HV_CURRENT')
	    #return np.abs( np.mean(h) )
        if detector == 'gmd_fl1_slow':
            return dcs.get_device_val('TTF2.FEL/BKR.FLASH.STATE/BKR.FLASH.STATE/SLOW.INTENSITY' ) 
	    

        # default 'BKR' gmd
        h = np.array(dcs.get_device_td('TTF2.FEL/BKR.FLASH.STATE/BKR.FLASH.STATE/ENERGY.CLIP.SPECT'))
        val = np.mean(h)
        return val



    def get_sase_pos(self):

        x1 = dcs.get_device_val('TTF2.FEL/GMDPOSMON/TUNNEL/IX.POS')
        y1 = dcs.get_device_val('TTF2.FEL/GMDPOSMON/TUNNEL/IY.POS')

        x2 = dcs.get_device_val('TTF2.FEL/GMDPOSMON/BDA/IX.POS')
        y2 = dcs.get_device_val('TTF2.FEL/GMDPOSMON/BDA/IY.POS')
    
        return [ (x1,y1), (x2,y2) ] 

    def get_spectrum(self, f=None, detector='tunnel_default'):

        f_min = 13.0 # spectrum window (nm). TODO: replace with readout
        f_max = 14.0
        
        spec = np.array(dcs.get_device_td('TTF2.EXP/PBD.PHOTONWL.ML/WAVE_LENGTH/VAL.TD'))
    
        if f == None:
            f = np.linspace(f_min, f_max, len(spec))
    
        return f, spec
 
    def get_value(self, device_name):
        ch = 'TTF2.MAGNETS/STEERER/' + device_name + '/PS.RBV'
        return dcs.get_device_val(ch)
    
    def set_value(self, device_name, val):
        ch = 'TTF2.MAGNETS/STEERER/' + device_name + '/PS'
        return dcs.set_device_val(ch, val)
 
 
class FLASH1DeviceProperties:
    def __init__(self):
        self.patterns = {}
        self.limits = {}
        self.patterns['launch_steerer'] = re.compile('[HV][0-9]+SMATCH')
        self.limits['launch_steerer'] = [-4,4]
        
        self.patterns['intra_steerer'] = re.compile('H3UND[0-9]')
        self.limits['intra_steerer'] = [-5.0,-2.0]
        
        self.patterns['QF'] = re.compile('Q5UND1.3.5')
        self.limits['QF'] = [4,9]
        
        self.patterns['QD'] = re.compile('Q5UND2.4')
        self.limits['QD'] = [-9,-4]
        
        self.patterns['Q13MATCH'] = re.compile('Q13SMATCH')
        self.limits['Q13MATCH'] = [47.0,49.0]

        self.patterns['Q15MATCH'] = re.compile('Q15SMATCH')
        self.limits['Q15MATCH'] = [-16.0,-14.0]

        self.patterns['H3DBC3'] = re.compile('H3DBC3')
        self.limits['H3DBC3'] = [-0.15,-0.07]

        self.patterns['V3DBC3'] = re.compile('V3DBC3')
        self.limits['V3DBC3'] = [0.046,0.106]

        self.patterns['H10ACC7'] = re.compile('H10ACC7')
        self.limits['H10ACC7'] = [0.8,1.3]

        self.patterns['V10ACC7'] = re.compile('V10ACC7')
        self.limits['V10ACC7'] = [-2.6,-1.8]

        self.patterns['H8TCOL'] = re.compile('H8TCOL')
        self.limits['H8TCOL'] = [0.02,0.06]

        self.patterns['V8TCOL'] = re.compile('V8TCOL')
        self.limits['V8TCOL'] = [0.09,0.15]
        
        
    def get_limits(self, device):
        for k in self.patterns.keys():
            #print 'testing', k
            if self.patterns[k].match(device) != None:
                return self.limits[k]
        return [-0.11, -0.08]   