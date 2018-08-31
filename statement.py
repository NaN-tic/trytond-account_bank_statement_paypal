# -*- coding: utf-8 -*-
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import csv
from StringIO import StringIO
from trytond.model import ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Bool, Not

__all__ = ['Configuration', 'Import', 'ImportStart']

locales = {
    'en': {
        'date_field': 'Date',
        'description_field': 'Transaction ID',
        'gross_field': 'Gross',
        'net_field': 'Net',
        'fee_field': 'Fee',
        'date_pattern': '%m/%d/%Y',
        'decimal_separator': '.',
        'thousands_separator': ',',
        },
    'es': {
        'date_field': 'Fecha',
        'description_field': 'Id. de transacción',
        'gross_field': 'Bruto',
        'net_field': 'Neto',
        'fee_field': 'Tarifa',
        'date_pattern': '%d/%m/%Y',
        'decimal_separator': ',',
        'thousands_separator': '.',
        }}


class Configuration:
    __metaclass__ = PoolMeta
    __name__ = 'account.configuration'
    paypal_amount_field = fields.Selection([
                ('gross_field', 'Gross'),
                ('net_field', 'Net'),
                ], 'Field to import amount')
    paypal_fee = fields.Boolean('Paypal Fee',
        help="Import Paypal Fee.")
    paypal_fee_account = fields.Many2One('account.account', 'Paypal Fee Account',
        domain=[('kind', '=', 'expense')],
        states={
            'required': Bool(Eval('paypal_fee')),
            'invisible': Not(Bool(Eval('paypal_fee'))),
            })

    @staticmethod
    def default_paypal_amount_field():
        return 'net_field'

    @staticmethod
    def default_paypal_fee():
        return True


class ImportStart:
    __name__ = 'account.bank.statement.import.start'
    __metaclass__ = PoolMeta

    @classmethod
    def __setup__(cls):
        super(ImportStart, cls).__setup__()
        cls.type.selection += [
            ('paypal-en', 'Paypal EN'), ('paypal-es', 'Paypal ES')]


class Import:
    __name__ = 'account.bank.statement.import'
    __metaclass__ = PoolMeta

    @classmethod
    def __setup__(cls):
        super(Import, cls).__setup__()
        cls._error_messages.update({
                'no_paypal_fee_account': ('No Paypal Fee Account configured.'),
                })

    def process(self, statement):
        super(Import, self).process(statement)
        if self.start.type not in ['paypal-en', 'paypal-es']:
            return
        pool = Pool()
        Line = pool.get('account.bank.statement.line')
        MoveLine = pool.get('account.bank.statement.move.line')
        Config = pool.get('account.configuration')

        config = Config(1)

        csv_file = StringIO(
            self.start.import_file.decode('utf-8-sig').encode('utf-8'))
        try:
            reader = csv.DictReader(csv_file)
        except csv.Error, e:
            self.raise_user_error('format_error', str(e))

        locale = self.start.type.split('-')[1]
        lines = []
        for record in reader:
            # Strip keys
            record = dict((k.strip(), x) for k, x in record.items() if k)
            line = Line()
            line.statement = statement
            line.date = self.string_to_date(
                record[locales[locale]['date_field']],
                patterns=(locales[locale]['date_pattern'],),
                )
            line.description = record[locales[locale]['description_field']]
            line.amount = self.string_to_number(
                record[locales[locale][config.paypal_amount_field]],
                decimal_separator=locales[locale]['decimal_separator'],
                thousands_separator=locales[locale]['thousands_separator'],
                )

            fee = self.string_to_number(
                record[locales[locale]['fee_field']],
                decimal_separator=locales[locale]['decimal_separator'],
                thousands_separator=locales[locale]['thousands_separator'],
                )
            if fee and config.paypal_fee:
                if not config.paypal_fee_account:
                    self.raise_user_error('no_paypal_fee_account')
                move_line = MoveLine()
                move_line.date = line.date.date()
                move_line.amount = fee
                move_line.account = config.paypal_fee_account

                line.lines = [move_line]

            lines.append(line)

        Line.save(lines)
