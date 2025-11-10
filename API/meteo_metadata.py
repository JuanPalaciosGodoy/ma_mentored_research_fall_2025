from enum import Enum

class HourlyWeather(Enum):
    """Hourly weather parameters"""
    TEMPERATURE_2M = "temperature_2m"
    RELATIVE_HUMIDITY_2M = "relative_humidity_2m"
    DEW_POINT_2M = "dewpoint_2m"
    APPARENT_TEMPERATURE = "apparent_temperature"
    PRESSURE_MSL = "pressure_msl"
    SURFACE_PRESSURE = "surface_pressure"
    CLOUD_COVER = "cloud_cover"
    CLOUD_COVER_LOW = "cloud_cover_low"
    CLOUD_COVER_MID = "cloud_cover_mid"
    CLOUD_COVER_HIGH = "cloud_cover_high"
    VISIBILITY = "visibility"
    EVAPOTRANSPIRATION = "evapotranspiration"
    ET0_FAO_EVAPOTRANSPIRATION = "et0_fao_evapotranspiration"
    VAPOUR_PRESSURE_DEFICIT = "vapour_pressure_deficit"
    WIND_SPEED_10M = "wind_speed_10m"
    WIND_SPEED_80M = "wind_speed_80m"
    WIND_SPEED_120M = "wind_speed_120m"
    WIND_SPEED_180M = "wind_speed_180m"
    WIND_DIRECTION_10M = "wind_direction_10m"
    WIND_DIRECTION_80M = "wind_direction_80m"
    WIND_DIRECTION_120M = "wind_direction_120m"
    WIND_DIRECTION_180M = "wind_direction_180m"
    WIND_GUSTS_10M = "wind_gusts_10m"
    SHORTWAVE_RADIATION = "shortwave_radiation"
    DIRECT_RADIATION = "direct_radiation"
    DIRECT_NORMAL_IRRADIANCE = "direct_normal_irradiance"
    DIFFUSE_RADIATION = "diffuse_radiation"
    GLOBAL_TILTED_IRRADIANCE = "global_tilted_irradiance"
    TERRESTRIAL_RADIATION = "terrestrial_radiation"
    SHORTWAVE_RADIATION_INSTANT = "shortwave_radiation_instant"
    DIRECT_RADIATION_INSTANT = "direct_radiation_instant"
    DIFFUSE_RADIATION_INSTANT = "diffuse_radiation_instant"
    DIRECT_NORMAL_IRRADIANCE_INSTANT = "direct_normal_irradiance_instant"
    GLOBAL_TILTED_IRRADIANCE_INSTANT = "global_tilted_irradiance_instant"
    TERRESTRIAL_RADIATION_INSTANT = "terrestrial_radiation_instant"
    PRECIPITATION = "precipitation"
    SNOWFALL = "snowfall"
    PRECIPITATION_PROBABILITY = "precipitation_probability"
    RAIN = "rain"
    SHOWERS = "showers"
    WEATHER_CODE = "weather_code"
    SNOW_DEPTH = "snow_depth"
    FREEZING_LEVEL_HEIGHT = "freezing_level_height"
    CAPE = "cape"
    LIFTED_INDEX = "lifted_index"
    SOIL_TEMPERATURE_0CM = "soil_temperature_0cm"
    SOIL_TEMPERATURE_6CM = "soil_temperature_6cm"
    SOIL_TEMPERATURE_18CM = "soil_temperature_18cm"
    SOIL_TEMPERATURE_54CM = "soil_temperature_54cm"
    SOIL_MOISTURE_0_1CM = "soil_moisture_0_to_1cm"
    SOIL_MOISTURE_1_3CM = "soil_moisture_1_to_3cm"
    SOIL_MOISTURE_3_9CM = "soil_moisture_3_to_9cm"
    SOIL_MOISTURE_9_27CM = "soil_moisture_9_to_27cm"
    SOIL_MOISTURE_27_81CM = "soil_moisture_27_to_81cm"


