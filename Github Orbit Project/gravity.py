from mass import *
from support_functions import *

"""Gravitation class is responsible for calculating initial data provided by each Mass() object 
instanciated in the Main class, then updating each mass's data structures for the next calculation. """
class Gravitation:
    time_step = 3000                                    # Default 3000 seconds per frame. Optimal upper limit for collsion handling
    def __init__(self,main):
        assert abs(self.time_step) <= 3000
        self.main = main
        self.current_system = main.input
        self.initialise_data_structures()
    def initialise_data_structures(self):
        self.map, self.p_total = {}, []
        self.dT = Gravitation.time_step*self.main.TIME_LAPSE
        self.removed, self.rem_ids, self.new_ids, self.new = [],[],[],[]
        self.mass_join_errors =0
    

    # 1. Creating a method which ientidies all mass instances surrounding the current 
    # mass. A dictionary / self.map contains {mass : surrounding masses} elements.
    def mass_network(self):
        dict = {}
        limit = int(self.main.AU*self.main.SCREEN_SCALE/math.sin(math.pi/4))
        if self.main.SCREEN_SCALE < 1: limit = (1/self.main.SCREEN_SCALE)*int(self.main.AU*self.main.SCREEN_SCALE/math.sin(math.pi/4))
        for ind in range(len(self.current_system)):
            current = self.current_system[ind]
            if type(current) == Mass:
                if (current.s[0]**2 + current.s[1]**2)**0.5 <= limit or self.main.center_object_ID is not None: 
                    vals = []
                    for n in self.current_system:
                        if (n.s[0]**2 + n.s[1]**2)**0.5 <= limit or self.main.center_object_ID is not None:  
                            if self.current_system[ind] != n:
                                vals.append(n)
                    dict[self.current_system[ind]] = tuple(vals)
        self.map = dict
        self.current_system = [n for n in self.map]

    # 2. The following method will itterate through this dictionary and update the 
    # Mass.others data structure, creating a 'gravitational network' of mass instances
    def get_neighbours(self):
        for n in self.map:
            others = []
            for i in self.map[n]:
                others.append(i)
            n.others=others

    # 3. Calculate vector spanning between center of current object and surrounding objects
    def r_vectors(self):
        for n in self.map:
            out = []
            if len(n.others)>0:
                for i in self.map[n]:
                    r = [-(n.s[j]-i.s[j]) for j in range(2)]
                    out.append(r)
            n.r = out

    # 4. Calculating the magnitude of these vectors 
    def R_mag(self):
        for n in self.current_system:
            result = []
            for i in n.r:
                dist = ((i[0])**2 + (i[1])**2)**0.5
                result.append(dist)
            n.r_mag = result

    # 5. Calculating the acceleration vector of current object due to gravitational force 
    # exerted by surrounding objects
    def g_vectors(self):
        for n in self.current_system:
            result = []
            if len(n.others) > 0:
                for k in range(len(n.r_mag)):
                    if n.r_mag[k] > n.real_diameter + n.others[k].real_diameter:
                        gx = round(self.main.G*n.others[k].m*n.r[k][0]/(n.r_mag[k]**3),10)
                        gy = round(self.main.G*n.others[k].m*n.r[k][1]/(n.r_mag[k]**3),10)
                                                        # Becomes a inverse cubic function of vector magnitude when written in vector form.
                    else: 
                        gx,gy=0,0                       # Assuming gn = 0 below surface of each object to avoid
                        n.others[k].g = [[0,0]]         # assymptotic gravity and erroneous position updates
                    result.append([gx,gy])
            n.g = result

    # 6. Adding these g vectors together to find the overall/resultant vector acting on current object.
    def resultant_g(self):
        for n in self.current_system:
            gR_x, gR_y = 0,0
            if len(n.others)>0:
                for i in n.g:
                    gR_x += i[0]
                    gR_y += i[1]
            n.gR = [gR_x, gR_y]

    # 7. From this we can directly calculate the current object's resultant velocity vector.
    def calc_velocity(self):
        for n in self.current_system:
            vx,vy = 0,0
            if len(n.gR) >0:
                vx += n.v[0] + n.gR[0]*self.dT 
                vy += n.v[1] + n.gR[1]*self.dT
            n.v = [vx,vy]
            n.p = [n.m*vx,n.m*vy]

    # 8. This allows us to determine the current position of the object 
    def reposition(self):
        for n in self.current_system:
            sx,sy = 0,0
            if len(n.gR) >0: 
                sx += n.s[0] + n.v[0]*self.dT 
                sy += n.s[1] + n.v[1]*self.dT 
            n.s = [sx,sy]
            n.individual_position = pygame_array([n.s[0]], [n.s[1]], 
                                    self.main.screen_width, 
                                    self.main.screen_height)[0]            


    # 9. The following method seperates collided masses from other masses. 
    # This function only deals with vector magnitudes.
    def remove_collided(self):
        for n in self.current_system:
            vf_x, vf_y = 0,0
            for distance in n.r_mag:
                ind = n.r_mag.index(distance)
                near = n.others[ind]
                if near.locale == n.locale:
                    vf_x = abs(n.v[0]) + abs(near.v[0]) 
                    vf_y = abs(n.v[1]) + abs(near.v[1]) 
                vf_mag = (vf_x**2 +vf_y**2)**0.5 
                radii = [n.real_diameter/2, near.real_diameter/2]     
                contact_dist = sum(radii)
                adjust_to_5000 = 5000/self.dT   
                dT = self.dT*adjust_to_5000                 # *  Below 3000, the accuracy of final velocities is compomised violating momentum transfer
                LIMIT = contact_dist + vf_mag*dT            # The reason is unlcear but it may be an artifact of this method which 
                if distance < LIMIT:                       # doesn't account for direction of travel for very near objects.
                    n.gR=[0,0]                              # This adjustment to the originally planned time step, solves it. 3000 is the optimal limit for collisions, but the downside is that if we zoom in such that Main.SCREEN_SCALE
                    self.removed.append(n)                  # is less than 0.2, the higher resolution reveals smaller colliding objects (e.g astroid and Earth)
            if n in self.removed: continue                  # don't make physical contact like they appear to for Main.SCREE_SCALE >=1
            else:                      
                if n.ID == self.main.center_object_ID:
                    vf_x -= abs(n.v[0])
                    vf_y -= abs(n.v[1])
                self.new.append(n)  
        if len(self.removed): 
            for n in self.new: n.gR=[0,0]                   # All net gravity temporarily suspended to while dealing with collisions
            self.current_system = self.new

    # 10.
    # This following replaces the removed masses with a new mass, conserving momentum etc.
    # Methods 9. and 10. cover the vast majority of circumstances.
    def combine_removed_masses(self):
        localities = [n.locale for n in self.removed]
        distinct_zones, appended= [], []
        for n in localities: 
            if n not in distinct_zones: distinct_zones.append(n)
        if len(self.removed):
            to_append = []
            for u in distinct_zones:
                cluster = [n for n in self.removed if n.locale == u]
                masses_collected = [n.m for n in cluster]
                ind = masses_collected.index(max(masses_collected))
                self.substitute_colour = cluster[ind].colour
                m_total = sum([n.m for n in cluster])              # Total collided mass
                CoM_x = sum([n.s[0]*n.m for n in cluster])/m_total # Center of mass
                CoM_y = sum([n.s[1]*n.m for n in cluster])/m_total
                px = sum([n.m*n.v[0] for n in cluster])            # momentum x component
                py = sum([n.m*n.v[1] for n in cluster])            # momentum y component
                avg_density = sum([n.avg_density*n.m for n in cluster])/m_total 
                v_final = [n/m_total for n in [px,py]]
                M = Mass(m=m_total, s=[CoM_x, CoM_y], v=v_final, colour = self.substitute_colour, avg_density = avg_density)
                M.gR=[0,0]
                if self.main.center_object_ID in [n.ID for n in cluster]: 
                    M.ID = self.main.center_object_ID 
                to_append.append(M) 
            appended = to_append
        for n in appended:
            self.new.append(n) 
        self.current_system = self.new
        self.rem_ids = [j.ID for j in self.removed]
        self.new_ids = [j.ID for j in self.new]
        self.removed, self.new = [], []

    # 11. Method for delivering a way of identifying approximate location 
    def object_locale_data(self):
        for n in self.current_system: 
            unit = 1
            locale = []
            for i in n.s:
                if i !=0: 
                    unit = i/abs(i)
                    locale.append(round(unit*math.log10(abs(i))))
                else: 
                    unit = 0
                    locale.append(unit)
            n.locale = locale
