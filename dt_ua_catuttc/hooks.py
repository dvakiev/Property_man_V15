# Copyright 2022 DotTek
# @author: Dmytro Pavlov (<dottek.ukraine@gmail.com>)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).
import logging
import xlrd
from pathlib import Path


_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    _logger.info("Uploading CATUTTC data into db...")
    cr.execute("""
        DELETE FROM catuttc_region;
        DELETE FROM catuttc_district;
        DELETE FROM catuttc_community;
        DELETE FROM catuttc_locality;
        DELETE FROM catuttc_locality_district;
    """)
    wb = xlrd.open_workbook(Path(__file__).parent / "data" / "catuttc.xlsx")
    sheet = wb.sheet_by_index(0)
    row_count = sheet.nrows

    for cur_row in range(3, row_count):
        _logger.info("\t" + f"uploading row [{cur_row}]")

        region = sheet.cell(cur_row, 0).value
        district = sheet.cell(cur_row, 1).value
        community = sheet.cell(cur_row, 2).value
        locality = sheet.cell(cur_row, 3).value
        locality_district = sheet.cell(cur_row, 4).value
        category_letter = sheet.cell(cur_row, 5).value
        name = sheet.cell(cur_row, 6).value
        if not name:
            continue

        if not any((district, community,locality, locality_district)):
            cr.execute(f"""
                INSERT INTO catuttc_region(name, code, category_id)
                VALUES(%s, %s, (SELECT id FROM catuttc_category WHERE letter = %s))
            """, (name, region, category_letter))

        elif district and not any((community, locality, locality_district)):
            cr.execute(f"""
                INSERT INTO catuttc_district(name, code, category_id, region_id)
                VALUES(%s, %s,  (SELECT id FROM catuttc_category WHERE letter = %s),
                                (SELECT id FROM catuttc_region WHERE code = %s))
            """, (name, district, category_letter, region))

        elif community and not any((locality, locality_district)):
            cr.execute(f"""
                INSERT INTO catuttc_community(name, code, category_id, region_id, district_id)
                VALUES(%s, %s,  (SELECT id FROM catuttc_category WHERE letter = %s),
                                (SELECT id FROM catuttc_region WHERE code = %s),
                                (SELECT id FROM catuttc_district WHERE code = %s))
            """, (name, community, category_letter, region, district))

        elif locality and not locality_district:
            cr.execute(f"""
                INSERT INTO catuttc_locality(name, code, category_id, region_id, district_id, community_id)
                VALUES(%s, %s,  (SELECT id FROM catuttc_category WHERE letter = %s),
                                (SELECT id FROM catuttc_region WHERE code = %s),
                                (SELECT id FROM catuttc_district WHERE code = %s),
                                (SELECT id FROM catuttc_community WHERE code = %s))
            """, (name, locality, category_letter, region, district, community))

        elif locality_district:
            cr.execute(f"""
                INSERT INTO catuttc_locality_district(name, code, category_id, region_id,
                                                    district_id, community_id, locality_id)
                VALUES(%s, %s,  (SELECT id FROM catuttc_category WHERE letter = %s),
                                (SELECT id FROM catuttc_region WHERE code = %s),
                                (SELECT id FROM catuttc_district WHERE code = %s),
                                (SELECT id FROM catuttc_community WHERE code = %s),
                                (SELECT id FROM catuttc_locality WHERE code = %s))
            """, (name, locality_district, category_letter, region, district, community, locality))

_logger.info("Uploading complete.")
