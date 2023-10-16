# --------------------------------------------
# HANDLERS.PY --------------------------------
# --------------------------------------------
# Handlers function for py TG bot ------------
# --------------------------------------------
# --------------------------------------------

from subprocess import call, check_output
from pandas import read_csv
from numpy import float64
from matplotlib.pyplot import subplots
from ptb.util import setup_logger, pybrownie, write_args
from os import listdir

botlogger = setup_logger('pybot',
                         f"pyscripts/ropsten/logs/pybot.log")


def help(update, context):
    """get help message"""
    msg = """
You can control me by sending these commands:

/command       - Type handler to see his usage
/balance           - See team balance
/buy                  - Purchase tokens from team
/sell                   - Sell tokens of a team
/oploan             - Open loan
/clloan               - Close loan
/chdirect           - Start a direct challange with a team
/chteam            - Start a challange between all teams
/chovernight    - Influence the market
/pltprice            - Plot price progress
/notify                - Notify events start
/unotify              - Notify events stop
/logs                   - See last python logs
/journalctl         - See last service logs
"""
    update.message.reply_text(msg)


def logs(update, context):
    """get logs parsing args, otherwise print usage information"""
    cmd = "tail -n"
    cmd = cmd.split(' ')
    try:
        if (len(context.args) < 1):
            update.message.reply_text('Usage: /logs <type> <nline>')
        else:
            type = context.args[0]
            nline = context.args[1]
            cmd.append(nline)
            if type == 'mng':
                cmd.append("pyscripts/ropsten/logs/management.log")
                out = check_output(cmd)
                update.message.reply_text(out.decode())
            elif type == 'mnt':
                cmd.append("pyscripts/ropsten/logs/monitor.log")
                out = check_output(cmd)
                update.message.reply_text(out.decode())
            elif type == 'bot':
                cmd.append("pyscripts/ropsten/logs/pybot.log")
                out = check_output(cmd)
                update.message.reply_text(out.decode())
            else:
                update.message.reply_text("(logs) Wrong logs type")
    except Exception:
        botlogger.error("(logs) Errors", exc_info=True)
        update.message.reply_text("(logs) Errors, check bot log")


def journalctl(update, context):
    """get service logs parsing args, otherwise print usage information"""
    try:
        if (len(context.args) < 2):
            update.message.reply_text('Usage: /journalctl <service> <type>')
        else:
            service = context.args[0]
            type = context.args[1]
            if type == '1':
                cmd = "sudo journalctl -n 30 -u"
                cmd = cmd.split(' ')
                cmd.append(service+'.service')
                out = check_output(cmd)
                update.message.reply_text(out.decode())
            else:
                cmd = "sudo systemctl status"
                cmd = cmd.split(' ')
                cmd.append(service+'.service')
                out = check_output(cmd)
                update.message.reply_text(out.decode())
    except Exception:
        botlogger.error("(journalctl) Errors", exc_info=True)
        update.message.reply_text("(journalctl) Errors, check bot log")


def command(update, context):
    """
    get documentation about scripts that these bot run,
    if args are parsed, otherwise print usage information
    """
    dict = {'balance':     'balance-digest.py',
            'buy':         'buy.py',
            'sell':        'sell.py',
            'oploan':      'open-loan.py',
            'clloan':      'close-loan.py',
            'chdirect':    'direct-start-win.py',
            'chteam':      'team-start-win.py',
            'chovernight': 'overnight-start-win.py'}
    try:
        if (len(context.args) < 1):
            update.message.reply_text('Usage: /command <handler>')
        else:
            handler = context.args[0]
            if handler == 'logs':
                update.message.reply_text(
                    "(command) No --help avaiable, see usage of handler")
            elif handler == 'journalctl':
                update.message.reply_text(
                    "(command) No --help avaiable, see usage of handler")
            elif handler == 'pltprice':
                update.message.reply_text(
                    "(command) No --help avaiable, see usage of handler")
            else:
                cmd = f"{pybrownie()} pyscripts/ropsten/{dict[handler]} --help"
                cmd = cmd.split(' ')
                out = check_output(cmd)
                update.message.reply_text(out.decode())
    except Exception:
        botlogger.error("(command) Errors", exc_info=True)
        update.message.reply_text("(command) Errors, check bot log")


def balance(update, context):
    """
    grep a balance digest if args are parsed,
    otherwise print usage information
    """
    cmd = f"{pybrownie()} pyscripts/ropsten/balance-digest.py"
    cmd = cmd.split(' ')
    try:
        if (len(context.args) < 1):
            update.message.reply_text('Usage: /balance <team>')
        else:
            cmd.append(context.args[0])
            out = check_output(cmd)
            out = out.splitlines()[72:]
            tout = ''
            for byte in out:
                tout += (byte.decode()+'\n')
            update.message.reply_text(tout[:-2])
    except Exception:
        botlogger.error("(balance) Errors", exc_info=True)
        update.message.reply_text("(balance) Errors, check bot log")


