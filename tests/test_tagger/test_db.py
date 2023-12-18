import json
from pathlib import Path
from unittest.mock import patch

import doc_db

class TestDB_Collection:

    def __get_list_of_para_text(self): 
        ret_val = [
            "Begründung",
            "I. Antrag",
            "Gestützt auf Art139 Abs1 B-VG begehrt die Antragstellerin mit ihrem am 21. Dezember 2021 eingebrachten Antrag, der Verfassungsgerichtshof möge",
            "\"1. […] In Punkt 1. der 456. Verordnung des Bundesministers für Soziales, Gesundheit, Pflege und Konsumentenschutz, BGBl II. Nr 456/21 vom 02.11.2021, mit der §1 Abs2 Z4 der 3. COVID-19-Maßnahmenverordnung (3. COVID-19-MV), BGBl II Nr 441/2021, geändert wird (1. Novelle zur 3. COVID-19-Maßnahmenverordnung), die Worte: 'die lit... und c entfallen....' [als verfassungswidrig aufheben]",
            "",
            "sowie",
            "",
            "2. aussprechen, dass §1 Abs2 Z4 litc der […] 3. COVID-19-Maßnahmenvero[r]dnung (3. COVID-19-MV) in der Fassung BGB[l]. II. Nr 441/2021 als verfassungswidrig aufzuheben ist und stattdessen dem §1 Abs2 Z3 der 3. COVID-19-Maßnahmenvero[r]dnung (3. COVID-19-MV) in der Fassung BGB[l] II. Nr 441/2021 als litc einzufügen ist: 'oder ein Nachweis über neutralisierende Antikörper, der nicht älter als 90 Tage ist.'",
            "",
            "In eventu:",
            "",
            "4. auszusprechen, dass in Punkt 1. der 456. Verordnung des Bundesministers für Soziales, Gesundheit, Pflege und Konsumentenschutz, BGBl II. Nr 456/21 vom 02.11.2021, mit der §1 Abs2 Z4 der 3. COVID-19-Maßnahmenverordnung (3. COVID-19-MV), BGBl II Nr 441/2021, geändert wird (1. Novelle zur 3. COVID-19-Maßnahmenverordnung), die Worte 'die lit.... und c entfallen....' und somit die 3. COVID-19-MV i.d.F BGBl II. Nr 456/21 vom 2.11.2021 hinsichtlich dieser Bestimmung in der Zeit vom 08.11.2021 bis 22.11.2021 verfassungswidrig war.\" ",
            "",
            "II. Rechtslage",
            "1. §1 und §23 Abs1 und Abs4 der Verordnung des Bundesministers für Soziales, Gesundheit, Pflege und Konsumentenschutz betreffend Maßnahmen, die zur Bekämpfung der Verbreitung von COVID-19 ergriffen werden (3. COVID-19-Maßnahmenverordnung – 3. COVID-19-MV), BGBl II 441/2021, lauteten:",
            "\"Auf Grund der §§3 Abs1, 4 Abs1, 4a Abs1 und 5 Abs1 des COVID-19-Maßnahmengesetzes, BGBl I Nr 12/2020, zuletzt geändert durch das Bundesgesetz BGBl I Nr 183/2021, sowie des §5c des Epidemiegesetzes 1950, BGBl Nr 186/1950, zuletzt geändert durch das Bundesgesetz BGBl I Nr 183/2021, wird verordnet:",
            "",
            "Allgemeine Bestimmungen",
            "",
            "§1. (1) Als Maske im Sinne dieser Verordnung gilt eine Atemschutzmaske der Schutzklasse FFP2 (FFP2-Maske) ohne Ausatemventil oder eine Maske mit mindestens gleichwertig genormtem Standard.",
            "",
            "(2) Als Nachweis über eine geringe epidemiologische Gefahr im Sinne dieser Verordnung gilt ein:",
            "1. '1G-Nachweis': Nachweis über eine mit einem zentral zugelassenen Impfstoff gegen COVID-19 erfolgte",
            "a) Zweitimpfung, wobei diese nicht länger als 360 Tage zurückliegen darf und zwischen der Erst- und Zweitimpfung mindestens 14 Tage verstrichen sein müssen,",
            "b) Impfung ab dem 22. Tag nach der Impfung bei Impfstoffen, bei denen nur eine Impfung vorgesehen ist, wobei diese nicht länger als 270 Tage zurückliegen darf,",
            "c) Impfung, sofern mindestens 21 Tage vor der Impfung ein positiver molekularbiologischer Test auf SARS-CoV-2 bzw vor der Impfung ein Nachweis über neutralisierende Antikörper vorlag, wobei die Impfung nicht länger als 360 Tage zurückliegen darf, oder",
            "d) weitere Impfung, wobei diese nicht länger als 360 Tage zurückliegen darf und zwischen dieser und einer Impfung im Sinne der",
            "aa) lita oder c mindestens 120 Tage oder",
            "bb) litb mindestens 14 Tage",
            "verstrichen sein müssen;",
            "2. '2G-Nachweis': Nachweis gemäß Z1 oder ein",
            "a) Genesungsnachweis über eine in den letzten 180 Tagen überstandene Infektion mit SARS-CoV-2 oder eine ärztliche Bestätigung über eine in den letzten 180 Tagen überstandene Infektion mit SARS-CoV-2, die molekularbiologisch bestätigt wurde, oder",
            "b) Absonderungsbescheid, wenn dieser für eine in den letzten 180 Tagen vor der vorgesehenen Testung nachweislich mit SARS-CoV-2 infizierte Person ausgestellt wurde;",
            "3. '2,5G-Nachweis': Nachweis gemäß Z1 oder 2 oder ein Nachweis einer befugten Stelle über ein negatives Ergebnis eines molekularbiologischen Tests auf SARS-CoV-2, dessen Abnahme nicht mehr als 72 Stunden zurückliegen darf;",
            "4. '3G-Nachweis': Nachweis gemäß Z1 bis 3 oder ein Nachweis",
            "a) einer befugten Stelle über ein negatives Ergebnis eines Antigentests auf SARS-CoV-2, dessen Abnahme nicht mehr als 24 Stunden zurückliegen darf,",
            "b) über ein negatives Ergebnis eines SARS-CoV-2-Antigentests zur Eigen-anwendung, der in einem behördlichen Datenverarbeitungssystem erfasst wird und dessen Abnahme nicht mehr als 24 Stunden zurückliegen darf,",
            "c) über neutralisierende Antikörper, der nicht älter als 90 Tage ist, oder",
            "d) gemäß §4 Z1 der COVID-19-Schulverordnung 2021/22 (C-SchVO 2021/22), BGBl II Nr 374/2021, (Corona-Testpass).",
            "Kann ein 3G-Nachweis nicht vorgelegt werden, ist ausnahmsweise ein SARS-CoV-2-Antigentest zur Eigenanwendung unter Aufsicht des Betreibers einer Betriebsstätte gemäß den §§4 bis 6, einer nicht öffentlichen Sportstätte gemäß §7, einer Freizeiteinrichtung gemäß §8, eines Alten- und Pflegeheims oder einer stationären Wohneinrichtung der Behindertenhilfe (§10), einer Krankenanstalt, Kuranstalt oder eines sonstigen Ortes, an dem eine Gesundheitsdienstleistung erbracht wird (§11) oder des für eine Zusammenkunft Verantwortlichen (§§12 bis 16) durchzuführen.",
            "",
            "(3) Ein Corona-Testpass gilt in der Woche, in der die Testintervalle gemäß §19 Abs1 C-SchVO 2021/2022 eingehalten werden, auch am Freitag, Samstag und Sonntag dieser Woche als 3G-Nachweis.",
            "",
            "(4) Nachweise gemäß Abs2 sind in lateinischer Schrift in deutscher oder englischer Sprache oder in Form eines Zertifikats gemäß §4b Abs1 des Epidemiegesetzes 1950 (EpiG), BGBl Nr 186/1950, vorzulegen.",
            "",
            "(5) Sofern in dieser Verordnung ein Nachweis gemäß Abs2 vorgesehen ist, ist dieser für die Dauer des Aufenthalts bereitzuhalten. Der Inhaber einer Betriebsstätte, der Verantwortliche für einen bestimmten Ort oder der für eine Zusammenkunft Verantwortliche ist zur Ermittlung folgender personenbezogener Daten der betroffenen Person ermächtigt:",
            "           1. Name,",
            "           2. Geburtsdatum,",
            "           3. Gültigkeit bzw Gültigkeitsdauer des Nachweises und",
            "           4. Barcode bzw QR-Code.",
            "",
            "Darüber hinaus ist er berechtigt, Daten zur Identitätsfeststellung zu ermitteln. Eine Vervielfältigung oder Aufbewahrung der Nachweise und der in den Nachweisen enthaltenen personenbezogenen Daten ist mit Ausnahme der Erhebung von Kontaktdaten gemäß §17 ebenso unzulässig wie die Verarbeitung der im Rahmen der Identitätsfeststellung erhobenen Daten. Dies gilt sinngemäß auch für Zertifikate nach §4b Abs1 EpiG.",
            "",
            "(6) Sofern in dieser Verordnung ein COVID-19-Präventionskonzept vorgeschrieben wird, ist ein dem Stand der Wissenschaft entsprechendes Konzept zur Minimierung des Infektionsrisikos mit SARS-CoV-2 auszuarbeiten und umzusetzen. Das COVID-19-Präventionskonzept hat insbesondere zu enthalten:",
            "1. spezifische Hygienemaßnahmen,",
            "2. Regelungen zum Verhalten bei Auftreten einer SARS-CoV-2-Infektion,",
            "3. Regelungen betreffend die Nutzung sanitärer Einrichtungen,",
            "4. gegebenenfalls Regelungen betreffend die Konsumation von Speisen und Getränken,",
            "5. Regelungen zur Steuerung der Personenströme und Regulierung der Anzahl der Personen,",
            "6. Regelungen betreffend Entzerrungsmaßnahmen, wie Absperrungen und Bodenmarkierungen,",
            "7. Vorgaben zur Schulung der Mitarbeiter in Bezug auf Hygienemaßnahmen und die Aufsicht der Durchführung eines SARS-CoV-2-Antigentests zur Eigenanwendung.",
            "",
            "(7) Als COVID-19-Beauftragte dürfen nur geeignete Personen bestellt werden. Voraussetzung für eine solche Eignung ist zumindest die Kenntnis des COVID-19-Präventionskonzepts sowie der örtlichen Gegebenheiten und der organisatorischen Abläufe. Der COVID-19-Beauftragte ist Ansprechperson für die Behörden und hat die Umsetzung des COVID-19-Präventionskonzepts zu überwachen.",
            "",
            "Inkrafttreten und Übergangsrecht",
            "",
            "§23. (1) Diese Verordnung tritt mit 1. November 2021 in Kraft und mit Ablauf des 30. November 2021 außer Kraft. Die §§12 bis 16 treten mit Ablauf des 28. November 2021 außer Kraft.",
            "",
            "(2 - 3) […]",
            "",
            "(4) Bereits vor Inkrafttreten dieser Verordnung ausgestellte ärztliche Bestätigungen über eine in den letzten sechs Monaten erfolgte und aktuell abgelaufene Infektion und Nachweise über neutralisierende Antikörper behalten für die jeweilige Dauer ihre Gültigkeit.",
            "",
            "(5) […]\"",
            "",
            "2. Die Verordnung des Bundesministers für Soziales, Gesundheit, Pflege und Konsumentenschutz, mit der die 3. COVID-19-Maßnahmenverordnung (3. COVID-19-MV) geändert wird (1. Novelle zur 3. COVID-19-Maßnahmenverordnung), BGBl II 456/2021, lautete auszugsweise (ohne die Hervorhebungen im Original):",
            "\"Auf Grund der §§3 Abs1, 4 Abs1, 4a Abs1 und 5 Abs1 des COVID-19-Maßnahmengesetzes, BGBl I Nr 12/2020, zuletzt geändert durch das Bundesgesetz BGBl I Nr 183/2021, wird verordnet:",
            "Die Verordnung betreffend Maßnahmen, die zur Bekämpfung der Verbreitung von COVID-19 ergriffen werden (3. COVID-19-Maßnahmenverordnung – 3. COVID-19-MV), BGBl II Nr 441/2021, wird wie folgt geändert:",
            "1. In §1 Abs2 Z4 wird der lita das Wort 'oder' angefügt; die litb und c entfallen und litd erhält die Literabezeichnung 'b)'.",
            "[…]",
            "10. Dem §23 werden folgende Abs6 und 7 angefügt:",
            "'(6) Zusammenkünfte gemäß §12 Abs3 gelten als bewilligt, wenn bereits vor Inkrafttreten der Verordnung BGBl II Nr 456/2021 eine Bewilligung vorlag und die Voraussetzungen des §12 Abs3 Z2 eingehalten werden.",
            "(7) §1 Abs2, §5 Abs2, §9 Abs1a und 1b, §12 Abs3 Z2 und Abs8, §13, §19 Abs11, §20 Abs2 und §23 Abs6 in der Fassung der Verordnung BGBl II Nr 456/2021 treten am 8. November 2021 in Kraft.' \"",
            "3. Mit der Verordnung des Bundesministers für Soziales, Gesundheit, Pflege und Konsumentenschutz, mit der die 3. COVID-19-Maßnahmenverordnung (3. COVID-19-MV) und die Verordnung BGBl II Nr 456/2021 geändert werden (2. Novelle zur 3. COVID-19-Maßnahmenverordnung), BGBl II 459/2021, wurde unter anderem in §23 Abs4 der 3. COVID-19-Maßnahmenverordnung die Wortfolge \"und Nachweise über neutralisierende Antikörper\" mit Wirkung vom 8. November 2021 aufgehoben und §1 der 2. Novelle zur 3. COVID-19-MV neu gefasst. ",
            "4. Die 3. COVID-19-Maßnahmenverordnung, BGBl II 441/2021, idF BGBl II 456/2021 und BGBl II 459/2021 wurde durch §24 Abs2 der Verordnung des Bundesministers für Soziales, Gesundheit, Pflege und Konsumentenschutz, mit der besondere Schutzmaßnahmen gegen die Verbreitung von COVID-19 getroffen werden (5. COVID-19-Schutzmaßnahmenverordnung – 5. COVID-19-SchuMaV), BGBl II 465/2021, mit Ablauf des 14. November 2021 aufgehoben. ",
            "5. Im Zeitpunkt der Antragstellung (21. Dezember 2021) stand die Verordnung des Bundesministers für Soziales, Gesundheit, Pflege und Konsumentenschutz, mit der besondere Schutzmaßnahmen gegen die Verbreitung von COVID-19 getroffen werden, 6. COVID-19-Schutzmaßnahmenverordnung, BGBl II 537/2021, in der Fassung BGBl II 556/2021 in Geltung. ",
            "III. Antragsvorbringen und Vorverfahren",
            "1. Die Antragstellerin bringt vor, am 16. Dezember 2020 positiv auf COVID-19 getestet und mit Bescheid des Magistrats der Stadt Wien vom 16. Dezember 2020 abgesondert worden zu sein. Bis zum 6. Juli 2021 habe sie als COVID-19-Genesene gegolten. Schon vor dem 6. Juli 2021, aber auch danach, habe sie sich in regelmäßigen Abständen einem Antikörpertest unterzogen, der stets das Vorhandensein neutralisierender Antikörper ergeben habe. Der zuletzt am 27. September 2021 in einem zugelassenen Labor durchgeführte Antikörpertest habe neutralisierende Antikörper im Umfang von 168 BAU/ml ergeben. Mit diesem Nachweis habe sie bis zum 8. November 2021 den \"3G-Nachweis\" erbringen können und \"somit ohne wesentliche Einschränkungen ihr Leben beruflich, privat und familiär ohne Einschränkungen wahrnehmen und auch über die Verwendung ihres Einkommens verfügen\" können. Seit dem 8. November 2021 sei dies \"schlagartig\" anders, weil ihr Nachweis über neutralisierende Antikörper nicht mehr als \"3G-Nachweis\" gelte. Dies, obwohl sie nach überwiegender medizinischer Literatur, aber auch nach Auskunft der von ihr konsultierten Ärzte gleich gut, wahrscheinlich aber besser als Geimpfte gegen eine Reinfektion und gegebenenfalls gegen schwere oder gar lebensbedrohliche Verläufe geschützt sei. In einem vom ORF ausgestrahlten, bei diesem aber nicht mehr abrufbaren Video habe die Virologin ******** gesagt, der Umstand, dass \"Genesene jetzt herausgefallen sind, habe pädagogische Gründe. Sicher käme es zu Re-Infektion bei Genesenen, aber das sei wohl auch bei Geimpften so. Aus wissenschaftlichen Gründen müsse das nicht sein, da[s] hätte mehr pädagogische Gründe um Genesene zu einer Impfung zu motivieren\". Aus einer schriftlichen Anfragebeantwortung des Bundesministers für Soziales, Gesundheit, Pflege und Konsumentenschutz (7546/AB, XXVII. GP) ergebe sich, dass eine Reinfektion Genesener in den ersten sechs Monaten nach der Erstinfektion häufiger als in den folgenden sechs Monaten auftreten würde. Die \"Erste Studie über Re-Infektionen in ganz Österreich\" der AGES vom 23. Februar 2021 komme zum Ergebnis, dass Personen mit einer durchgemachten SARS-CoV-2-Infektion einen ähnlich starken Schutz vor einer neuerlichen Infektion hätten wie Geimpfte. Die Innsbrucker Virologin von Laer werde in der Tageszeitung \"Der Standard\" vom 12. September 2021 dahingehend zitiert, dass der Immunschutz bei Genesenen sogar stabiler als bei Geimpften sei; bei Genesenen könne man noch nach 18 Monaten Antikörper nachweisen, nach der \"Pfizer-Impfung\" sinke der Titerwert um rund sechs Prozent pro Monat; ab dem von der Weltgesundheitsorganisation WHO standardisierten Antikörperwert von 100 BAU/ml sei ein Schutz gegeben. Die Deutsche Gesellschaft für Virologie halte in ihrer Stellungnahme vom 30. September 2021 fest, dass die nachgewiesene Dauer des Schutzes nach durchgemachten SARS-CoV-2-Infektionen mindestens ein Jahr betrage; aus immunologische Sicht sei von einer deutlich längeren Schutzdauer auszugehen, die aber auf Grund des begrenzten Beobachtungszeitraums noch nicht durch entsprechende Studien belegt sei; aufgrund der aktuellen Kenntnisse sollten Genesene bei Regelungen zur Pandemiebekämpfung den vollständig Geimpften zunächst für mindestens ein Jahr gleichgestellt werden. Die Schweiz würde dies auch berücksichtigen.",
            "Die 3. COVID-19-Maßnahmenverordnung und die 1. Novelle zu dieser Verordnung würden die Antragstellerin in den verfassungsgesetzlich gewährleisteten Rechten auf Gleichheit vor dem Gesetz, auf Unversehrtheit des Eigentums und auf Freizügigkeit verletzen. Durch diese Verordnungen sei die Antragstellerin seit 2. November 2021 durch die Zuordnung ihres Genesenenstatus zu \"3G\" statt zu \"2G\" sowie seit 8. November 2021 durch den auf sie anzuwendenden \"Lock-Down für Ungeimpfte\" unmittelbar, rechtlich und aktuell betroffen. Die Antragstellerin könne aufgrund der angefochtenen Bestimmungen seit 8. November 2021 mit ihrem Nachweis neutralisierender Antikörper die ihr zuvor möglichen Aktivitäten, wie den Besuch von Schwimmbädern und anderen Freizeiteinrichtungen, bestimmten Betriebsstätten des Handels oder Betriebsstätten der Gastronomie nicht mehr rechtmäßig setzen. Ihr Individualantrag sei der einzig zumutbare Weg, ihre Bedenken dem Verfassungsgerichtshof zu unterbreiten.",
            "In der Sache bringt die Antragstellerin – auf das Wesentliche zusammengefasst – vor, schon die Einordnung eines Nachweises über neutralisierende Antikörper unter \"3G\" statt zumindest unter \"2G\" sei unsachlich, weil damit Genesene trotz nachweislich vorhandener neutralisierender Antikörper unsachlich anders als Genese innerhalb von 180 Tagen nach der Infektion behandelt würden. Auch die Streichung der Möglichkeit eines Nachweises über neutralisierende Antikörper in §1 Abs2 Z4 litc der 3. COVID-19-Maßnahmenverordnung durch die erste Novelle zu dieser Verordnung, BGBl II 456/2021, sei unsachlich. Schließlich sei unsachlich, dass der Nachweis neutralisierender Antikörper in der 3. COVID-19-Maßnahmenverordnung im Zeitraum vom 8. November 2021 bis zum 22. November 2021 anders als in der COVID-19-Einreiseverordnung behandelt worden sei, welche diesen Nachweis in dieser Zeit noch akzeptiert habe.",
            "2. Der Bundesminister für Soziales, Gesundheit, Pflege und Konsumentenschutz als verordnungserlassende Behörde hat eine Äußerung erstattet, in der die Zulässigkeit des Antrages bestritten und im Übrigen den Bedenken in der Sache entgegengetreten wird.",
            "IV. Zulässigkeit",
            "1. Der Antrag ist nicht zulässig.",
            "2. Gemäß Art139 Abs1 Z3 B‐VG erkennt der Verfassungsgerichtshof über Gesetzwidrigkeit von Verordnungen auf Antrag einer Person, die unmittelbar durch diese Gesetzwidrigkeit in ihren Rechten verletzt zu sein behauptet, wenn die Verordnung ohne Fällung einer gerichtlichen Entscheidung oder ohne Erlassung eines Bescheides für diese Person wirksam geworden ist.",
            "Voraussetzung der Antragslegitimation gemäß Art139 Abs1 Z3 B-VG ist einerseits, dass der Antragsteller behauptet, unmittelbar durch die angefochtene Verordnung – im Hinblick auf deren Gesetzwidrigkeit – in seinen Rechten verletzt worden zu sein, dann aber auch, dass die Verordnung für den Antragsteller tatsächlich, und zwar ohne Fällung einer gerichtlichen Entscheidung oder ohne Erlassung eines Bescheides wirksam geworden ist. Grundlegende Voraussetzung der Antragslegitimation ist, dass die Verordnung in die Rechtssphäre des Antragstellers nachteilig eingreift und diese – im Falle ihrer Gesetzwidrigkeit – verletzt.",
            "Es ist darüber hinaus erforderlich, dass die Verordnung selbst tatsächlich in die Rechtssphäre des Antragstellers unmittelbar eingreift. Ein derartiger Eingriff ist nur dann anzunehmen, wenn dieser nach Art und Ausmaß durch die Verordnung selbst eindeutig bestimmt ist, wenn er die (rechtlich geschützten) Interessen des Antragstellers nicht bloß potentiell, sondern aktuell beeinträchtigt und wenn dem Antragsteller kein anderer zumutbarer Weg zur Abwehr des – behaupteterweise – rechtswidrigen Eingriffes zur Verfügung steht (VfSlg 13.944/1994, 15.234/1998, 15.947/2000).",
            "2.1. Wird eine Verordnung mit Individualantrag angefochten, die im Zeitpunkt der Antragstellung bereits außer Kraft getreten ist, fehlt es idR an der Zulässigkeitsvoraussetzung einer – aktuellen – Beeinträchtigung von rechtlich geschützten Interessen des Antragstellers im Zeitpunkt der Antragstellung (vgl VfGH 1.10.2020, G272/2020; 29.9.2021, V571/2020; 16.12.2021, V302/2021), sofern der Antragsteller nicht das Vorliegen besonderer Umstände darlegen kann, die aus rechtsstaatlichen Gründen die Zulässigkeit der Stellung eines Individualantrages auf Verordnungsprüfung auch noch nach Außerkrafttreten der Verordnung verlangen. ",
            "2.2. Nach der ständigen Rechtsprechung des Verfassungsgerichtshofes ist ferner die Anfechtung einer Novellierungsanordnung nur dann zulässig, wenn eine Bestimmung durch die betreffende Novelle aufgehoben worden ist und sich das Bedenken gegen diese Aufhebung richtet und die Gesetz- oder Verfassungswidrigkeit auf keinem anderen Wege beseitigt werden kann (vgl zB VfSlg 19.658/2012 und 20.213/2017 sowie zuletzt VfGH 12.6.2919, G34/2019 ua; 13.12.2019, G67/2019 ua; 21.9.2020, V507/2020; 14.6.2021, V537/2020).",
            "3. Mit ihrem Hauptantrag begehrt die Antragstellerin, der Verfassungsgerichtshof möge eine Novellierungsanordnung zu einer im Antragszeitpunkt bereits außer Kraft getretenen Verordnung (Antragspunkt 1) sowie eine weitere Bestimmung einer im Zeitpunkt der Antragstellung bereits außer Kraft getretenen Verordnung (Antragspunkt 2) aufheben. Da diese Bestimmungen die Antragstellerin schon im Zeitpunkt der Antragstellung nicht mehr in ihrer Rechtssphäre berühren konnten (sondern allenfalls die im Zeitpunkt der Antragstellung geltende Nachfolgeverordnung, soweit sie die von der Antragstellerin als sachlich geboten erachtete Ausnahme nicht enthalten haben sollte) und auch keine besonderen Umstände geltend gemacht wurden, warum die bereits außer Kraft getretene Bestimmung für die Antragstellerin nach wie vor eine nachteilige Wirkung entfaltet, ist der Hauptantrag (Antragspunkte 1 und 2) schon aus diesem Grund unzulässig (hingewiesen sei noch darauf, dass der mit Antragspunkt 2 des Weiteren begehrte Ausspruch auf Einfügung einer Wortfolge in einen Verordnungstext nicht mehr vom Verordnungskontrollauftrag des Verfassungsgerichtshofes gedeckt und daher ebenfalls unzulässig ist). Entsprechendes gilt für den (als \"4.\" nummerierten) Eventualantrag, der daher ebenfalls als unzulässig zurückzuweisen ist. ",
            "V. Ergebnis",
            "1. Der Antrag wird als unzulässig zurückgewiesen.",
            "2. Dies konnte gemäß §19 Abs3 Z2 lite VfGG ohne mündliche Verhandlung in nichtöffentlicher Sitzung beschlossen werden."
        ]
        return ret_val

    def test_add_valid_html_decision(self):
        # arrange 
        html_file = Path.cwd() / "tests/test_tagger/test_data/JFT_20220223_21V00315_00.html"
        if not html_file.exists():
            raise FileNotFoundError(f"File {html_file} does not exist, check your test data files")
        test_db_path = Path.cwd() / "tests/test_tagger/test_data/"
        test_db = doc_db.DBCollection(test_db_path)

        # act
        test_db.add_html_decision(html_file)

        # assert
        try: 
            assert (test_db.db_path.db_path_judikatur / "vfgh/2022/JFT_20220223_21V00315_00.json").exists()
            json_data = json.loads((test_db.db_path.db_path_judikatur / "vfgh/2022/JFT_20220223_21V00315_00.json").read_text(encoding="utf-8"))
            assert json_data["document_id"] == "JFT_20220223_21V00315_00"
            # check first paragraph of db entry 
            assert json_data["document_body"][0]["text"] == "Begründung"
            for para_actual, para_expected in zip(json_data["document_body"], self.__get_list_of_para_text()):
                assert para_actual["text"] == para_expected
            for para in json_data["document_body"]:
                assert para["annotations"] == []

        # cleanup
        finally: 
            (test_db.db_path.db_path_judikatur / "vfgh/2022/JFT_20220223_21V00315_00.json").unlink()
            (test_db.db_path.db_path_judikatur / "vfgh/2022").rmdir()
