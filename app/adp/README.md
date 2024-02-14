# ADP Program Extraction and Reformatting
This utility takes any file that contains ADP model numbers and ratings
and extracts them into a database.

Every Model Number is tagged with
* the name of the file it came from (or "program")
* the name of the sheet it was on
* the universal name of the customer for which the program is for

In addition, reference files are used to generate feature values, a category name, and pricing.

**These include**
* Material Group
* Series
* Tonnage
* Pallet Qty
* Minimum Qty
* Width
* Depth (or Length)
* Height
* Weight
* Metering Device
* Cabinet
* Zero Discount Price
* Material Group Discount**
* Material Group Net Price**
* SNP Discount**
* SNP Price**
* Net Price**
***Customer-specific*

Ratings are extracted by looking for certain names used as column
headers, and taking everything underneath it that looks like ratings information.

Using a reference database of registered ratings from ADP, the actual ratings values of the extracted ratings are matched either by AHRI Number or the model numbers (if no AHRI number was present in the document from which the ratings were extracted.)

Once extracted, new program files can be generated programatically using templates.

## Extraction
### Product Models
Extraction is done file by file, sheet by sheet, iterating through every cell in every row and checking if the contents are a model-like string. This is done with regex contained within an Object representing the ADP product series.

Example of HE Series (i.e. HG30924D145B1205AP)
```python
class HE(ModelSeries):
    text_len = (18,)
    regex = r'''
        (?P<paint>[H|A|G|J|N|P|R|T|Y])
        (?P<mat>[E|G])
        (?P<scode>\d{2}|\d\D)
        (?P<meter>\d)
        (?P<ton>\d{2})
        (?P<depth>[A|C|D|E])
        (?P<width>\d{3})
        (?P<notch>B)
        (?P<height>\d{2})
        (?P<config>\d{2})
        (?P<AP>AP)
    '''
    ...
```
The regex in every model series leverages [named capture groups](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Regular_expressions/Named_capturing_group) for each component of the model number, as described by the model nomenclature.

Named Capture Groups are exported nicely into a dictionary upon instantiation of the ModelSeries object and persisted as `attributes`
```python
# adp-models/model_series.py

class ModelSeries()
    def __init__(self, re_match: re.Match):
        self.attributes = re_match.groupdict()

    ...
```

Once a match is made to one of these models, reference files and objects are used to define all features (cabinet color, w/d/h, orientation, etc.) as well as the zero discount price. Some mappings are contained in the parent `ModelSeries` class so that they are available to all series, and some are local to only a particular series.

Example of some cross references set up for HE Series:
```python
# adp-models/models.py

class HE(ModelSeries)
    ...
    pallet_qtys = pd.read_csv('./specs/he-pallet-qty.csv')
    weights = pd.read_csv('./specs/he-weights.csv')

    mat_config_map = {
        'E': {
            '01': 'CU_VERT',
            '05': 'CU_VERT',
            '20': 'CU_MP',
            '22': 'CU_MP',
        },
        'G': {
            '01': 'AL_VERT',
            '05': 'AL_VERT',
            '20': 'AL_MP',
            '22': 'AL_MP',
        },
    }
    orientations = {
        '00': ('Right Hand', 'Uncased'),
        '04': ('Left Hand', 'Uncased'),
        '01': ('Right Hand', 'Upflow'),
        '05': ('Left Hand', 'Upflow'),
        '20': ('Right Hand', 'Multiposition'),
        '22': ('Left Hand', 'Multiposition'),
    }
    ...
```
And some examples of using the information in `attributes` to start defining features
```python
# adp-models/models.py

class HE(ModelSeries)
    ...
    def __init__(self, re_match: re.Match):
        super().__init__(re_match) # initializes attributes
        if self.attributes['paint'] == 'H':
            self.cabinet_config = Cabinet.EMBOSSED
        else:
            self.cabinet_config = Cabinet.PAINTED
        width: int = int(self.attributes['width'])
        height: int = int(self.attributes['height'])
        if width % 10 == 2:
            self.width = width/10 + 0.05
        else:
            self.width = width/10
        self.depth = self.coil_depth_mapping[self.attributes['depth']]
        self.height = height + 0.5 if self.depth != 'uncased' else height
        self.material = self.material_mapping[self.attributes['mat']]
        self.metering = self.metering_mapping[int(self.attributes['meter'])]
    ...
```
Every `ModelSeries` object implements its own `record` method, which instantiates a standard `dict` object by updating the `ModelSeries` implementation of `record`, in which all possible columns are contained and set to `None`, and updates only relevant values. This method is used later to build a table of all model records.

