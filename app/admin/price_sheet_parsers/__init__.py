import app.admin.price_sheet_parsers.adp.parts as adp_parts
import app.admin.price_sheet_parsers.adp.SC as SC
import app.admin.price_sheet_parsers.adp.HD as HD
import app.admin.price_sheet_parsers.adp.V as V
import app.admin.price_sheet_parsers.adp.MH as MH
import app.admin.price_sheet_parsers.adp.HH as HH
import app.admin.price_sheet_parsers.adp.HE as HE
import app.admin.price_sheet_parsers.adp.AMH as AMH
import app.admin.price_sheet_parsers.adp.S as S
import app.admin.price_sheet_parsers.adp.F as F
import app.admin.price_sheet_parsers.adp.B as B
import app.admin.price_sheet_parsers.adp.CP as CP

adp_parts_sheet = adp_parts.adp_parts_sheet_parser
adp_sc_series_sheet = SC.adp_coils_sc_sheet_parser
adp_hd_series_sheet = HD.adp_coils_hd_sheet_parser
adp_v_series_sheet = V.adp_coils_v_sheet_parser
adp_mh_series_sheet = MH.adp_coils_mh_sheet_parser
adp_hh_series_sheet = HH.adp_coils_hh_sheet_parser
adp_he_series_sheet = HE.adp_coils_he_sheet_parser
adp_amh_series_sheet = AMH.adp_ahs_amh_sheet_parser
adp_s_series_sheet = S.adp_ahs_s_sheet_parser
adp_f_series_sheet = F.adp_ahs_f_sheet_parser
adp_b_series_sheet = B.adp_ahs_b_sheet_parser
adp_cp_series_sheet = CP.adp_ahs_cp_series_handler

__all__ = [
    adp_parts_sheet,
    adp_sc_series_sheet,
    adp_hd_series_sheet,
    adp_sc_series_sheet,
    adp_v_series_sheet,
    adp_hh_series_sheet,
    adp_he_series_sheet,
    adp_amh_series_sheet,
    adp_s_series_sheet,
    adp_f_series_sheet,
    adp_b_series_sheet,
    adp_cp_series_sheet,
]
