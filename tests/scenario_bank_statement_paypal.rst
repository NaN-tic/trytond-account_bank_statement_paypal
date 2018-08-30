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
    >>> from trytond.modules.account_bank_statement_paypal.tests.tools \
    ...     import read_file
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts
    >>> today = datetime.date.today()
    >>> now = datetime.datetime.now()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Activate account_bank_statement_paypal module::

    >>> Module = Model.get('ir.module')
    >>> account_invoice_module, = Module.find(
    ...     [('name', '=', 'account_bank_statement_paypal')])
    >>> account_invoice_module.click('install')
    >>> Wizard('ir.module.install_upgrade').execute('upgrade')

Create company::

    >>> Currency = Model.get('currency.currency')
    >>> CurrencyRate = Model.get('currency.currency.rate')
    >>> currencies = Currency.find([('code', '=', 'USD')])
    >>> if not currencies:
    ...     currency = Currency(name='US Dollar', symbol=u'$', code='USD',
    ...         rounding=Decimal('0.01'), mon_grouping='[]',
    ...         mon_decimal_point='.')
    ...     currency.save()
    ...     CurrencyRate(date=today + relativedelta(month=1, day=1),
    ...         rate=Decimal('1.0'), currency=currency).save()
    ... else:
    ...     currency, = currencies
    >>> Company = Model.get('company.company')
    >>> Party = Model.get('party.party')
    >>> company_config = Wizard('company.company.config')
    >>> company_config.execute('company')
    >>> company = company_config.form
    >>> party = Party(name='Dunder Mifflin')
    >>> party.save()
    >>> company.party = party
    >>> company.currency = currency
    >>> company_config.execute('add')
    >>> company, = Company.find([])

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create fiscal year::

    >>> FiscalYear = Model.get('account.fiscalyear')
    >>> Sequence = Model.get('ir.sequence')
    >>> SequenceStrict = Model.get('ir.sequence.strict')
    >>> fiscalyear = FiscalYear(name=str(today.year))
    >>> fiscalyear.start_date = today + relativedelta(month=1, day=1)
    >>> fiscalyear.end_date = today + relativedelta(month=12, day=31)
    >>> fiscalyear.company = company
    >>> post_move_seq = Sequence(name=str(today.year), code='account.move',
    ...     company=company)
    >>> post_move_seq.save()
    >>> fiscalyear.post_move_sequence = post_move_seq
    >>> invoice_seq = SequenceStrict(name=str(today.year),
    ...     code='account.invoice', company=company)
    >>> invoice_seq.save()
    >>> fiscalyear.out_invoice_sequence = invoice_seq
    >>> fiscalyear.in_invoice_sequence = invoice_seq
    >>> fiscalyear.out_credit_note_sequence = invoice_seq
    >>> fiscalyear.in_credit_note_sequence = invoice_seq
    >>> fiscalyear.save()
    >>> FiscalYear.create_period([fiscalyear.id], config.context)

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> account_tax = accounts['tax']
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
    >>> sequence = Sequence(name='Bank', code='account.journal',
    ...     company=company)
    >>> sequence.save()
    >>> AccountJournal = Model.get('account.journal')
    >>> account_journal = AccountJournal(name='Statement',
    ...     type='cash',
    ...     credit_account=cash,
    ...     debit_account=cash,
    ...     sequence=sequence)
    >>> account_journal.save()

Create Statement Journal::

    >>> StatementJournal = Model.get('account.bank.statement.journal')
    >>> statement_journal = StatementJournal(name='Test',
    ...     journal=account_journal, currency=company.currency)
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
    >>> wizard.form.import_file = read_file(paypal_file)
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
    >>> wizard.form.import_file = read_file(paypal_file)
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
