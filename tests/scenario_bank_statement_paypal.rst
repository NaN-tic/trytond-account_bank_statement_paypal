======================================
Account Bank Statement Paypal Scenario
======================================

Imports::

    >>> import datetime
    >>> import os
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard, Report
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.currency.tests.tools import get_currency
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences
    >>> today = datetime.date.today()
    >>> now = datetime.datetime.now()

Activate account_bank_statement_paypal module::

    >>> config = activate_modules('account_bank_statement_paypal')

Create company::

    >>> currency = get_currency('EUR')
    >>> _ = create_company(currency=currency)
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> payable = accounts['payable']
    >>> cash = accounts['cash']
    >>> cash.bank_reconcile = True
    >>> cash.save()

Configure default Paypal Fee Account::

    >>> Configuration = Model.get('account.configuration')
    >>> config = Configuration(1)
    >>> config.paypal_fee = True
    >>> config.paypal_fee_account = expense
    >>> config.save()

Create party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Party')
    >>> party.save()

Create Journal::

    >>> Sequence = Model.get('ir.sequence')
    >>> SequenceType = Model.get('ir.sequence.type')
    >>> sequence_type, = SequenceType.find([('name', '=', 'Account Journal')])
    >>> sequence = Sequence(name='Bank', sequence_type=sequence_type,
    ...     company=company)
    >>> sequence.save()
    >>> AccountJournal = Model.get('account.journal')
    >>> account_journal = AccountJournal(name='Statement',
    ...     type='cash',
    ...     sequence=sequence)
    >>> account_journal.save()

Create Statement Journal::

    >>> StatementJournal = Model.get('account.bank.statement.journal')
    >>> statement_journal = StatementJournal(name='Test',
    ...     journal=account_journal, currency=company.currency, account=cash)
    >>> statement_journal.save()

Create Bank Statement::

    >>> BankStatement = Model.get('account.bank.statement')
    >>> StatementLine = Model.get('account.bank.statement.line')

    >>> statement = BankStatement(journal=statement_journal, date=now)
    >>> statement.save()
    >>> statement.reload()

Import paypal EN file::

    >>> paypal_file = os.path.join(os.path.dirname(__file__), 'paypal-en.csv')
    >>> wizard = Wizard('account.bank.statement.import', [statement])
    >>> wizard.form.import_file = open(paypal_file, 'rb').read()
    >>> wizard.form.type = 'paypal-en'
    >>> wizard.form.confirm = True
    >>> wizard.execute('import_file')
    >>> statement.reload()
    >>> len(statement.lines)
    4
    >>> [l.amount for l in statement.lines]
    [Decimal('24.40'), Decimal('-8.13'), Decimal('24.60'), Decimal('32.54')]
    >>> account_lines = []
    >>> for line in statement.lines:
    ...     [account_line.amount for account_line in line.lines]
    []
    []
    [Decimal('-1.10')]
    [Decimal('-1.33')]

Create Bank Statement::

    >>> BankStatement = Model.get('account.bank.statement')
    >>> StatementLine = Model.get('account.bank.statement.line')

    >>> statement = BankStatement(journal=statement_journal, date=now)
    >>> statement.save()
    >>> statement.reload()

Import paypal ES file::

    >>> paypal_file = os.path.join(os.path.dirname(__file__), 'paypal-es.csv')
    >>> wizard = Wizard('account.bank.statement.import', [statement])
    >>> wizard.form.import_file = open(paypal_file, 'rb').read()
    >>> wizard.form.type = 'paypal-es'
    >>> wizard.form.confirm = True
    >>> wizard.execute('import_file')
    >>> statement.reload()
    >>> len(statement.lines)
    4
    >>> [l.amount for l in statement.lines]
    [Decimal('108.19'), Decimal('-2071.00'), Decimal('-2071.00'), Decimal('29.75')]
    >>> for line in statement.lines:
    ...     [account_line.amount for account_line in line.lines]
    [Decimal('-3.59')]
    []
    []
    [Decimal('-1.25')]
