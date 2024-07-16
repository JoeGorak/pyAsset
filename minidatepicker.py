"""
    MiniDatePicker.py

    A custom class that looks like the wx.DatePickerCtrl but with the ability to customise
    the calendar and the output format. (DatePickerCtrl is seemingly stuck with MM/DD/YYYY format)
    Works with wx.DateTime or python datetime values
    With or without an activating button
    Uses wx.adv.GenericCalendarCtrl
    Uses locale to enable different languages for the calendar

    An attempt has been made to allow days marked with attributes denoting Holiday, Marked, Restricted to live with each other

    Dates can be marked, restricted, defined as holidays and have ToolTip notes
     Marked and Restricted dates can be defined as a simple date or use more advanced rules for example the 3rd Friday of the month
     or every Tuesday of the month. Note: they can be year specific or every year

    Marked dates are marked with a Border, either Square or Oval
    Holidays are normally highlighted with a different Foreground/Background colour
    Restricted dates are marked using an Italic StrikeThrough font

    Defined Holidays can be year specific or every year on that Month/Day

    Official Holidays rely on the python 'holidays' package being available (pip install --upgrade holidays)
        official holidays are automatically entered into the Notes for you
    You may add in more than one region's official holidays and they will be denoted by the country code
     and region code if appropriate.

    Notes are date specific or every year and can follow the rules for Marked and Restricted dates, namely:
            All of a specified week day in a month;
            The specified occurrence of a weekday in a month e.g. 3rd Tuesday or last Friday of the month
            The last day of the month
            The last weekday of the month

    Navigation:
     The Escape key will exit the Calendar
     The Arrow keys will navigate the calendar
     The PageUp/PageDown keys will retreat and advance and the month respectively, as will MouseScrollUp and MouseScrollDown
     The Home and End keys jump to the First and Last day of the month, respectively.
     A right click on the calendar on a blank day, will display All the notes for the month.
     Date ToolTips will be displayed as and when appropriate, depending of the position in the calendar and settings

    MiniDatePicker(parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.BORDER_SIMPLE, name="MiniDatePicker", date=0, formatter=''):

        @param parent:   Parent window. Must not be None.
        @param id:       identifier. A value of -1 indicates a default value.
        @param pos:      MiniDatePicker position. If the position (-1, -1) is specified
                         then a default position is chosen.
        @param size:     If the default size (-1, -1) is specified then a default size is calculated.
                         Size should be able to accomodate the specified formatter string + button
        @param style:    Alignment (Left,Middle,Right).
        @param name:     Widget name.
        @param date:     Initial date (an invalid date = today)
        @param formatter A date formatting string in the form of a lambda function
                         The formatter will be called with a wx.DateTime thus we can use .Format()
                          the wxPython version of the standard ANSI C strftime
                         default lambda dt: dt.FormatISODate()
                          = ISO 8601 format "YYYY-MM-DD".
                         or a lambda function with a format string e.g.:
                            lambda dt: (f'{dt.Format("%a %d-%m-%Y")}')
                         e.g.:
                            format = lambda dt: (f'{dt.Format("%a %d-%m-%Y")}')
                            format = lambda dt: (f'{dt.Format("%A %d %B %Y")}')
                         or
                            fmt = "%Y/%m/%d"
                            format = lambda dt: (dt.Format(fmt))
                            format = lambda dt: (dt.Format("%Y/%m/%d"))
                            format = lambda dt: (dt.FormatISODate())
                        for those who prefer strftime formatting:
                            format = (lambda dt: (f'{wx.wxdate2pydate(dt).strftime("%A %d-%B-%Y")}'))

    TextCtrl Styles: wx.TE_READONLY (Default)
            wx.TE_RIGHT
            wx.TE_LEFT
            wx.TE_CENTRE

            wx.BORDER_NONE is always applied to the internal textctrl
            wx.BORDER_SIMPLE is the default border for the control itself

    Events: EVT_DATE_CHANGED A date change occurred in the control

    Event Functions:
        GetValue()          Returns formatted date in the event as a string

        GetDate()           Returns wxDateTime date in the event, with all of its attendant functions

        GetDateTime()       Returns python datetime of date in the event

        GetTimeStamp()      Returns seconds since Jan 1, 1970 UTC for current date

    Functions:
        GetValue()          Returns formatted date in the event as a string

        GetDate()           Returns wxDateTime date in the control

        GetDateTimeValue()  Returns python datetime of date in the control

        GetTimeStamp()      Returns seconds since Jan 1, 1970 UTC for selected date

        GetLocale()         Returns tuple of current language code and encoding

        SetValue(date)      Sets the date in the control
                            expects a wx.DateTime, a python datetime datetime or a timestamp
                            Any invalid date defaults to wx.DateTime.Today()

        SetFormatter(formatter) Date format in the form of a lambda
            default:    lambda dt: dt.FormatISODate()

        SetButton(Boolean)  Shows or Hides Ctrl Button

        SetButtonBitmap(bitmap=None)  Set a specified image to used for the Button
                                      This is also used for the Focus image unless overridden (see below)
                                      You may use a file name or a wx.Bitmap

        SetButtonBitmapFocus(bitmap=None)  Set a specified image to used for the Button focus
                                      You may use a file name or a wx.Bitmap

        SetLocale(locale)   Set the locale for Calendar day and month names
                             e.g. 'de_DE.UTF-8' German
                                  'es_ES.UTF-8' Spanish
                             depends on the locale being available on the machine

        SetCalendarStyle(style)
            wx.adv.CAL_SUNDAY_FIRST: Show Sunday as the first day in the week
            wx.adv.CAL_MONDAY_FIRST: Show Monday as the first day in the week
            wx.adv.CAL_SHOW_HOLIDAYS: Highlight holidays in the calendar (only generic)
            wx.adv.CAL_NO_YEAR_CHANGE: Disable the year changing (deprecated, only generic)
            wx.adv.CAL_NO_MONTH_CHANGE: Disable the month (and, implicitly, the year) changing
            wx.adv.CAL_SHOW_SURROUNDING_WEEKS: Show the neighbouring weeks in the previous and next months
            wx.adv.CAL_SEQUENTIAL_MONTH_SELECTION: more compact, style for the month and year selection controls.
            wx.adv.CAL_SHOW_WEEK_NUMBERS

        SetCalendarHighlights(colFg, colBg)     Colours to mark the currently selected date

        SetCalendarHolidayColours(colFg, colBg) Colours to mark Holidays

        SetCalendarHeaders(colFg, colBg)

        SetCalendarFg(colFg)    Set Calendar ForegroundColour

        SetCalendarBg(colBg)    Set Calendar BackgroundColour

        SetCalendarFont(font=None)  Set font of the calendar to a wx.Font
                Alter the font family, weight, size, etc

        SetCalendarMarkDates(markdates = {}) Mark dates with a Border
                A dictionary containing year and month tuple as the key and a list of days for the values to be marked
                e.g.
                    {
                     (2023, 7) : [2,5,7,11,30],
                     (2023, 8) : [7,12,13,20,27],
                     (2023, 9) : [1,27]
                    }

                Values of less than 0 indicate not a specific date but a day: -1 Monday, -2 Tuesday, ... -7 Sunday
                 allowing you to mark all Mondays and Fridays in the month of January e.g {(2023, 1) : [-1, -5]}
                 You may include a mixture of negative and positive numbers (days and specific dates)

                Negative values beyond that indicate the nth weekday, (the indexing is a bit confusing because it's off by 1
                 the first digit represents the day and the 2nd digit represents the occurrence i.e.

                -11, 1st Monday | -12, 2nd Monday | -13, 3rd Monday | -14, 4th Monday | -15, 5th or Last Monday
                -21, 1st Tuesday | -22, 2nd Tuesday | -23, 3rd Tuesday | -24, 4th Tuesday | -25, 5th or Last Tuesday
                ..............................................................................................................
                -71, 1st Sunday | -72, 2nd Sunday | -73, 3rd Sunday | -74, 4th Sunday | -75, 5th or Last Sunday

                If the 5th occurrence of a weekday doesn't exist, the last occurrence of the weekday is substituted.

                -99 Stands for the last day of the month
                -98 is for the last weekday of the month

        SetCalendarMarkBorder(border=wx.adv.CAL_BORDER_SQUARE, bcolour=wx.NullColour)
                Defines the border type to mark dates wx.adv.CAL_BORDER_SQUARE (default)
                and a border colour e.g. wx.NullColour (Default), wx.RED  or a hex value '#800080' etc
                Valid border values are:
                    wx.adv.CAL_BORDER_NONE      - 0
                    wx.adv.CAL_BORDER_SQUARE    - 1
                    wx.adv.CAL_BORDER_ROUND     - 2


        SetCalendarHolidays(holidays = {})
                A dictionary containing year and month tuple as the key and a list of days for the values e.g.
                    {
                     (2023, 1) : [1,],
                     (2023, 7) : [1,30],
                     (2023, 8) : [7,15,27],
                     (2023, 12) : [25,26]
                    }

                Holidays can also be 'fixed' Holidays occurring every year on the same day by setting the year to zero in the key
                e.g.
                    {
                     (0, 1) : [1,],                            # January 1st is a Holiday every year
                     (2023, 7) : [1,30],
                     (2023, 8) : [7,15,27],
                     (0, 12) : [25,26]                         # Christmas Day and Boxing Day are Holidays every year
                    }

        SetCalendarNotes(notes = {})
                A dictionary containing a year, month, day tuple as the key and a string for the note e.g.
                    {
                     (2023, 1, 1) : "New Year's Day",
                     (2023, 12, 25) : "Christmas Day"
                    }

                Like Holidays, Notes can be assigned to a specific day every year
                    {
                     (0, 1, 1) : "New Year's Day",
                     (0, 12, 25) : "Christmas Day"
                    }

                To compliment Marked Dates and Restricted Dates, notes can also be assigned a negative day following the
                 the same pattern as Marked Dates and Restricted Dates.
                Allowing you to match Notes with Marked Dates and Restricted Dates.

                    {
                     (0, 1, -11) : "The 1st Monday of January/the year",
                     (0, 1, -35) : "The last Wednesday of January",
                     (0, 2, -5)  : "Every Friday in February"
                    }

                If you set Official Holidays, they are enter automatically into the notes, marked with a leading asterix (*).

                Notes are displayed as a ToolTip, when the day is hovered over or Right clicked
                 or if the mouse is over the calendar and the Arrow keys are used to navigate the calendar to that day.

                A right click on the calendar on a blank day, will display All the notes for the month.

        SetCalendarRestrictDates(rdates = {})
                A dictionary containing a year and month tuple as the key and a list of days, for the days that
                 are Not selectable within that year/month i.e. the reverse of Marked Dates
                 e.g.
                    {
                     (2023, 1) : [1,15],
                     (2023, 3) : [1,15],
                     (2023, 5) : [1,15],
                     (2023, 7) : [1,15,23],
                     (2023, 9) : [1,15],
                     (2023, 11) : [1,15]
                    }

                All dates in the 'restricted' dictionary use an Italic StruckThrough font and cannot be selected

                See SetCalendarMarkDates for the ability to use negative values to calculate dictionary values to restrict
                more complicated entries like All Mondays or the 2nd and 4th Tuesday for example, by using negative values.

        SetCalendarDateRange(lowerdate=wx.DefaultDateTime, upperdate=wx.DefaultDateTime)
                Either 2 wx.DateTime values to restrict the selectable dates
                or just a lower date or just an upper date
                (The oddity of wx.DateTime months from 0 is catered for)
                Returns False if the dates are not wx.DateTime objects
                wx.DefaultDateTime equals no date selected.

                Dates outside of the range will display an "Out of Range" ToolTip, with the defined range.

        SetCalendarOnlyWeekDays(boolean) Default False
                If set only weekdays are selectable. weekends and holidays use an Italic StruckThrough font and cannot be selected
                Holidays are treated as Not a weekday i.e. no work

        AddOfficialHolidays(country='', subdiv='', language='') Default blank, blank, blank
                Only available if the python 'holidays' module was successfully imported
                Currently supports 134 country codes using country ISO 3166-1 alpha-2 codes and the optional subdivision
                 (state, region etc) using ISO 3166-2 codes.
                Language must be an ISO 639-1 (2-letter) language code. If the language translation is not supported
                the original holiday names are returned.

                For details: https://python-holidays.readthedocs.io/en/latest/
                 (or the file 'python-holidays — holidays documentation.html' supplied with this program)
                e.g.
                    country='ES'                    Spain
                    country='ES' and subdiv='AN'    Spain, Andalucia
                    country='UK' and subdiv='ENG'   United Kingdom, England
                    country='US' and subdiv='SC'    USA, South Carolina

                function returns True if successful, an existing country and subdivision (if supplied)
                 or False if there was an error

                This function can be called multiple times, once for each country or region in a country
                 that you wish marked on the calendar.
                The first call sets the primary holiday region.
                May be useful if you are operating in more than one geographical area, with differing holidays

    Default Values:
        date    -       Today
        style   -       READ_ONLY

Author:     J Healey
Created:    04/12/2022
Copyright:  J Healey - 2022-2023
License:    GPL 3 or any later version
Email:      <rolfofsaxony@gmx.com>
Version     1.5

A thank you to Richard Townsend (RichardT) for the inspiration of the date dictionaries for some of the functions.

Changelog:
1.5     Add optional holidays package
        A fast, efficient Python library for generating country and subdivision- (e.g. state or province) specific
         sets of government-designated holidays on the fly.
        Alter the font_family, weight, size etc of the calendar popup
        New functions:
            AddOfficialHolidays - to add Official holiday zones using 'python holidays package'
            SetCalendarFont()   - Change calendar font_family, weight, style, size etc
        Fix for MSW, added style wx.PU_CONTAINS_CONTROLS to the Popup, which allows the month choice drop down
         to function

1.4     New Functions
         SetCalendarHolidayColours
         SetCalendarHolidays
         SetCalendarMarkBorder
         SetCalendarMarkDates
        Permit the definition of Holidays and key dates to be highlighted and the method of highlighting;
         by colour for holidays and border type, plus border colour, for marked days
        SetCalendarDateRange
         allows the restriction of dates to a range, that can be selected
        SetCalendarNotes
            Allows for notes to be assigned to individual days in the calendar.
            If notes exist for a day, when hovered over the ToolTip will display the note.
            Envisaged to be used in conjunction with Holidays and Marked days to provide detail
        SetCalendarRestrictDates
            Set a dictionary of dates that are Not selectable
        SetCalendarOnlyWeekDays
            Only weekdays are selectable i.e. weekends and holidays are not

1.3     New function SetButtonBitmap()
        Allows a specified image to be used for the button
        (also allows bitmap from wx.ArtProvider to be used)

        New function SetButtonBitmapFocus()
        Allow a specified image to be used for the button focus

1.2     Specifically SetFocus() on the button

1.1     subclass changes from wx.Control to wx.Panel to handle tab traversal
        The image will indicate Focus
        Demonstration colours set to Hex

Usage example:

import wx
import minidatepicker as MDP
class Frame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "MiniDatePicker Demo")
        format = (lambda dt: (f'{dt.Format("%A %d-%m-%Y")}'))
        panel = wx.Panel(self)
        mdp = MDP.MiniDatePicker(panel, -1, pos=(50, 50), size=(-1,-1), style=0, date=0, formatter=format)
        self.Show()

app = wx.App()
frame = Frame(None)
app.MainLoop()

"""

