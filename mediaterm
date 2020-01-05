#!/bin/bash

# Mit dem Bash-Skript MediaTerm lassen sich Filme aus den Mediatheken
# der öffentlich-rechtlichen Fernsehsender ressourcenschonend im
# Linux-Terminal suchen, abspielen, herunterladen und als Bookmarks
# speichern. MediaTerm greift dabei auf die Filmliste des Programms
# MediathekView (https://mediathekview.de/) zurück.

# http://martikel.bplaced.net/skripte1/mediaterm.html

#################################################################
#
#  Copyright (c) 2017 Martin O'Connor (mar.oco@arcor.de)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see http://www.gnu.org/licenses/.
#
################################################################

#### Vorbelegte Variablen

dir=$HOME/MediaTerm   #Verzeichnis, in dem Filmliste und Bookmarks gespeichert werden
dldir=$(pwd)   #Zielverzeichnis für den Download von Videos (aktuelles Arbeitsverzeichnis ... bei Bedarf ändern)

player="mpv --really-quiet"   #Player mpv mit Optionen

#---------------------------------------------------------------

datum1=01.01.0000   #fiktive untere Zeitgrenze bei Nichtnutzung der Option -A
datum2=31.12.9999   #fiktive obere Zeitgrenze bei Nichtnutzung der Option -B

longer=0   #fiktive untere Grenze für Filmdauer bei Nichtnutzung der Option -L
shorter=86399   #fiktive obere Grenze für Filmdauer bei Nichtnutzung der Option -K

#### Bei Beenden oder irregulärem Abbruch des Skripts wird die History-Datei gelöscht
trap "rm -f $dir/mt_history" EXIT

#### OPTIONEN

while getopts ":A:B:bghHK:lL:nostuvw" opt; do
    case $opt in
        b)
            bopt=1
            ;;
        A)
            datum1=$(echo "$OPTARG" | awk -F "." 'NF==3{print $3"."$2"."$1}; NF==2{print $2"."$1.".01"}; NF==1{print $1".01.01"}')   #Datum wird invertiert: tt.mm.jjjj -> jjjj.mm.tt
            ;;
        B)
            datum2=$(echo "$OPTARG" | awk -F "." 'NF==3{print $3"."$2"."$1}; NF==2{print $2"."$1".31"}; NF==1{print $1"12.31"}')   #Datum wird invertiert: tt.mm.jjjj -> jjjj.mm.tt
            ;;
        g)
            gopt=1
            ;;
        h)
            hopt=1
            ;;
        K)
            Kopt=1
            shorter="$(($OPTARG*60))" #Umrechnung der Minuten in Sekunden
            ;;
        L)
            Lopt=1
            longer="$(($OPTARG*60))" #Umrechnung der Minuten in Sekunden
            ;;
        l)
            lopt=1
            ;;
        n)
            nopt=1
            ;;
        o)
            oopt=1
            ;;
        s)
            sopt=1
            ;;
        t)
            topt=1
            ;;
        u)
            uopt=1
            ;;
        v)
            if [ ! -f $dir/filmliste ]; then
                flstand="[Datei \"filmliste\" nicht gefunden]"
            else
                flstand=$(head -n +1 $dir/filmliste | cut -d"\"" -f6 | tr -d '\n'; echo " ($(($(cat $dir/filmliste | wc -l) - 1)) Filme)")
            fi
            echo "MediaTerm 8.0, 2019-10-18"
            echo "Filmliste vom $flstand"
            exit
            ;;
        w)
            wopt=1
            ;;
        H)
            Hopt=1   #undokumentierte interne Option, um Ausführung von Suchen auf der internen Kommandozeile zu markieren
            ;;
        \?)
            printf "Ungültige Option: -$OPTARG\n\"mediaterm -h\" gibt weitere Informationen.\n"
            exit
            ;;
    esac
done

#Variable für Anzeige der Suchanfrage in der History und unterhalb der Trefferliste
if [ ! -z $Hopt ]; then
    suchanfrage=$(for i in "${@:2}"; do echo -n " $i"; done)   #"versteckte" Option -H soll nicht angezeigt werden
else
    suchanfrage=$(for i in "${@}"; do phrase=$(echo "$i" | grep -E '[ "]'); if [ ! -z "$phrase" ]; then echo -n " \"$i\""; else echo -n " $i"; fi; done)
fi
suchanfrage=$(echo "$suchanfrage" | sed "s/^[ \t]*//")

# String für Überprüfung der Länge der Suchanfrage
for i in "${@}"; do
    string="$string""$i"
done

# Abbruch bei Suchanfragen mit weniger als 3 Zeichen (Ausnahme: Optionen -b, -h, -l, -o, -u und -w)
if [[ ! $string =~ ^-[bhlouw]$ ]]; then
    if [[ $(echo -n "$string" | wc -m) = [1-2] ]]; then
        echo "Suchanfragen mit weniger als drei Zeichen werden nicht unterstützt!"
        exit
    fi
fi

# Einfügen der Suchanfrage in den Such- und Kommandoverlauf
history -r $dir/mt_history
if [[ -z $Hopt ]]; then
    history -s -- "$suchanfrage"
fi

shift $(($OPTIND -1))

if [[ -z $1 && ! -z $nopt && -z $lopt ]]; then
      echo "Es wurde kein Suchwort eingegeben (bei Option -n erforderlich)."
      exit
fi

#---------------------------------------------------------------
# Hilfe
#---------------------------------------------------------------
fett=$(tput bold)
normal=$(tput sgr0)
unterstr=$(tput smul)

if [ ! -z $hopt ]; then

# Zeige den folgenden Textblock an

    fmt -s -w $(tput cols) << ende-hilfetext | less -ir -Ps"Zum Beenden der Hilfe Taste q drücken"

Mit MediaTerm können im Terminal Filme aus den Mediatheken der öffentlich-rechtlichen Fernsehsender gesucht, mit dem Mediaplayer mpv abgespielt sowie heruntergeladen werden.