Example using the HE Series
*Note: `Fields` is a string enum, which I'm using throughout as my references to table fields instead of typing out the string values. the `formatted` method returns the value in title casing.*
```python
# adp-models/models.py

class HE(ModelSeries)
    ...
    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.SHEET.formatted(): self.sheet,
            Fields.MODEL_NUMBER.formatted(): str(self),
            Fields.CATEGORY.formatted(): self.category(),
            Fields.MPG.name: self.mat_grp,
            Fields.SERIES.formatted(): self.__series_name__(),
            Fields.TONNAGE.formatted(): self.tonnage,
            Fields.PALLET_QTY.formatted(): self.pallet_qty,
            Fields.WIDTH.formatted(): self.width,
            Fields.DEPTH.formatted(): self.depth,
            Fields.HEIGHT.formatted(): self.height,
            Fields.WEIGHT.formatted(): self.weight,
            Fields.CABINET.formatted(): self.cabinet_config.name.title(),
            Fields.METERING.formatted(): self.metering,
            Fields.ZERO_DISCOUNT_PRICE.formatted(): self.zero_disc_price,
        }
        model_record.update(values)
        return model_record
    ...
```
All of these `ModelSeries` subclasses are then packaged into a tuple for a convenient import
```python
MODELS = (HE,HD,HH,V,MH,SC,F,B,S,CP,CE,CF)
```
A separate `Validator` class is used to compare the value in a cell to the model's regex. If the regex matches on the content, `is_model` returns an instance of the `ModelSeries` class, otherwise `False`. The text length attribute (a tuple) is also used as another check.

```python
# validator.py
import re
from adp_models.models import ModelSeries

class Validator:
    def __init__(self, raw_text: str, model_series: ModelSeries) -> None:
        self.raw_text = (
            str(raw_text)
                .strip()
                .upper()
                .replace(' ','')
                .replace('-','')
        ) if raw_text else None
        self.text_len = len(self.raw_text) if self.raw_text else 0
        self.model_series = model_series
    
    def is_model(self) -> ModelSeries|bool:
        if self.text_len not in self.model_series.text_len or not self.raw_text:
            return False
        model = re.compile(self.model_series.regex, re.VERBOSE)
        model_parsed = model.match(self.raw_text)
        if model_parsed:
            return self.model_series(model_parsed)
        else:
            return False
```
This validator is used in a loop that tries all `ModelSeries` objects contained in `MODELS` against a cell value. The outcome, after bubbling up the model instances is a `set` of `ModelSeries` instances for a each program file.

The magic happens when utilizing the `record` method on each instance to build a standard `DataFrame` of objects. Note the transformation made in the second loop from `results` to `records` to a `df`.

Since all of the dfs have the same columns, we can safely concatenate them all into one customer programs `DataFrame`.
```python
# extraction/models.py
def extract_all_programs_from_dir(dir: str) -> pd.DataFrame:
    data: dict[str, dict[str, set[ModelSeries]]] = dict()
    for root, _, files in os.walk(dir):
        for file in files:
            program: str = os.path.basename(file).replace('.xlsx','')
            program = re.sub(r'\d{4}-\d{1,2}-\d{1,2}', '', program).strip()
            # iterates through sheets in the file and each cell in the file
            results: set[ModelSeries] = extract_models_from_file(os.path.join(root,file))
            if not data.get(program):
                data[program] = {'models': set()}
            data[program]['models'] |= results
    dfs = []
    for program in data:
        records = [record.record() for record in data[program]['models']]
        df = pd.DataFrame.from_records(data=records).dropna(how="all").drop_duplicates()
        if df.isna().all().all():
            pass
        df['Program'] = program
        dfs.append(df)
    result = pd.concat(dfs).sort_values(by=['Program','Category','Series','MPG','Tonnage','Width'])
    return result
```
This data gets additional treatment for customer-specific information (i.e. pricing, past sales) and it is then saved into a database, separating coils from air handlers.
### Ratings
Ratings extraction is not as complicated. All cells are iterated through in all sheets in all files, checking for the value: **AHRINumber** , which is a header for tables with ratings in them. Then every value in a few columns in all  rows underneath that encounter are captured, transformed into a table, enriched with a reference of all ADP ratings, and saved to a database.
## File Generation
The above approach is agnostic how the original programs were formatted. If a full model number is found anywhere while searching, the value is captured. Once the models and ratings are extracted to the database, new files can be generated from templates using `openpyxl`

#### template
Here is a template of the new format
![snapshot of excel file template for the new program format](./static/template-snapshot.png)
The formatted section with a light-blue header is where product information will go, and this format is to be copied underneath for each product category contained in the customer program.

#### data
The data extracted that we'll use is in a structured format in a database. We can separate files by unique customers and product blocks by Category. With respect to the template, the Category will go in the light-blue section, and the product information will be listed below the category (with headers).
![snapshot of customer program data in a database](./static/programs-db-snap.png)