import pygame, sys
from pygame.locals import *
import numpy as np
import csv
import sys

if len(sys.argv) == 1:
    print("Error: must provide integer timestep")
    sys.exit()
timestep = sys.argv[1]
if not timestep.isnumeric():
    print("Error: timstep must be an integer")
    sys.exit()
timestep = int(timestep)
if timestep < 100 or timestep > 5000:
    print("Error: timestep must be between 100 and 5000")
    sys.exit()
pygame.init()
paused = False
width = 650
height = 650
white = [255, 255, 255]
yellow = [255, 255, 0]
orange = [255, 87, 51]
red = [255, 0, 0]
blue = [0, 0, 255]
black = [0, 0, 0]
fps = 60
font = pygame.font.SysFont('Calibri', 18, False, False)
framePerSec = pygame.time.Clock()
display = pygame.display.set_mode((width, height))
pygame.display.set_caption("Milankovitch Cycles (timestep: " + str(timestep) + " years)")

class Orbit(object):
    def __init__(self, eccentricity):
        super().__init__()
        self.update(eccentricity)
    def update(self, eccentricity):
        self.eccentricity = eccentricity
        self.a = 100
        self.b = self.a*np.sqrt(1-eccentricity**2)
        self.c = eccentricity*self.a
        self.center_x = width*(1/6)+self.c
        self.center_y = height-485
    def draw(self):
        pygame.draw.ellipse(display, red, (self.center_x-self.a, self.center_y-self.b, self.a*2, self.b*2), 5)

class Sun(object):
    def __init__(self):
        super().__init__()
        self.center_x = width*(1/6)
        self.center_y = height-485
    def draw(self):
        pygame.draw.circle(display, orange, (self.center_x, self.center_y), 15)
        pygame.draw.circle(display, yellow, (self.center_x, self.center_y), 10)

class Earth(object):
    def __init__(self, obliquity):
        super().__init__()
        self.update(obliquity)
        self.center_x = width*(3/4)
        self.center_y = height*(1/4)-15
    def draw(self):
        axis_coords = self.rotate([self.center_x, self.center_y-100, self.center_x, self.center_y+100])
        equator_coords = self.rotate([self.center_x-70, self.center_y, self.center_x+69, self.center_y])
        pygame.draw.line(display, red, (axis_coords[0], axis_coords[1]), (axis_coords[2], axis_coords[3]), 5)
        pygame.draw.line(display, white, (self.center_x, self.center_y-100), (self.center_x, self.center_y+100), 3)
        pygame.draw.circle(display, blue, (self.center_x, self.center_y), 70)
        pygame.draw.line(display, white, (equator_coords[0], equator_coords[1]), (equator_coords[2], equator_coords[3]), 3)
    def update(self, obliquity):
        self.obliquity = obliquity*(np.pi/180)
    def rotate(self, coords):
        start_x_rot = np.cos(self.obliquity)*(coords[0]-self.center_x)-np.sin(self.obliquity)*(coords[1]-self.center_y)+self.center_x
        start_y_rot = np.sin(self.obliquity)*(coords[0]-self.center_x)+np.cos(self.obliquity)*(coords[1]-self.center_y)+self.center_y
        end_x_rot = np.cos(self.obliquity)*(coords[2]-self.center_x)-np.sin(self.obliquity)*(coords[3]-self.center_y)+self.center_x
        end_y_rot = np.sin(self.obliquity)*(coords[2]-self.center_x)+np.cos(self.obliquity)*(coords[3]-self.center_y)+self.center_y
        return [start_x_rot, start_y_rot, end_x_rot, end_y_rot]