class DailyWeather(Enum):
    """Daily weather parameters"""
    MAX_TEMP = "temperature_2m_max"
    MIN_TEMP = "temperature_2m_min"
    APPARENT_TEMPERATURE_MAX = "apparent_temperature_max"
    APPARENT_TEMPERATURE_MIN = "apparent_temperature_min"
    PRECIPITATION_SUM = "precipitation_sum"
    RAIN_SUM = "rain_sum"
    SHOWERS_SUM = "showers_sum"
    SNOWFALL_SUM = "snowfall_sum"
    PRECIPITATION_HOURS = "precipitation_hours"
    PRECIPITATION_PROBABILITY_MAX = "precipitation_probability_max"
    PRECIPITATION_PROBABILITY_MIN = "precipitation_probability_min"
    PRECIPITATION_PROBABILITY_MEAN = "precipitation_probability_mean"
    WEATHER_CODE = "weather_code"
    SUNRISE = "sunrise"
    SUNSET = "sunset"
    SUNSHINE_DURATION = "sunshine_duration"
    DAYLIGHT_DURATION = "daylight_duration"
    WIND_SPEED_10M_MAX = "wind_speed_10m_max"
    WIND_GUSTS_10M_MAX = "wind_gusts_10m_max"
    WIND_DIRECTION_10M_DOMINANT = "wind_direction_10m_dominant"
    SHORTWAVE_RADIATION_SUM = "shortwave_radiation_sum"
    ET0_FAO_EVAPOTRANSPIRATION = "et0_fao_evapotranspiration"
    UV_INDEX_MAX = "uv_index_max"
    UV_INDEX_CLEAR_SKY_MAX = "uv_index_clear_sky_max"


class CurrentWeather(Enum):
    """Current weather parameters"""
    TEMPERATURE_2M = "temperature_2m"
    RELATIVE_HUMIDITY_2M = "relative_humidity_2m"
    APPARENT_TEMPERATURE = "apparent_temperature"
    IS_DAY = "is_day"
    PRECIPITATION = "precipitation"
    RAIN = "rain"
    SHOWERS = "showers"
    SNOWFALL = "snowfall"
    WEATHER_CODE = "weather_code"
    CLOUD_COVER = "cloud_cover"
    PRESSURE_MSL = "pressure_msl"
    SURFACE_PRESSURE = "surface_pressure"
    WIND_SPEED_10M = "wind_speed_10m"
    WIND_DIRECTION_10M = "wind_direction_10m"
    WIND_GUSTS_10M = "wind_gusts_10m"


class MinutelyWeather(Enum):
    """15-Minutely weather parameters"""
    TEMPERATURE_2M = "temperature_2m"
    RELATIVE_HUMIDITY_2M = "relative_humidity_2m"
    DEW_POINT_2M = "dewpoint_2m"
    APPARENT_TEMPERATURE = "apparent_temperature"
    SHORTWAVE_RADIATION = "shortwave_radiation"
    DIRECT_RADIATION = "direct_radiation"
    DIFFUSE_RADIATION = "diffuse_radiation"
    DIRECT_NORMAL_IRRADIANCE = "direct_normal_irradiance"
    GLOBAL_TILTED_IRRADIANCE = "global_tilted_irradiance"
    PRECIPITATION = "precipitation"
    SNOWFALL = "snowfall"
    RAIN = "rain"
    SHOWERS = "showers"
    SNOWFALL_HEIGHT = "snowfall_height"
    FREEZING_LEVEL_HEIGHT = "freezing_level_height"
    CAPE = "cape"
    WIND_SPEED_10M = "wind_speed_10m"
    WIND_SPEED_80M = "wind_speed_80m"
    WIND_DIRECTION_10M = "wind_direction_10m"
    WIND_DIRECTION_80M = "wind_direction_80m"
    WIND_GUSTS_10M = "wind_gusts_10m"
    VISIBILITY = "visibility"
    WEATHER_CODE = "weather_code"


