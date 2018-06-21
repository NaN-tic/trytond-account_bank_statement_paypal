#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.pool import Pool
from . import statement


def register():
    Pool.register(
        statement.Configuration,
        statement.ConfigurationPaypal,
        statement.ImportStart,
        module='account_bank_statement_paypal', type_='model')
    Pool.register(
        statement.Import,
        module='account_bank_statement_paypal', type_='wizard')