class Precession(object):
    def __init__(self, precession_data, obliquity_data):
        super().__init__()
        self.precession_data = precession_data
        self.obliquity_data = normalize(obliquity_data, 70, 90)
    def draw(self, timestep):
        self.center_x = width*(1/4)
        self.center_y = height*(3/4)-5
        obliquity = self.obliquity_data[timestep]
        a = obliquity
        b = 15
        h = width*(1/4)
        k1 = height*(3/4)-90
        k2 = height*(3/4)+70
        self.list_of_pixels = np.arange(int(width*(1/4)-a+1),int(width*(1/4)+a+1))
        positive_pixels1 = np.zeros(len(self.list_of_pixels))
        negative_pixels1 = np.zeros(len(self.list_of_pixels))
        positive_pixels2 = np.zeros(len(self.list_of_pixels))
        negative_pixels2 = np.zeros(len(self.list_of_pixels))
        for i in range(len(self.list_of_pixels)):
            positive_pixels1[i] = b*np.sqrt(1-((self.list_of_pixels[i]-h)**2/a**2))+k1
            negative_pixels1[i] = -b*np.sqrt(1-((self.list_of_pixels[i]-h)**2/a**2))+k1+3
            positive_pixels2[i] = b*np.sqrt(1-((self.list_of_pixels[i]-h)**2/a**2))+k2
            negative_pixels2[i] = -b*np.sqrt(1-((self.list_of_pixels[i]-h)**2/a**2))+k2+3
        self.list_of_pixels1 = np.append(self.list_of_pixels, np.flip(self.list_of_pixels))
        self.list_of_pixels2 = np.append(np.flip(self.list_of_pixels), self.list_of_pixels)
        self.ellipse_pixels1 = np.append(positive_pixels1, np.flip(negative_pixels1))
        self.ellipse_pixels2 = np.append(negative_pixels2, np.flip(positive_pixels2))
        self.precession_data_norm = normalize(self.precession_data,0,len(self.list_of_pixels1))
        precession = int(self.precession_data_norm[timestep])
        point1 = [self.list_of_pixels1[precession-1], self.ellipse_pixels1[precession-1]]
        point2 = [self.list_of_pixels2[precession-1], self.ellipse_pixels2[precession-1]]
        for i in range(len(self.list_of_pixels2)):
            display.set_at((self.list_of_pixels2[i], int(self.ellipse_pixels2[i])), white)
            display.set_at((self.list_of_pixels2[i], int(self.ellipse_pixels2[i])+1), white)
            display.set_at((self.list_of_pixels2[i], int(self.ellipse_pixels2[i])-1), white)
        pygame.draw.line(display, red, (point1[0], point1[1]), (point2[0], point2[1]), 7)
        m_perp = -1/self.slope(point1)
        equator1 = self.point([self.center_x, self.center_y], 29, m_perp)
        equator2 = self.point([self.center_x, self.center_y], -29, m_perp)
        for i in range(len(self.list_of_pixels1)):
            display.set_at((self.list_of_pixels1[i], int(self.ellipse_pixels1[i])), white)
            display.set_at((self.list_of_pixels1[i], int(self.ellipse_pixels1[i])+1), white)
            display.set_at((self.list_of_pixels1[i], int(self.ellipse_pixels1[i])-1), white)
        pygame.draw.circle(display, blue, (self.center_x, self.center_y), 30)
        pygame.draw.line(display, white, (equator1[0], equator1[1]), (equator2[0], equator2[1]), 3)
    def point(self, point, distance, slope):
        if point[0] > width*(1/4):
            distance = -1*distance
        m = slope
        x = int(point[0]+(distance/np.sqrt(1+m**2)))
        y = int(point[1]+((distance*m)/np.sqrt(1+m**2)))
        return [x,y]
    def slope(self, point):
        return (point[1]-self.center_y)/(point[0]-self.center_x)

