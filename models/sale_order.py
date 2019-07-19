# -*- encoding: utf-8 -*-

import csv
from io import StringIO
from os import path
from datetime import datetime
import string
import random

from odoo import api, fields, models

FIELDS = [
    ('customer', 'partner_id'),
    ('end_date', 'validity_date')
]
SYS_DATE_FORMAT = '%m-%d-%Y'
ODOO_DATE_FORMAT = '%Y-%m-%d'

class SaleOrder(models.Model):

    """Inherit Sale Order model to add a method to import
       sale orders"""

    _inherit = 'sale.order'

    @api.model
    def cron_import_data(self, file_path, file_name):
        """
        Cron job to import sale orders.

        :param file_path:
        :param file_name:
        :return: False if unable to open file, return true it the
        import was done with no issues.
        """

        # Store all the odoo fields in a list and insert id in the
        # beginning.
        _fields = [f[1] for f in FIELDS]
        _fields.insert(0, 'id')

        # Try to open the file, if failed return False. If file is opened,
        # create a DictReader then close the file.
        try:
            file_with_path = path.join(file_path, file_name)
            file = open(file_with_path)
        except IOError:
            return False
        reader = csv.DictReader(file)

        # Create a StringIO that will be used to store a csv file that
        # will be imported to the model (mocking the import process
        # that could be done from backend tree views)
        file_import = StringIO()
        csv_import = csv.DictWriter(file_import, fieldnames=_fields,
                                    quotechar='\"', quoting=csv.QUOTE_NONE)
        csv_import.writeheader()
        # Loop over each line and over each field so that we can handle
        # special cases in the data that is being read from the other
        # system in this case possibly a csv file that is being exported
        # and stored at a specific directory in the system. Once all data
        # has been handled each record is written onto the csv writer.
        for line in reader:
            data = {f:False for f in _fields}
            data['id'] = self.generate_record_id()
            for field in FIELDS:
                if field[1] == 'validity_date':
                    date = datetime.strptime(line[field[0]],
                                             SYS_DATE_FORMAT).date()
                    date_value = fields.Date.to_string(date)
                    data[field[1]] = date_value
                else:
                    data[field[1]] = line[field[0]]
            csv_import.writerow(data)

        # Do the actual import by creating a base_import.import
        # object and do the actual import.
        import_wizard = self.env['base_import.import'].create({
            'res_model': 'sale.order',
            'file': file_import.getvalue(),
            'file_type': 'text/csv',
        })
        results = import_wizard.sudo().do(
            _fields,
            [],
            {
                'quoting': '"',
                'separator': ',',
                'date_format': ODOO_DATE_FORMAT,
                'headers': True
            }
        )

        # Method `do` in the base_import.import model returns
        # an empty list when succeeds else it returns a list
        # of the errors that took place while attempting the import
        file.close()
        if len(list(filter(lambda x: type(x) == 'int', results))) \
                == 0:
            return True
        else:
            return False


    @api.model
    def generate_record_id(self):
        """
        Class method to create an external ID for each
        record that is randomly generated.

        :return: string representing the external id
        """

        letters = [c for c in string.ascii_lowercase]
        s_1 = ''.join(random.choice(letters) for i in range(2))
        s_2 = ''.join(random.choice(letters) for i in range(8))
        return "__export__.sale_order_{}_{}".format(s_1, s_2)