class AirQuality(Enum):
    """Air quality parameters"""
    PM10 = "pm10"
    PM2_5 = "pm2_5"
    CARBON_MONOXIDE = "carbon_monoxide"
    NITROGEN_DIOXIDE = "nitrogen_dioxide"
    SULPHUR_DIOXIDE = "sulphur_dioxide"
    OZONE = "ozone"
    AEROSOL_OPTICAL_DEPTH = "aerosol_optical_depth"
    DUST = "dust"
    UV_INDEX = "uv_index"
    UV_INDEX_CLEAR_SKY = "uv_index_clear_sky"
    AMMONIA = "ammonia"
    ALDER_POLLEN = "alder_pollen"
    BIRCH_POLLEN = "birch_pollen"
    GRASS_POLLEN = "grass_pollen"
    MUGWORT_POLLEN = "mugwort_pollen"
    OLIVE_POLLEN = "olive_pollen"
    RAGWEED_POLLEN = "ragweed_pollen"
    EUROPEAN_AQI = "european_aqi"
    EUROPEAN_AQI_PM2_5 = "european_aqi_pm2_5"
    EUROPEAN_AQI_PM10 = "european_aqi_pm10"
    EUROPEAN_AQI_NO2 = "european_aqi_nitrogen_dioxide"
    EUROPEAN_AQI_O3 = "european_aqi_ozone"
    EUROPEAN_AQI_SO2 = "european_aqi_sulphur_dioxide"
    US_AQI = "us_aqi"
    US_AQI_PM2_5 = "us_aqi_pm2_5"
    US_AQI_PM10 = "us_aqi_pm10"
    US_AQI_NO2 = "us_aqi_nitrogen_dioxide"
    US_AQI_O3 = "us_aqi_ozone"
    US_AQI_SO2 = "us_aqi_sulphur_dioxide"
    US_AQI_CO = "us_aqi_carbon_monoxide"


class MarineWeather(Enum):
    """Marine weather parameters"""
    WAVE_HEIGHT = "wave_height"
    WAVE_DIRECTION = "wave_direction"
    WAVE_PERIOD = "wave_period"
    WIND_WAVE_HEIGHT = "wind_wave_height"
    WIND_WAVE_DIRECTION = "wind_wave_direction"
    WIND_WAVE_PERIOD = "wind_wave_period"
    WIND_WAVE_PEAK_PERIOD = "wind_wave_peak_period"
    SWELL_WAVE_HEIGHT = "swell_wave_height"
    SWELL_WAVE_DIRECTION = "swell_wave_direction"
    SWELL_WAVE_PERIOD = "swell_wave_period"
    SWELL_WAVE_PEAK_PERIOD = "swell_wave_peak_period"
    OCEAN_CURRENT_VELOCITY = "ocean_current_velocity"
    OCEAN_CURRENT_DIRECTION = "ocean_current_direction"


class FloodParameters(Enum):
    """Flood forecast parameters"""
    RIVER_DISCHARGE = "river_discharge"
    RIVER_DISCHARGE_MEAN = "river_discharge_mean"
    RIVER_DISCHARGE_MEDIAN = "river_discharge_median"
    RIVER_DISCHARGE_MAX = "river_discharge_max"
    RIVER_DISCHARGE_MIN = "river_discharge_min"
    RIVER_DISCHARGE_P25 = "river_discharge_p25"
    RIVER_DISCHARGE_P75 = "river_discharge_p75"