class Insolation(object):
    def __init__(self):
        super().__init__()
        self.lats = np.arange(90,-90,-7.4)
        self.lons = np.arange(-180,180,14.8)
        self.insolation = np.zeros([len(self.lats), len(self.lons)])
    def update(self, timestep):
        self.eccentricity = eccentricity_data[timestep]
        self.obliquity = obliquity_data[timestep]*(np.pi/180)
        self.precession = precession_data_tilt[timestep]*(np.pi/180)
        for i in range(len(self.lats)):
            for j in range(len(self.lons)):
                lat = self.lats[i]*(np.pi/180)
                lon = self.lons[j]*(np.pi/180)
                dec = self.obliquity*np.sin(lon)
                arg = np.tan(lat)*np.tan(dec)
                h0 = None
                if arg > 1:
                    h0 = np.pi
                elif arg < -1:
                    h0 = 0
                else:
                    h0 = np.arccos(-arg)
                dist = 1+self.eccentricity*np.cos(lon-self.precession)
                self.insolation[i,j] = (1367/np.pi)*(dist**2)*((h0*np.sin(lat))*np.sin(dec)+np.cos(lat)*np.cos(dec)*np.sin(h0))
    def draw(self):
        self.insolation = normalize(self.insolation, 0, 19)
        colors = [(28,3,252),(3,61,252),(3,115,252),(3,202,252),(3,244,252),
                  (3,242,219),(3,252,177),(2,252,132),(3,252,73),(23,252,3),
                  (98,252,3),(117,252,3),(240,252,3),(252,207,3),(252,169,3),
                  (252,132,3),(252,94,3),(252,53,3),(252,32,3),(252,3,3)]
        for i in range(np.shape(self.insolation)[0]):
            for j in range(np.shape(self.insolation)[1]):
                insolation = int(self.insolation[j,i])
                pygame.draw.rect(display, colors[insolation], ((width/2)+50+(i*10), (height/2)+37+(j*10), 10, 10))

def precession_handler(precession : Precession, timestep):
    precession.draw(timestep)

def orbit_handler(orbit : Orbit, timestep):
    orbit.draw()
    orbit.update(eccentricity_data_norm[timestep])

def tilt_handler(earth: Earth, timestep):
    earth.draw()
    earth.update(obliquity_data_norm[timestep])

def insolation_handler(insolation : Insolation, timestep):
    insolation.update(timestep)
    insolation.draw()

def text_handler(timestep):
    time_to_display = str(round(time_interp[timestep]/1000000,3))
    eccentricity_to_display = str(round(eccentricity_data[timestep],3))
    preccession_to_display = str(round(precession_data_tilt[timestep],3))
    obliquity_to_display = str(round(obliquity_data[timestep],2))
    if len(time_to_display) == 3:
        time_to_display = time_to_display + "00"
    if len(time_to_display) == 4:
        time_to_display = time_to_display + "0"
    if len(time_to_display) == 5 and timestep > (1/2)*len(time_interp):
        time_to_display = time_to_display + "0"
    if float(preccession_to_display) > 0:
        preccession_to_display = " " + preccession_to_display
    display.blit(font.render("Time: " + time_to_display + " Ma", True, white), (10, 35))
    display.blit(font.render("Eccentricity: " + eccentricity_to_display, True, white), (10, 10))
    display.blit(font.render("Precession: " + preccession_to_display, True, white), (10, 335))
    display.blit(font.render("Obliquity: " + obliquity_to_display, True, white), (335, 10))
    display.blit(font.render("90N", True, white), (335, 365))
    display.blit(font.render("90S", True, white), (335, 588))
    display.blit(font.render(" EQ", True, white), (335, 475))
    display.blit(font.render("SEP", True, white), (370, 615))
    display.blit(font.render("JAN", True, white), (444, 615))
    display.blit(font.render("MAY", True, white), (518, 615))
    display.blit(font.render("SEP", True, white), (592, 615))
    display.blit(font.render("Solar Radiation (W/m^2)", True, white), (400, 335))

def read_csv(fname):
    file = open(fname + ".csv")
    csvreader = csv.reader(file)
    data = []
    for row in csvreader:
        data.append(float(row[1]))
    return np.array(data)

