import os
import re
import itertools
from app.db import DB_V2
from io import BytesIO
from pypdf import PdfReader
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session

TextArray = list[list[str]]
BytesLike = bytes | BytesIO


@dataclass
class CustomerDetail:
    customer_number: int
    ship_to_customer_name: str
    ship_to_customer_address: str
    sold_to_customer_name: str
    sold_to_customer_address: str


@dataclass
class OrderDetail:
    order_confirmation_date: str
    order_confirmation_number: int
    purchase_order_number: str
    terms_of_payment: str
    terms_of_delivery: str


@dataclass
class OrderTaxAndTotal:
    subtotal: int
    total_amount: int
    state_tax: int
    county_tax: int


@dataclass
class OrderProduct:
    item_sequence_number: str
    material_number: int
    material_description: str
    ship_from: str
    delivery_date: str
    quantity: int | float
    unit_of_measure: str
    unit_price: int
    total: int


@dataclass
class OrderProducts:
    products: list[OrderProduct]

    def __iter__(self):
        return iter(self.products)


@dataclass
class Confirmation:
    customer: CustomerDetail
    order_details: OrderDetail
    order_products: OrderProducts
    order_tax_and_total: OrderTaxAndTotal

    # def __post_init__(self) -> None:
    #     products_total = sum(product.total for product in self.order_products.products)
    #     diff = abs(products_total - self.order_tax_and_total.subtotal)
    #     is_within_1_cent = diff <= 1
    #     assert is_within_1_cent, '\nMismatched totals'\
    #             f'\n\tsum of products = ${products_total/100:,.2f}'\
    #             f'\n\tsubtotal amount = ${self.order_tax_and_total.subtotal/100:,.2f}'\
    #             f'\n\tdiff = ${diff/100:,.2f}'


def extract_customer_details(text_array: TextArray) -> CustomerDetail:

    def build_string(sub_array: TextArray) -> str:
        result = str()
        for row in sub_array:
            combined_text = " ".join(row) + " "
            try:
                float(combined_text)
            except:
                result += combined_text
            else:
                continue
        return result

    ship_to_customer_address_upper_bound = 0
    ship_to_customer_address_lower_bound = 0
    sold_to_customer_address_upper_bound = 0
    sold_to_customer_address_lower_bound = 0
    customer_number = 0
    required_values = [
        ship_to_customer_address_upper_bound,
        ship_to_customer_address_lower_bound,
        sold_to_customer_address_upper_bound,
        sold_to_customer_address_lower_bound,
        customer_number,
    ]
    for i, row in enumerate(text_array):
        if all(required_values):
            break
        elif (
            " ".join(row) == "Ship-to Party Address"
            and not ship_to_customer_address_upper_bound
        ):
            ship_to_customer_address_upper_bound = i + 1
            for j, row_2 in enumerate(text_array[:i][::-1]):
                if "sold-topartyaddress" in "".join(row_2).replace(" ", "").lower():
                    sold_to_customer_address_upper_bound = (
                        ship_to_customer_address_upper_bound - j - 1
                    )
                    sold_to_customer_address_lower_bound = i
                    break
        elif (
            row[:3] == ["Item", "Material", "Description"]
            and not ship_to_customer_address_lower_bound
        ):
            ship_to_customer_address_lower_bound = i
        elif row[:2] == ["Customer", "No."]:
            customer_number = int(row[-1])

    sold_to_address_bounds = slice(
        sold_to_customer_address_lower_bound - 2, sold_to_customer_address_lower_bound
    )
    sold_to_customer_bounds = slice(
        sold_to_customer_address_upper_bound, sold_to_address_bounds.start
    )
    sold_to_customer = build_string(text_array[sold_to_customer_bounds])
    sold_to_address = build_string(text_array[sold_to_address_bounds])

    ship_to_address_bounds = slice(
        ship_to_customer_address_lower_bound - 2, ship_to_customer_address_lower_bound
    )
    ship_to_customer_bounds = slice(
        ship_to_customer_address_upper_bound, ship_to_address_bounds.start
    )
    ship_to_customer = build_string(text_array[ship_to_customer_bounds])
    ship_to_address = build_string(text_array[ship_to_address_bounds])

    return CustomerDetail(
        customer_number=customer_number,
        ship_to_customer_name=ship_to_customer.strip(),
        ship_to_customer_address=ship_to_address.strip(),
        sold_to_customer_name=sold_to_customer.strip(),
        sold_to_customer_address=sold_to_address.strip(),
    )