def buy(update, context):
    """
    buy tx if args are parsed,
    otherwise print usage information
    """
    cmd = f"{pybrownie()} pyscripts/ropsten/buy.py"
    cmd = cmd.split(' ')
    try:
        if (len(context.args) < 2):
            update.message.reply_text('Usage: /buy <team> <tknAmount>')
        else:
            cmd.append(context.args[0])
            cmd.append(context.args[1])
            val = call(cmd)
            if val:
                update.message.reply_text(
                    f'(buy) Return err code {val}, check mng logs')
            else:
                update.message.reply_text('(buy) Purchase processed')
    except Exception:
        botlogger.error("(buy) Errors", exc_info=True)
        update.message.reply_text('(buy) Errors, check bot log')


def sell(update, context):
    """
    sell tx if args are parsed,
    otherwise print usage information
    """
    cmd = f"{pybrownie()} pyscripts/ropsten/sell.py"
    cmd = cmd.split(' ')
    try:
        if (len(context.args) < 2):
            update.message.reply_text('Usage: /sell <team> <tknAmount>')
        else:
            cmd.append(context.args[0])
            cmd.append(context.args[1])
            val = call(cmd)
            if val:
                update.message.reply_text(
                    f'(sell) Return err code {val}, check mng logs')
            else:
                update.message.reply_text('(sell) Purchase processed')
    except Exception:
        botlogger.error("(sell) Errors", exc_info=True)
        update.message.reply_text('(sell) Errors, check bot log')


def openLoan(update, context):
    """
    openLoan if args are parsed,
    otherwise print usage information
    """
    cmd = f"{pybrownie()} pyscripts/ropsten/open-loan.py"
    cmd = cmd.split(' ')
    try:
        if (len(context.args) < 1):
            update.message.reply_text('Usage: /oploan <PaC>')
        else:
            cmd.append(context.args[0])
            val = call(cmd)
            if val:
                update.message.reply_text(
                    f'(openLoan) Return err code {val}, check mng logs')
            else:
                update.message.reply_text('(openLoan) Loan opened')
    except Exception:
        botlogger.error("(openLoan) Errors", exc_info=True)
        update.message.reply_text('(openLoan) Errors, check bot log')


def closeLoan(update, context):
    """
    closeLoan if args are parsed,
    otherwise print usage information
    """
    cmd = f"{pybrownie()} pyscripts/ropsten/close-loan.py"
    cmd = cmd.split(' ')
    try:
        if (len(context.args) < 1):
            update.message.reply_text('Usage: /clloan <id>')
        else:
            cmd.append(context.args[0])
            val = call(cmd)
            if val:
                update.message.reply_text(
                    f'(closeLoan) Return err code {val}, check mng logs')
            else:
                update.message.reply_text('(closeLoan) Loan closed')
    except Exception:
        botlogger.error("(closeLoan) Errors", exc_info=True)
        update.message.reply_text('(closeLoan) Errors, check bot log')


def directChallenge(update, context):
    """
    create custom service to start and win direct challenge
    if args are parsed, otherwise print usage information
    """
    cmd = "sudo systemctl start pybot-direct-start-win.service"
    cmd = cmd.split(' ')
    try:
        if (len(context.args) < 2):
            update.message.reply_text('Usage: /chdirect <team> <multiplier>')
        else:
            team = context.args[0]
            multiplier = context.args[1]
            write_args('pybot-direct-start-win', team, multiplier)
            val = call(cmd)
            if val:
                update.message.reply_text(
                    f'(directChallenge) Return err code {val}, ' +
                    'service not started, check mng logs')
            else:
                update.message.reply_text('(directChallenge) Service started')
    except Exception:
        botlogger.error("(directChallenge) Errors", exc_info=True)
        update.message.reply_text('(directChallenge) Errors, check bot log')


def teamChallenge(update, context):
    """
    create custom service to start and win team challenge
    if args are parsed, otherwise print usage information
    """
    cmd = "sudo systemctl start pybot-team-start-win.service"
    cmd = cmd.split(' ')
    try:
        if (len(context.args) < 1):
            update.message.reply_text('Usage: /chteam <multiplier>')
        else:
            multiplier = context.args[0]
            write_args('pybot-team-start-win', multiplier)
            val = call(cmd)
            if val:
                update.message.reply_text(
                    f'(teamChallenge) Return err code {val}, ' +
                    'service not started, check mng logs')
            else:
                update.message.reply_text('(teamChallenge) Service started')
    except Exception:
        botlogger.error("(teamChallenge) Errors", exc_info=True)
        update.message.reply_text('(teamChallenge) Errors, check bot log')