def get_data():
    laskar_eccentricity = read_csv("eccen_20ma")
    laskar_precession = read_csv("precession_20ma")
    laskar_obliquity = read_csv("obliquity_20ma")
    all_data = np.zeros([np.shape(laskar_eccentricity)[0], 4])
    all_data[:,0] = np.arange(np.shape(laskar_eccentricity)[0])*1000
    all_data[:,1] = laskar_eccentricity
    all_data[:,2] = laskar_precession
    all_data[:,3] = laskar_obliquity
    return all_data

def normalize(data, a, b):
    min = np.min(data)
    max = np.max(data)
    return (b-a)*((data-min)/(max-min))+a

def plot_handler(data, x_buffer):
    for i in range(np.shape(data)[0]):
        display.set_at((i+x_buffer, int(height-data[i])), white)
    pygame.draw.circle(display, red, (x_buffer, int(height-data[0])), 10)

def draw_lines():
    pygame.draw.line(display, white, (width/2,0), (width/2,height), 1)
    pygame.draw.line(display, white, (0,height/2), (width,height/2), 1)

def convert_180_360(data_180):
    data_360 = np.zeros(len(data_180))
    prev = -999
    for i in range(len(data_180)):
        curr = data_180[i]
        if curr < prev:
            data_360[i] = 360 - data_180[i]
        else:
            data_360[i] = data_180[i]
        prev = curr
    return data_360

def key_handler():
    global paused
    global curr_timestep
    if pygame.key.get_pressed()[K_SPACE]:
        if paused:
            paused = False
        else:
            paused = True
    elif pygame.key.get_pressed()[K_LEFT] and paused:
        curr_timestep += -1
        if curr_timestep == 0:
            curr_timestep = np.shape(time_interp)[0]-1
        main_handler(curr_timestep)
        main_handler(curr_timestep)
    elif pygame.key.get_pressed()[K_RIGHT] and paused:
        curr_timestep += 1
        if curr_timestep == np.shape(time_interp)[0]:
            curr_timestep = 0
        main_handler(curr_timestep)
        
all_data = get_data()
time = all_data[:,0]
time_interp = np.arange(0, 20000000, timestep)
eccentricity_data = np.interp(time_interp, time, all_data[:,1])
eccentricity_data_norm = normalize(eccentricity_data, 0, 0.8)
eccentricity_data_plot = normalize(eccentricity_data, 340, 380)
precession_data = np.interp(time_interp, time, all_data[:,2])
precession_data_tilt = np.arcsin(precession_data/eccentricity_data)*(180/np.pi)+90
precession_data_display = convert_180_360(precession_data_tilt)
precession_data_plot = normalize(precession_data, 15, 55)
obliquity_data = np.interp(time_interp, time, all_data[:,3])
obliquity_data_norm = normalize(obliquity_data, 5, 40)
obliquity_data_plot = normalize(obliquity_data, 340, 380)
curr_timestep = 0
sun = Sun()
orbit = Orbit(eccentricity_data_norm[curr_timestep])
earth = Earth(obliquity_data_norm[curr_timestep])
precession = Precession(precession_data_display, obliquity_data)
insolation = Insolation()

def main_handler(timestep):
    display.fill(black)
    sun.draw()
    orbit_handler(orbit, timestep)
    tilt_handler(earth, timestep)
    precession_handler(precession, timestep)
    insolation_handler(insolation, timestep)
    text_handler(timestep)
    plot_handler(eccentricity_data_plot[timestep:timestep+275], 25)
    plot_handler(obliquity_data_plot[timestep:timestep+275], 350)
    plot_handler(precession_data_plot[timestep:timestep+275], 25)
    draw_lines()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            key_handler()
    if not paused:
        main_handler(curr_timestep)
        curr_timestep += 1
        if curr_timestep == np.shape(time_interp)[0]:
            curr_timestep = 1
    pygame.display.update()
    framePerSec.tick(fps)