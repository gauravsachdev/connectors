#!/usr/bin/env python
# -*- coding: utf-8 -*-

from geoedfframework.utils.GeoEDFError import GeoEDFError
from geoedfframework.GeoEDFPlugin import GeoEDFPlugin

import requests
import sys
import json
import urllib
import urllib.request

""" Module for implementing the Dam flood inundation map input connector plugin. 
    This module will implement the get() method required for all input plugins.
"""

class DamFIMInput(GeoEDFPlugin):

    # no optional params yet, but keep around for future extension
    # a comma separated list of scenarios is required
    __optional_params = []
    __required_params = ['dam_id','scenarios']

    # we use just kwargs since we need to be able to process the list of attributes
    # and their values to create the dependency graph in the GeoEDFInput super class
    def __init__(self, **kwargs):

        # list to hold all the parameter names; will be accessed in super to 
        # construct dependency graph
        self.provided_params = self.__required_params + self.__optional_params

        # check that all required params have been provided
        for param in self.__required_params:
            if param not in kwargs:
                raise GeoEDFError('Required parameter %s for DamFIMInput not provided' % param)

        # set all required parameters
        for key in self.__required_params:
            setattr(self,key,kwargs.get(key))

        # set optional parameters
        for key in self.__optional_params:
            # if key not provided in optional arguments, defaults value to None
            setattr(self,key,kwargs.get(key,None))

        # class super class init
        super().__init__()

    # each Input plugin needs to implement this method
    # if error, raise exception; if not, return True
    def get(self):

        # user provided scenarios to download
        user_scenarios = self.scenarios.split(',')
        
        # loop through scenarios available for this dam and download those that match the provided
        # scenario names
        r = requests.get("https://fim.sec.usace.army.mil/ci/fim/getEAPLayers?id=" + self.dam_id)
        dam_scenarios = json.loads(r.content)
        for scenario in dam_scenarios:
            for user_scenario in user_scenarios:
                if user_scenario in scenario['displayName']:
                    # then download
                    link = "https://fim.sec.usace.army.mil/ci/download/start?LAYERID="\
                    + str(scenario["layerId"])\
                    + "&type=s3&RASTER_INFO_ID=" + str(scenario["rasterInfoID"])\
                    + "&TABLE=FLOOD_DEPTH&TABLE_ID=" + str(scenario["floodDepthID"])

                    #construct filename out of load and breach condition
                    fileName = '%s/%s_%s_%s.tiff' % (self.target_path,scenario['loadCondition'],scenario['breachCondition'],self.dam_id)
                    # download file
                    try:
                        file = urllib.request.urlretrieve(link, fileName)
                    except urllib.error.HTTPError as err:
                        raise GeoEDFError("DamFIMInput for %s   - HTTPError" % self.dam_id)
                    except requests.exceptions.ConnectionError as err:
                        raise GeoEDFError("DamFIMInput for %s   - ConnectionError" % self.dam_id)
                    except requests.exceptions.Timeout:
                        raise GeoEDFError("DamFIMInput for %s   - Timeout" % self.dam_id)
                    except requests.exceptions.TooManyRedirects:
                        raise GeoEDFError("DamFIMInput for %s   - TooManyRedirects" % self.dam_id)
                    except requests.exceptions.RequestException as e:
                        raise GeoEDFError("DamFIMInput for %s   - Error" % self.dam_id)
        return True