def extract_order_details(text_array: TextArray) -> OrderDetail:
    order_confirmation_number = None
    order_confirmation_date = None
    purchase_order_number = None
    terms_of_payment = None
    terms_of_delivery = None
    required = [
        order_confirmation_number,
        order_confirmation_date,
        purchase_order_number,
        terms_of_payment,
        terms_of_delivery,
    ]
    for row in text_array:
        if all(required):
            break
        elif len(row) < 3:
            continue
        elif row[:2] == ["Order", "Number/Date"]:
            order_confirmation_number = int(row[2])
            order_confirmation_date = row[-1]
        elif row[:3] == ["Purchase", "Order", "No."]:
            # purchase_order_number = row[-1]
            purchase_order_number = " ".join(row[3:])
        elif row[:3] == ["Terms", "of", "Payment"]:
            terms_of_payment = " ".join(row[3:])
        elif row[:3] == ["Terms", "of", "Delivery"]:
            terms_of_delivery = " ".join(row[3:])
    return OrderDetail(
        order_confirmation_date=order_confirmation_date,
        order_confirmation_number=order_confirmation_number,
        purchase_order_number=purchase_order_number,
        terms_of_payment=terms_of_payment,
        terms_of_delivery=terms_of_delivery,
    )


def extract_order_tax_and_total(text_array: TextArray) -> OrderTaxAndTotal:
    sub_total = 0
    total = 0
    state_tax = 0
    county_tax = 0
    for row in text_array:
        try:
            if all([sub_total, total, state_tax, county_tax]):
                break
            elif row[:2] == ["Sub", "Total(Items)"]:
                sub_total = int(float(row[-1].replace(",", "")) * 100)
            elif row[0] == "Total":
                total = int(float(row[-1].replace(",", "")) * 100)
            elif row[:2] == ["State", "Tax"]:
                state_tax = int(float(row[-1].replace(",", "")) * 100)
            elif row[:2] == ["County", "Tax"]:
                county_tax = int(float(row[-1].replace(",", "")) * 100)
        except IndexError:
            continue
    return OrderTaxAndTotal(
        subtotal=sub_total,
        total_amount=total,
        state_tax=state_tax,
        county_tax=county_tax,
    )


def extract_order_products(text_array: TextArray) -> OrderProducts:
    item_seq_pattern = re.compile(r"^\d{4}$")
    mat_number_pattern = re.compile(r"^\d{6}$")
    date_pattern = re.compile(r"^\d{2}/\d{2}/\d{4}")

    product_boundary_starts = list()
    ship_from_lines = list()
    splits_starts = list()
    splits_runs = [[]]
    splits_bounds = []
    for i, row in enumerate(text_array):
        match row:
            case ["Split", "the", "overall", "quantity", *other]:
                splits_starts.append(i)
            case [a, b, c, *other] if date_pattern.match(c) and other == [
                "Party",
                "Address",
            ]:
                try:
                    float(a)
                except:
                    pass
                else:
                    if current_run := splits_runs[-1]:
                        if current_run[-1] + 1 == i:
                            current_run.append(i)
                        else:
                            splits_runs.append([i])
                    else:
                        splits_runs[-1].append(i)
            case [a, b, c] if date_pattern.match(c):
                try:
                    float(a)
                except:
                    pass
                else:
                    if current_run := splits_runs[-1]:
                        if current_run[-1] + 1 == i:
                            current_run.append(i)
                        else:
                            splits_runs.append([i])
                    else:
                        splits_runs[-1].append(i)
            case ["Ship", "From:", *other]:
                ship_from_lines.append(i)
            case [a, b, *others] if item_seq_pattern.match(
                a
            ) and mat_number_pattern.match(b):
                product_boundary_starts.append(i)
    product_boundary_ends = [i - 1 for i in product_boundary_starts[1:]]
    if splits_starts:
        splits_ends = [splitrun[-1] for splitrun in splits_runs]
        splits_bounds = list(zip(splits_starts, splits_ends))
        if splits_ends[-1] > ship_from_lines[-1]:
            product_boundary_ends.append(splits_ends[-1])
        else:
            product_boundary_ends.append(ship_from_lines[-1])
    else:
        product_boundary_ends.append(ship_from_lines[-1])

    # (start, end) where end is inclusive
    product_blocks = list(
        zip(
            product_boundary_starts[: len(product_boundary_ends)], product_boundary_ends
        )
    )
    result = list()
    for start, end in product_blocks:
        item_sequence_number = text_array[start][0]
        material_number = int(text_array[start][1].replace(",", ""))
        material_description = " ".join(
            text_array[start + 1][:-3]
        )  # exclue unit price UOM
        if text_array[end][-2:] == ["Party", "Address"]:
            ship_from_array = text_array[end][:-2]
            ship_from_array[-1] = ship_from_array[-1].removesuffix("Sold-to")
            ship_from = " ".join(ship_from_array[2:])
        else:
            ship_from = " ".join(text_array[end][2:])

        used_split = False
        for i, split in enumerate(splits_bounds):
            if split[-1] == end:
                used_split = True
                unit_price = int(float(text_array[start][-2].replace(",", "")) * 100)
                for line_item in splits_runs[i]:
                    qty, uom, date, *other = text_array[line_item]
                    if other:
                        date = re.sub(r"[^0-9/]", "", date)
                    quantity = float(qty)
                    total = int(unit_price * quantity)
                    result.append(
                        OrderProduct(
                            item_sequence_number=item_sequence_number,
                            material_number=material_number,
                            material_description=material_description,
                            ship_from=ship_from,
                            delivery_date=date,
                            quantity=quantity,
                            unit_of_measure=uom,
                            unit_price=unit_price,
                            total=total,
                        )
                    )
                break
        if not used_split:
            shift = 0
            delivery_date: str = text_array[start][2]
            if not date_pattern.match(delivery_date):
                shift += 1
                delivery_date = None

            quantity: str = text_array[start][3 - shift]
            quantity = int(quantity.split(".")[0].replace(",", ""))
            unit_of_measure = text_array[start][4 - shift]
            try:
                unit_price = text_array[start][5 - shift].replace(",", "")
                unit_price = int((float(unit_price) * 100) + 0.5)
                total = text_array[start][6 - shift].replace(",", "")
                total = int((float(total) * 100) + 0.5)
            except (IndexError, ValueError) as e:
                unit_price = 0
                total = 0

            result.append(
                OrderProduct(
                    item_sequence_number=item_sequence_number,
                    material_number=material_number,
                    material_description=material_description,
                    ship_from=ship_from,
                    delivery_date=delivery_date,
                    quantity=quantity,
                    unit_of_measure=unit_of_measure,
                    unit_price=unit_price,
                    total=total,
                )
            )
    return OrderProducts(products=result)


