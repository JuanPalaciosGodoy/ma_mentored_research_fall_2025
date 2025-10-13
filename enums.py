from enum import Enum

class Markets(Enum):
    ELECTRICITY = "electricity"
    COAL = "coal"
    CRUDE_OIL_IMPORTS = "crude-oil-imports"
    NATURAL_GAS = "natural-gas"
    INTERNATIONAL = "international"


class Route(Enum):
    RTO = "rto"
    STATE_ELECTRICITY_PROFILES = "state-electricity-profiles" # State Specific Data
    RETAIL_SALES = "retail-sales" # Electricity Sales to Ultimate Customers
    OPERATING_GENERATOR_CAPACITY = "operating-generator-capacity" # Inventory of Operable Generators
    FACILITY_FUEL = "facility-fuel" # Electric Power for Operations for Individiual Power Plants
    ELECTRIC_POWER_OPERATIONAL_DATA = "electric-power-operational-data" # Electric Power Operations (Annual and Monthly)

class MarketUrl(Enum):
    # rto
    RETAIL_SALES = "retail-sales"
    ELECTRIC_POWER_OPERATIONAL_DATA = "electric-power-operational-data"
    FUEL_TYPE_DATA = "fuel-type-data" # Hourly Generation by Energy Source
    INTERCHANGE_DATA = "interchange-data" # Hourly Interchange By Neighboring Balancing Authority
    REGION_DATA = "region-data" # Hourly Demand, Demand Forecast, Generation, And Interchange
    REGION_SUB_BA_DATA = "region-sub-ba-data" # Hourly Generation by Sub Region
    DAILY_REGION_DATA = "daily-region-data" # Daily Demand, Demand Forecast, Generation And Interchange
    DAILY_FUEL_TYPE_DATA = "daily-fuel-type-data" # Daily Generation by Energy Source
    DAILY_INTERCHANGE_DATA = "daily-interchange-data" # Hourly Interchange By Neighboring Balancing Authority
    DAILY_REGION_SUB_BA_DATA = "daily-region-sub-ba-data" # Hourly Generation by Sub Region

    # state-electricity-profiles
    EMISSIONS_BY_STATE_DATE = "emissions-by-state-by-fuel" # Emissions from Energy Consumption at Conventional...
    SOURCE_DISPOSITION = "source-disposition" # Supply and Disposition of Electricity
    CAPABILITY = "capability" # Generating Capacity
    ENERGY_EFFICIENCY = "energy-efficiency" # Costs and Savings From Energy Efficiency Programs
    METERS = "meters" # Advanced Metering Infraestructure
    NET_METERING = "net-metering" # Electricity Net Metering: Customers and Capacity
    SUMMARY = "summary" # State Ranking for Key Statistics