import wx
import wx.adv
from wx.lib.embeddedimage import PyEmbeddedImage
import datetime
import calendar
import locale
try:
    import holidays
    holidays_available = True
except ModuleNotFoundError:
    holidays_available = False

img = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABg2lDQ1BJQ0MgcHJvZmlsZQAA'
    b'KJF9kT1Iw0AcxV9TS0UiDu0g4pChOlkQFXHUKhShQqgVWnUwufQLmjQkKS6OgmvBwY/FqoOL'
    b's64OroIg+AHi6OSk6CIl/i8ptIj14Lgf7+497t4BQqPCdLtnHNANx0onE1I2tyqFXyEihAhi'
    b'EBVmm3OynELX8XWPAF/v4jyr+7k/R7+WtxkQkIhnmWk5xBvE05uOyXmfOMpKikZ8Tjxm0QWJ'
    b'H7mu+vzGueixwDOjViY9TxwlloodrHYwK1k68RRxTNMNyheyPmuctzjrlRpr3ZO/UMwbK8tc'
    b'pzmMJBaxBBkSVNRQRgUO4rQapNhI036ii3/I88vkUslVBiPHAqrQoXh+8D/43a1dmJzwk8QE'
    b'EHpx3Y8RILwLNOuu+33sus0TIPgMXBltf7UBzHySXm9rsSNgYBu4uG5r6h5wuQMMPpmKpXhS'
    b'kKZQKADvZ/RNOSByC/St+b219nH6AGSoq9QNcHAIjBYpe73Lu3s7e/v3TKu/H0FDcpMpQj/v'
    b'AAAACXBIWXMAAAsTAAALEwEAmpwYAAACk0lEQVRIx43W3+unQxQH8Nc83w9tVutHNj9v5M4q'
    b'tty7oC2u2Fy58KOV9g/AlRJygQvlRrIlpbhSW7uJorCKlKQoJand7AVJYm3Z7zMu9v18zWfM'
    b'J6aeZs7MmTNnznm/zzwFE6p/WunkLczNXEnfyhO2Rza2rLfpP4xPG4zPm2xsNR6NPN/uNuq8'
    b'nAa3W4tGaRQrrsZFkX/FIbyO3dG7PHq/RP4d9+NIs/YHTi+OrzKYcS2OZtNpvIqbcQfuyqFv'
    b'pH80e45hP26JM1fhYtyDHzGvUGuttZSyB3/hWdyAn3P4KXwYg+dywAfx9mTmf8JH+A5P45Ls'
    b'Ox/XUkpJzM/kJofxJ17JjR7GTfgGX2EfHsHZ3PRM5OsynvvEtTCrGR+Ih3fmJvsTgmsSEtE5'
    b'lb5N7g7qVgO0LIk/FM9r5N14uUPM3TiY/bVbK5hbDPdEaudq8/VQnBu4Lzo7XJiWJA8Y2reK'
    b'5/F4jN6L9/EaHsQFsVewHZtWSfLUeTBqBbfitxi6HTfiisjn1pTPA2daNZ7PDengh8R9b9Cz'
    b'L0g6G73bcGUguSv7/1UypkFYlnA9iZfwPR4K+V7EM/H2cIh2JGG7sCszFXW1oZDNeA57Ujre'
    b'CkSfSClYpYRcH3Ie7EJU2ySPilnBCXwW4rwdKH4axlYcDwe+xnsbSvlO1vt6Lsa/TGH7OP0X'
    b'+Dy6J/BtdD5pbK1BfjVg8aL4QlMIj2btscaBN5s9D3RkW4hWpwaztXmAapfwTdAdEbOF/BoP'
    b'JlyamD/VvU6tV/OgrCxzu3BZq7NqFE/iXdzXkW5UOspAZznonaVUY6t9zeRdKMu4YeVUa507'
    b'lg51lrXlPS+dh6MwTJibw6dBSdn4J1K6R39ofPDH8L9/c/4GBa36v+mJzSMAAAAASUVORK5C'
    b'YII=')

