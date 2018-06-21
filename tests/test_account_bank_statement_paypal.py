# This file is part of the account_bank_statement_paypal module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import doctest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import doctest_teardown, doctest_checker


class AccountBankStatementPaypalTestCase(ModuleTestCase):
    'Test Account Bank Statement Paypal module'
    module = 'account_bank_statement_paypal'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountBankStatementPaypalTestCase))
    suite.addTests(doctest.DocFileSuite('scenario_bank_statement_paypal.rst',
            tearDown=doctest_teardown, encoding='utf-8',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
            checker=doctest_checker))
    return suite
