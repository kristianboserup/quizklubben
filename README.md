# Quizklubben

En lokal almenvidenquiz til en quizaften med venner. Quizmasteren styrer det hele fra sin computer.

- Seks kategorier: Geografi, Underholdning, Historie, Kunst og litteratur, Natur og videnskab samt Sport og fritid.
- Let, Mellem, Svær eller Blandet. Banken indeholder 90 spørgsmål; en standardquiz har 30 spørgsmål.
- Frie svar med Afgiv svar, automatisk pointgivning og manuel godkendelse.
- Kategoriresultater, delte placeringer og samlet vinder.
- Automatisk lokal JSON-gemning, sikkerhedskopier og fuld genstart.

## Spil online

[Åbn Quizklubben](https://kristianboserup.github.io/quizklubben/)

Onlineudgaven gemmer deltagere og resultater i browseren på din egen enhed. Der sendes ingen quizresultater til GitHub. Brug JSON-sikkerhedskopi for at flytte en quiz til en anden computer. Den lokale Python-udgave gemmer stadig automatisk i en JSON-fil på disken.

## Start lokalt

Python 3.9 eller nyere kræves. Ingen ekstra Python-pakker.

På Windows: dobbeltklik på `Start-Quiz.cmd`.

På Windows, macOS eller Linux kan serveren også startes fra mappen med:

```sh
python server.py
```

Brug `python3 server.py`, hvis Python hedder `python3` på din computer.
Åbn derefter http://127.0.0.1:8765. Serveren lytter kun på din egen computer.

Alternativt kan `quiz.html` åbnes direkte i browseren. Så gemmes data i browserlager i stedet for i en lokal JSON-fil.

## Spil

Vælg sværhedsgrad, tilføj deltagere og tryk Start quiz. Skriv hver deltagers svar og tryk Afgiv svar. Et korrekt svar giver 1 point; forkerte og manglende svar giver 0. Godkend svar kan bruges ved en korrekt formulering, automatikken ikke genkender. Gentagen bedømmelse giver ikke dobbelt point.

Efter fem spørgsmål vises kategoriens resultat. Fortsæt til næste kategori, og kår aftenens vinder efter den sjette kategori.

## Gemning

Den aktive quiz gemmes i `data/quiz-state.json`. Vent på Gemt i JSON-fil, før du lukker. Brug én aktiv quizmasterfane for at undgå konflikter. Under Indstillinger kan du hente og indlæse en sikkerhedskopi.

Genstart quiz rydder alle aktive quizdata efter bekræftelse, inklusive deltagere, egne spørgsmål, svar og point. Den starter en ren standardquiz.

## Filer

- `quiz.html`: app, design og spørgsmålsbank.
- `server.py`: lokal HTTP-server og JSON-lagring.
- `Start-Quiz.cmd`: Windows-startfil.
- `Sporgsmalskilder.md`: udvalgte faktatjek af spørgsmål.

Personlige quizdata, logs og lokale sikkerhedskopier er udeladt og ignoreres af Git.
