# Copyright (C) 2001-2014 Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
Handle uncheckable URLs.
"""

import re
from . import urlbase


class UnknownUrl(urlbase.UrlBase):
    """Handle unknown or just plain broken URLs."""

    def build_url(self):
        """Only logs that this URL is unknown."""
        super().build_url()
        if self.is_ignored():
            self.add_info(
                _("%(scheme)s URL ignored.") % {"scheme": self.scheme.capitalize()}
            )
            self.set_result(_("ignored"))
        else:
            self.set_result(_("URL is unrecognized or has invalid syntax"), valid=False)

    def is_ignored(self):
        """Return True if this URL scheme is ignored."""
        return is_unknown_scheme(self.scheme)

    def can_get_content(self):
        """Unknown URLs have no content.

        @return: False
        @rtype: bool
        """
        return False


# do not edit anything below since these entries are generated from
# scripts/update_iana_uri_schemes.sh
# DO NOT REMOVE

# from https://www.iana.org/assignments/uri-schemes/uri-schemes.xhtml
ignored_schemes_permanent = r"""
|aaa        # Diameter Protocol
|aaas       # Diameter Protocol with Secure Transport
|about      # about
|acap       # application configuration access protocol
|acct       # acct
|cap        # Calendar Access Protocol
|cid        # content identifier
|coap       # coap
|coap\+tcp  # coap+tcp [1]
|coap\+ws   # coap+ws [1]
|coaps      # coaps
|coaps\+tcp # coaps+tcp [1]
|coaps\+ws  # coaps+ws [1]
|crid       # TV-Anytime Content Reference Identifier
|data       # data
|dav        # dav
|dict       # dictionary service protocol
|dns        # Domain Name System
|example    # example
|geo        # Geographic Locations
|go         # go
|gopher     # The Gopher Protocol
|h323       # H.323
|iax        # Inter-Asterisk eXchange Version 2
|icap       # Internet Content Adaptation Protocol
|im         # Instant Messaging
|imap       # internet message access protocol
|info       # Information Assets with Identifiers in Public Namespaces. [RFC4452] (section 3) defines an "info" registry of public namespaces, which is maintained by NISO and can be accessed from [http://info-uri.info/].
|ipp        # Internet Printing Protocol
|ipps       # Internet Printing Protocol over HTTPS
|iris       # Internet Registry Information Service
|iris\.beep # iris.beep
|iris\.lwz  # iris.lwz
|iris\.xpc  # iris.xpc
|iris\.xpcs # iris.xpcs
|jabber     # jabber
|ldap       # Lightweight Directory Access Protocol
|leaptofrogans # leaptofrogans
|mid        # message identifier
|msrp       # Message Session Relay Protocol
|msrps      # Message Session Relay Protocol Secure
|mtqp       # Message Tracking Query Protocol
|mupdate    # Mailbox Update (MUPDATE) Protocol
|nfs        # network file system protocol
|ni         # ni
|nih        # nih
|opaquelocktoken # opaquelocktokent
|pkcs11     # PKCS#11
|pop        # Post Office Protocol v3
|pres       # Presence
|reload     # reload
|rtsp       # Real-Time Streaming Protocol (RTSP)
|rtsps      # Real-Time Streaming Protocol (RTSP) over TLS
|rtspu      # Real-Time Streaming Protocol (RTSP) over unreliable datagram transport
|service    # service location
|session    # session
|shttp      # Secure Hypertext Transfer Protocol
|sieve      # ManageSieve Protocol
|sip        # session initiation protocol
|sips       # secure session initiation protocol
|sms        # Short Message Service
|snmp       # Simple Network Management Protocol
|soap\.beep # soap.beep
|soap\.beeps # soap.beeps
|stun       # stun
|stuns      # stuns
|tag        # tag
|tel        # telephone
|telnet     # Reference to interactive sessions
|tftp       # Trivial File Transfer Protocol
|thismessage # multipart/related relative reference resolution
|tip        # Transaction Internet Protocol
|tn3270     # Interactive 3270 emulation sessions
|turn       # turn
|turns      # turns
|tv         # TV Broadcasts
|urn        # Uniform Resource Names
|vemmi      # versatile multimedia interface
|vnc        # Remote Framebuffer Protocol
|ws         # WebSocket connections
|wss        # Encrypted WebSocket connections
|xcon       # xcon
|xcon\-userid # xcon-userid
|xmlrpc\.beep # xmlrpc.beep
|xmlrpc\.beeps # xmlrpc.beeps
|xmpp       # Extensible Messaging and Presence Protocol
|z39\.50r   # Z39.50 Retrieval
|z39\.50s   # Z39.50 Session
"""

ignored_schemes_provisional = r"""
|acd        # acd
|acr        # acr
|adiumxtra  # adiumxtra
|adt        # adt
|afp        # afp
|afs        # Andrew File System global file names
|aim        # aim
|amss       # amss
|android    # android
|appdata    # appdata
|apt        # apt
|ark        # ark
|attachment # attachment
|aw         # aw
|barion     # barion
|beshare    # beshare
|bitcoin    # bitcoin
|bitcoincash # bitcoincash
|blob       # blob
|bolo       # bolo
|browserext # browserext
|cabal      # cabal
|calculator # calculator
|callto     # callto
|cast       # cast
|casts      # casts
|chrome     # chrome
|chrome\-extension # chrome-extension
|com\-eventbrite\-attendee # com-eventbrite-attendee
|content    # content
|conti      # conti
|cvs        # cvs
|dab        # dab
|dat        # dat
|diaspora   # diaspora
|did        # did
|dis        # dis
|dlna\-playcontainer # dlna-playcontainer
|dlna\-playsingle # dlna-playsingle
|dntp       # dntp
|doi        # doi
|dpp        # dpp
|drm        # drm
|drop       # drop
|dtmi       # dtmi
|dtn        # DTNRG research and development
|dvb        # dvb
|dweb       # dweb
|ed2k       # ed2k
|elsi       # elsi
|ethereum   # ethereum
|facetime   # facetime
|feed       # feed
|feedready  # feedready
|finger     # finger
|first\-run\-pen\-experience # first-run-pen-experience
|fish       # fish
|fm         # fm
|fuchsia\-pkg # fuchsia-pkg
|gg         # gg
|git        # git
|gizmoproject # gizmoproject
|graph      # graph
|gtalk      # gtalk
|ham        # ham
|hcap       # hcap
|hcp        # hcp
|hxxp       # hxxp
|hxxps      # hxxps
|hydrazone  # hydrazone
|hyper      # hyper
|icon       # icon
|iotdisco   # iotdisco
|ipfs       # ipfs
|ipn        # ipn
|ipns       # ipns
|irc        # irc
|irc6       # irc6
|ircs       # ircs
|isostore   # isostore
|itms       # itms
|jar        # jar
|jms        # Java Message Service
|keyparc    # keyparc
|lastfm     # lastfm
|lbry       # lbry
|ldaps      # ldaps
|lorawan    # lorawan
|lvlt       # lvlt
|magnet     # magnet
|maps       # maps
|market     # market
|matrix     # matrix
|message    # message
|microsoft\.windows\.camera # microsoft.windows.camera
|microsoft\.windows\.camera\.multipicker # microsoft.windows.camera.multipicker
|microsoft\.windows\.camera\.picker # microsoft.windows.camera.picker
|mms        # mms
|mongodb    # mongodb
|moz        # moz
|ms\-access # ms-access
|ms\-browser\-extension # ms-browser-extension
|ms\-calculator # ms-calculator
|ms\-drive\-to # ms-drive-to
|ms\-enrollment # ms-enrollment
|ms\-excel  # ms-excel
|ms\-eyecontrolspeech # ms-eyecontrolspeech
|ms\-gamebarservices # ms-gamebarservices
|ms\-gamingoverlay # ms-gamingoverlay
|ms\-getoffice # ms-getoffice
|ms\-help   # ms-help
|ms\-infopath # ms-infopath
|ms\-inputapp # ms-inputapp
|ms\-lockscreencomponent\-config # ms-lockscreencomponent-config
|ms\-media\-stream\-id # ms-media-stream-id
|ms\-mixedrealitycapture # ms-mixedrealitycapture
|ms\-mobileplans # ms-mobileplans
|ms\-officeapp # ms-officeapp
|ms\-people # ms-people
|ms\-powerpoint # ms-powerpoint
|ms\-project # ms-project
|ms\-publisher # ms-publisher
|ms\-restoretabcompanion # ms-restoretabcompanion
|ms\-screenclip # ms-screenclip
|ms\-screensketch # ms-screensketch
|ms\-search # ms-search
|ms\-search\-repair # ms-search-repair
|ms\-secondary\-screen\-controller # ms-secondary-screen-controller
|ms\-secondary\-screen\-setup # ms-secondary-screen-setup
|ms\-settings # ms-settings
|ms\-settings\-airplanemode # ms-settings-airplanemode
|ms\-settings\-bluetooth # ms-settings-bluetooth
|ms\-settings\-camera # ms-settings-camera
|ms\-settings\-cellular # ms-settings-cellular
|ms\-settings\-cloudstorage # ms-settings-cloudstorage
|ms\-settings\-connectabledevices # ms-settings-connectabledevices
|ms\-settings\-displays\-topology # ms-settings-displays-topology
|ms\-settings\-emailandaccounts # ms-settings-emailandaccounts
|ms\-settings\-language # ms-settings-language
|ms\-settings\-location # ms-settings-location
|ms\-settings\-lock # ms-settings-lock
|ms\-settings\-nfctransactions # ms-settings-nfctransactions
|ms\-settings\-notifications # ms-settings-notifications
|ms\-settings\-power # ms-settings-power
|ms\-settings\-privacy # ms-settings-privacy
|ms\-settings\-proximity # ms-settings-proximity
|ms\-settings\-screenrotation # ms-settings-screenrotation
|ms\-settings\-wifi # ms-settings-wifi
|ms\-settings\-workplace # ms-settings-workplace
|ms\-spd    # ms-spd
|ms\-sttoverlay # ms-sttoverlay
|ms\-transit\-to # ms-transit-to
|ms\-useractivityset # ms-useractivityset
|ms\-virtualtouchpad # ms-virtualtouchpad
|ms\-visio  # ms-visio
|ms\-walk\-to # ms-walk-to
|ms\-whiteboard # ms-whiteboard
|ms\-whiteboard\-cmd # ms-whiteboard-cmd
|ms\-word   # ms-word
|msnim      # msnim
|mss        # mss
|mumble     # mumble
|mvn        # mvn
|notes      # notes
|ocf        # ocf
|oid        # oid
|onenote    # onenote
|onenote\-cmd # onenote-cmd
|openpgp4fpr # openpgp4fpr
|otpauth    # otpauth
|palm       # palm
|paparazzi  # paparazzi
|payment    # payment
|payto      # payto
|platform   # platform
|proxy      # proxy
|psyc       # psyc
|pttp       # pttp
|pwid       # pwid
|qb         # qb
|query      # query
|quic\-transport # quic-transport
|redis      # redis
|rediss     # rediss
|res        # res
|resource   # resource
|rmi        # rmi
|rsync      # rsync
|rtmfp      # rtmfp
|rtmp       # rtmp
|secondlife # query
|sftp       # query
|sgn        # sgn
|simpleledger # simpleledger
|skype      # skype
|smb        # smb
|smtp       # smtp
|soldat     # soldat
|spiffe     # spiffe
|spotify    # spotify
|ssb        # ssb
|ssh        # ssh
|steam      # steam
|submit     # submit
|svn        # svn
|swh        # swh
|teamspeak  # teamspeak
|teliaeid   # teliaeid
|things     # things
|tool       # tool
|udp        # udp
|unreal     # unreal
|upt        # upt
|ut2004     # ut2004
|v\-event   # v-event
|ventrilo   # ventrilo
|view\-source # view-source
|vscode     # vscode
|vscode\-insiders # vscode-insiders
|vsls       # vsls
|webcal     # webcal
|wtai       # wtai
|wyciwyg    # wyciwyg
|xfire      # xfire
|xri        # xri
|ymsgr      # ymsgr
"""

ignored_schemes_historical = r"""
|fax        # fax
|filesystem # filesystem
|mailserver # Access to data available from mail servers
|modem      # modem
|pack       # pack
|prospero   # Prospero Directory Service
|snews      # NNTP over SSL/TLS
|videotex   # videotex
|wais       # Wide Area Information Servers
|wpid       # wpid
|z39\.50    # Z39.50 information access
"""

ignored_schemes_other = r"""
|clsid      # Microsoft specific
|find       # Mozilla specific
|isbn       # ISBN (int. book numbers)
|javascript # JavaScript
|slack      # Slack Technologies client
"""

ignored_schemes = "^(%s%s%s%s)$" % (
    ignored_schemes_permanent,
    ignored_schemes_provisional,
    ignored_schemes_historical,
    ignored_schemes_other,
)
ignored_schemes_re = re.compile(ignored_schemes, re.VERBOSE)

is_unknown_scheme = ignored_schemes_re.match