imgf = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAA'
    b'CXBIWXMAAAsTAAALEwEAmpwYAAADf0lEQVRIx+2V3yusWxjHP2u9o8Y7k92e6DQ1U3KUGiXp'
    b'iDZGUepEtF1RdlImuVEucCGk1K7hD9BEfuz2nXBzqIkLdS7VODXDldygEfmVkTBr7at3mjFj'
    b'37k7z9X7Pms96/v8+H7XEt/3vms+0CQfbB8OYEv/+fbnNx4fH1FKsXGxgfpX0dvbSyKRQGvN'
    b'9fU1QghcLhdaa5xOJ6urq4g6wdc/viKEwOFw8OP4RzZAT0kP7e3tOJ1O3G43gUCA0H8hdnZ2'
    b'2NraQilFT08PSinm5uaQUtLW1kYkEiHwV4CpqSni8TgPDw9sbGzw8+RnJsD9/T15eXmMj49z'
    b'fHxMYWEhWms8Hg+NjY1IKbHZbCilaGpqQgiB1+tFSklRURF+v5/S0lImJye5u7vLnkEymcQ0'
    b'Tc7Ozpifnyc/P5+BgQGcTicLCwtEo1F8Ph8VFRXEYjFCoRB2u51AIIBpmoRCIU5PTzFNEyll'
    b'NoBhGAAIITAMg3A4jNfrZXt7G601kUiEeDzO+fk5BwcHAITDYTweD+FwGCFE6tD0b9vbqWut'
    b'0VqzuLjIwsICQgi01iQSCQYHB1PBWms2NzdZX1/HMAyEEBlrWRXkWrR8VrAFlp6hlJJkMpny'
    b'CyFQSmUDWAenB6ebEILR0VGCwSBSStbW1mhubqavr4/l5WVeXl5QSqG1TrU7o0XpGeQyrTX7'
    b'+/sUFBSglGJ3d5fDw0Ourq5QSmGz2X4vNCklWutUecXFxSQSCS4vL/H5fMRiMaLRKHa7Ha01'
    b'e3t7XFxccHd3x9PTE1LKDPa8e1VYfZ6enmZoaIiSkhKWlpZwu90MDw8zMTGBzWZjfn6etrY2'
    b'+vv7CQaDPD8/k075rAqszIUQSCkZGxvj/v6ex8dHurq6iMfjzMzM4HA4eH19pbe3l5OTE/Ly'
    b'8lhfX89oUQYJ3gJY/a6vr6empgbTNOns7MQwDGpra/H7/QghaG1txePxUF5eTktLy7tEyRKa'
    b'ZTU1NVRWVuJyuWhoaMDlclFVVUV1dTWGYVBfX09ZWRmVlZXU1dWlGPRboVkc1lozMjKC1hop'
    b'JR0dHQghmJ2dTe3t7u5OxaysrGSI7V2hWcNJF9hbYeWib64Ecw759vYW0zSZmppK+dKzsip6'
    b'e61YvqenJ25ubjL2iPQ3+eafG46OjjJEl+vqsA7OBe7z+fj096fcM/jc+pkvrV/+f/Qz7BdH'
    b'Sp/4DuCblwAAAABJRU5ErkJggg==')

__version__ = 1.5


mdpEVT = wx.NewEventType()
EVT_DATE_CHANGED = wx.PyEventBinder(mdpEVT, 1)


