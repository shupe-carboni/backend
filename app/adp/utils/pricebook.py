from dotenv import load_dotenv; load_dotenv()
import os
from copy import copy
import pandas as pd
import openpyxl as opxl
from typing import Literal
from openpyxl.cell.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.drawing.image import Image
from openpyxl.utils import range_boundaries
from openpyxl.styles import Font, Alignment
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
from openpyxl.utils.units import pixels_to_EMU
from openpyxl.utils.cell import coordinate_from_string, column_index_from_string
from programs import CustomerProgram


NOMENCLATURE_COL_WIDTH = 20
NOMENCLATURES = os.getenv('NOMENCLATURES')
STATIC_DIR = os.getenv('STATIC_DIR')

class AnchorPosition:
    def __init__(self, anchor_cell: str, offset_x: int, offset_y: int) -> None:
        coords = coordinate_from_string(anchor_cell)
        ## anchoring works off of 0-indexing, coordinates are 1-indexed
        col, row = column_index_from_string(coords[0])-1, coords[1]-1
        x_emu = pixels_to_EMU(offset_x)
        y_emu = pixels_to_EMU(offset_y)
        self.anchor = AnchorMarker(col=col, colOff=x_emu, row=row, rowOff=y_emu)

class Logo:
    def __init__(
            self,
            img_path: str,
            price_pos: AnchorPosition,
            ratings_pos: AnchorPosition,
            parts_pos: AnchorPosition,
            nomen_long_pos: AnchorPosition,
            nomen_med_pos: AnchorPosition,
            nomen_short_pos: AnchorPosition
        ) -> None:
        self.img_path = img_path
        self.price_pos = price_pos
        self.ratings_pos = ratings_pos
        self.parts_pos = parts_pos
        self.nomen_long_pos = nomen_long_pos
        self.nomen_med_pos = nomen_med_pos
        self.nomen_short_pos = nomen_short_pos
    
    def create_image(self, sheet_type: str) -> Image:
        """Images must be created fresh in every addition
            using the same Image instance can cause a file write issue
            and the custom anchoring hides another issue that's more tricky,
            which is that ALL images in all tabs will anchor to the last
            anchor setting used -- unless a new image object is provided"""
        img = Image(self.img_path)
        img_size = XDRPositiveSize2D(
            cx=pixels_to_EMU(img.width),
            cy=pixels_to_EMU(img.height)
        )
        types = {
            'pricing': self.price_pos,
            'ratings': self.ratings_pos, 
            'parts': self.parts_pos,
            'nomen-long': self.nomen_long_pos,
            'nomen-med': self.nomen_med_pos,
            'nomen-short': self.nomen_short_pos,
        }
        img.anchor = OneCellAnchor(
            _from=types[sheet_type].anchor,
            ext=img_size,
        )
        return img

class Logos:
    def __init__(self, *args: Logo) -> None:
        self.logos = args
    def __iter__(self):
        return iter(self.logos)
    def __str__(self) -> str:
        return str(self.logos)
    def __repr__(self) -> str:
        return str(self.logos)
    
class Cursor:
    """Track state of the cursor and provide movements
        Unpackable by `**` but replaces "col" with "column" as a key name"""
    def __init__(self) -> None:
        self.col = 1
        self.row = 1
    
    def keys(self):
        return ['row','column']
    
    def __getitem__(self, key):
        if key == 'row':
            return self.row
        elif key == 'column':
            return self.col

    def move_by(self, rows: int=0, cols: int=0) -> 'Cursor':
        self.col += cols
        self.row += rows
        return self
    
    def move_to(self, row: int=None, col: int=None) -> 'Cursor':
        self.col = col if col else self.col
        self.row = row if row else self.row
        return self
    
    def slam_left(self) -> 'Cursor':
        self.col = 1
        return self