${fett}VORAUSSETZUNGEN FUER DAS FUNKTIONIEREN DES SKRIPTS:${normal}
      mpv, wget, xz-utils und ffmpeg müssen installiert sein.

${fett}AUFRUF:${normal}
      mediaterm [-A DATUM|-B DATUM|-g|-K MINUTEN|-L MINUTEN|-n|-o|-s|-t|-w] [+]Suchstring1 [[+|~]Suchstring2 ...]
      mediaterm -l[n|o|w]
      mediaterm -b
      mediaterm -u
      mediaterm -v
      mediaterm -h

      "mediaterm" ohne Optionen oder Argumente ausgeführt - aber auch jede erfolgreiche Suche aus dem Terminal - öffnet die interne Eingabezeile von MediaTerm. Auf ihr werden Suchanfragen nach obigem Muster OHNE einleitende Angabe des Befehls "mediaterm" ausgeführt. Von ihr wird mit vorgegebenen Kommandos u.a. auch das Abspielen und das Herunterladen der gefundenen Filme gesteuert. Eine Übersicht aller Kommando-Kürzel lässt sich per Eingabe von "k" in der internen Eingabe anzeigen.

${fett}OPTIONEN:${normal}
      ${fett}-A DATUM${normal}   Sucht nur Sendungen neuer als DATUM (und vom DATUM); DATUM muss im Format [[TT.]MM.]JJJJ eingegeben werden.
      ${fett}-B DATUM${normal}   Sucht nur Sendungen älter als DATUM (und vom DATUM); DATUM muss im Format [[TT.]MM.]JJJJ eingegeben werden.
      ${fett}-b${normal}   Anzeige, Abspielen und Löschen der Bookmarks.
      ${fett}-g${normal}   Unterscheidet bei der Suche zwischen Groß- und Kleinbuchstaben.
      ${fett}-h${normal}   Zeigt diese Hilfe an.
      ${fett}-K MINUTEN${normal}   Sucht nur Filme, deren Dauer kürzer/gleich MINUTEN (ganze Zahl) ist.
      ${fett}-L MINUTEN${normal}   Sucht nur Filme, deren Dauer länger/gleich MINUTEN (ganze Zahl) ist.
      ${fett}-l${normal}   Listet alle Livestreams auf (Suchstrings werden nicht berücksichtigt).
      ${fett}-n${normal}   Gibt die Ergebnisliste ohne interne Kommandozeile aus.
      ${fett}-o${normal}   Gibt die Ergebnisliste ohne Farben aus.
      ${fett}-s${normal}   Sortiert Suchtreffer absteigend nach Sendedatum (neueste zuoberst).
      ${fett}-t${normal}   Sortiert Suchtreffer aufsteigend nach Sendedatum (neueste zuunterst).
      ${fett}-u${normal}   Aktualisiert die Filmliste.
      ${fett}-v${normal}   Zeigt die MediaTerm-Version, das Erstellungsdatum der Filmliste und die Anzahl der Filme.
      ${fett}-w${normal}   Deaktiviert die worterhaltenden Zeilenumbrüche in der Ergebnisliste.

${fett}SUCH-OPERATOREN:${normal}
       ${fett}+${normal}   Ein "+" unmittelbar vor einem Suchstring bewirkt, dass dieser als Einzelwort gesucht wird und NICHT als Zeichenfolge auch innerhalb von Wörtern.
       ${fett}~${normal}   Eine Tilde (~) unmittelbar vor einem Suchstring schließt diesen für die Suche gezielt aus. Dieser Operator kann nicht mit dem ersten Suchstring verwendet werden.
       ${fett}" "${normal} Zwei oder mehr in Anführungszeichen gesetzte Wörter (z.B. "Thomas Mann") werden als exakte Wortfolge (Phrase) gesucht, d.h. die Wörter müssen in dieser Reihenfolge direkt aufeinander folgen. (Bei Nutzung auf der internen Eingabezeile wird aus programmtechnischen Gründen eine Phrase automatisch in den gleichwertigen Ausdruck Wort1\sWort2\sWort3 ... konvertiert.)

${fett}ANWENDUNGSBEISPIELE:${normal}
   ${unterstr}mediaterm alpen klimawandel${normal}
      ... listet alle Filme auf, in deren Titel, Beschreibung oder URL die Zeichenfolgen "alpen" und "klimawandel" vorkommen (unabhängig von Groß-/Kleinschreibung). Die gefundenen Filme können per Eingabe der jeweiligen Treffernummer gestreamt, heruntergeladen oder als Bookmark gespeichert werden.

   ${unterstr}mediaterm -now alpen klimawandel${normal}
      ... liefert die gleiche Trefferliste in roher Form, d.h. ohne Kommandoeingabe (-n), ohne Farbe (-o) und ohne worterhaltende Zeilenumbrüche (-w). Dies ist beispielsweise sinnvoll, wenn die Liste weiterverarbeitet oder in eine Datei umgeleitet werden soll.

   ${unterstr}mediaterm +gier${normal}
      ... sucht nur nach Treffern, in denen "gier" bzw. "Gier" als ganzes Wort vorkommt; beispielsweise bleiben "gierig", "Magier" oder "Passagiere" unberücksichtigt.

   ${unterstr}mediaterm -A 15.05.2015 -B 2016 alpen klimawandel${normal}
      ... beschränkt die Suche auf Sendungen aus dem Zeitraum 15.05.2015-31.12.2016.

   ${unterstr}mediaterm -L 45 -K 120 alpen klimawandel${normal}
      ... beschränkt die Suche auf Filme, die länger oder gleich 45 Minuten sowie kürzer oder gleich 2 Stunden dauern.

   ${unterstr}mediaterm python ~monty${normal}
      ... vermindert die Ergebnismenge der Suche nach "python" um alle Treffer, in denen die Zeichenfolge "monty" vorkommt.

ende-hilfetext

# Falls Hilfe aus der internen Kommandozeile aufgerufen, kein "exit"
    if [ -z $Hopt ]; then
        exit 0
    fi
fi

#---------------------------------------------------------------

#### FUNKTIONEN hits, icli, bmcomm, bmcli, urlqual, pageview