class mdpEvent(wx.PyCommandEvent):
    def __init__(self, eventType, eventId=1, date=None, value=''):
        """
        Default class constructor.

        :param `eventType`: the event type;
        :param `eventId`: the event identifier.
        """
        wx.PyCommandEvent.__init__(self, eventType, eventId)
        self._eventType = eventType
        self.date = date
        self.value = value

    def GetDate(self):
        """
        Retrieve the date value of the control at the time
        this event was generated, Returning a wx.DateTime object"""
        return self.date

    def GetValue(self):
        """
        Retrieve the formatted date value of the control at the time
        this event was generated, Returning a string"""
        return self.value.title()

    def GetDateTime(self):
        """
        Retrieve the date value of the control at the time
        this event was generated, Returning a python datetime object"""
        return wx.wxdate2pydate(self.date)

    def GetTimeStamp(self):
        """
        Retrieve the date value represented as seconds since Jan 1, 1970 UTC.
        Returning a integer
        """
        return int(self.date.GetValue()/1000)


class MiniDatePicker(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.BORDER_SIMPLE, name="MiniDatePicker", date=0, formatter='', button_alignment=wx.RIGHT):

        wx.Control.__init__(self, parent, id, pos=pos, size=size, style=style, name=name)
        self.parent = parent
        self._date = date
        if formatter:
            format = formatter
        else:
            format = lambda dt: dt.FormatISODate()
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        self.SetWindowStyle(wx.BORDER_NONE)
        self._style = style
        self._calendar_style = wx.adv.CAL_MONDAY_FIRST|wx.adv.CAL_SHOW_HOLIDAYS
        self._calendar_headercolours = None
        self._calendar_highlightcolours = None
        self._calendar_holidaycolours = None
        self._calendar_Bg = None
        self._calendar_Fg = None
        self._calendar_Font = None
        self._calendar_MarkDates = {}
        self._calendar_MarkBorder = (wx.adv.CAL_BORDER_SQUARE, wx.NullColour)
        self._calendar_Holidays = {}
        self._calendar_RestrictDates = {}
        self._calendar_daterange = (wx.DefaultDateTime, wx.DefaultDateTime)
        self._calendar_Notes = {}
        self._calendar_SetOnlyWeekDays = False
        self._calendar_OfficialHolidays = False
        self._calendar_AddOfficialHolidays = []

        if size == wx.DefaultSize:
            dc = wx.ScreenDC()
            dc.SetFont(font)
            trialdate = format(wx.DateTime(28,9,2022)) # a Wednesday in September = longest names in English
            w, h = dc.GetTextExtent(trialdate)
            size = (w+64, -1) # Add image width (24) plus a buffer
            del dc
        self._pop = False
        self._veto = False
        #try:
        #    locale.setlocale(locale.LC_TIME, ".".join(locale.getlocale()))
        #except Exception as e:
        #    pass
        txtstyle = wx.TE_READONLY

        if style & wx.TE_LEFT or style == wx.TE_LEFT:
            txtstyle = txtstyle | wx.TE_LEFT
        elif style & wx.TE_RIGHT:
            txtstyle = txtstyle | wx.TE_RIGHT
        else:
            txtstyle = txtstyle | wx.TE_CENTRE
        if style & wx.TE_READONLY:
            txtstyle = txtstyle | wx.TE_READONLY
        if style & wx.BORDER_NONE:
            txtstyle = txtstyle | wx.BORDER_NONE

        # MiniDatePicker
        self.ctl = wx.TextCtrl(self, id, value=str(self._date),
                               pos=pos, size=size, style=txtstyle, name=name)
        self.button = wx.Button(self, -1, size=(40, -1))
        self.button.SetBitmap(img.Bitmap)
        self.button.SetBitmapFocus(imgf.Bitmap)
        self.button.SetFocus()
        self.MinSize = self.GetBestSize()
        # End

        # Bind the events
        self._formatter = format
        self.button.Bind(wx.EVT_BUTTON, self.OnCalendar)
        self.ctl.Bind(wx.EVT_LEFT_DOWN, self.OnCalendar)
        self.SetValue(date)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        if button_alignment == wx.RIGHT:
            sizer.Add(self.ctl, 1, wx.EXPAND, 0)
            sizer.Add(self.button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        else:
            sizer.Add(self.button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
            sizer.Add(self.ctl, 1, wx.EXPAND, 0)
        self.SetSizerAndFit(sizer)
        self.ctl.DisableFocusFromKeyboard()
        self.Show()

    def OnCalendar(self, _event=None):
        if self._pop:
            return
        self._pop = True # controls only one popup at any one time
        self.calendar = CalendarPopup(
            self, self._date, self.OnDate, self.GetTopLevelParent(), wx.PU_CONTAINS_CONTROLS|wx.SIMPLE_BORDER)
        pos = self.ClientToScreen((0, 0))
        size = self.GetSize()
        self.calendar.Position(pos, (0, size.height))

    def SetFormatter(self, formatter):
        '''formatter will be called with a wx.DateTime'''
        self._formatter = formatter
        self.OnDate(self._date)

    def SetLocale(self, alias):
        try:
            locale.setlocale(locale.LC_TIME, locale=alias)
        except Exception as e:
            locale.setlocale(locale.LC_TIME, locale='')
        self.SetValue(self._date)

    def SetCalendarStyle(self, style=0):
        self._calendar_style = style

    def SetCalendarHeaders(self, colFg=wx.NullColour, colBg=wx.NullColour):
        self._calendar_headercolours = colFg, colBg

    def SetCalendarHighlights(self, colFg=wx.NullColour, colBg=wx.NullColour):
        self._calendar_highlightcolours = colFg, colBg

    def SetCalendarHolidayColours(self, colFg=wx.NullColour, colBg=wx.NullColour):
        self._calendar_holidaycolours = colFg, colBg

    def SetCalendarFg(self, colFg=wx.NullColour):
        self._calendar_Fg = colFg

    def SetCalendarBg(self, colBg=wx.NullColour):
        self._calendar_Bg = colBg

    def SetCalendarFont(self, font=None):
        self._calendar_Font = font

    def SetCalendarMarkDates(self, markdates = {}):
        self._calendar_MarkDates = markdates

    def SetCalendarMarkBorder(self, border=wx.adv.CAL_BORDER_SQUARE, bcolour=wx.NullColour):
        self._calendar_MarkBorder = (border, bcolour)

    def SetCalendarHolidays(self, holidays = {}):
        self._calendar_Holidays = holidays

    def AddOfficialHolidays(self, country='', subdiv='', language=''):
        if not holidays_available:
            return False
        country = country.upper()
        subdiv = subdiv.upper()
        try:
            supported = holidays.country_holidays(country=country).subdivisions
        except Exception as e:
            return False
        if subdiv:
            if subdiv not in supported:
                return False
        if not self._calendar_OfficialHolidays:
            self._calendar_OfficialHolidays = (country, subdiv, language)
        else:
            self._calendar_AddOfficialHolidays.append([country, subdiv, language])
        return True

    def SetCalendarRestrictDates(self, rdates = {}):
        self._calendar_RestrictDates = rdates

    def SetCalendarDateRange(self, lowerdate=wx.DefaultDateTime, upperdate=wx.DefaultDateTime):
        if not isinstance(lowerdate, wx.DateTime):
            return False
        if not isinstance(upperdate, wx.DateTime):
            return False
        self._calendar_daterange = (lowerdate, upperdate)
        return True

    def SetCalendarNotes(self, notes = {}):
        self._calendar_Notes = notes

    def SetCalendarOnlyWeekDays(self, wds = False):
        self._calendar_SetOnlyWeekDays = wds
        if wds:
            self._calendar_style = self._calendar_style | wx.adv.CAL_SHOW_HOLIDAYS

    def SetButton(self, button=True):
        if button:
            self.button.Show()
        else:
            self.button.Hide()
        self.Layout()

    def SetButtonBitmap(self, bitmap=None):
        if not bitmap:
            return
        bitmap = wx.Bitmap(bitmap)
        self.button.SetBitmap(bitmap)
        self.button.SetBitmapFocus(bitmap)

    def SetButtonBitmapFocus(self, bitmap=None):
        if not bitmap:
            return
        bitmap = wx.Bitmap(bitmap)
        self.button.SetBitmapFocus(bitmap)

    def OnDate(self, date):
        self._date = date
        self.ctl.SetValue(self._formatter(date).title())
        self.MinSize = self.GetBestSize()
        if self._veto:
            self._veto = False
            return
        event = mdpEvent(mdpEVT, self.GetId(), date=date, value=self._formatter(date))
        event.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(event)

    def GetValue(self):
        return self.ctl.GetValue()

    def GetDate(self):
        return self._date

    def GetDateTimeValue(self):
        """
        Return a python datetime object"""
        return wx.wxdate2pydate(self._date)

    def GetTimeStamp(self):
        """
        Retrieve the date value represented as seconds since Jan 1, 1970 UTC.
        Returning a integer
        """
        return int(self._date.GetValue()/1000)

    def GetLocale(self):
        return locale.getlocale(category=locale.LC_TIME)

    def SetValue(self, date):
        if isinstance(date, wx.DateTime) or isinstance(date, str):
            pass
        elif isinstance(date, datetime.date):
            date = wx.pydate2wxdate(date)
        elif isinstance(date, int) and date > 0:
            date = wx.DateTime.FromTimeT(date)
        elif isinstance(date, float) and date > 0:
            date = wx.DateTime.FromTimeT(int(date))
        else:  # Invalid date value default to today's date
            date = wx.DateTime.Today()
        if not isinstance(date, str):
            self._date = date.ResetTime()
        self._veto = True
        self.SetFormatter(self._formatter)


class CalendarPopup(wx.PopupTransientWindow):
    def __init__(self, parent, date, callback, *args, **kwargs):
        '''date is the initial date; callback is called with the chosen date'''
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.callback = callback
        self.calendar = wx.adv.GenericCalendarCtrl(self, pos=(5, 5), style=parent._calendar_style)
        self.calendar.SetDate(date)
        self.Holidays = {}
        self.OfficialHolidays = {}
        self.RestrictedDates = {}
        self.MarkDates = {}
        self.Notes = {}

        if parent._calendar_headercolours:
            self.calendar.SetHeaderColours(parent._calendar_headercolours[0],parent._calendar_headercolours[1])
        if parent._calendar_highlightcolours:
            self.calendar.SetHighlightColours(parent._calendar_highlightcolours[0],parent._calendar_highlightcolours[1])
        if parent._calendar_holidaycolours:
            self.calendar.SetHolidayColours(parent._calendar_holidaycolours[0],parent._calendar_holidaycolours[1])
        if parent._calendar_Bg:
            self.calendar.SetBackgroundColour(parent._calendar_Bg)
            self.SetBackgroundColour(parent._calendar_Bg)
        if parent._calendar_Fg:
            self.calendar.SetForegroundColour(parent._calendar_Fg)
        if parent._calendar_Font:
            self.calendar.SetFont(parent._calendar_Font)
        self.markborder = parent._calendar_MarkBorder
        if parent._calendar_MarkDates:
            self.SetMarkDates(parent._calendar_MarkDates)
        if parent._calendar_Holidays:
            self.SetHolidays(parent._calendar_Holidays)
        if parent._calendar_OfficialHolidays:
            self.SetOfficialHolidays(parent._calendar_OfficialHolidays)
        if parent._calendar_daterange[0].IsValid() or parent._calendar_daterange[1].IsValid():
            self.SetDateRange(parent._calendar_daterange[0], parent._calendar_daterange[1])
        if parent._calendar_RestrictDates:
            self.SetRestrictDates(parent._calendar_RestrictDates)
        if parent._calendar_Notes:
            self.SetNotes(parent._calendar_Notes)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.calendar, 1, wx.ALL | wx.EXPAND)
        self.SetSizerAndFit(sizer)
        self.calendar.Bind(wx.adv.EVT_CALENDAR_MONTH, self.OnChange)
        self.calendar.Bind(wx.adv.EVT_CALENDAR_YEAR, self.OnChange)
        self.calendar.Bind(wx.adv.EVT_CALENDAR, self.OnChosen)
        self.calendar.Bind(wx.adv.EVT_CALENDAR_SEL_CHANGED, self.OnToolTip)
        self.calendar.Bind(wx.EVT_MOTION, self.OnToolTip)
        self.calendar.Bind(wx.EVT_RIGHT_DOWN, self.OnToolTip)
        self.calendar.Bind(wx.EVT_KEY_DOWN, self.OnKey)
        self.Popup()

    def OnChosen(self, _event=None):
        ''' Test chosen date for inclusion in restricted dates if set
            Test if set to only allow weekdays, test if it is a weekday or a holiday, whicj is treated as not a weekday
        '''
        d = self.calendar.GetDate()
        if self.RestrictedDates:
            test = (d.year, d.month+1)
            days = self.RestrictedDates.get(test, ())
            if not days or d.day not in days:
                pass
            else:
                return

        if self.parent._calendar_SetOnlyWeekDays and not d.IsWorkDay(): # Weekend
            return
        if self.parent._calendar_SetOnlyWeekDays: # Holiday
            attr = self.calendar.GetAttr(d.day)
            if attr.IsHoliday():
                return

        self.callback(self.calendar.GetDate())
        self.parent._pop = False
        self.Dismiss()

    def OnChange(self, event):
        # If the year changed, recalculate the dictionaries for Marked, Restricted, Official Holidays and Note dates
        if event.GetEventType() == wx.adv.EVT_CALENDAR_YEAR.typeId:
            self.MarkDates = self.GenerateDates(self.parent._calendar_MarkDates)
            self.RestrictedDates = self.GenerateDates(self.parent._calendar_RestrictDates)
            self.SetOfficialHolidays(self.parent._calendar_OfficialHolidays)
            self.Notes = self.GenerateNotes(self.parent._calendar_Notes)

        date = event.GetDate()
        self.OnMonthChange()

    def OnDismiss(self, event=None):
        self.parent._pop = False

    def OnKey(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.parent._pop = False
            self.Dismiss()
        event.Skip()

    def SetMarkDates(self, markdates):
        self.MarkDates = self.GenerateDates(markdates)
        self.OnMonthChange()

    def OnMonthChange(self):
        font = self.calendar.GetFont()
        font.SetStrikethrough(True)
        font.MakeItalic()
        date = self.calendar.GetDate()
        days_in_month = date.GetLastMonthDay().day
        mark_days = self.MarkDates.get((date.year, date.month+1), [])    # get dict values or an empty list if none
        h_days = self.Holidays.get((date.year, date.month+1), [])
        fixed_h_days = self.Holidays.get((0, date.month+1), [])
        r_days = self.RestrictedDates.get((date.year, date.month+1), [])
        oh_days = self.OfficialHolidays.get((date.year, date.month+1), [])

        if isinstance(mark_days, int): # Allow for people forgetting it must be a tuple, when entering a single day
            mark_days = tuple((mark_days,))
        if isinstance(h_days, int):
            h_days = tuple((h_days,))
        if isinstance(fixed_h_days, int):
            fixed_h_days = tuple((fixed_h_days,))
        if isinstance(r_days, int):
            r_days = tuple((r_days,))

        for d in range(1, days_in_month+1):
            attr = self.calendar.GetAttr(d)
            highlight_attr = wx.adv.CalendarDateAttr()
            if d in mark_days:                                                  # Marked Day
                highlight_attr.SetBorder(self.markborder[0])
                highlight_attr.SetBorderColour(self.markborder[1])
            if d in h_days:                                                     # Holiday
                highlight_attr.SetHoliday(True)
            if d in fixed_h_days:                                               # Fixed Holiday
                highlight_attr.SetHoliday(True)
            if d in oh_days:                                                    # Official Holidays
                highlight_attr.SetHoliday(True)
            if not wx.DateTime(d, date.month, date.year).IsWorkDay():           # Weekend
                highlight_attr.SetHoliday(True)
            if d in r_days:                                                     # Resticted Day (override holiday)
                highlight_attr.SetFont(font)
            if highlight_attr.IsHoliday():
                if self.parent._calendar_SetOnlyWeekDays:
                    highlight_attr.SetFont(font)
            if highlight_attr is not None:
                self.calendar.SetAttr(d, highlight_attr)
            else:
                self.calendar.ResetAttr(d)

        self.calendar.Refresh()

    def SetHolidays(self, holidays):
        self.Holidays = holidays
        self.OnMonthChange()

    def SetOfficialHolidays(self, holiday_codes):
        self.OfficialHolidays = {}
        if not holiday_codes:                                                   # holiday codes not set
            return
        country, subdiv, language = holiday_codes
        self.country_name = country
        for c in holidays.registry.COUNTRIES.values():
            if country in c:
                self.country_name = c[0]

        d = self.calendar.GetDate()
        for k, v in holidays.country_holidays(country=country, subdiv=subdiv, years=d.year, language=language).items():
            existing = self.OfficialHolidays.get((k.year, k.month), [])
            if k.day not in existing:
                self.OfficialHolidays[(k.year, k.month)] = existing + [k.day]

        for item in self.parent._calendar_AddOfficialHolidays:
            country, subdiv, language = item
            for k, v in holidays.country_holidays(country=country, subdiv=subdiv, years=d.year, language=language).items():
                existing = self.OfficialHolidays.get((k.year, k.month), [])
                if k.day not in existing:
                    self.OfficialHolidays[(k.year, k.month)] = existing + [k.day]

        self.OnMonthChange()

    def SetDateRange(self, lowerdate=wx.DefaultDateTime, upperdate=wx.DefaultDateTime):
        if lowerdate.IsValid() or upperdate.IsValid():
            if lowerdate.IsValid():
                lowerdate = wx.DateTime(lowerdate.day, lowerdate.month-1, lowerdate.year)
            if upperdate.IsValid():
                upperdate =  wx.DateTime(upperdate.day, upperdate.month-1, upperdate.year)
            self.calendar.SetDateRange(lowerdate, upperdate)

    def SetNotes(self, notes):
        self.Notes = self.GenerateNotes(notes)

    def SetRestrictDates(self, rdates):
        self.RestrictedDates = self.GenerateDates(rdates)
        self.OnMonthChange()

    def restricted_date_range(self, start, end):
        '''
            Generate dates between a start and end date
        '''
        for i in range((end - start).days + 1):
            yield start + datetime.timedelta(days = i)

    def day_in_range(self, start, end, day):
        '''
            Test if date is the required day of the week
        '''
        for d in self.restricted_date_range(start, end):
            if d.isoweekday() == day:
                yield d

    def GenerateDates(self, date_dict):
        ''' Generated on start and when the year changes (Marked and Restricted dictionaries)
            This routine generates a new dictionary from the one passed in and returns the generated dictionary.
            This because the original passed in dictionary may include date codes e.g. -99 for the last day of a month
             or -1 all Mondays or -23 the 3rd Tuesday, which need to be calculated for the given month in the given year.
            An added complication is that the year may be set to zero, denoting all years, so if the calendar year is
             changed, this routine is run again, to ensure that the dates are relevant to the current year.
        '''
        generated_dict = {}

        for year, month in date_dict:
            gen_year = year
            if gen_year == 0:               # Zero entry = All years, so generate dates for the currently selected year
                d = self.calendar.GetDate()
                gen_year = d.year
            day_map = calendar.monthcalendar(gen_year, month)
            for neg in list(date_dict.get((year, month))):
                if neg >= 0:
                    existing = generated_dict.get((gen_year, month), [])
                    if neg not in existing:
                        generated_dict[(gen_year, month)] = existing + [neg]
                    continue
                first_week_day, last_day_no = calendar.monthrange(gen_year, month)
                d1 = datetime.datetime(gen_year, month, 1)
                d2 = datetime.datetime(gen_year, month, last_day_no)
                if neg < 0 and neg >= -7:                                       # Every specified weekday
                    for i in self.day_in_range(d1, d2, abs(neg)):
                        existing = generated_dict.get((gen_year, month), [])
                        if i.day not in existing:
                            generated_dict[(gen_year, month)] = existing + [i.day]
                    continue
                if neg == -99:                                                  # Last day of the month
                    first_week_day, last_day_no = calendar.monthrange(gen_year, month)
                    existing = generated_dict.get((gen_year, month), [])
                    if last_day_no not in existing:
                        generated_dict[(gen_year, month)] = existing + [last_day_no]
                    continue
                if neg == -98:                                                  # Last weekday of the month
                    first_week_day, last_day_no = calendar.monthrange(gen_year, month)
                    ld = datetime.date(gen_year, month, last_day_no)
                    while ld.isoweekday() > 5:                                  # Last day of month is not a weekday
                        ld -= datetime.timedelta(days=1)                        # deduct days to get to Friday
                    existing = generated_dict.get((gen_year, month), [])
                    if ld.day not in existing:
                        generated_dict[(gen_year, month)] = existing + [ld.day]
                    continue
                if neg <= -11 and neg >= -75:                                   # Occurrence of a weekday
                    if neg <= -11 and neg >= -15:                               # Monday 1-5
                        map_idx = 0
                        occ = neg + 11
                    elif neg <= -21 and neg >= -25:                             # Tuesday 1-5
                        map_idx = 1
                        occ = neg + 21
                    elif neg <= -31 and neg >= -35:                             # Wednesday 1-5
                        map_idx = 2
                        occ = neg + 31
                    elif neg <= -41 and neg >= -45:                             # Thursday 1-5
                        map_idx = 3
                        occ = neg + 41
                    elif neg <= -51 and neg >= -55:                             # Friday 1-5
                        map_idx = 4
                        occ = neg + 51
                    elif neg <= -61 and neg >= -65:                             # Saturday 1-5
                        map_idx = 5
                        occ = neg + 61
                    elif neg <= -71 and neg >= -75:                             # Sunday 1-5
                        map_idx = 6
                        occ = neg + 71
                    else:                                                       # Undefined
                        continue
                    week_map = [index for (index, item) in enumerate(day_map) if item[map_idx]]
                    if abs(occ) >= len(week_map):
                        occ = len(week_map) - 1
                    week_idx = week_map[abs(occ)]
                    map_day = day_map[week_idx][map_idx]
                    existing = generated_dict.get((gen_year, month), [])
                    if map_day not in existing:
                        generated_dict[(gen_year, month)] = existing + [map_day]
        return generated_dict

    def GenerateNotes(self, date_dict):
        ''' Generated on start and when the year changes
            This routine generates a new dictionary of Notes from the one passed in and returns the generated dictionary.
            This because the original passed in dictionary may include date codes e.g. -99 for the last of a month
             or -1 all Mondays or -23 the 3rd Tuesday, which need to be calculated for the given month in the given year.
            An added complication is that the year may be set to zero, denoting all years, so if the calendar year is changed,
             this routine is run again, to ensure that the dates are relevant to the current year.
            Because some of the notes are calculated, a date may have muliple notes, so the notes are accumulated, to form
            a single note entry, seperated by a + sign
            If Official Holidays are included, these too are recalculated for the current year.
        '''
        generated_dict = {}
        for year, month, day in date_dict:
            gen_year = year
            if gen_year == 0:               # Zero entry = All years, so generate dates for the currently selected year
                d = self.calendar.GetDate()
                gen_year = d.year
            day_map = calendar.monthcalendar(gen_year, month)
            note = date_dict.get((year, month, day))
            if day >= 0:
                use_note = generated_dict.get((gen_year, month, day), '')
                if use_note:
                    use_note = use_note+"\n  + "+note
                else:
                    use_note = note
                generated_dict[(gen_year, month, day)] = use_note
                continue
            first_week_day, last_day_no = calendar.monthrange(gen_year, month)
            d1 = datetime.datetime(gen_year, month, 1)
            d2 = datetime.datetime(gen_year, month, last_day_no)
            if day < 0 and day >= -7:                                       # Every specified weekday
                for i in self.day_in_range(d1, d2, abs(day)):
                    use_note = generated_dict.get((gen_year, month, i.day), '')
                    if use_note:
                        use_note = use_note+"\n  + "+note
                    else:
                        use_note = note
                    generated_dict[(gen_year, month, i.day)] = use_note
                continue
            if day == -99:                                                  # Last day of the month
                first_week_day, last_day_no = calendar.monthrange(gen_year, month)
                use_note = generated_dict.get((gen_year, month, last_day_no), '')
                if use_note:
                    use_note = use_note+"\n  + "+note
                else:
                    use_note = note
                generated_dict[(gen_year, month, last_day_no)] = use_note
                continue
            if day == -98:                                                  # Last weekday of the month
                first_week_day, last_day_no = calendar.monthrange(gen_year, month)
                ld = datetime.date(gen_year, month, last_day_no)
                while ld.isoweekday() > 5:                                  # Last day of month is not a weekday
                    ld -= datetime.timedelta(days=1)                        # deduct days to get to Friday
                use_note = generated_dict.get((gen_year, month, ld.day), '')
                if use_note:
                    use_note = use_note+"\n  + "+note
                else:
                    use_note = note
                generated_dict[(gen_year, month, ld.day)] = use_note
                continue
            if day <= -11 and day >= -75:                                   # Occurrence of a weekday
                if day <= -11 and day >= -15:                               # Monday 1-5
                    map_idx = 0
                    occ = day + 11
                elif day <= -21 and day >= -25:                             # Tuesday 1-5
                    map_idx = 1
                    occ = day + 21
                elif day <= -31 and day >= -35:                             # Wednesday 1-5
                    map_idx = 2
                    occ = day + 31
                elif day <= -41 and day >= -45:                             # Thursday 1-5
                    map_idx = 3
                    occ = day + 41
                elif day <= -51 and day >= -55:                             # Friday 1-5
                    map_idx = 4
                    occ = day + 51
                elif day <= -61 and day >= -65:                             # Saturday 1-5
                    map_idx = 5
                    occ = day + 61
                elif day <= -71 and day >= -75:                             # Sunday 1-5
                    map_idx = 6
                    occ = day + 71
                else:                                                       # Undefined
                    continue
                week_map = [index for (index, item) in enumerate(day_map) if item[map_idx]]
                if abs(occ) >= len(week_map):
                    occ = len(week_map) - 1
                week_idx = week_map[abs(occ)]
                map_day = day_map[week_idx][map_idx]
                use_note = generated_dict.get((gen_year, month, map_day), '')
                if use_note:
                    use_note = use_note+"\n  + "+note
                else:
                    use_note = note
                generated_dict[(gen_year, month, map_day)] = use_note

        # If official holidays are available write them into the notes

        if holidays_available and self.parent._calendar_OfficialHolidays:
            country, subdiv, language = self.parent._calendar_OfficialHolidays
            d = self.calendar.GetDate()
            for k, v in holidays.country_holidays(country=country, subdiv=subdiv, years=d.year, language=language).items():
                use_note = generated_dict.get((k.year, k.month, k.day), '')
                if use_note:
                    use_note = use_note+"\n  + * "+v
                else:
                    use_note = " * "+v
                generated_dict[(k.year, k.month, k.day)] = use_note

            for item in self.parent._calendar_AddOfficialHolidays:
                country, subdiv, language = item
                for k, v in holidays.country_holidays(country=country, subdiv=subdiv, years=d.year, language=language).items():
                    use_note = generated_dict.get((k.year, k.month, k.day), '')
                    if use_note:
                        use_note = use_note+"\n  + *"+' '.join(item)+v
                    else:
                        use_note = " *"+' '.join(item)+v
                    generated_dict[(k.year, k.month, k.day)] = use_note


        return generated_dict

    def OnToolTip(self, event):
        '''
        If Right click on a non date area, displays all Notes for the month
        Test for date range restrictions.
        Generate and display tooltips for each day based on position, if there are:
            Notes or Restricted entries for the day
        '''
        try:
            pos = event.EventObject.GetPosition()
            click_code, click_date, click_day = self.calendar.HitTest(pos)

            # Show all holidays for the month in popup
            #  if not a valid date position or surrounding week of previous/next month (if shown).
            if click_code == 0 or click_code == 5:
                if event.GetEventType() == wx.EVT_RIGHT_DOWN.typeId:
                    click_date = self.calendar.GetDate()
                    if holidays_available and self.parent._calendar_OfficialHolidays:
                        country, subdiv, language = self.parent._calendar_OfficialHolidays
                    else:
                        country = subdiv = language = ''
                    hdr = msg = ''
                    if country:
                        hdr = "Inc holidays for "+self.country_name
                        if subdiv:
                            hdr += " region "+subdiv
                        hdr += "\n"
                    else:
                        hdr = ''
                    vmax = 200
                    for k, v in sorted(self.Notes.items()):
                        if k[0] == click_date.year and k[1] == click_date.month + 1:
                            msg += "\n"+str(k[2]).zfill(2)+ " "+ v
                            vmax = max(vmax, self.GetTextExtent(v)[0]+50)
                    vmax = max(vmax, self.GetTextExtent(hdr)[0])
                    if msg:
                        msg = 'Notes for '+click_date.Format('%B') + '\n' + hdr + msg
                        wx.TipWindow(self,msg,maxLength=vmax)
                return
            elif click_code != 2:                           # Something other than a valid date or a blank date
                self.calendar.SetToolTip('')
                return
        except Exception:
            click_date = self.calendar.GetDate()

        self.calendar.SetToolTip('')
        range_check, lower, upper = self.calendar.GetDateRange()
        if range_check:
            if (lower != wx.DefaultDateTime and click_date.IsEarlierThan(lower)) or \
                (upper != wx.DefaultDateTime and click_date.IsLaterThan(upper)):
                msg = str(self.parent._formatter(click_date)).title()+'\n'+"Out of Range\n"
                if lower != wx.DefaultDateTime:
                    msg += str(lower.Format("%d-%b-%Y")).title()+' > '
                else:
                    msg += "Any date > "
                if upper != wx.DefaultDateTime:
                    msg += str(upper.Format("%d-%b-%Y")).title()
                else:
                    msg += "Any date"
                self.calendar.SetToolTip(msg)
                return

        restricted = self.RestrictedDates.get((click_date.year, click_date.month + 1), [])
        restricted_set = False
        if click_date.day in restricted:
            restricted_set = True
        if self.parent._calendar_SetOnlyWeekDays and not click_date.IsWorkDay():
            restricted_set = True
        d = (click_date.year, click_date.month + 1, click_date.day)
        note = self.Notes.get(d, '')                        # Year/Month/Day specific Note or blank
        if restricted_set:
            note = "** Restricted **\n\n"+ note
        if not note:
            return
        self.calendar.SetToolTip(str(self.parent._formatter(click_date)).title()+'\n'+note)


class DemoFrame(wx.Frame):
    '''
        This demonstration code attempts to provide at least one example of every option, even if it's commented out
        It may offer examples of various options for the same thing, which explains its rather messy look
        The bulk of the marked dates, holidays, restrictions and notes are set around August 2023, when the testing
        was performed, so feel free to navigate to that month or change the values.
    '''
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "MiniDatePicker Demo")

        #format = (lambda dt:
        #    (f'{dt.GetWeekDayName(dt.GetWeekDay())} {str(dt.day).zfill(2)}/{str(dt.month+1).zfill(2)}/{dt.year}')
        #    )

        #format = (lambda dt: (f'{dt.Format("%a %d-%m-%Y")}'))

        #Using a strftime format converting wx.DateTime to datetime.datetime
        #format = (lambda dt: (f'{wx.wxdate2pydate(dt).strftime("%A %d-%B-%Y")}'))

        format = (lambda dt: (f'{dt.Format("%A %d %B %Y")}'))

        panel = wx.Panel(self)

        self.mdp = MiniDatePicker(panel, -1, pos=(50, 50), style=wx.TE_CENTRE, date=0, formatter=format)

        #self.mdp.SetLocale('fr_FR.UTF-8')                                          # Set Locale for Language
        #self.mdp.SetFormatter(format)                                              # Set format seperately

        x=datetime.datetime.now()
        #self.mdp.SetValue(x.timestamp())                                           # Set Date
        #self.mdp.SetValue(wx.DateTime.Today())
        self.mdp.SetValue(0)

        #font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        #font.SetFractionalPointSize(16)
        #self.mdp.SetCalendarFont(font)                                              # Set Calendar Font


        #self.mdp.SetButton(False)                                                  # Turn Button Off
        #self.mdp.SetButtonBitmap('./Off.png')                                      # Specify button bitmap
        #self.mdp.SetButtonBitmapFocus('./On.png')                                  # Specify button focus bitmap
            # Another option for the bitmap is to use wx.ArtProvider e.g.
            # bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN, client=wx.ART_BUTTON)
            # self.mdp.SetButtonBitmap(bmp)
        #self.mdp.button.SetBackgroundColour('#ffffff')                             # button background white

        self.mdp.SetCalendarStyle(wx.adv.CAL_SHOW_WEEK_NUMBERS|wx.adv.CAL_MONDAY_FIRST)
        self.mdp.ctl.SetBackgroundColour('#e1ffe1')                                 # lightgreen
        self.mdp.SetCalendarHeaders(colFg='#ff0000', colBg='#90ee90')               # red/lightgreen
        #self.mdp.SetCalendarHighlights(colFg='#ff0000', colBg='#90ee90')           # red/lightgreen
        self.mdp.SetCalendarHolidayColours(colFg='#ff0000', colBg='')               # Holidays red/None

        self.mdp.SetCalendarBg(colBg='#f0ffff')                                     # Background Colour Azure
        #self.mdp.SetCalendarFg(colFg='#0000ff')                                     # Foreground Colour Blue
        self.mdp.SetCalendarMarkBorder(border=wx.adv.CAL_BORDER_SQUARE, bcolour=wx.BLUE) # Mark Border NONE, SQUARE or ROUND + Colour
        #self.mdp.SetCalendarOnlyWeekDays(True)                                     # Only non holiday weekdays are selectable
        self.mdp.SetToolTip('Struck through dates are not selectable')

        self.mdp.SetCalendarMarkDates({
                                       (0, 1) : [-11,-23,1],                   # 1st Monday, 3rd Tuesday and the 1st January
                                       (x.year, 7) : [2,5,7,11,30],
                                       (x.year, 8) : [7,12,13,20,27],
                                       (0, 9) : [1,27,-98]                     # 1st, 27th and the last weekday of September
                                      })

        self.mdp.SetCalendarHolidays({
                                     (0, 1) : [1,],                                 # January 1st every year
                                     (x.year, 8) : [7,15],
                                     (0, 12) : [25,26]                              # 25th & 26th December every year
                                    })

        self.mdp.SetCalendarNotes({
                                     (0, 1, 1) : "New Year's Day",                  # January 1st every year
                                     (0, 1, -11) : "First Monday of the year",
                                     (0, 1, -1) : "A Monday in January",
                                     (0, 1, -23) : "3rd Tuesday of the year",
                                     (0, 1, -99) : "Last day of January",
                                     (0, 1, -35) : "The last Wednesday of January",
                                     (0, 2, -5)  : "Every Friday in February",
                                     (x.year, 8, 7) : "Marked for no reason whatsoever", # This year only
                                     (x.year, 8, 15) : "A holiday August 15 2023",       # This year only
                                     (x.year, 8, 20) : "Marked for reason X",            # this year only
                                     (0, 9, -98) : "Last weekday of September",
                                     (0, 12, 25) : "Merry Christmas!",
                                     (0, 2, -99) : "Last day of February"
                                    })

        self.mdp.SetCalendarRestrictDates({
                                       (0, 1) : [-1, -2, 5],     # exclude Mondays and Tuesdays, 5th of January All years
                                       (0, 2) : [-99,],          # exclude last day of February - All years
                                       (0, 8) : [-98,]           # exclude last weekday of August - All years
                                        })

        # Restrict Calendar to a date range (define a lowerdate or an upperdate or both
        #self.mdp.SetCalendarDateRange(lowerdate=wx.DateTime(23,8,2023), upperdate=wx.DateTime(23,9,2023))

        # Official Holidays requires the python holidays module (pip install --upgrade holidays)
        #self.mdp.AddOfficialHolidays(country="GB", subdiv="ENG", language="")   # Primary region England
        #self.mdp.AddOfficialHolidays(country="GB", subdiv="SCT", language="")   # Additional region Scotland
        #self.mdp.AddOfficialHolidays(country="ES", subdiv="AN", language="")    # Additional region Spain, Andalucia


        #------------------------------ 2nd Calendar ------------------------------#

        self.mdp2 = MiniDatePicker(panel, -1, pos=(50, 150), style=wx.TE_CENTRE, date=0, \
                                   formatter=None, button_alignment=wx.LEFT)

        self.mdp2.SetCalendarRestrictDates({
                                       (0, 1) : [-1, -2],        # exclude Mondays and Tuesdays  - All years
                                       (x.year, 2) : [-1, -2],   # exclude Mondays and Tuesdays     - This year
                                       (0, 3) : [-99, -1, -2, 5],   # exclude Mondays and Tuesdays + last day + 5th - All years
                                       (x.year, 4) : [-1, -2],   # exclude Mondays and Tuesdays     - This year
                                       (x.year, 5) : [-1, -2],   # exclude Mondays and Tuesdays     - This year
                                       (x.year, 6) : [-1, -2]    # exclude Mondays and Tuesdays     - This year
                                      })
        self.mdp2.SetToolTip("Struck through dates are not selectable")
        self.mdp2.SetCalendarOnlyWeekDays(False)                                     # Weekends and holidays selectable
        self.mdp2.SetCalendarStyle(wx.adv.CAL_MONDAY_FIRST)
        font = wx.Font(16, wx.FONTFAMILY_ROMAN,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_SEMIBOLD)
        self.mdp2.SetCalendarFont(font)                                              # Set Calendar Font

        y = x + datetime.timedelta(weeks=+4)
        self.mdp2.SetValue(y.timestamp())

        self.Bind(EVT_DATE_CHANGED, self.OnEvent)
        self.Centre()

    def OnEvent(self, event):
        obj = event.GetEventObject()
        print("\nevt", event.GetValue())

        x = event.GetDate() # wx.DateTime object
        print("evt", x)
        print("Day", x.GetDayOfYear(),"Week", x.GetWeekOfYear(), "Name", x.GetWeekDayName(x.GetWeekDay()))

        print("evt", event.GetDateTime()) # datetime.datime object
        print("evt", event.GetTimeStamp())
        print("func", obj.GetValue())
        print("func", obj.GetDate())
        print("func", obj.GetDateTimeValue())
        print("func", obj.GetTimeStamp())
        print("func", obj.GetLocale())


if __name__ == '__main__':
    app = wx.App()
    frame = DemoFrame(None)
    frame.Show()
    app.MainLoop()