class WeatherModels(Enum):
    """Weather forecast models"""
    BEST_MATCH = "best_match"
    ECMWF_IFS04 = "ecmwf_ifs04"
    METNO_NORDIC = "metno_nordic"
    GFS_SEAMLESS = "gfs_seamless"
    GFS_GLOBAL = "gfs_global"
    GFS_HRRR = "gfs_hrrr"
    JMA_SEAMLESS = "jma_seamless"
    JMA_MSM = "jma_msm"
    JMA_GSM = "jma_gsm"
    ICON_SEAMLESS = "icon_seamless"
    ICON_GLOBAL = "icon_global"
    ICON_EU = "icon_eu"
    ICON_D2 = "icon_d2"
    GEM_SEAMLESS = "gem_seamless"
    GEM_GLOBAL = "gem_global"
    GEM_REGIONAL = "gem_regional"
    GEM_HRDPS_CONTINENTAL = "gem_hrdps_continental"
    METEOFRANCE_SEAMLESS = "meteofrance_seamless"
    METEOFRANCE_ARPEGE_WORLD = "meteofrance_arpege_world"
    METEOFRANCE_ARPEGE_EUROPE = "meteofrance_arpege_europe"
    METEOFRANCE_AROME_FRANCE = "meteofrance_arome_france"
    METEOFRANCE_AROME_FRANCE_HD = "meteofrance_arome_france_hd"
    ARPAE_COSMO_SEAMLESS = "arpae_cosmo_seamless"
    ARPAE_COSMO_2I = "arpae_cosmo_2i"
    ARPAE_COSMO_2I_RUC = "arpae_cosmo_2i_ruc"
    ARPAE_COSMO_5M = "arpae_cosmo_5m"


class TemperatureUnit(Enum):
    """Temperature units"""
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"


class WindSpeedUnit(Enum):
    """Wind speed units"""
    KMH = "kmh"
    MS = "ms"
    MPH = "mph"
    KN = "kn"


class PrecipitationUnit(Enum):
    """Precipitation units"""
    MM = "mm"
    INCH = "inch"


class TimeFormat(Enum):
    """Time format options"""
    ISO8601 = "iso8601"
    UNIXTIME = "unixtime"

from enum import Enum

class Timezone(Enum):
    """Common timezones supported by Open-Meteo"""
    # Auto-detect
    AUTO = "auto"
    
    # GMT/UTC
    GMT = "GMT"
    UTC = "UTC"
    
    # Europe
    EUROPE_LONDON = "Europe/London"
    EUROPE_PARIS = "Europe/Paris"
    EUROPE_BERLIN = "Europe/Berlin"
    EUROPE_ROME = "Europe/Rome"
    EUROPE_MADRID = "Europe/Madrid"
    EUROPE_AMSTERDAM = "Europe/Amsterdam"
    EUROPE_BRUSSELS = "Europe/Brussels"
    EUROPE_VIENNA = "Europe/Vienna"
    EUROPE_WARSAW = "Europe/Warsaw"
    EUROPE_ATHENS = "Europe/Athens"
    EUROPE_BUDAPEST = "Europe/Budapest"
    EUROPE_PRAGUE = "Europe/Prague"
    EUROPE_STOCKHOLM = "Europe/Stockholm"
    EUROPE_OSLO = "Europe/Oslo"
    EUROPE_COPENHAGEN = "Europe/Copenhagen"
    EUROPE_HELSINKI = "Europe/Helsinki"
    EUROPE_DUBLIN = "Europe/Dublin"
    EUROPE_LISBON = "Europe/Lisbon"
    EUROPE_MOSCOW = "Europe/Moscow"
    EUROPE_ISTANBUL = "Europe/Istanbul"
    EUROPE_KIEV = "Europe/Kiev"
    EUROPE_BUCHAREST = "Europe/Bucharest"
    EUROPE_ZURICH = "Europe/Zurich"
    
    # America - North
    AMERICA_NEW_YORK = "America/New_York"
    AMERICA_CHICAGO = "America/Chicago"
    AMERICA_DENVER = "America/Denver"
    AMERICA_LOS_ANGELES = "America/Los_Angeles"
    AMERICA_ANCHORAGE = "America/Anchorage"
    AMERICA_PHOENIX = "America/Phoenix"
    AMERICA_TORONTO = "America/Toronto"
    AMERICA_VANCOUVER = "America/Vancouver"
    AMERICA_MEXICO_CITY = "America/Mexico_City"
    AMERICA_MONTREAL = "America/Montreal"
    AMERICA_HALIFAX = "America/Halifax"
    
    # America - South
    AMERICA_SAO_PAULO = "America/Sao_Paulo"
    AMERICA_BUENOS_AIRES = "America/Buenos_Aires"
    AMERICA_SANTIAGO = "America/Santiago"
    AMERICA_BOGOTA = "America/Bogota"
    AMERICA_LIMA = "America/Lima"
    AMERICA_CARACAS = "America/Caracas"
    
    # Asia
    ASIA_TOKYO = "Asia/Tokyo"
    ASIA_SHANGHAI = "Asia/Shanghai"
    ASIA_HONG_KONG = "Asia/Hong_Kong"
    ASIA_SINGAPORE = "Asia/Singapore"
    ASIA_SEOUL = "Asia/Seoul"
    ASIA_BANGKOK = "Asia/Bangkok"
    ASIA_JAKARTA = "Asia/Jakarta"
    ASIA_MANILA = "Asia/Manila"
    ASIA_DUBAI = "Asia/Dubai"
    ASIA_KOLKATA = "Asia/Kolkata"
    ASIA_KARACHI = "Asia/Karachi"
    ASIA_DHAKA = "Asia/Dhaka"
    ASIA_TEHRAN = "Asia/Tehran"
    ASIA_JERUSALEM = "Asia/Jerusalem"
    ASIA_RIYADH = "Asia/Riyadh"
    ASIA_KABUL = "Asia/Kabul"
    ASIA_TAIPEI = "Asia/Taipei"
    ASIA_KUALA_LUMPUR = "Asia/Kuala_Lumpur"
    
    # Australia & Pacific
    AUSTRALIA_SYDNEY = "Australia/Sydney"
    AUSTRALIA_MELBOURNE = "Australia/Melbourne"
    AUSTRALIA_BRISBANE = "Australia/Brisbane"
    AUSTRALIA_PERTH = "Australia/Perth"
    AUSTRALIA_ADELAIDE = "Australia/Adelaide"
    PACIFIC_AUCKLAND = "Pacific/Auckland"
    PACIFIC_FIJI = "Pacific/Fiji"
    PACIFIC_HONOLULU = "Pacific/Honolulu"
    
    # Africa
    AFRICA_CAIRO = "Africa/Cairo"
    AFRICA_JOHANNESBURG = "Africa/Johannesburg"
    AFRICA_LAGOS = "Africa/Lagos"
    AFRICA_NAIROBI = "Africa/Nairobi"
    AFRICA_CASABLANCA = "Africa/Casablanca"
    AFRICA_ALGIERS = "Africa/Algiers"