## TODO combine somehow with the database actions at the bottom?
def extract_from_file(file: str | BytesLike) -> Confirmation:
    match file:
        case bytes():
            file = BytesIO(file)
    reader = PdfReader(file)
    last_page_i = len(reader.pages) - 1
    if last_page_i < 1:
        raise Exception("Confirmation is one page. It may be blank.")
    order_products: list[OrderProducts] = list()
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        text_array = [line.split() for line in text.split("\n")]
        if i == 0:
            customer = extract_customer_details(text_array)
            order_details = extract_order_details(text_array)
            order_products.append(extract_order_products(text_array))
        elif i == last_page_i:
            try:
                order_products.append(extract_order_products(text_array))
            except Exception as e:
                pass
            order_tax_and_total = extract_order_tax_and_total(text_array)
        else:
            order_products.append(extract_order_products(text_array))
    order_products_flat = OrderProducts(products=list(itertools.chain(*order_products)))
    return Confirmation(
        customer=customer,
        order_tax_and_total=order_tax_and_total,
        order_details=order_details,
        order_products=order_products_flat,
    )


# TODO remove
def extract_all_files() -> tuple[list[Confirmation], list[str]]:
    all_results: list[dict] = list()
    file_list = os.listdir("./files")
    num_files = len(file_list)
    failures = list()
    for i, file in enumerate(file_list):
        msg = f"reading file {i+1} of {num_files}"
        print(msg, end="")
        try:
            result = extract_from_file("./files/" + file)
        except Exception as e:
            failures.append(f"{file} {e}")
        else:
            all_results.append(result)
        print("\b" * len(msg), end="")
    print("\nDone")
    return all_results, failures


def save_record(session: Session, record: Confirmation) -> None:
    conf_statement = """
        INSERT INTO hardcast_confirmations (
            order_confirmation_number,
            order_confirmation_date,
            purchase_order_number,
            customer_number,
            sold_to_customer_name,
            sold_to_customer_address,
            ship_to_customer_name,
            ship_to_customer_address,
            terms_of_payment,
            terms_of_delivery,
            subtotal,
            state_tax,
            county_tax,
            total_amount
        )
        VALUES (
            :order_confirmation_number,
            :order_confirmation_date,
            :purchase_order_number,
            :customer_number,
            :sold_to_customer_name,
            :sold_to_customer_address,
            :ship_to_customer_name,
            :ship_to_customer_address,
            :terms_of_payment,
            :terms_of_delivery,
            :subtotal,
            :state_tax,
            :county_tax,
            :total_amount
        )
        RETURNING id;
    """
    conf_product_statement = """
        INSERT INTO hardcast_confirmation_products(
            order_id,
            item_sequence_number,
            material_number,
            material_description,
            ship_from,
            delivery_date,
            quantity,
            unit_of_measure,
            unit_price,
            total
        )
        VALUES (
            :order_id,
            :item_sequence_number,
            :material_number,
            :material_description,
            :ship_from,
            :delivery_date,
            :quantity,
            :unit_of_measure,
            :unit_price,
            :total
        );
    """
    customer_info = asdict(record.customer)
    order_details = asdict(record.order_details)
    order_products = record.order_products
    order_tax_and_total = asdict(record.order_tax_and_total)

    conf_params = dict(**customer_info, **order_details, **order_tax_and_total)
    result = DB_V2.execute(session, conf_statement, conf_params)
    new_order_id: int = result.scalar_one()

    item_dicts: list[dict] = list()
    for order_item in order_products:
        order_item_dict = asdict(order_item)
        order_item_dict["order_id"] = new_order_id
        item_dicts.append(order_item_dict)
    DB_V2.execute(session, conf_product_statement, item_dicts)
