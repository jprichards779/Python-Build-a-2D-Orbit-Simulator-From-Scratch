import pygame
from pygame.locals import *
import random 
from gravity import *

""" Main class contains contains the gaming loop which executes all the methods above. """   
class Main:                          
    AU, G = 1.496*10**11, 6.67430*10**-11           # Average distance between Sun and Earth # Newton's Gravitational Constant                                       
    SCREEN_SCALE = 3                              # Number of AU either side of screen center / origin
    TIME_LAPSE = 1
    DOT_SCALE = 700                                 # Apparent object size e.g 700 corresponds to 700 times the size as it would appear in reality.       
    SPACE_COLOUR = (0,0,0)       
    assert SCREEN_SCALE >= 1 
    assert DOT_SCALE >=500 and DOT_SCALE <=1000           
                                                        
    v_Earth = 29789                          
    v_Merc = 29789*(1/0.378)**0.5           
    v_Ven = 29789*(1/0.72)**0.5             
    v_Mar = 29789*(1/1.5)**0.5
    v_Jup = 29789*(1/5.2)**0.5
    v_Sat = 29789*(1/9.5)**0.5
    v_Ura = 29789*(1/19)**0.5
    v_Nep = 29789*(1/30)**0.5
    Mass.distance_unit = SCREEN_SCALE*AU     
    Mass.scale *= DOT_SCALE 
    SOLAR_SYSTEM = [Mass(m=1.989*10**30, s=[0,0],       v=[0,0],      colour=(255,255,250), avg_density=1408),
                    Mass(m=3.285*10**23, s=[0.378*AU,0],v=[0,v_Merc], colour=(200,180,0),   avg_density=5429),
                    Mass(m=4.867*10**24, s=[0.72*AU,0], v=[0,v_Ven],  colour=(200,180,0),   avg_density=5243),
                    Mass(m=5.972*10**24, s=[AU,0],      v=[0,v_Earth],colour=(70,160,255),  avg_density=5514),
                    Mass(m=6.389*10**23, s=[-1.5*AU,0], v=[0,-v_Mar], colour=(200,100,60),  avg_density=3934),
                    Mass(m=1.898*10**27, s=[-5.2*AU,0], v=[0,-v_Jup], colour=(200,150,100), avg_density=1326),
                    Mass(m=5.972*10**24, s=[9.5*AU,0],  v=[0,v_Sat],  colour=(150,150,70),  avg_density=687),
                    Mass(m=8.681*10**25, s=[19*AU,0],   v=[0,v_Ura],  colour=(0,100,150),   avg_density=1270),
                    Mass(m=1.024*10**26, s=[30*AU,0],   v=[0,-v_Nep], colour=(0,100,255),   avg_density=1638),]

    def __init__(self):  
        pygame.init()
        self.screen_width, self.screen_height = 700, 700 
        self.size = (self.screen_width, self.screen_height) 
        self.screen = pygame.display.set_mode(self.size)
        self.lines = pygame.Surface(self.size) 
        self.icon = pygame.image.load("image.png")
        self.run = True
        self.initialise_data_structures(input=self.SOLAR_SYSTEM, center_object_ID=None)   
        # self.initialise_data_structures(input=self.SOLAR_SYSTEM, center_object_ID=3) 
        # self.initialise_data_structures()   
    def initialise_data_structures(self, input=[], center_object_ID=None):
        self.countdown = 2000000
        self.started = False
        self.drawing = False 
        self.text_x, self.text_y = self.screen_width, self.screen_height/2
        self.input = input
        self.center_object_ID = center_object_ID
        if len(self.input) == 0: self.center_object_ID = None 
        self.time_elapsed, self.recent_event_log, self.recent_event_times = 0, [], []
        self.mouse_history = []
        self.mass_added = 0  

    def caption(self, years=False):
        title = f"|Time: 0.0 calendar years|"
        if years and self.started: title = f"|Time: {round(self.time_elapsed/(365*24*3600),1)} calendar years|"
        title += " "*30
        title += "____2D Orbit Simulator____"
        pygame.display.set_caption(title)

    def update_displayed_info(self):
        if self.drawing and not self.started: 
            self.time_elapsed = 0
            self.started = True

    def draw(self, Model_System):
        zoom_out = (1/(Mass.distance_unit)) 
        lines = pygame.Surface(self.size) 
        lines.fill(self.SPACE_COLOUR)
        points, radii, colours = [],[],[]
        if not self.drawing:
            font1 = pygame.font.SysFont("Arial", 36)
            font2 = pygame.font.SysFont("Cambria", 25)
            text1 = "WHEN THE SCREEN CLEARS . . ."
            text2 = ". . . click on / touch the screen to create new masses."
            coordinates1 = (self.text_x/5, self.text_y -25)
            coordinates2 = (self.text_x/10, self.text_y+25)
            text_surface1 = font1.render(text1, True, (255,0,0))
            text_surface2 = font2.render(text2, False, (30,100,255))
            self.screen.blit(text_surface1,coordinates1)
            self.screen.blit(text_surface2,coordinates2)
        else:
            center = self.frame_of_reference(Model_System)
            for n in Model_System.current_system:
                assert type(n) == Mass
                n.screen_position = pygame_array([zoom_out*(n.s[0]-center[0])],
                                                [zoom_out*(n.s[1]-center[1])], 
                                                self.screen_width, self.screen_height)[0]
                points.append(n.screen_position)
                n.individual_position = points[0]
                radii.append(n.dot_diameter)
                colours.append(n.colour)
            # Rendering so objects appear to glow
            for n in range(len(points)): pygame.draw.circle(lines,(0,0,2), points[n], 30*radii[n]) 
            for n in range(len(points)): pygame.draw.circle(lines,(0,0,5), points[n], 10*radii[n]) 
            for n in range(len(points)): pygame.draw.circle(lines,(0,0,30), points[n], 4*radii[n]) 
            for n in range(len(points)): pygame.draw.circle(lines,(0,10,60), points[n], 2.5*radii[n])
            for n in range(len(points)):
                if radii[n]>1: pygame.draw.circle(lines,(10,40,180), points[n], 1.6*radii[n])
            for n in range(len(points)):
                if radii[n]>1: pygame.draw.circle(lines,(110,160,255), points[n], 1.2*radii[n]) 
            for n in range(len(points)): pygame.draw.circle(lines,colours[n], points[n], radii[n])
            self.screen.blit(lines, (0, 0))

    def clock_tick(self, Model):
        if not self.drawing:
            self.time_elapsed+=Model.time_step   
        else: self.time_elapsed+=Model.dT
    
    # The following method will cause the screen/viewer to follow a given object trajetcory
    # Object will appear to be fixed at the center of the screen with all others moving in relation to it.
    def frame_of_reference(self, Model_System):
        center=[0,0]
        if self.center_object_ID is not None and len(self.input)>0:
            if len(Model_System.new_ids) > 0:
                index = Model_System.new_ids.index(self.center_object_ID)
                if index < len(Model_System.current_system):
                    center = Model_System.current_system[index].s
            else: 
                center = self.input[self.center_object_ID].s
        return center
    
    def event_loop(self, Model_System, mass_range=[10**27, 10**30]):
        zones = [n.locale for n in Model_System.current_system]
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                    self.run = False
            if len(self.recent_event_log) >=2:
                self.recent_event_log = []
                self.recent_event_times=[]
            if event.type == MOUSEBUTTONDOWN:
                initial = pygame.mouse.get_pos()
                self.mouse_history.append(initial)
                self.recent_event_log.append(initial)
                self.recent_event_times.append(self.time_elapsed) 
            elif event.type == MOUSEBUTTONUP:
                final = pygame.mouse.get_pos()
                self.recent_event_log.append(final)
                self.recent_event_times.append(self.time_elapsed)
            if len(self.recent_event_log) == 2 and self.drawing:
                event_count = self.mouse_history.count(self.recent_event_log[0])
                if self.recent_event_log[0] in self.mouse_history and event_count == 1:
                    t0, t1 = self.recent_event_times[0], self.recent_event_times[1]
                    pts1, pts2 = self.recent_event_log[0], self.recent_event_log[-1]
                    s0 = translate_points_on_screen(pts=pts1, WIDTH=self.screen_width, 
                                                HEIGHT=self.screen_height, screen_scale=Mass.distance_unit)
                    s1 = translate_points_on_screen(pts=pts2, WIDTH=self.screen_width, 
                                                HEIGHT=self.screen_height, screen_scale=Mass.distance_unit)
                    v_x_adjust, v_y_adjust = None,None
                    if self.center_object_ID is not None:
                        for n in Model_System.current_system:
                            if n.ID == self.center_object_ID:
                                s0[0], s0[1] = s0[0]+n.s[0], s0[1]+n.s[1]
                                s1[0], s1[1] = s1[0]+n.s[0], s1[1]+n.s[1]
                                v_x_adjust, v_y_adjust = n.v[0], n.v[1]
                    ds_x, ds_y = s1[0]-s0[0], s1[1]-s0[1]
                    dt = abs(t1-t0)
                    if dt > 1000: # Must be greater than zero...larger number will reduce velocity magnitude
                        [min_mass, max_mass] = mass_range
                        if min_mass > 10**32: min_mass = 10**32
                        if max_mass > 10**33: max_mass = 10**33
                        colours = [(250,255,255), (200,240,255)]
                        colour = random.choice(colours)
                        m = random.randrange(min_mass, max_mass)
                        vx, vy = ds_x/dt, ds_y/dt
                        if (v_x_adjust and v_y_adjust) is not None:
                            vx+=v_x_adjust
                            vy+=v_y_adjust
                        if self.SCREEN_SCALE <= 2: v = [vx,vy]
                        else: v = [vx/self.SCREEN_SCALE, vy/self.SCREEN_SCALE]
                        M = Mass(m=m, s=s1, v=v, colour=colour, avg_density=2000)
                        self.mass_added += M.m
                        self.mouse_history = []
                        if M.locale not in zones: Model_System.current_system.append(M) 
             

    def update_position(self, Model_System):
        if len(Model_System.current_system) > 0 and self.drawing:
            Model_System.mass_network()
            Model_System.get_neighbours()
            Model_System.r_vectors()
            Model_System.R_mag()
            Model_System.g_vectors()
            Model_System.resultant_g()
            Model_System.remove_collided() 
            Model_System.object_locale_data()     
            Model_System.combine_removed_masses() 
            Model_System.calc_velocity()
            Model_System.reposition() 
        if self.time_elapsed >= self.countdown and self.drawing == False: self.drawing=True

    # Execution
    def main(self):
        pygame.display.set_icon(self.icon)
        Model_System = Gravitation(self) 
        while self.run: 
            # Display 
            self.caption(years=True)  
            self.draw(Model_System)  
            self.update_displayed_info()
            # Technical
            self.event_loop(Model_System, mass_range=[10**27,10**29])    
            self.frame_of_reference(Model_System)
            self.update_position(Model_System)
            self.clock_tick(Model_System)
            pygame.display.update()
        pygame.quit()
Main().main()