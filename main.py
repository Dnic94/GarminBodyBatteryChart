#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################################################################
__program__ = "GBBC"
__version__ = "0.1"
__description__ = f"""{__program__} {__version__}:

Little dirty script to create a multi day chart from various screenshots of the Garmin Connect app
showing the Body Battery screen.
"""

__author__ = "Dominic Schwarz (@Dnic94 <github@dnic42.de>)"
__created__ = "2022-04-30"

########################################################################################################################

import argparse
import datetime
import logging.handlers
import os

import cv2
import numpy as np

# TODO


"""Place imports here"""

logger = logging.getLogger()
if logger.hasHandlers():
    logger.handlers.clear()

logger.setLevel(logging.DEBUG)

# always write everything to the rotating log files
if not os.path.exists("logs"):
    os.mkdir("logs")
log_file_handler = logging.handlers.TimedRotatingFileHandler(
    f"logs/{__program__}.log", when="midnight", backupCount=30
)
log_file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s [%(levelname)s](%(name)s:%(funcName)s:%(lineno)d): %(message)s"
    )
)
log_file_handler.setLevel(logging.DEBUG)
logger.addHandler(log_file_handler)

# also log to the console at a level determined by the --verbose flag
console_handler = logging.StreamHandler()  # sys.stderr
console_handler.setLevel(
    logging.CRITICAL
)  # set later by set_log_level_from_verbose() in interactive sessions
console_handler.setFormatter(
    logging.Formatter("[%(levelname)s](%(name)s): %(message)s")
)
logger.addHandler(console_handler)

# add arguments for the script
parser = argparse.ArgumentParser(
    description=f"{__description__}",
    epilog=f"{__author__} - {__created__}",
    fromfile_prefix_chars="@",
)
parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    help="Verbose Level, can be repeated up to three times (-vvv).",
)
# TODO
parser.add_argument(
    "-d",
    "--directory",
    action="store",
    help="Directory containing the screenshots.",
    required=True,
)
"""Place additional args here"""


def setLogLevel(args):
    if not args.verbose:
        console_handler.setLevel("ERROR")
    elif args.verbose == 1:
        console_handler.setLevel("WARNING")
    elif args.verbose == 2:
        console_handler.setLevel("INFO")
    elif args.verbose >= 3:
        console_handler.setLevel("DEBUG")
    else:
        logger.critical("UNEXPLAINED NEGATIVE COUNT!")


########################################################################################################################
########################################################################################################################
########################################################################################################################
def main(args):
    week_chart = None
    month_chart = None
    # Append Month to X (right) -> 1  or Y (bottom) -> 0 Dimension
    # Month to X (right) will fail to save the result if count of screenshots is too high
    month_direction = 0
    chart = None
    screenshot_list = os.listdir(args.directory)
    screenshot_list.sort(reverse=True)  # Reverse order for correct sorting
    day_counter = 0
    week_counter = 0

    for screenshot_file in screenshot_list:
        day_counter = day_counter + 1
        screenshot = cv2.imread(f"{args.directory}/{screenshot_file}")  # read image
        day_chart = screenshot[
            195 : 1440 - 225, 190 : 3120 - 110
        ]  # Remove Heading and Trailing
        # Row up 7 Screenshots for 1 Week
        if week_chart is None:
            week_chart = day_chart
        else:
            week_chart = np.concatenate((week_chart, day_chart), axis=1)

        # Next Line after 7 Days
        if day_counter == 7:
            if month_chart is None:
                month_chart = week_chart
            else:
                month_chart = np.concatenate((month_chart, week_chart), axis=0)
            day_counter = 0
            week_chart = None
            week_counter = week_counter + 1

            # New Block after 4 Weeks
            if week_counter == 4:
                if chart is None:
                    chart = month_chart
                else:
                    chart = np.concatenate(
                        (chart, month_chart), axis=month_direction
                    )

                week_counter = 0
                month_chart = None

    if week_counter > 0 or day_counter > 0 or chart is None:
        if month_chart is None:
            month_chart = week_chart
        else:
            # add padding to match width
            month_chart_height, month_chart_width, blub = month_chart.shape
            week_chart_height, week_chart_width, blub = week_chart.shape
            week_chart = cv2.copyMakeBorder(
                week_chart,
                0,
                0,
                month_chart_width - week_chart_width,
                0,
                cv2.BORDER_CONSTANT,
                (0, 0, 0),
            )

            month_chart = np.concatenate((month_chart, week_chart), axis=0)

        if chart is None:
            chart = month_chart
        else:
            chart_height, chart_width, blub = chart.shape
            month_chart_height, month_chart_width, blub = month_chart.shape

            if month_direction == 0:
                # Append the new Month to the bottom
                # add padding to match width
                month_chart = cv2.copyMakeBorder(
                    month_chart,
                    0,
                    0,
                    0,
                    chart_width - month_chart_width,
                    cv2.BORDER_CONSTANT,
                    (0, 0, 0),
                )
                chart = np.concatenate((chart, month_chart), axis=0)

            else:
                # Append the new Month to the right
                # add padding to match height
                month_chart = cv2.copyMakeBorder(
                    month_chart,
                    0,
                    chart_height - month_chart_height,
                    0,
                    0,
                    cv2.BORDER_CONSTANT,
                    (0, 0, 0),
                )
                chart = np.concatenate((chart, month_chart), axis=1)

    # save result
    date = datetime.datetime.today().strftime("%Y%m%d")
    result = cv2.imwrite(f"{date}_gbbc.jpg", chart)
    print(result)

    # cv2.imshow('Chart', chart)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return result


########################################################################################################################
########################################################################################################################
########################################################################################################################
if __name__ == "__main__":
    args = parser.parse_args()
    setLogLevel(args)
    main(args)