class PriceBook:

    def __init__(self,
                 template: str,
                 program: CustomerProgram,
                 save_path: str,
        ) -> None:
        self.template_wb = opxl.load_workbook(template)
        self._9_col_template = self.template_wb['9-col']
        self.parts_template = self.template_wb['parts-template']
        self.nomenclatures = opxl.load_workbook(NOMENCLATURES)
        self.program = program
        self.save_path = os.path.join(save_path, self.program.new_file_name())
        self.check_for_existing_file()
        self.cursor = Cursor()
        adp_logo = Logo(
            img_path=os.path.join(STATIC_DIR,'adp-program-logo.png'),
            price_pos=AnchorPosition("E2", offset_x=0, offset_y=0),
            parts_pos=AnchorPosition("C2", offset_x=50, offset_y=0),
            ratings_pos=AnchorPosition("C2", offset_x=60, offset_y=0),
            nomen_long_pos=AnchorPosition("E2", offset_x=75, offset_y=0),
            nomen_med_pos=AnchorPosition("D2", offset_x=75, offset_y=0),
            nomen_short_pos=AnchorPosition("C2", offset_x=75, offset_y=0),
        )
        sca_logo = Logo(
            img_path=os.path.join(STATIC_DIR,'sca-logo.png'),
            price_pos=AnchorPosition("H1", offset_x=100, offset_y=0),
            parts_pos=AnchorPosition("D1", offset_x=0, offset_y=0),
            ratings_pos=AnchorPosition("F1", offset_x=0, offset_y=0),
            nomen_long_pos=AnchorPosition("H1", offset_x=100, offset_y=0),
            nomen_med_pos=AnchorPosition("G1", offset_x=100, offset_y=0),
            nomen_short_pos=AnchorPosition("F1", offset_x=100, offset_y=0),
        )
        customer_logo = Logo(
            img_path=program.logo_path,
            price_pos=AnchorPosition("A2", offset_x=10, offset_y=0),
            parts_pos=AnchorPosition("A2", offset_x=10, offset_y=0),
            ratings_pos=AnchorPosition("A2", offset_x=10, offset_y=0),
            nomen_long_pos=AnchorPosition("A2", offset_x=10, offset_y=0),
            nomen_med_pos=AnchorPosition("A2", offset_x=10, offset_y=0),
            nomen_short_pos=AnchorPosition("A2", offset_x=10, offset_y=0),
        )
        self.logos = Logos(adp_logo, sca_logo, customer_logo)
    
    def check_for_existing_file(self):
        if os.path.exists(self.save_path):
            self.active_wb = opxl.load_workbook(self.save_path)
            self.active = self.active_wb.active
            self.existing_file = True
        else:
            self.active_wb = self.template_wb
            self.active = self._9_col_template
            self.existing_file = False

    def copy_cell_style(self, src_cell, new_cell):
        # Copy font, fill, border, and alignment
        new_cell.font = copy(src_cell.font)
        new_cell.fill = copy(src_cell.fill)
        new_cell.border = copy(src_cell.border)
        new_cell.alignment = copy(src_cell.alignment)
        new_cell.number_format = src_cell.number_format
        new_cell.protection = copy(src_cell.protection)

    def copy_cell(self, src_cell: Cell, dest_row: int, dest_col: int):
        """Copy content and style from one cell to another."""
        new_cell = self.active.cell(dest_row, dest_col, src_cell.value)
        self.copy_cell_style(src_cell, new_cell)
        # NOTE below causes an error with styling indexing with 'Nomenclature' tab operations.
        # so it was swapped out for the `copy_cell_style` method
        # new_cell._style = copy(src_cell._style)
    
    def merged_col_bounds(self, cell: Cell) -> tuple[int,int,int]|None:
        for merge_range in self.active.merged_cells.ranges:
            min_col,min_row,max_col,max_row = range_boundaries(str(merge_range))
            if min_col <= cell.column <= max_col:
                if min_row <= cell.row <= max_row:
                    return min_col, max_col, min_row
    
    @staticmethod
    def copy_dimensions(src: Worksheet, dest: Worksheet) -> None:
        for idx, col_dim in src.column_dimensions.items():
            dest.column_dimensions[idx] = copy(col_dim)
        for idx, row_dim in src.row_dimensions.items():
            dest.row_dimensions[idx] = copy(row_dim)
        return

    def active_cell(self, value=None) -> Cell:
        return self.active.cell(**self.cursor, value=value)

    def new_sheet(
            self,
            template: Worksheet,
            title: str,
            sheet_type: str,
        ) -> 'PriceBook':
        if self.existing_file:
            # existing files would be overwritten
            # but existing sheet names are handled automatically by appending an integer
            new_sheet: Worksheet = self.active_wb.create_sheet(title=title.strip(), index=-2)
            self.copy_dimensions(template, new_sheet)
        else:
            new_sheet = self.active_wb.copy_worksheet(template)
            new_sheet.title = title.strip()
        self.active = new_sheet
        for logo in self.logos:
            logo_img = logo.create_image(sheet_type=sheet_type)
            self.active.add_image(logo_img, logo_img.anchor)
        self.active.sheet_view.showGridLines = False
        self.cursor.move_to(1,1)
        return self

    def new_price_sheet(self, title: str) -> 'PriceBook':
        sheet_type = 'pricing'
        new_sheet_template = self._9_col_template
        self.min_col, self.min_row, self.max_col, self.max_row = range_boundaries("A12:I15")
        self.product_block: tuple[tuple[Cell]] = self._9_col_template["A12:I15"]

        new_sheet = self.new_sheet(template=new_sheet_template, title=title, sheet_type=sheet_type)
        if self.existing_file:
            self.cursor.move_by(11-3)
            self.append_blank_product_block()
            self.cursor.move_to(10,1)
            confidential_pricing = self.active_cell(value="Confidential Pricing")
            confidential_pricing.font = Font(name='Calibri', size=16, bold=True) 
            confidential_pricing.alignment = Alignment(horizontal='center', vertical='center')
            self.active.merge_cells(
                    start_row= self.cursor.row,
                    end_row=self.cursor.row,
                    start_column=self.min_col,
                    end_column=self.max_col
                )
        self.cursor.move_to(1,1)
        return new_sheet
    
    def new_ratings_sheet(self, title: str="M1 Ratings") -> 'PriceBook':
        sheet_type = 'ratings'
        template = self.template_wb['ratings']
        return self.new_sheet(template=template, title=title, sheet_type=sheet_type)
    
    def new_parts_sheet(self) -> 'PriceBook':
        sheet_type = "parts"
        template = self.parts_template
        title = "Parts"
        return self.new_sheet(template=template, title=title, sheet_type=sheet_type)
    
    def new_nomenclature_sheet(self, len_option: Literal['long', 'med', 'short']) -> 'PriceBook':
        sheet_type = f'nomen-{len_option}'
        template = self.template_wb[sheet_type]
        title = 'Nomenclature'
        return self.new_sheet(template=template, title=title, sheet_type=sheet_type)

    def movex(self, n_cols: int) -> 'PriceBook':
        self.cursor.move_by(cols=n_cols)
        return self

    def movey(self, n_rows: int) -> 'PriceBook':
        self.cursor.move_by(rows=n_rows)
        return self

    def insert_rows(self, n_rows: int=1) -> 'PriceBook':
        starting_row = self.cursor.row
        last_current_row = self.active[self.cursor.row]
        self.active.insert_rows(self.cursor.row, amount=n_rows)
        for _ in range(1, n_rows+1):
            for col, cell in enumerate(self.active[self.cursor.row]):
                cell._style = copy(last_current_row[col]._style)
            self.cursor.move_by(rows=1)
        self.cursor.move_to(row=starting_row)
        return self

    def append_blank_product_block(self) -> 'PriceBook':
        self.cursor.slam_left()
        self.cursor.move_by(rows=3)
        row_offset = self.cursor.row - self.min_row
        ## copy new product block from template
        for row in self.product_block:
            for cell in row:
                new_row = cell.row + row_offset
                new_col = cell.column
                self.copy_cell(cell, new_row, new_col)
        self.active.merge_cells(
            start_row=self.cursor.row,
            start_column=self.cursor.col,
            end_row=self.cursor.row,
            end_column=len(self.product_block[0])+self.cursor.col-1
        )
        return self
    
    def find_min_coords_with_data(self, sheet: Worksheet=None) -> tuple[int|None, int|None]:
        if not sheet:
            sheet = self.active
        min_row = sheet.max_row
        min_col = sheet.max_column
        for row in sheet.iter_rows():
            for cell in row:
                if cell.value:
                    min_row = min(min_row, cell.row)
                    min_col = min(min_col, cell.column)
        if min_row == sheet.max_row:
            min_row = None
        if min_col == sheet.max_column:
            min_col = None
        return min_row, min_col

    def insert_nomenclature_block(self, series: str) -> 'PriceBook':
        nomenclature_sheet: Worksheet = self.nomenclatures[series]
        for row in nomenclature_sheet:
            for cell in row:
                new_row = cell.row + self.cursor.row - 1
                new_col = cell.column + self.cursor.col -1
                self.copy_cell(cell, new_row, new_col)
        _, min_col = self.find_min_coords_with_data(nomenclature_sheet)
        self.active.merge_cells(
            start_row=self.cursor.row,
            start_column=min_col,
            end_row=self.cursor.row,
            end_column=nomenclature_sheet.max_column
        )
        self.cursor.move_by(rows=self.max_row)
        return self
    
    def attach_nomenclature_tab(self) -> 'PriceBook':
        long_nomens = {'HE', 'HH', 'B', 'F', 'CP'}
        medium_nomens = {'V', 'CE'}
        if self.program.series_contained.intersection(long_nomens):
            self.new_nomenclature_sheet('long').movey(12)
        elif self.program.series_contained.intersection(medium_nomens):
            self.new_nomenclature_sheet('med').movey(12)
        else:
            self.new_nomenclature_sheet('short').movey(12)

        for series in self.program.series_contained:
            self.insert_nomenclature_block(series).movey(2)
        for col in self.active.iter_cols():
            col_letter = col[0].column_letter
            self.active.column_dimensions[col_letter].width = NOMENCLATURE_COL_WIDTH
        return self
    
    def save_and_close(self):
        try:
            if not self.existing_file:
                self.active_wb.remove(self._9_col_template)
                self.active_wb.remove(self.template_wb['ratings'])
                for option in ('long', 'med', 'short'):
                    self.active_wb.remove(self.template_wb[f'nomen-{option}'])
                self.active_wb.remove(self.parts_template)
            # set the opening sheet to the first sheet, which should be the model list
            self.active_wb.active = 0
            self.active_wb.save(self.save_path)
        except IndexError as e:
            import traceback as tb
            print(f"file empty on save for {self.program.customer}")
            print(tb.format_exc())
            os.remove(self.save_path)
        finally:
            self.template_wb.close()
        return self
    
    def add_footer(self) -> 'PriceBook':
        for name, value in self.program.terms.items():
            cell = self.active_cell(name)
            cell.font = Font(bold=True)
            self.movex(1)
            cell = self.active_cell(value['value'])
            for style_name, style_value in value['style'].items():
                cell.__setattr__(style_name, style_value)
            self.cursor.slam_left().move_by(rows=1)
        return self

    def insert_data(self, df: pd.DataFrame, headers: bool=True, offset: tuple=(0,0)) -> 'PriceBook':
        if headers:
            for col in df.columns:
                self.active_cell(value=str(col))
                self.cursor.move_by(cols=1)
            self.cursor.slam_left()
            self.cursor.move_by(rows=1)
            self.cursor.move_by(*offset)

        for label, data in df.iterrows():
            for datum in data:
                self.active_cell(value=datum)
                self.cursor.move_by(cols=1)
            self.cursor.move_by(rows=1)
            self.cursor.slam_left()
            self.cursor.move_by(*offset)
        if headers:
            if 'Pallet Qty' in df.columns:
                self.cursor.move_by(cols=1)
                disclaimer = self.active_cell('* Must order in pallet quantities')
                disclaimer.font = Font(bold=True, italic=True)
            elif 'Min Qty' in df.columns:
                self.cursor.move_by(cols=1)
                disclaimer = self.active_cell('* Must order at least the minimum quantity per-SKU')
                disclaimer.font = Font(bold=True, italic=True)
        return self

    def build_program(self) -> 'PriceBook':
        """
            One file per "program"
            One product block per "category"
        """
        self.new_price_sheet(title='Model List')
        self.cursor.move_by(11).slam_left()
        for i, program in enumerate(self.program):
            data_by_category: dict[str, pd.DataFrame] = {
                category: program.category_data(category)
                for category in program.product_categories
            }
            for j, cat_data in enumerate(data_by_category.items()):
                cat, df = cat_data
                rows = df.shape[0]
                if i > 0 or j > 0:
                    self.append_blank_product_block()
                self.active_cell(value=cat) # put in category 
                (
                self.movey(2) # the first data row
                    .adjust_number_of_formatted_rows(self.max_row-self.min_row-1, rows)
                    .movey(-1) # headers row
                    .insert_data(df)
                )
        return self.movex(-self.cursor.col+1).movey(2).add_footer()
    
    def adjust_number_of_formatted_rows(self, startin_row_num: int, target_row_num: int) -> 'PriceBook':
        diff = target_row_num - startin_row_num
        if diff > 0:
            self.insert_rows(n_rows=diff)
        elif diff < 0:
            self.active.delete_rows(self.cursor.row, amount=abs(diff))
        return self
    
    def attach_parts(self) -> 'PriceBook':
        """unlike the model numbers tab, headers have been provided"""
        data = self.program.parts
        if data.empty:
            print("\tskipped parts due to empty table")
            return self
        num_rows = data.shape[0]
        self.new_parts_sheet()\
            .movex(1)\
            .movey(13)\
            .adjust_number_of_formatted_rows(2, num_rows)\
            .insert_data(data, headers=False,offset=(0,1))
        return self

    def attach_ratings(self) -> 'PriceBook':
        data = self.program.ratings
        if data.empty or self.existing_file:
            return self

        def set_series_name(oemseries: str) -> str:
            if any([val in oemseries for val in ('4AC', '4HP')]):
                start, end = (0,5)
            elif oemseries.startswith('YHE') or oemseries.startswith('AC0'):
                start, end = (0,3)
            else:
                start, end = (0,4)
            return oemseries[start:end]

        data['OEM Series'] = data['OEM Series'].fillna(data['OutdoorModel']).apply(set_series_name)
        ratings: dict[str, pd.DataFrame] = {
            oem_series: data[data['OEM Series'] == oem_series]
            for oem_series in data['OEM Series'].unique()
        }
        substituted_series = []
        new_series = dict()
        for series, data in ratings.items():
            unique_oems = data['OEM Name'].unique().tolist()
            if len(unique_oems) > 1:
                for oem in unique_oems:
                    new_series[f'{series} {oem}'] = data[data['OEM Name'] == oem]
                substituted_series.append(series)
        if substituted_series:
            ratings |= new_series
            for series in substituted_series:
                del ratings[series]

        for tab, table in ratings.items():
            rows = table.shape[0]
            self.new_ratings_sheet(title=tab)
            self.cursor.move_to(row=14) # second row for data
            self.adjust_number_of_formatted_rows(3, rows)
            self.cursor.move_by(rows=-1) # back to first data row

            # column names are already in the template
            # rearrange data to align with the template and copy it in
            # template_cols = ('AHRINumber','OEMName','OutdoorModel',
            #                 'IndoorModel','FurnaceModel',
            #                 'SEER2','EER95F2',
            #                 'Capacity2','HSPF2')
            
            table = table.sort_values(by=['OEM Series','ADP Series','Model Number','Coil Model Number'])

            for label, row in table.iterrows():
                if not row['AHRI Ref Number']:
                    row_view = row[['AHRINumber','OEMName','OutdoorModel',
                                    'IndoorModel','FurnaceModel','SEER2',
                                    'EER2','Capacity2','HSPF2']]
                else:
                    row_view = row[['AHRI Ref Number','OEM Name','Model Number',
                                    'Coil Model Number','Furnace Model Number','SEER2',
                                    'EER2','Capacity2','HSPF2']]
                for datum in row_view:
                    cell = self.active_cell(value=datum)
                    if not datum or datum == '0':
                        cell.value = None
                    self.cursor.move_by(cols=1)
                self.cursor.slam_left()
                self.cursor.move_by(rows=1)
            
        return self
