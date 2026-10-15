"""
Módulo de views legado mantido para compatibilidade retroativa.
As views ativas e canônicas residem no pacote api_tcc.api.*.
"""

from api_tcc.api.views_ingestao import PrescricaoListView

__all__ = ["PrescricaoListView"]