def overnightChallenge(update, context):
    """
    create custom service to start and win overnight challenge
    if args are parsed, otherwise print usage information
    """
    cmd = "sudo systemctl start pybot-overnight-start-win.service"
    cmd = cmd.split(' ')
    try:
        if (len(context.args) < 2):
            update.message.reply_text(
                'Usage: /chovernight <percentage> <multiplier>')
        else:
            percentage = context.args[0]
            multiplier = context.args[1]
            write_args('pybot-overnight-start-win', percentage, multiplier)
            val = call(cmd)
            if val:
                update.message.reply_text(
                    f'(overnightChallenge) Return err code {val}, ' +
                    'service not started, check mng logs')
            else:
                update.message.reply_text(
                    '(overnightChallenge) Service started')
    except Exception:
        botlogger.error("(overnightChallenge) Errors", exc_info=True)
        update.message.reply_text('(overnightChallenge) Errors, check bot log')


def plotPrice(update, context):
    """
    plot price progress, and buy-sell events
    if args are parsed, otherwise print usage information
    """
    path = "pyscripts/ropsten/mnts"
    try:
        if (len(context.args) < 2):
            update.message.reply_text(
                'Usage: /pltprice <team> <slice>')
        else:
            team = context.args[0].upper()
            slice = int(context.args[1])
            col = {'AMPM-ORG': 'green', 'TEAMF': 'purple', 'TEAMM': 'blue'}
            prc = read_csv(f"{path}/lastprice-{team}.history",
                           header=None,
                           dtype=float64,
                           names=['id', team])
            prc.drop_duplicates(keep='first', inplace=True)
            prc.reset_index(drop=True, inplace=True)
            slice_id = prc['id'][prc['id'].size-slice]
            prc = prc[-slice:]
            fig, ax = subplots(figsize=(14, 8))
            prc.plot.line(x='id', y=team, c=col[team], lw=0.7, ax=ax)
            if team != 'AMPM-ORG':
                ebuy = read_csv(f"{path}/buy.history",
                                header=None,
                                dtype=float64,
                                names=['id', 'TEAMF', 'TEAMM'])
                ebuy = ebuy[ebuy['id'] >= slice_id]
                esell = read_csv(f"{path}/sell.history",
                                 header=None,
                                 dtype=float64,
                                 names=['id', 'TEAMF', 'TEAMM'])
                esell = esell[esell['id'] >= slice_id]
                ebuy.plot.scatter(x='id', y=team, marker='o', c='k', ax=ax)
                esell.plot.scatter(x='id', y=team, marker='^', c='k', ax=ax)
            fig.savefig(f"{path}/{team}.png")
            with open(f"{path}/{team}.png", 'rb') as fs:
                update.message.reply_photo(photo=fs)
    except Exception:
        botlogger.error("(plotPrice) Errors", exc_info=True)
        update.message.reply_text('(plotPrice) Errors, check bot log')


def alarm(context):
    """Send the alert message"""
    job = context.job
    files = listdir('pyscripts/ropsten/args/')
    if 'pybot-direct-win.args' in files:
        context.bot.send_message(job.context,
                                 text='(notify) Direct challenge started!')
        call(['mv', 'pyscripts/ropsten/args/pybot-direct-win.args',
              'pyscripts/ropsten/args/pybot-direct-win.args.bk'])
    elif 'pybot-team-win.args' in files:
        context.bot.send_message(job.context,
                                 text='(notify) Team challenge started!')
        call(['mv', 'pyscripts/ropsten/args/pybot-team-win.args',
              'pyscripts/ropsten/args/pybot-team-win.args.bk'])

    elif 'pybot-overnight-win.args' in files:
        context.bot.send_message(job.context,
                                 text='(notify) Overnight challenge started!')
        call(['mv', 'pyscripts/ropsten/args/pybot-overnight-win.args',
              'pyscripts/ropsten/args/pybot-overnight-win.args.bk'])

    else:
        None


def notify_events(update, context):
    """Add a notify events to job queue"""
    chat_id = update.message.chat_id
    try:
        if (len(context.args) < 1):
            update.message.reply_text(
                'Usage: /notify minute')
            return
        min = int(context.args[0])
        if min < 0:
            update.message.reply_text(
                '(notify) Sorry we can not go back to future!')
            return

        # Add job to queue and stop current one if there is a timer already
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()
        new_job = context.job_queue.run_repeating(alarm, interval=(min*60),
                                                  first=0, context=chat_id)
        context.chat_data['job'] = new_job
        update.message.reply_text(
            '(notify) Notify successfully set and started!')
    except Exception:
        botlogger.error("(notify) Errors", exc_info=True)
        update.message.reply_text('(notify) Errors, check bot log')


def unotify_events(update, context):
    """Un-notify events msg, killing the job"""
    if 'job' not in context.chat_data:
        update.message.reply_text('(unotify) Notify not active')
        return
    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']
    update.message.reply_text('(unotify) Notify successfully stopped!')
