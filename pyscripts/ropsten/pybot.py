# --------------------------------------------
# PYBOT.PY -----------------------------------
# --------------------------------------------
# Python telegram bot  -----------------------
# --------------------------------------------
# --------------------------------------------

from ptb import handlers as hnd
from ptb.util import getpybotTKN
from telegram.ext import Updater, CommandHandler


def main():
    """Run the bot"""

    updater = Updater(getpybotTKN(), use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help",
                                  hnd.help))
    dp.add_handler(CommandHandler("command",
                                  hnd.command))
    dp.add_handler(CommandHandler("balance",
                                  hnd.balance,))
    dp.add_handler(CommandHandler("buy",
                                  hnd.buy))
    dp.add_handler(CommandHandler("sell",
                                  hnd.sell))
    dp.add_handler(CommandHandler("oploan",
                                  hnd.openLoan))
    dp.add_handler(CommandHandler("clloan",
                                  hnd.closeLoan))
    dp.add_handler(CommandHandler("chdirect",
                                  hnd.directChallenge))
    dp.add_handler(CommandHandler("chteam",
                                  hnd.teamChallenge))
    dp.add_handler(CommandHandler("chovernight",
                                  hnd.overnightChallenge))
    dp.add_handler(CommandHandler("pltprice",
                                  hnd.plotPrice))
    dp.add_handler(CommandHandler("notify",
                                  hnd.notify_events,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unotify",
                                  hnd.unotify_events,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("logs",
                                  hnd.logs))
    dp.add_handler(CommandHandler("journalctl",
                                  hnd.journalctl))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
