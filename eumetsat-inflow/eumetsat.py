import io
import zipfile
import logging
from datetime import datetime, timedelta

import eumdac
import xarray as xr
import numpy as np
from math import radians, sin, cos, sqrt, atan2

COLLECTION_ID = "EO:EUM:DAT:0417"  # SLSTR Level 2 Fire Radiative Power - Sentinel-3
FRP_NETCDF_FILENAME = 'FRP_MWIR1km_standard.nc'
LATITUDE_VAR = 'latitude'
LONGITUDE_VAR = 'longitude'
FRP_VAR = 'FRP_MWIR'
FIRE_DIMENSION = 'fires_MWIR1km_standard'

# Satellites to search
FIRE_SATELLITES = ["Sentinel-3A", "Sentinel-3B"]

def getProducts(consumer_key, consumer_secret, bbox, start_date, end_date, satellites):
    # Get token
    token = eumdac.AccessToken(credentials=(consumer_key, consumer_secret))

    # Connect and get collection
    datastore = eumdac.DataStore(token)
    collection = datastore.get_collection(COLLECTION_ID)
    
    # Search for products
    products = []    
    for satellite in satellites:   
      for product in collection.search(
        bbox=bbox,
        dtstart=start_date,
        dtend=end_date,
        sat=satellite
      ):
        products.append(product)

    if not products:
      return None
    
    return products
    
    

def extractFireDataFromProduct(product_obj):
	fire_coordinates = []
	product_identifier = str(product_obj)
	try:
		# Leer el contenido del producto en memoria
		with product_obj.open() as f:
			zip_buffer = io.BytesIO(f.read())

		with zipfile.ZipFile(zip_buffer) as z:
			mwir_standard_nc_file_path = None
			# Buscar el archivo NetCDF específico para FRP MWIR1km estándar
			for name in z.namelist():
				if FRP_NETCDF_FILENAME in name:
					mwir_standard_nc_file_path = name
					break

			if mwir_standard_nc_file_path:
				# Abrir el archivo NetCDF desde la memoria
				with z.open(mwir_standard_nc_file_path) as nc_file:
					nc_bytes = io.BytesIO(nc_file.read())
				ds_mwir_standard = xr.open_dataset(nc_bytes, engine="h5netcdf")

				# Verificar si todos los elementos requeridos están presentes
				required_data_vars = [LATITUDE_VAR, LONGITUDE_VAR, FRP_VAR]
				if all(var in ds_mwir_standard.data_vars for var in required_data_vars) and FIRE_DIMENSION in ds_mwir_standard.dims:
					# Filtrar los puntos donde FRP_MWIR tiene valor
					fire_events = ds_mwir_standard.where(ds_mwir_standard[FRP_VAR].notnull(), drop=True)

					if fire_events[FIRE_DIMENSION].size > 0:
						latitudes = fire_events[LATITUDE_VAR].values
						longitudes = fire_events[LONGITUDE_VAR].values
						frp_values = fire_events[FRP_VAR].values

						del fire_events

						# Almacenar las coordenadas y el valor de FRP
						for lat, lon, frp in zip(latitudes, longitudes, frp_values):
							fire_coordinates.append((lat, lon, frp))

						del latitudes
						del longitudes
						del frp_values
						ds_mwir_standard.close()
						del ds_mwir_standard
						nc_bytes.close()
						del nc_bytes
					else:
						logging.warning(f"No se encontraron eventos de incendio válidos en '{FRP_NETCDF_FILENAME}' para el producto: {product_identifier}")
				else:
					logging.warning(f"Variables o dimensión requeridas no encontradas en '{FRP_NETCDF_FILENAME}' para el producto: {product_identifier}")
			else:
				logging.warning(f"No se encontró el archivo '{FRP_NETCDF_FILENAME}' dentro del producto: {product_identifier}")
	except Exception as e:
		logging.warning(f"Error procesando el producto {product_identifier}: {e}")
	finally:
		if 'zip_buffer' in locals():
			zip_buffer.close()
			del zip_buffer

	return fire_coordinates

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia entre dos coordenadas usando la fórmula de Haversine.
    Devuelve la distancia en kilómetros.
    """
    R = 6371.0  # Radio de la Tierra en kilómetros

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

def findNearestFireEvent(target_lat, target_lon, fires_data):
    """
    Encuentra el evento de incendio más cercano a un punto de referencia dado
    en una lista de coordenadas de incendios.

    Args:
        target_lat (float): Latitud del punto de referencia.
        target_lon (float): Longitud del punto de referencia.
        lfires_data (list): Lista de tuplas (latitud, longitud, FRP) de eventos de incendio.

    Returns:
        tuple: Una tupla que contiene (distancia_km, latitud, longitud, FRP)
               del evento de incendio más cercano. None si la lista está vacía.
    """
    if not fires_data:
        return None

    min_distance = float('inf')
    nearest_fire = None

    for lat, lon, frp in fires_data:
        distance = haversine(target_lat, target_lon, lat, lon)
        if distance < min_distance:
            min_distance = distance
            nearest_fire = (min_distance, lat, lon, frp)

    return nearest_fire


def getNearestFire(consumer_key, consumer_secret, ref_lat, ref_lon, bbox):
	try:
		# Get time interval
		now = datetime.utcnow()        
		yesterday = now - timedelta(days=1)
		start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
		end_date = now.replace(hour=23, minute=59, second=59, microsecond=0)

		# Get products
		products = getProducts(consumer_key, consumer_secret, bbox, start_date, end_date, FIRE_SATELLITES)
		if not products:
			logging.info("Not EUMETSAT products found")
			return None
    
    	# Process products to get fires data
		fires_data = []
		for product in products:
			fires_data.extend(extractFireDataFromProduct(product))
		if not fires_data:
			logging.info("Not data fires found on products.")
			return None

    	# Find nearearest fire
		nearest_fire_data = findNearestFireEvent(ref_lat, ref_lon, fires_data)
		if not nearest_fire_data:
			logging.info("Unable to find nearest fire")
			return None

		distance, latitude, longitud, frp = nearest_fire_data
		return {
				"distance": round(distance, 1),
				"latitude": float(latitude),
				"longitud": float(longitud),
				"frp": int(frp)
		}
	except Exception as e:
		logging.error(f"Error at getNearestFire: {str(e)}")
		return None
