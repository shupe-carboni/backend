import re
from adp_models.model_series import ModelSeries, Fields
from utils.validator import Validator
from app.db import Database

DATABASE = Database('adp')


class CF(ModelSeries):
    text_len = (12,)
    regex = r'''
        (?P<series>CF)
        (?P<application>[C|P|W])
        (?P<ton>\d{2})
        (?P<motor>[C|V|X])
        (?P<scode>\D{2}\d|\D\d{2})
        (?P<heat>\d{2})
        (?P<voltage>\d)
    '''
    mappings = DATABASE.load_df('carrier_cf_label_mapping')
    def __init__(self, re_match: re.Match):
        super().__init__(re_match)
        self.tonnage = int(self.attributes['ton'])
        actual_model = self.mappings.loc[
            self.mappings['model_alias'] == str(self)[:-3],
            'model']
        if not actual_model.empty:
            actual_model = actual_model.item()
        else:
            actual_model = str()
        match self.attributes['application']:
            case 'C':
                from adp_models.F import F
                self.model_obj = Validator(
                    raw_text=actual_model,
                    model_series=F,
                ).is_model()
                self._record = self.model_obj.record()
            case 'P':
                from adp_models.B import B
                self.model_obj = Validator(
                    raw_text=actual_model,
                    model_series=B,
                ).is_model()
                self._record = self.model_obj.record()
            case 'W':
                from adp_models.S import S
                self.model_obj = Validator(
                    raw_text=actual_model,
                    model_series=S,
                ).is_model()
                self._record = self.model_obj.record()
            

    def record(self) -> dict:
        self._record.update({
            Fields.PRIVATE_LABEL.formatted(): str(self),
            Fields.CATEGORY.formatted(): self.model_obj.category(),
        })
        return self._record