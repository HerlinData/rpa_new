# Scrapers del proyecto

from .sites.salesys.reports.rga import RGAScraper
from .sites.salesys.reports.nomina import NominaScraper

__all__ = [
    'RGAScraper',
    'NominaScraper'
]