# Definition der FUNKTION hits: Formatierung und Ausgabe der Suchergebnisse
function hits {

    # Meldung bei leerer Treffermenge
    if [ ! "$out"  ]; then
        if [ ! -z $oopt ]; then
            printf "\033[1mZu der Suche wurden leider keine Treffer gefunden.\033[0m\n"
        else
            printf "\033[0;31mZu der Suche wurden leider keine Treffer gefunden.\033[0m\n"
        fi
        #Bei leerer Treffermenge Anwendung nur beenden, wenn Suchanfrage auf der Kommandozeile (Terminal) ausgeführt wurde.
        if [[ -z $Hopt && "$suchanfrage" != " Bookmark $input" ]]; then
            exit
        fi

    # Ausgabe der Ergebnisliste bei nichtleerer Treffermenge
    else
        # Kompakte Ausgabe der Ergebnisliste Livestreams
        if [ ! -z $lopt ]; then
            echo "$out" | \
                awk -F "\",\"" '{print "("NR")", "\033[0;32m"$4"\033[0m"" ("$1")", "\n" "\033[0;34m"$10"\033[0m","\n"}' | \
                ( if [ ! -z $oopt ]; then sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g"; else tee; fi ) |   #Entfernt Farbformatierungen bei Option -o \
                tr -d '\\' |   #Entfernt Escape-Backslashes aus Ausgabe \
                ( if [[ -z $wopt ]]; then fmt -s -w $(tput cols); else tee; fi )   #Worterhaltende Zeilenumbrüche (außer bei Option -w)

        # Detaillierte Ausgabe der übrigen Ergebnislisten
        elif [ ! -z "$out" ]; then
            echo "$out" | \
                awk -F "\",\"" '{ORS=" "}; {print "("NR")", "\033[0;32m"$4"\033[0m"" ("$1": "$3")"}; {if($14!=""){printf "[n"} else{printf "[-"}}; {if($16!=""){print "/h]"} else{print "/-]"}}; {print "\n"  "\33[1m""Datum:""\033[0m",$5  ",",  $6,"Uhr","*",  "\33[1m""Dauer:""\033[0m",  $7,"\n" $9,  "\n" "\033[0;34m"$10"\033[0m"} {printf "\n\n"}' | \
                ( if [ ! -z $oopt ]; then sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g"; else tee; fi ) |   #Entfernt Farbformatierungen bei Option -o \
                tr -d '\\' |   #Entfernt Escape-Backslashes aus Ausgabe \
                ( if [[ -z $wopt ]]; then fmt -s -w $(tput cols); else tee; fi )   #Worterhaltende Zeilenumbrüche (außer bei Option -w)
        fi
    fi

# Anzeige der Suchanfrage unter der Trefferliste (außer bei Option -n)
if [ -z $nopt ]; then
    echo "[Suchanfrage: $suchanfrage]"
fi

# Bei Option -n nach Ausgabe der Trefferliste exit
if [ ! -z $nopt ]; then
    exit 0
fi
}

# Definition der FUNKTION icli: Interne Kommandozeile
function icli {
trefferzahl=$(echo "$out" | wc -l) #Anzahl der Treffer (= Zeilen von $out)
if [ -z "$out" ]; then
    trefferzahl=0
fi

printf '%.0s-' $(seq $(tput cols)); printf '\n'   #gestrichelte Trennlinie
if [ ! "$out" ]; then
    printf "\033[1mNach Fernsehsendungen suchen ...\033[0m\n\033[1mH\033[0m zeigt die Hilfe zur Suche; \033[1mq\033[0m beendet mediaterm; \033[1mk\033[0m listet zusätzliche Kommando-Optionen auf.\n"
else
    printf "\033[1mZum Abspielen Nummer des gewünschten Films eingeben (... oder neue Suche starten)\033[0m \n\033[1mq\033[0m beendet mediaterm. \033[1mk\033[0m zeigt zusätzliche Kommando-Optionen.\n" | ( if [[ -z $wopt ]]; then fmt -s -w $(tput cols); else tee; fi )
fi

while [ 1 ]; do
    # Benutzereingabe der Treffernummer bzw. eines Kommandos
    read -er -p "> " input

    # Einfügen der Benutzereingabe in den Such- und Kommandoverlauf
    history -s -- "$input"

    # Auflistung zusätzlicher Kommando-Optionen bei Kommando k
    if [ "$input" = "k" ]; then
        printf " \033[1mh\033[0m voranstellen, um Film in hoher Qualität abzuspielen (z.B. h6),\n \033[1mn\033[0m voranstellen, um Film in niedriger Qualität abzuspielen (z.B. n9),\n(zur Verfügbarkeit niedriger/hoher Qualität siehe Kennzeichnung [n/h] hinter Filmtitel)\n \033[1mb\033[0m voranstellen, um Bookmark zu speichern (z.B. b4),\n \033[1md\033[0m voranstellen, um Film in Standardqualität herunterzuladen (z.B. d17),\n \033[1mdh\033[0m voranstellen, um Film in hoher Qualität herunterzuladen (z.B. dh1),\n \033[1mdn\033[0m voranstellen, um Film in niedriger Qualität herunterzuladen (z.B. dn2),\n \033[1mw\033[0m voranstellen, um Internetseite zur Sendung im Browser zu öffnen (z.B. w35),\n \033[1mi\033[0m voranstellen, um alle zum Film gehörenden Links anzuzeigen (z.B. i2),\n \033[1mm\033[0m voranstellen, um bei Option -l Livestreams in mittlerer (statt höchster) Auflösung abzuspielen (z.B. m25),\n \033[1ma\033[0m (\033[1mA\033[0m) voranstellen, um nur 5 (10) Treffer ab Filmnr. anzuzeigen (z.B. a10 bzw. A10),\n(\033[1ma\033[0m bzw. \033[1mA\033[0m ohne Nummer entspricht a1 bzw. A1)\n \033[1m   +\033[0m (oder \033[1mv\033[0m) blättert vorwärts (in Teilansicht mit 5 bzw. 10 Treffern),\n \033[1m   -\033[0m (oder \033[1mr\033[0m) blättert rückwärts (in Teilansicht mit 5 bzw. 10 Treffern),\n \033[1mz\033[0m liest die Trefferliste neu ein,\n \033[1mB\033[0m wechselt in den Modus \"Bookmarks\" (Ansicht, Abspielen, Löschen),\n \033[1mH\033[0m zeigt die Hilfe zur Filmsuche.\n"

    elif [[ $input =~ ^q$|^quit$|^exit$ ]]; then
        exit   #Beenden des Programms bei Eingabe von "q", "quit" oder "exit"

    elif [ "$input" = "B" ]; then
        if [ ! -f $dir/bookmarks ]; then
            echo "Die Datei $dir/bookmarks existiert nicht."
        else
            bmcli   #Wechsel zur Kommandozeile Bookmarks
        fi
    
    elif [ "$input" = "H" ]; then

#----- Zeige den folgenden Textblock an (Suchhilfe): -----
fett=$(tput bold)
normal=$(tput sgr0)
unterstr=$(tput smul)

fmt -s -w $(tput cols) << ende-hilfe | less -Kr -Ps"Zum Beenden der Hilfe Taste q drücken"

                    ${fett}*** HILFE zur Filmsuche ***${normal}

${fett}OPTIONEN:${normal}
      ${fett}-A DATUM${normal}   Sucht nur Sendungen neuer als DATUM (und vom DATUM); DATUM muss im Format [[TT.]MM.]JJJJ eingegeben werden.
      ${fett}-B DATUM${normal}   Sucht nur Sendungen älter als DATUM (und vom DATUM); DATUM muss im Format [[TT.]MM.]JJJJ eingegeben werden.
      ${fett}-K MINUTEN${normal}   Sucht nur Filme kürzer als MINUTEN (ganze Zahl).
      ${fett}-L MINUTEN${normal}   Sucht nur Filme länger als MINUTEN (ganze Zahl).
      ${fett}-g${normal}   Unterscheidet bei der Suche zwischen Groß- und Kleinbuchstaben.
      ${fett}-h${normal}   Zeigt die ausführliche Hilfe an.
      ${fett}-l${normal}   Listet alle Livestreams auf (Suchstrings werden nicht berücksichtigt).
      ${fett}-s${normal}   Sortiert Suchtreffer absteigend nach Sendedatum (neueste zuoberst).
      ${fett}-t${normal}   Sortiert Suchtreffer aufsteigend nach Sendedatum (neueste zuunterst).

${fett}SUCH-OPERATOREN:${normal}
       ${fett}+${normal}   Ein "+" unmittelbar vor einem Suchstring bewirkt, dass dieser als Einzelwort gesucht wird und NICHT als Zeichenfolge auch innerhalb von Wörtern.
       ${fett}~${normal}   Eine Tilde (~) unmittelbar vor einem Suchstring schließt diesen für die Suche gezielt aus. Dieser Operator kann nicht mit dem ersten Suchstring verwendet werden.

${fett}SUCHBEISPIEL:${normal}
      ${unterstr}-gt +EU Gurke${normal}
            ... sucht nach Einträgen mit dem Einzelwort "EU" (exakte Wortsuche mit +) und dem Wort(teil) "Gurke". Dabei wird zwischen Groß- und Kleinschreibung unterschieden (-g), und die Treffer werden aufsteigend nach Sendedatum sortiert ausgegeben (-t).
ende-hilfe
#----- Ende Textblock ------
          icli

    elif [[ $input =~ ^a[0-9]?+$ ]]; then   #Anzeige von 5 Treffern ab Zeile ...
        if [ $trefferzahl -lt 5 ]; then
            echo "Kommando wird bei weniger als 5 Treffern nicht unterstützt!"
        else
            clear && printf '\e[3J'
            a=$(echo ${input//[!0-9]/})
            let a=$(( a < trefferzahl ? a : trefferzahl-4 ))
            let a=$(( a > 0 ? a : 1 ))
            let x=(a-1)*5+1
            let y=x+24
            pl=5
            pageview
            icli
        fi

    elif [[ $input =~ ^A[0-9]?+$ ]]; then   #Anzeige von 10 Treffern ab Zeile ...
        if [ $trefferzahl -lt 10 ]; then
            echo "Kommando wird bei weniger als 10 Treffern nicht unterstützt!"
        else
            clear && printf '\e[3J'
            a=$(echo ${input//[!0-9]/})
            let a=$(( a < trefferzahl ? a : trefferzahl-9 ))
            let a=$(( a > 0 ? a : 1 ))
            let x=(a-1)*5+1
            let y=x+49
            pl=10
            pageview
            icli
        fi

    elif [[ "$input" = "v" || "$input" = "+" ]]; then   #Blättern vorwärts
        if [ "$a" = "" ]; then
            echo "Blättern ist in der Gesamtansicht der Trefferliste nicht möglich. Bitte zuerst mit Kommando a oder A zu einem Eintrag springen." | ( if [[ -z $wopt ]]; then fmt -s -w $(tput cols); else tee; fi )
        else
            clear && printf '\e[3J'
            let a=$(( a+pl <= trefferzahl ? a+pl : a ))
            let x=(a-1)*5+1
            let y=x+pl*5-1
            pageview
            icli
        fi

    elif [[ "$input" = "r" || "$input" = "-" ]]; then   #Blättern rückwärts
        if [ "$a" = "" ]; then
            echo "Blättern ist in der Gesamtansicht der Trefferliste nicht möglich. Bitte zuerst mit Kommando a oder A zu einem Eintrag springen." | ( if [[ -z $wopt ]]; then fmt -s -w $(tput cols); else tee; fi )
        else
            clear && printf '\e[3J'
            let a=$(( a-pl > 0 ? a-pl : 1 ))
            let x=(a-1)*5+1
            let y=x+pl*5-1
            pageview
            icli
        fi

    elif [ "$input" = "z" ]; then
        a=""
        if [ ! -z "$out" ]; then
            hits   #Neueinlesen des Suchergebnisses
            icli
        else
            echo "Es liegt keine Suchanfrage vor."
        fi

    elif [[ $input =~ ^d[hn]?[0-9]+$ || $input =~ ^[bhimnw][0-9]+$ || $input =~ ^[0-9]+$ ]]; then
        filmnr=$(echo ${input//[!0-9]/}) # Variable $filmnr = Kommando ohne führenden Buchstaben
        if [[ $filmnr -gt $trefferzahl || $filmnr -eq 0 ]]; then
            echo "Kein Film mit dieser Nummer!"
        else
            # Bestätigung des ausgewählten Films
            echo "$out" | awk -F "\",\"" 'NR=='$filmnr'{print "Ausgewählt:", $4, "("$1":",$3")"}' | tr -d '\\'

            # ANSI-Escapesequenzen für URL-Farbe blau in Variablen,
            # wenn Option -o nicht gewählt
            if [[ -z $oopt ]]; then
                bluein="\\033[0;34m"
                blueout="\\033[0m"
            fi

            filmurl=$(echo "$out" | \
                awk -F "\",\"" 'NR=='$filmnr'{print $10}')
            # Abspielen des Videos in niedriger/hoher Qualität
            if [[ $input =~ ^[nh][0-9]+$ ]]; then
                if [[ "$input" = n* ]]; then
                    def=14   #Feld d. Ergebnisliste für niedr. Qualität in Variable def
                    qual="niedriger"
                else
                    def=16   #Feld d. Ergebnisliste für hohe Qualität in Variable def
                    qual="hoher"
                fi

                urlqual $def

                if [ "$filmurl" = "" ]; then
                    echo "Film nicht in $qual Auflösung verfügbar."
                else
                    echo "Bitte etwas Geduld ..."
                    $player "$filmurl" >/dev/null 2>&1
                    status=$?
                    if [ $status -ne 0 ]; then
                        echo "Diese URL konnte vom Player nicht abgespielt werden."
                    fi
                fi
            fi

            # Auflistung aller URLs (Kommando "i")
            if [[ "$input" = i* ]]; then
                echo "    [n] = Niedrige Qualität, [s] = Standardqualität, [h] = Hohe Qualität, [w] = Internetseite" |    #Legende der Abkürzungen \
                ( if [[ -z $wopt ]]; then fmt -s -w $(tput cols); else tee; fi )   #Worterhaltende Zeilenumbrüche (außer bei Option -w)
                urlqual 14
                if [[ "$filmurl" = "" ]]; then
                    echo "[n] nicht verfügbar"
                else
                    echo -e "[n] $bluein$filmurl$blueout"
                fi
                stanurl=$(echo "$out" | awk -F "\",\"" 'NR=='$filmnr'{print $10}')
                echo -e "[s] $bluein$stanurl$blueout"
                urlqual 16
                if [[ "$filmurl" = "" ]]; then
                    echo "[h] nicht verfügbar"
                else
                    echo -e "[h] $bluein$filmurl$blueout"
                fi
                weburl=$(echo "$out" | awk -F "\",\"" 'NR=='$filmnr'{print $11}')
                echo -e "[w] $bluein$weburl$blueout"
            fi

            # Download des Videos (Kommando "d...")
            qual="normaler"
            if [[ $input =~ ^d[hn]?[0-9]+$ ]]; then

                if [[ $input =~ ^d[hn][0-9]+$ ]]; then   #Film-URL für niedrige/hohe Qualität
                    if [[ "$input" = dn* ]]; then
                        def=14   #Feld d. Ergebnisliste für niedr. Qualität in Variable def
                        qual="niedriger"
                        urlqual $def
                    fi
                    if [[ "$input" = dh* ]]; then
                        def=16   #Feld d. Ergebnisliste für hohe Qualität in Variable def
                        qual="hoher"
                        urlqual $def
                    fi
                fi

                if [ "$filmurl" = "" ]; then
                    echo "Film nicht in $qual Auflösung verfügbar."
                else
                    ext="${filmurl##*.}"   #Dateiendung der Film-URL
                    echo -e "Download des Videos in $qual Qualität. \033[1mFalls gewünscht, bitte Speicherort und Dateiname anpassen.\033[0m"
                    if [ "$ext" = "m3u8" ]; then
                        xx="mp4"
                    else
                        xx=$ext
                    fi
                    read -ep "Speichern unter: " -i "$dldir/$(echo "$out" | awk -F "\",\"" -v ext=$xx 'NR=='$filmnr'{print $4"."ext}' | tr -d '\\' | tr ' ' '_' | tr '/' '-' )" downloadziel
                    if [[ "$ext" = "m3u8" ]]; then
                        # Download mit FFmpeg
                        ffmpeg -i $filmurl -c copy -bsf:a aac_adtstoasc "$downloadziel"
                    else
                        wget -nc -O $downloadziel $filmurl
                    fi
                    echo -e "\033[1mTrefferliste kann mit Kommando z neu eingelesen werden.\033[0m"
                fi
            fi

            # Anzeige der Internetseite zur Sendung im Standardbrowser (Kommando "w")
            if [[ "$input" = w* ]]; then
                weburl=$(echo "$out" | awk -F "\",\"" 'NR=='$filmnr'{print $11}')
                echo -e "URL: $bluein$weburl$blueout"
                read -p "Soll die Internetseite zu dieser Sendung im Browser geöffnet werden? (J/n)" antwort
                if [[ "$antwort" = J || "$antwort" = j || "$antwort" = "" ]]; then
                    xdg-open $(echo "$out" | awk -F "\",\"" 'NR=='$filmnr'{print $11}') >/dev/null 2>&1 &
                fi
            fi

            # Speichern als Bookmark
            if [[ "$input" = b* ]]; then
                echo "$out" | \
                awk -F "\",\"" 'NR=='$filmnr'{print $4,"* "$10}' | tr -d '\\' >> $dir/bookmarks
                printf "\033[1mFilm ($filmnr) wurde als Bookmark gespeichert.\033[0m\nWechsel zur Bookmarkübersicht mit Kommando \033[1mB\033[0m.\n"
            fi

            # Abspielen des Videos in Standardauflösung
            if [[ $input =~ ^[0-9]+$ || $input =~ ^m[0-9]+$ ]]; then

                # Abspielen von Livestreams in Auflösung kleiner/gleich 1024
                if [[ $input =~ ^m[0-9]+$ ]]; then
                    if [[ -z $lopt ]]; then
                        echo "Vorangestelltes m wird nicht berücksichtigt, da nur für Livestreams gültig!"
                    else
                        for res in 1024 960 852 720 640; do
                            filmurl_m=$(wget -q -O - $filmurl | grep -A1 "RESOLUTION=$res" | grep -v "RESOLUTION=$res" | head -1)
                            if [[ "$filmurl_m" != "" ]]; then
                                break
                            fi
                        done
                        # ggf. Konvertierung der relativen in absolute URL
                        if [[ "$filmurl_m" != http* ]]; then
                            filmurl_m="${filmurl%/*}/$filmurl_m"
                        fi
                        filmurl=$filmurl_m
                    fi
                fi

                echo "Bitte etwas Geduld ..."
                $player "$filmurl" >/dev/null 2>&1
                status=$?
                if [ $status -ne 0 ]; then
                    echo "Diese URL konnte vom Player nicht abgespielt werden."
                fi
            fi
        fi

    else
        # Ausführen der Suche von der internen Kommandozeile
        if [ ! -z $oopt ]; then
            o="-o"
        fi
        if [ ! -z $wopt ]; then
            w="-w"
        fi

        if [[ $(echo -n $input | wc -m) -lt 3 && ! $input =~ ^[-] ]]; then
            echo "Suchanfragen mit weniger als drei Zeichen werden nicht unterstützt!"
        else
            history -w $dir/mt_history
            H="-H"
            ninput=$(echo "$input" | awk -F\" '{OFS="\"";for(i=2;i<NF;i+=2)gsub(/ /,"\\s",$i);print}' | sed 's/"//g')  #Leerzeichen in Phrasen werden durch \\s ersetzt
            exec "$0" $H $o $w $ninput
        fi
    fi

done
}

# Defintion der FUNKTION bmcomm: Übersicht der Bookmark-Kommandos anzeigen
function bmcomm {
    printf '%.0s-' $(seq $(tput cols)); printf '\n'   #gestrichelte Trennlinie
    printf "\033[1mZum Abspielen Nummer des gewünschten Eintrags eingeben.\033[0m\n\033[1mq\033[0m beendet MediaTerm. \033[1mk\033[0m listet zusätzliche Kommando-Optionen auf.\n"
}

# Definition der FUNKTION bmcli: Kommandozeile Bookmarks
function bmcli {
    sed -i '/^\s*$/d' $dir/bookmarks   #entfernt eventuelle Leerzeilen aus der BM-Datei
    cat -b $dir/bookmarks | awk 'ORS="\n"{$1=$1;print}' | sed 'G'   #Aufbereitete Ausgabe der Bookmarks (mit Zeilennummerierung und Leerzeilen zw. Einträgen)
    bmcomm
    filmmax=$(cat $dir/bookmarks | wc -l)   #Anzahl der Bookmarks

    while [ 1 ]; do

    read -ep ">> " input
    history -s -- "$input"
    if [[ ! $input =~ ^[c,k,q,z,S]$ && ! $input =~ ^[0-9]+$ && ! $input = exit && ! $input = quit && ! $input =~ ^[al][0-9]+$ ]]; then
    echo "$input ist keine korrekte Eingabe."

    elif [ "$input" = "k" ]; then
        printf " \033[1ma\033[0m voranstellen (z.B. a5), um Bookmark als Suchergebnis anzuzeigen\n (= detaillierte Anzeige und zusätzliche Abspieloptionen, Trefferliste einer evtl. vorher durchgeführten Suche danach nicht mehr verfügbar!),\n \033[1mc\033[0m überprüft Gültigkeit aller Bookmarklinks,\n \033[1ml\033[0m voranstellen (z.B. l3), um Bookmark zu löschen,\n \033[1mz\033[0m liest Bookmarks neu ein,\n \033[1mS\033[0m wechselt in den Modus \"Suche/Treffer\".\n" | ( if [[ -z $wopt ]]; then fmt -s -w $(tput cols); else tee; fi )

    elif [[ $input =~ ^q$|^quit$|^exit$ ]]; then
        exit   #Beenden des Programs bei Kommando "q"

    # Linkchecker mit wget (Kommando "c")
    elif [ "$input" = "c" ]; then
        tabs 4
        for i in $(seq 1 $filmmax); do
            echo -e -n "$i\t"; wget -nv --server-response --spider --timeout=6 $(cat -b $dir/bookmarks | awk '{$1=$1;print}' | grep "^${i}[ ]" | cut -d "*" -f2) 2>&1 | grep 'HTTP/'
        done
        echo
        printf "\033[1mz\033[0m lädt Bookmarks neu.\n"
        bmcomm

    # Löschen eines Bookmarks, ${input//[!0-9]/} ist Nummer des zu löschenden Bookmarks
    elif [[ "$input" = l* ]]; then
        if [[ $(echo ${input//[!0-9]/}) -gt $filmmax || $(echo ${input//[!0-9]/}) -eq 0 ]]; then
            echo "Kein Bookmark mit dieser Nummer!"
        else
            read -p "Soll Bookmark ${input//[!0-9]/} gelöscht werden (J/n)" antwort
            if [[ $antwort = J || $antwort = j || -z $antwort ]]; then
                sed -i '/^\s*$/d' $dir/bookmarks   #entfernt eventuelle Leerzeilen aus der BM-Datei
                sed -i "${input//[!0-9]/}d" $dir/bookmarks
                echo
                cat -b $dir/bookmarks | awk '{$1=$1;print}' | sed 'G'
                echo -e "\033[1mBookmark wurde gelöscht.\033[0m"
                bmcomm
            else
                echo "Es wurde kein Bookmark gelöscht."
            fi
        fi

    # Wechsel in den Modus "Suchen/Treffer" (Kommando "S")
    elif [ "$input" = "S" ]; then
        if [ "$out" ]; then
            hits
            icli
        else
            icli
        fi

    # Anzeigen von Bookmarks und Kommandoübersicht (Kommando "z")
    elif [ "$input" = "z" ]; then
        bmcli

    # Detaillierte Anzeige und Abspieloptionen, ${input//[!0-9]/} ist Nummer des Bookmarks
    elif [[ "$input" = a* ]]; then
        input=$(echo ${input//[!0-9]/})
        if [[ $input -gt $filmmax || $(echo ${input//[!0-9]/}) -eq 0 ]]; then
            echo "Kein Bookmark mit dieser Nummer!"
        else
            bmurl=$(cat -b $dir/bookmarks | awk '{$1=$1;print}' | grep "^${input}[ ]" | cut -d "*" -f2)
            out=$(grep $bmurl $dir/filmliste)
            suchanfrage=" Bookmark $input"
            echo   #Leerzeile
            hits
            icli
        fi

    # Abspielen der Bookmarks
    else
        if [[ $input -gt $filmmax || $(echo ${input//[!0-9]/}) -eq 0 ]]; then
            echo "Kein Bookmark mit dieser Nummer!"
        else
            echo "Bitte etwas Geduld ..."
            $player $(cat -b $dir/bookmarks | awk '{$1=$1;print}' | grep "^${input}[ ]" | cut -d "*" -f2) >/dev/null 2>&1
            status=$?
            if [ $status -ne 0 ]; then
                echo "Diese URL konnte vom Player nicht abgespielt werden."
            fi
        fi
    fi
done
exit
}

# Definition der FUNKTION urlqual: setzt URLs niedriger und hoher Qualität zusammen.
# Parameter bestimmen sich nach Feldnummer von $out (14 niedrige, 16 hohe Qualität).
urlqual () {
filmurl=$(echo "$out" | \
    nl -s "\", \""  |   # Zeilennummerierung \
    awk -v url="$(echo "$out" | awk -F "\",\"" -v fn=$filmnr 'NR==fn{print $10}')" -v urlstammlaenge="$(echo "$out" | awk -F "\",\"" -v var="$1" -v fn=$filmnr 'NR==fn{print $var}' | cut -d"|" -f1)" -v urlsuffix="$(echo "$out" | awk -F "\",\"" -v var="$1" -v fn=$filmnr 'NR==fn{print $var}' | cut -d"|" -f2)" -F "\",\"" -v fn=$filmnr 'NR==fn{print substr(url,1,urlstammlaenge)urlsuffix}')
}

# Definition der FUNKTION pageview: Teilansicht mit fünf Treffern für Blätterfunktion
pageview () {
        echo
        echo "$out" | \
            awk -F "\",\"" '{ORS=" "}; {print "("NR")", "\033[0;32m"$4"\033[0m"" ("$1": "$3")"}; {if($14!=""){printf "[n"} else{printf "[-"}}; {if($16!=""){print "/h]"} else{print "/-]"}}; {print "\n"  "\33[1m""Datum:""\033[0m",$5  ",",  $6,"Uhr","*",  "\33[1m""Dauer:""\033[0m",  $7,"\n" $9,  "\n" "\033[0;34m"$10"\033[0m"} {printf "\n\n"}' | \
            awk -v x=$x -v y=$y 'NR==x,NR==y' | #nur 5/10 Treffer ab Nr. in Variable x \
            ( if [ ! -z $oopt ]; then sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g"; else tee; fi ) |   #Entfernt Farbformatierungen bei Option -o \
            tr -d '\\' |   #Entfernt Escape-Backslashes aus Ausgabe \
            ( if [[ -z $wopt ]]; then fmt -s -w $(tput cols); else tee; fi )   #Worterhaltende Zeilenumbrüche (außer bei Opshell scripttion -w)

echo "[Suchanfrage:$suchanfrage] (Treffer: $trefferzahl, Blättern mit +/-)" #Anzeige der Suchanfrage unter der Trefferliste
}

# <<<<< ENDE FUNKTIONEN <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

#### Aufrufen, Abspielen und Löschen der Bookmarks (Option -b)
if [ ! -z $bopt ]; then
    if [ ! -f $dir/bookmarks ]; then
        echo "Die Datei $dir/bookmarks existiert nicht."
        exit
    fi
    bmcli   #Funktion bmcli
fi

#### Herunterladen der Filmliste (falls nicht vorhanden oder bei Option -u)
if [[ ! -f $dir/filmliste  || ! -z $uopt ]]; then
    read -p "Soll die aktuelle Filmliste heruntergeladen und im Verzeichnis $dir (wird ggf. vom Programm angelegt) gespeichert werden? (J/n)" antwort
    echo

    # Fall: Download-Frage bejaht
    if [[ $antwort = J || $antwort = j || -z $antwort ]]; then
        mkdir -p $dir
        cd $dir

        # Prüfung der lokalen Filmliste auf Aktualität
        if [[ -f $dir/filmliste ]]; then
            listdate=$(awk -F "\",\"" 'NR=='1'{print $2}' $dir/filmliste | cut -d"\"" -f4 | awk -F "," '{ n=split($1,b,".");$1=b[3]"-"b[2]"-"b[1];print }')   #Erstellungsdatum aus lokaler Filmliste
            nlistdate=$(date -d "${listdate}" +%Y%m%d%H30)   #Normierung des Datums (Abrundung zur vollen Stunde + 30 Minuten)
        else
            nlistdate=0
        fi
        if [ $(($nlistdate + 200)) -gt $(TZ=Europe/Berlin date +%Y%m%d%H%M) ]; then
            printf "\033[1mDie gespeicherte Filmliste vom $(head -n +1 $dir/filmliste | cut -d"\"" -f6 | tr -d '\n') Uhr, ist aktuell! -- kein Download\033[0m \n"   #kein Download bis zur übernächsten vollen Stunde + 30 Minuten
        exit
        fi

        wget -nv --show-progress --user-agent=MediaTerm https://liste.mediathekview.de/Filmliste-akt.xz   # Herunterladen der komprimierten Filmliste
        # Prüfung des Exitstatus von Wget
        if [ $? -ne 0 ]; then
            echo "Die Filmliste konnte nicht heruntergeladen werden!"
        else
            echo "Die heruntergeladene Filmliste wird entpackt und aufbereitet ..."
            xz -d -f Filmliste-akt.xz   #Entpacken der Filmliste
            sed -i 's-"X":-\n-g' Filmliste-akt   #Ersetzen des Trenners "X" durch Zeilenumbruch
            cat Filmliste-akt | awk -F "\"" '!/\[\"\"/ { sender = $2; } { print sender"\",\""$0; }' | awk -F "\",\"" -v OFS="\",\"" '!($3==""){ thema = $3; } {sub($3,thema,$3); print}' > filmliste   #allen Zeilen Sender voranstellen und in alle Zeilen Thema einfügen
            rm Filmliste-akt*   #Löschen der nicht mehr benötigten Dateien
            # Entfernung von Zeilenumbruch-Escape-Sequenzen in Filmliste (d.h. in Film-Beschreibungen)
            sed -i 's/\(\(\\r\)*\(\\n\)\)\+/\ /g' filmliste
        fi

      # Fall: Download-Frage verneint
    else
        if [ ! -f $dir/filmliste ]; then
            printf "\033[1mOhne Filmliste funktioniert MediaTerm nicht.\033[0m \n"
            exit
        fi
    fi

    # Bei Option -u wird Programm nach Download beendet
    if [ ! -z $uopt ]; then
        exit
    fi
fi

#### Bei fehlendem Suchstring wird die interne Kommando(Such-)zeile ohne Trefferliste geöffnet (Ausnahme: Option -l, Livestreams).
if [[ -z $1 && -z $lopt ]]; then
    icli
fi

#### Suche (rohes Suchergebnis)

echo   #Leerzeile aus kosmetischen Gruenden

# Falls Option -l, Änderung des searchstrings zu "Livestream"
if [ ! -z $lopt ]; then
    out=$(grep $C -w "\"Livestream\"" $dir/filmliste)
else
    # Wenn Option -g NICHT gewählt, keine Unterscheidung zwischen Gross- und Kleinschreibung
    if [ -z $gopt ]; then
        C="I"   #sed-Option I (ignore case) in Variable c
    fi

    # Suchergebnis für ersten Suchstring
    if [[ $1 = \+* ]]; then
        out=$(tail -n +2 $dir/filmliste | sed -n "/\b${1:1}\b/$C p")   #Exakte Wortsuche
    else
        out=$(tail -n +2 $dir/filmliste | sed -n "/$1/$C p")
    fi
fi

# Filtern mit weiteren Suchstrings
for i in "${@:2}"; do
    if [[ $i = \+* ]]; then
        out=$(echo "$out" | sed -n "/\b${i:1}\b/$C p")   #Exakte Wortsuche
    elif [[ $i = \~\+* ]]; then
        out=$(echo "$out" | sed -n "/\b${i:2}\b/$C !p")  #Ausschluss eines exakten Wortes
    elif [[ $i = \~* ]]; then
        out=$(echo "$out" | sed -n "/${i:1}/$C !p")   #Ausschluss eines Strings
    else
        out=$(echo "$out" | sed -n "/$i/$C p")   #Normale Stringsuche
    fi
done

if [[ "$out" ]]; then
    # Filtern nach Zeitraum (Optionen -A, -B)
    if [ "$datum1" != "01.01.0000" ] || [ "$datum2" != "31.12.9999" ]; then
        out=$(echo "$out" | awk -F"\",\"" 'OFS="\",\""{ n=split($5,b,".");$5=b[3]"."b[2]"."b[1];print }' |   #Datumsfelder ($5) werden zwecks Vergleich invertiert \
            awk -F "\",\"" -v t1="$datum1" -v t2="$datum2" '{if (($5 <= t2)&&($5 >= t1)) {print} }' |   #Vergleich der Datumsfelder mit Optionsargumenten; Filtern mit if-Anweisung \
            awk -F"\",\"" 'OFS="\",\""{ n=split($5,b,".");$5=b[3]"."b[2]"."b[1];print}')   #Zurücksetzen der Datumsfelder ($5) in ihr ursprüngliches Format
    fi

    # Filtern nach Filmlänge (Optionen -K, -L)
    if [ ! -z $Kopt ] || [ ! -z $Lopt ]; then
        out=$(echo "$out" | awk -F"\",\"" 'OFS="\",\""{n=split($7,b,":"); $7=(b[1]*3600 + b[2]*60 + b[3]);print }' |   #Filmlänge ($7) wird in Sekunden konvertiert \
            awk -F "\",\"" -v d1="$longer" -v d2="$shorter" '{if (($7 >= d1)&&($7 <= d2)) {print} }' |   #Vergleich der Filmlänge mit Optionsargument; Filtern mit if-Anweisung \
            awk -F"\",\"" 'OFS="\",\""{hms="date -u -d @"$7 " +%T";hms | getline $7;close(hms);print}')   #Zurücksetzen der Felder "Dauer" ($7) in ihr ursprüngliches Format
    fi
fi

#### Sortieren nach Sendezeit (Optionen -s, -t)
# Sortierung aufsteigend
if [ ! -z $topt ]; then
    out=$(echo "$out" | awk -F "\",\"" '{print $5"*"$6"-"$0}' | sort -t"." -n -k3,3 -k2,2 -k1,1 | cut -d "-" -f 2-)
fi
# Sortierung absteigend
if [ ! -z $sopt ]; then
    out=$(echo "$out" | awk -F "\",\"" '{print $5"*"$6"-"$0}' | sort -t"." -r -n -k3,3 -k2,2 -k1,1 | cut -d "-" -f 2-)
fi

#### Formatierung und Ausgabe des Suchergebnisses
hits   #Funktion hits

#### Filme abspielen, herunterladen, als Bookmark speichern (interne Kommandozeile)
icli   #Funktion icli
