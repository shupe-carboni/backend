import re
from app.adp.adp_models.model_series import ModelSeries, Fields
from app.adp.utils.validator import Validator
from app.db import ADP_DB, Session

class CF(ModelSeries):
    text_len = (12,13)
    regex = r'''
        (?P<series>CF)
        (?P<application>[C|P|W])
        (?P<ton>\d{2})
        (?P<motor>[C|V|X])
        (?P<scode>\D{2}\d|\D\d{2})
        (?P<heat>\d{2})
        (?P<voltage>\d)
        (?P<rds>[N|R]?)
    '''
    def __init__(self, session: Session, re_match: re.Match):
        super().__init__(session, re_match)
        self.mappings = ADP_DB.load_df(session=session, table_name='carrier_cf_label_mapping')
        self.tonnage = int(self.attributes['ton'])
        if rds := self.attributes.get('rds',''):
            model_alias: str = str(self)[:-4] + rds
        else:
            model_alias: str = str(self)[:-3]

        actual_model = self.mappings.loc[
            self.mappings['model_alias'] == model_alias,
            'model']
        if not actual_model.empty:
            actual_model = actual_model.item()
        else:
            actual_model = str()
        match self.attributes['application']:
            case 'C':
                from app.adp.adp_models.F import F
                self.model_obj = Validator(
                    db_session=session,
                    raw_text=actual_model,
                    model_series=F,
                ).is_model()
                self._record = self.model_obj.record()
            case 'P':
                from app.adp.adp_models.B import B
                self.model_obj = Validator(
                    db_session=session,
                    raw_text=actual_model,
                    model_series=B,
                ).is_model()
                self._record = self.model_obj.record()
            case 'W':
                from app.adp.adp_models.S import S
                self.model_obj = Validator(
                    db_session=session,
                    raw_text=actual_model,
                    model_series=S,
                ).is_model()
                self._record = self.model_obj.record()
            

    def record(self) -> dict:
        self._record.update({
            Fields.PRIVATE_LABEL.value: str(self),
            Fields.CATEGORY.value: self.model_obj.category(),
        })
        return self._record