class TemperatureUnit(Enum):
    """Temperature units"""
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"


class WindSpeedUnit(Enum):
    """Wind speed units"""
    KMH = "kmh"           # Kilometers per hour
    MS = "ms"             # Meters per second
    MPH = "mph"           # Miles per hour
    KN = "kn"             # Knots


class PrecipitationUnit(Enum):
    """Precipitation units"""
    MM = "mm"             # Millimeters
    INCH = "inch"         # Inches


class TimeFormat(Enum):
    """Time format options"""
    ISO8601 = "iso8601"   # ISO 8601 format (e.g., 2024-01-15T12:00)
    UNIXTIME = "unixtime" # Unix timestamp


class CellSelection(Enum):
    """Cell selection method for location"""
    LAND = "land"         # Select land cell
    SEA = "sea"           # Select sea cell
    NEAREST = "nearest"   # Select nearest cell (default)


class PressureLevel(Enum):
    """Atmospheric pressure levels in hPa"""
    LEVEL_1000 = "1000hPa"
    LEVEL_975 = "975hPa"
    LEVEL_950 = "950hPa"
    LEVEL_925 = "925hPa"
    LEVEL_900 = "900hPa"
    LEVEL_850 = "850hPa"
    LEVEL_800 = "800hPa"
    LEVEL_700 = "700hPa"
    LEVEL_600 = "600hPa"
    LEVEL_500 = "500hPa"
    LEVEL_400 = "400hPa"
    LEVEL_300 = "300hPa"
    LEVEL_250 = "250hPa"
    LEVEL_200 = "200hPa"
    LEVEL_150 = "150hPa"
    LEVEL_100 = "100hPa"
    LEVEL_70 = "70hPa"
    LEVEL_50 = "50hPa"
    LEVEL_30 = "30hPa"


