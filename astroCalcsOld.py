import skyfield
from skyfield.api import Loader, Topos, Star
from skyfield import almanac
from skyfield.data import hipparcos

import what3words

import datetime
import time

class CalcMovement():



    def __init__(self, target, exposureT, loc):

        # Set up values from js
        self.target, self.targetType = target.split("%2F")
        self.exposureT = int(exposureT)
        w3w = loc
        print("Exposure initialised: " + self.target + ", " + str(self.exposureT) + ", " + w3w)

        # Set up data sets
        self.load = Loader('C:\Max\Programming\js\ScopeAlignment\SFData')
        self.data = self.load("de421.bsp")

        with self.load.open(hipparcos.URL) as f:
            self.df = hipparcos.load_dataframe(f)
        self.ts = self.load.timescale()

        self.earth = self.data["earth"]


        self.loc = ""
        self.lat = ""
        self.lng = ""
        self.location = ""
        self.tStart = 0

        self.firstRequest = True

        self.prevData = {"Az":0, "Alt":0}
        self.currData = {"Az":0, "Alt":0}
        self.deltaData = {"deltaAz":0, "deltaAlt":0}

        self.locationSetup(w3w)



    def locationSetup(self, w3w):

        # Set up locations
        geocoder = what3words.Geocoder("WMOHV7C8")

        #Retrieve user's What3Words location
        res = geocoder.convert_to_coordinates(str(w3w))

        #Check the contents of the dict returned by What3Words
        if "error" in res.keys():
            print("A '" + res["error"]["code"] + "' error has occured:")
            print("" + res["error"]["message"] + "")

        else:
            #Get the lat,lng of the nearest main location
            #Put into Skyfield and Astropy format
            self.loc = str(res["nearestPlace"])
            self.lat = str(res["coordinates"]["lat"])
            self.lng = str(res["coordinates"]["lng"])

            #Putting into Skyfield format
            if self.lat[0] == "-":
                self.lat = self.lat.replace("-", "")
                self.lat += " S"
            else:
                self.lat += " N"

            if self.lng[0] == "-":
                self.lng = self.lng.replace("-", "")
                self.lng += " W"
            else:
                self.lng += " E"

            #Confirm with message to user
            print("Approximate location set to: " + self.loc + ".\nLatitude: " + self.lat + "\nLongitude: " + self.lng + "")

            self.location = self.earth + Topos(str(self.lat), str(self.lng))



    def track(self):
        if self.target == "test":
            ExposureComplete = False

            if self.firstRequest:
                self.tStart = time.time()
                self.firstRequest = False

            if time.time() - self.tStart > self.exposureT:
                ExposureComplete = True
                self.firstRequest = True

            self.deltaData = {"deltaAz":0.0002, "deltaAlt":-0.0002} #usually 0.00002
        else:

            #Set Skyfield time and location
            t = self.ts.now()
            ExposureComplete = False

            if self.firstRequest:
                self.tStart = time.time()
                self.firstRequest = False

            if time.time() - self.tStart > self.exposureT:
                ExposureComplete = True
                self.firstRequest = True

            #Checks the type of target
            #Either a star from Hipparcos or a planet(or the moon) from Skyfield
            if self.targetType == "skyfield":
                try:
                    val = int(self.target)
                    target = self.data[int(self.target)]
                except ValueError:
                    target = self.data[str(self.target)]

                astro = self.location.at(t).observe(target)
            elif self.targetType == "star":
                target = int(self.target)
                astro = self.location.at(t).observe(Star.from_dataframe(self.df.loc[target]))

            #Compute altitude and azimuth
            app = astro.apparent()
            alt, az, distance = app.altaz()

            self.currData = {"Az":az.degrees, "Alt":alt.degrees}

            if self.prevData["Az"] == 0:
                self.deltaData["deltaAz"] = 0
                self.deltaData["deltaAlt"] = 0
            else:
                self.deltaData["deltaAz"] = self.currData["Az"] - self.prevData["Az"]
                self.deltaData["deltaAlt"] = self.currData["Alt"] - self.prevData["Alt"]

            self.prevData["Az"] = self.currData["Az"]
            self.prevData["Alt"] = self.currData["Alt"]

        return self.deltaData, ExposureComplete
