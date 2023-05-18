# Adapted by Aman Aberra from NEURON python tutorial:
# https://github.com/neuronsimulator/nrn/blob/master/docs/tutorials/ballandstick.py
from neuron import h
import numpy as np
h.load_file("stdrun.hoc")


class Cell:
    def __init__(self, gid, mode='passive'):
        self._gid = gid
        self.mode = mode
        self._setup_morphology()
        self.all = self.soma.wholetree()
        self._setup_biophysics()        
        h.define_shape()    
        self._setup_recordings()
        
    def __repr__(self):
        return "{}[{}]".format(self.name, self._gid)
    

class BallAndStick(Cell):
    name = "BallAndStick"

    def _setup_morphology(self,dend_diam0=5,dend_diam1=1):
        self.soma = h.Section(name="soma", cell=self)
        # soma geometry
        self.soma.L = self.soma.diam = 13 # from https://www.beckman.com/resources/product-applications/
        self.soma.nseg = 1
        
    def _setup_biophysics(self):
        for sec in self.all:
            sec.Ra = 500  #  Ohm * cm, set from Nguyen et al
            sec.cm = 0.000012  # micro Farads / cm^2, set from Nguyen et al
            sec.insert('extracellular') # allows recording membrane current
        # Make both soma and dendrite passive with same parameters
        for sec in self.all:
            sec.insert('pas')
            for seg in sec:
                seg.pas.g = 1e-4 # S/cm2
                seg.pas.e = -75 # mV, set from Nguyen et al
        if self.mode == 'LIF':                        
            self.spkout = h.SpikeOut(self.soma(0.5))
            h.thresh_SpikeOut = -50	# (mV)
            h.refrac_SpikeOut = 4 # (ms)
            h.vrefrac_SpikeOut = self.soma.e_pas # (mV) reset potential
            h.grefrac_SpikeOut = 100 # (uS) clamped at reset
           
    
    def _setup_recordings(self):
        if self.mode == 'passive':
            self._spike_detector = h.NetCon(self.soma(0.5)._ref_v, None, sec=self.soma) # monitor V in soma for spiking
        elif self.mode == 'LIF':
            self._spike_detector = h.NetCon(self.spkout,None)
        self.spike_times = h.Vector() 
        self._spike_detector.record(self.spike_times) # Record spike times to spike_times Vector        
        self.soma_v = h.Vector().record(self.soma(0.5)._ref_v) # Record somatic voltage        
        self.soma_im = h.Vector().record(self.soma(0.5)._ref_i_membrane) # record somatic membrane current
        