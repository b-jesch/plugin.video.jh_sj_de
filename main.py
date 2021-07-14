# coding=utf-8
"""Kodi Plugin for www.serienjunkies.de"""
import sys
from urllib.parse import urlencode, parse_qsl
import requests
import xbmc
import xbmcgui  # pylint: disable=E0401
import xbmcplugin  # pylint: disable=E0401
import xbmcaddon  # pylint: disable=E0401
from bs4 import BeautifulSoup
import os


URL = sys.argv[0]
HANDLE = int(sys.argv[1])
FALLBACK = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'fallback.jpg')

ADDON = xbmcaddon.Addon()
LOC = ADDON.getLocalizedString

services = list()
if ADDON.getSetting('amazon').upper() == 'TRUE': services.append(LOC(32110))
if ADDON.getSetting('netflix').upper() == 'TRUE': services.append(LOC(32111))
if ADDON.getSetting('disney').upper() == 'TRUE': services.append(LOC(32112))
if ADDON.getSetting('joyn').upper() == 'TRUE': services.append(LOC(32113))
if ADDON.getSetting('joyn_primetime').upper() == 'TRUE': services.append(LOC(32114))
if ADDON.getSetting('appletv').upper() == 'TRUE': services.append(LOC(32115))
if ADDON.getSetting('now').upper() == 'TRUE': services.append(LOC(32116))
if ADDON.getSetting('starzplay').upper() == 'TRUE': services.append(LOC(32117))
if ADDON.getSetting('magentatv').upper() == 'TRUE': services.append(LOC(32118))


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    """
    return '{0}?{1}'.format(URL, urlencode(kwargs))


def check_resource(url):
    """
    Check availability of online resources
    """
    res = requests.get(url, stream=True)
    try:
        res.raise_for_status()
        return url
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
        xbmc.log('No resource found, use fallback', xbmc.LOGDEBUG)
    return FALLBACK


def list_tv_shows():
    """
    List tv shows
    """
    xbmcplugin.setPluginCategory(HANDLE, "Deutschland")
    xbmcplugin.setContent(HANDLE, 'videos')

    response = requests.get("https://www.serienjunkies.de/docs/serienplaner.html")
    soup = BeautifulSoup(response.text, "html.parser")
    elements = soup.find_all("div", class_="tablerow")
    xbmc.log('{} items found'.format(len(elements)), xbmc.LOGDEBUG)
    for element in elements:
        try:
            label = element.find_all("a")[0].text
            transmitter = element.find_all("a")[-1].get("title")
            if not transmitter:
                transmitter = element.find_all("img")[-1].get("title")
            if transmitter in services:
                continue
            list_item = xbmcgui.ListItem(label=label)
            tv_show_id = element.find_all("a")[0].get("href").split("/")[1]
            art = check_resource("https://s-cdn.serienjunkies.de/n/" + tv_show_id + ".jpg")
            list_item.setArt({
                'poster': art, 'icon': art, 'thumb': art, 'fanart': art
            })
            appointment = element.find_all("div")[1].find_all("div")[1].text
            plot = transmitter + ": " + appointment
            list_item.setInfo('video', {'plot': plot})
            list_item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(
                HANDLE,
                get_url(action='show_tv_show_info', header=label, message=plot), list_item, False
            )
        except IndexError:
            continue
    xbmcplugin.endOfDirectory(HANDLE, updateListing=True, cacheToDisc=False)


def show_tv_show_info(header="", message=""):
    xbmcgui.Dialog().ok(header, message)


def router(paramstring):
    """
    Router function that calls other functions depending on the provided paramstring
    """
    params = dict(parse_qsl(paramstring))
    if params:
        if params['action'] == 'show_tv_show_info':
            show_tv_show_info(params['header'], params['message'])
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        list_tv_shows()


if __name__ == '__main__':
    router(sys.argv[2][1:])
