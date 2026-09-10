import logging  
from datetime import datetime  
from django.utils.timezone import make_aware, is_aware  
from django.db import IntegrityError  
from api_tcc.models import LeituraTelemetria, Colheitadeira, Machine  
  
logger = logging.getLogger(__name__)  
