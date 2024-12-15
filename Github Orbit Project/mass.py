import math


"""Instances of the the following Mass class hold all the data concerning the their whereabouts"""
class Mass:
    id, distance_unit, scale = 0, 1, 1                           
    def __init__(self,m=0,s=[0,0],v=[0,0], colour=(255,255,255), avg_density=1000):
        self.ID = Mass.id   
        Mass.id += 1
        self.assertions(m,v)
        self.colour = colour
        self.m, self.avg_density, self.s, self.v = m,avg_density,s,v
        self.initialise_data_structures()   
    def initialise_data_structures(self):
        self.others, self.v_mag, self.r = [],[],[]
        self.p = []
        self.r_mag, self.g, self.gR = [],[],[]
        self.locale = None #                                Base 10 log scale of position vector elements
        self.individual_position = None #                   Astronomical locations of objects on screen
        self.screen_position = None
        self.dot_diameter, self.real_diameter = self.calc_sphere_diam() 
    
    def assertions(self,m,v):
        assert m >= 10**22                     # Minimum mass needs to be 10**22, else mass collision methods won't work reliably
        assert Mass.distance_unit > 0 
    def calc_sphere_diam(self):
        enlarge = Mass.scale
        D = 2*(3*self.m/(4*math.pi*self.avg_density))**(1/3)
        d = enlarge*D/Mass.distance_unit
        if d < 1: d = 1
        return d, D 