class PressureLevelVariable(Enum):
    """Variables available at pressure levels"""
    TEMPERATURE = "temperature"
    RELATIVE_HUMIDITY = "relative_humidity"
    CLOUD_COVER = "cloud_cover"
    WIND_SPEED = "wind_speed"
    WIND_DIRECTION = "wind_direction"
    GEOPOTENTIAL_HEIGHT = "geopotential_height"
    DEWPOINT = "dewpoint"


class LengthUnit(Enum):
    """Length/distance units"""
    METRIC = "metric"     # Meters, kilometers
    IMPERIAL = "imperial" # Feet, miles


class VisibilityUnit(Enum):
    """Visibility units"""
    KM = "km"             # Kilometers
    MILES = "miles"       # Miles
    METERS = "m"          # Meters
    FEET = "ft"           # Feet


class ForecastDays(Enum):
    """Number of forecast days (for some APIs)"""
    DAYS_1 = "1"
    DAYS_3 = "3"
    DAYS_5 = "5"
    DAYS_7 = "7"
    DAYS_10 = "10"
    DAYS_14 = "14"
    DAYS_16 = "16"


class PastDays(Enum):
    """Number of past days to include"""
    DAYS_0 = "0"
    DAYS_1 = "1"
    DAYS_2 = "2"
    DAYS_3 = "3"
    DAYS_5 = "5"
    DAYS_7 = "7"
    DAYS_14 = "14"
    DAYS_31 = "31"
    DAYS_61 = "61"
    DAYS_92 = "92"


class APIResponseFormat(Enum):
    """API response format"""
    JSON = "json"
    PROTOBUF = "protobuf"


class TiltAngle(Enum):
    """Solar panel tilt angles for radiation calculations"""
    ANGLE_0 = "0"
    ANGLE_15 = "15"
    ANGLE_30 = "30"
    ANGLE_45 = "45"
    ANGLE_60 = "60"
    ANGLE_75 = "75"
    ANGLE_90 = "90"


class AzimuthAngle(Enum):
    """Solar panel azimuth angles (0=North, 90=East, 180=South, 270=West)"""
    NORTH = "0"
    NORTHEAST = "45"
    EAST = "90"
    SOUTHEAST = "135"
    SOUTH = "180"
    SOUTHWEST = "225"
    WEST = "270"
    NORTHWEST = "315"


class ElevationModel(Enum):
    """Digital elevation models"""
    SRTM90 = "srtm90"     # 90m resolution
    COPERNICUS30 = "copernicus_30"  # 30m resolution
    COPERNICUS90 = "copernicus_90"  # 90m resolution


class MarineModel(Enum):
    """Marine forecast models"""
    BEST_MATCH = "best_match"
    EWAM = "ewam"
    MFWAM = "mfwam"
    GWAM = "gwam"


class AirQualityModel(Enum):
    """Air quality forecast models"""
    BEST_MATCH = "best_match"
    CAMS_EUROPE = "cams_europe"
    CAMS_GLOBAL = "cams_global"


class ClimateModel(Enum):
    """Climate projection models"""
    CMCC_CM2_VHR4 = "CMCC_CM2_VHR4"
    FGOALS_F3_H = "FGOALS_f3_H"
    HiRAM_SIT_HR = "HiRAM_SIT_HR"
    MRI_AGCM3_2_S = "MRI_AGCM3_2_S"
    EC_EARTH3P_HR = "EC_Earth3P_HR"
    MPI_ESM1_2_XR = "MPI_ESM1_2_XR"
    NICAM16_8S = "NICAM16_8S"


class ClimateScenario(Enum):
    """Climate change scenarios"""
    SSP126 = "ssp126"     # Low emissions
    SSP245 = "ssp245"     # Medium emissions
    SSP370 = "ssp370"     # High emissions
    SSP585 = "ssp585"     # Very high emissions


class Ensemble(Enum):
    """Ensemble member selection"""
    MEAN = "mean"
    MEDIAN = "median"
    SPREAD = "spread"
    ALL = "all"