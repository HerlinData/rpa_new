# Scrapers del proyecto

from .sites.salesys.reports.rga import RGAScraper
from .sites.salesys.reports.estado_agente_v2 import EstadoAgenteV2Scraper

__all__ = [
    'RGAScraper',
    'EstadoAgenteV2Scraper'
]
