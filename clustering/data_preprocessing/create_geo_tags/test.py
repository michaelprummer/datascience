"""
Um das Skript zu starten muss 'import ogr' funktionen. Dafuer muss 'pip install gdal' gemacht werden.
TM_WORLD_BORDERS-0.3.zip entpacken und alle Dateien (alle Dateien sind wichtig!!) im gleichen Ordner wie dieses Skript speichern.
Ebenso muss countries.py im gleichen Ordner sein.
Skript funktioniert, wenn 2 mal True geprintet wird.
"""
import countries
from __future__ import print_function

cc = countries.CountryChecker('TM_WORLD_BORDERS-0.3.shp')

lng = 48.812264
lat = 9.174781
country = cc.getCountry(countries.Point(lng,lat)).iso
print(country=="DE")

lng = 25.066771
lat = -77.343586
country = cc.getCountry(countries.Point(lng,lat)).iso
print(country=="BS")
