#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 22:31:24 2020

@author: edip.demirbilek
"""


from wanikani_api.client import Client
import math
import cherrypy

import time


def getCharacters(entry):
    return entry.characters


def getReadings(entry):
    result = []

    for reading in entry.readings:
        if reading.primary:
            result.append(reading.reading)

#    for reading in entry.readings:
#        if not reading.primary:
#            result.append(reading.reading)

    return "/".join(map(str, result))


def getMeanings(entry):
    result = []
    for meaning in entry.meanings:
        if meaning.primary:
            result.append(meaning)

#    for meaning in entry.meanings:
#        if not meaning.primary:
#                result.append(meaning)

    return "/".join(map(str, result))


def getNextRow(data, index, num_cols):

    end = index + num_cols

    if index >= len(data):
        return None

    if index + num_cols >= len(data):
        end = len(data)

    return data[index:end]


def convertArrayToMatrix(data, row_len):
    matrix = []
    data_len = len(data)
    num_rows = math.ceil(data_len/row_len)

    index = 0
    for row in range(0, num_rows):
        matrix.append(getNextRow(data, index, row_len))
        index += row_len

    return matrix


def getFormattedCellValue(data):
    data = [str(d).replace('None', '') for d in data]

    data[0] = "<h2>" + str(data[0]) + "</h2>"
    data[-1] = "<br>" + str(data[-1])
    return "".join(map(str, data))


def getLevelHtml(level, data_type, row_len):
    # https://pypi.org/project/wanikani-api/
        v2_api_key = ""
        client = Client(v2_api_key)

        result = client.subjects(types=data_type, levels=level)

        data = []

        for entry in result:
            P1 = getCharacters(entry)
            P3 = getMeanings(entry)

            if not data_type == 'radical':
                P2 = getReadings(entry)
                data.append([P1, P2, P3])
            else:
                data.append([P1, P3])

        matrix = convertArrayToMatrix(data, row_len)

        table_head = "<table id=\"table\" border=\"1\" class=\"dataframe\"> <tbody>"
        table_tail = "</tbody> </table>"
        table_str = table_head

        for row in matrix:
            table_str += "<tr>"
            for cell in row:
                table_str += "<td align=\"center\">"
                table_str += getFormattedCellValue(cell)
                table_str += "</td>"
            table_str += "</tr>"

        table_str += table_tail

        html_str = "<h2> Level " + str(level) + ": " + data_type + "</h2>"
        html_str += table_str

        return html_str

# max-width: 2480px;
# http://www.unitconversion.org/typography/pixels-x-to-centimeters-conversion.html
def getHtmlHeadAndTail():

    head = '''<html>
                <head>
                    <style>
                      #table{
                        max-width: 780px;
                        width:100%;
                      }
                      #table td{
                        width: auto;
                        overflow: hidden;
                        word-wrap: break-word;
                      }
                      #table h2 {
                        margin-bottom: -6px;
                        }
                      #table h3 {
                        margin-bottom: -6px;
                        }
                      #table h1 {
                        margin-bottom: -6px;
                        }
                    </style>
                </head>
                <body>'''

    tail = '''</body>
                </html>'''
    return head, tail


# https://www.tutorialspoint.com/cherrypy/cherrypy_quick_guide.htm
class WaniKani(object):
    @cherrypy.expose
    def index(self):

        head, tail = getHtmlHeadAndTail()

        html_str = head

        for level in range(1, 61):
            html_str += getLevelHtml(level, "radical", 10)
            html_str += getLevelHtml(level, "kanji", 10)
            html_str += getLevelHtml(level, "vocabulary", 5)
            html_str += "<br>"
            print(level)
            time.sleep(2.5)

        html_str += tail

        return html_str


if __name__ == '__main__':

    cherrypy.quickstart(WaniKani())