METADATA = {
    Markets.ELECTRICITY.value: {
        Route.FACILITY_FUEL.value: {
            "frequency": {
                1: "monthly",
                2: "quarterly",
                3: "annual"
            },
            "data": {
                1: "average-heat-content",
                2: "consumption-for-eg",
                3: "consumption-for-eg-btu",
                4: "generation",
                5: "gross-generation",
                6: "total-consumption",
                7: "total-consumption-btu"
            }
        },
        Route.OPERATING_GENERATOR_CAPACITY.value: {
            "frequency": {
                1: "monthly"
            },
            "data": {
                1: "county",
                2: "latitude",
                3: "longitude",
                4: "nameplate-capacity-mw",
                5: "net-summer-capacity-mw",
                6: "net-winter-capacity-mw",
                7: "operating-year-month",
                8: "planned-derate-summer-cap-mw",
                9: "planned-derate-year-month",
                10: "planned-retirement-year-month",
                11: "planned-uprate-summer-cap-mw",
                12: "planned-uprate-year-month"
            }
        },
        Route.RETAIL_SALES.value: {
            "frequency" :{
                1: "monthly",
                2: "quarterly",
                3: "annual"
            },
            "data": {
                1: "customers",
                2: "price",
                3: "revenue",
                4: "sales"
            }
        },
        Route.RTO.value: {
            MarketUrl.DAILY_REGION_SUB_BA_DATA.value: {
                "frequency": {
                    1: "daily"
                },
                "data": {
                    1: "value"
                }
            },
            MarketUrl.DAILY_INTERCHANGE_DATA.value: {
                "frequency": {
                    1: "daily"
                },
                "data": {
                    1: "value"
                }
            },
            MarketUrl.DAILY_FUEL_TYPE_DATA.value: {
                "frequency": {
                    1: "daily"
                },
                "data": {
                    1: "value"
                }
            },
            MarketUrl.DAILY_REGION_DATA.value: {
                "frequency": {
                    1: "daily"
                },
                "data": {
                    1: "value"
                }
            },
            MarketUrl.REGION_DATA.value: {
                "frequency": {
                    1: "hourly",
                    2: "local-hourly"
                },
                "data": {
                    1: "value"
                }
            },
            MarketUrl.FUEL_TYPE_DATA.value: {
                "frequency": {
                    1: "hourly",
                    2: "local-hourly"
                },
                "data": {
                    1: "value"
                }
            },
            MarketUrl.REGION_SUB_BA_DATA.value: {
                "frequency": {
                    1: "hourly",
                    2: "local-hourly"
                },
                "data": {
                    1: "value"
                }
            },
            MarketUrl.INTERCHANGE_DATA.value: {
                "frequency": {
                    1: "hourly",
                    2: "local-hourly"
                },
                "data": {
                    1: "value"
                }
            }
        },
        Route.ELECTRIC_POWER_OPERATIONAL_DATA.value: {
            "frequency": {
                1: "annual",
                2: "quarterly",
                3: "monthly"
            },
            "data": {
                1: "ash-content",
                2: "consumption-for-eg",
                3: "consumption-for-eg-btu",
                4: "consumption-uto",
                5: "consumption-uto-btu",
                6: "cost",
                7: "cost-per-btu",
                8: "generation",
                9: "heat-content",
                10: "receipts",
                11: "receipts-btu",
                12: "stocks",
                13: "sulfur-content",
                14: "total-consumption",
                15: "total-consumption-btu"
            }
        },
        Route.STATE_ELECTRICITY_PROFILES.value: {
            MarketUrl.SUMMARY.value: {
                "frequency": "annual",
                "data": {
                    1: "average-retail-price",
                    2: "average-retail-price-rank",
                    3: "capacity-elec-utilities",
                    4: "capacity-elect-utilities-rank",
                    5: "capacity-ipp",
                    6: "capacity-ipp-rank",
                    7: "carbon-dioxide",
                    8: "carbon-dioxide-lbs",
                    9: "carbon-dioxide-rank",
                    10: "carbon-dioxide-rank-lbs",
                    11: "direct-use",
                    12: "direct-use-rank",
                    13: "eop-sales",
                    14: "eop-sales-rank",
                    15: "fsp-sales-rank",
                    16: "fsp-service-provider-sales",
                    17: "generation-elect-utils",
                    18: "generation-elect-utils-rank",
                    19: "generation-ipp",
                    20: "generation-ipp-rank",
                    21: "net-generation",
                    22: "net-generation-rank",
                    23: "net-summer-capacity",
                    24: "net-summer-capacity-rank",
                    25: "nitrogen-oxide",
                    26: "nitrogen-oxide-lbs",
                    27: "nitrogen-oxide-rank",
                    28: "nitrogen-oxide-rank-lbs",
                    29: "prime-source",
                    30: "sulfer-dioxide",
                    31: "sulfer-dioxide-lbs",
                    32: "sulfer-dioxide-rank",
                    33: "sulfer-dioxide-rank-lbs",
                    34: "total-retail-sales",
                    35: "total-retail-sales-rank"
                }
            },
            MarketUrl.METERS.value: {
                "frequency": {
                    1: "annual",
                },
                "data": {
                    1: "meters"
                }
            },
            MarketUrl.NET_METERING.value: {
                "frequency": {
                    1: "annual",
                },
                "data": {
                    1: "capacity",
                    2: "customers"
                }
            },
            MarketUrl.ENERGY_EFFICIENCY.value: {
                "frequency": {
                    1: "annual",
                },
                "data": {
                    1: "all-other-costs",
                    2: "customer-incentive",
                    3: "energy-savings",
                    4: "potential-peak-savings"
                }
            },
            MarketUrl.CAPABILITY.value: {
                "frequency": {
                    1: "annual",
                },
                "data": {
                    1: "capability"
                }
            },
            MarketUrl.EMISSIONS_BY_STATE_DATE.value :{
                "frequency": {
                    1: "annual",
                },
                "data": {
                    1: "co2-rate-lbs-mwh",
                    2: "co2-thousand-metric-tons",
                    3: "nox-rate-lbs-mwh",
                    4: "nox-short-tons",
                    5: "so2-rate-lbs-mwh",
                    6: "so2-short-tons",
                }
            },
            MarketUrl.SOURCE_DISPOSITION.value: {
                "frequency": {
                    1: "annual",
                },
                "data": {
                    1: "combined-heat-and-pwr-comm",
                    2: "combined-heat-and-pwr-elect",
                    3: "combined-heat-and-pwr-indust",
                    4: "direct-use",
                    5: "elect-pwr-sector-gen-subtotal",
                    6: "electric-utilities",
                    7: "energy-only-providers",
                    8: "estimated-losses",
                    9: "facility-direct",
                    10: "full-service-providers",
                    11: "independent-power-producers",
                    12: "indust-and-comm-gen-subtotal",
                    13: "net-interstate-trade",
                    14: "net-trade-index",
                    15: "total-disposition",
                    16: "total-elect-indust",
                    17: "total-international-exports",
                    18: "total-international-imports",
                    19: "total-net-generation",
                    20: "total-supply",
                    21: "unaccounted"
                }
            }
        }
    }
}