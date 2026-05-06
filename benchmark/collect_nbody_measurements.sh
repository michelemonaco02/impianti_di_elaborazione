#!/bin/bash

# ==============================================================================
# collect_nbody_measurements.sh
# ==============================================================================
#
# Scopo:
#   Questo script esegue il benchmark n-body per diverse configurazioni di carico
#   e salva i tempi di esecuzione in un file CSV.
#
# Contesto dell'elaborato:
#   Vogliamo confrontare statisticamente le prestazioni di due macchine diverse.
#   Per farlo, dobbiamo raccogliere più osservazioni del tempo di esecuzione del
#   benchmark su ciascuna macchina e per ciascuna configurazione.
#
#   In questo script:
#     - una singola esecuzione del programma nbody corrisponde a una osservazione;
#     - non vengono fatte medie di più ripetizioni;
#     - per ogni configurazione vengono raccolte OBSERVATIONS osservazioni;
#     - i dati raccolti saranno poi usati per calcolare:
#         * media campionaria;
#         * deviazione standard campionaria;
#         * numerosità campionaria richiesta;
#         * intervalli di confidenza;
#         * test statistici.
#
# Requisiti:
#   1. Il file eseguibile ./nbody deve essere già stato compilato.
#      Esempio:
#        gcc -O3 nbody.c -o nbody -lm
#
#   2. Il comando taskset deve essere disponibile.
#      Su Ubuntu di solito è già presente. In caso contrario:
#        sudo apt install util-linux
#
#   3. Lo script deve essere eseguito nella stessa directory in cui si trova ./nbody.
#
# Perché usiamo taskset:
#   taskset -c 0 vincola il processo al core logico 0.
#   Questo riduce la variabilità dovuta alla migrazione del processo tra core diversi.
#
# Output:
#   Lo script produce un file CSV chiamato:
#
#        misure_<PC_NAME>.csv
#
#   con colonne:
#
#        pc,configurazione,osservazione,tempo_s,energia_iniziale,energia_finale
#
#   Dove:
#     - pc: nome della macchina, ad esempio PC1 o PC2;
#     - configurazione: numero di iterazioni del benchmark n-body;
#     - osservazione: indice dell'osservazione, da 1 a OBSERVATIONS;
#     - tempo_s: tempo di esecuzione in secondi;
#     - energia_iniziale: energia del sistema prima della simulazione;
#     - energia_finale: energia del sistema dopo la simulazione.
#
# Nota importante:
#   Nel nostro nbody.c il parametro passato da terminale NON rappresenta il numero
#   di corpi simulati. Il numero di corpi è fissato nel codice.
#   Il parametro rappresenta invece il numero di iterazioni temporali della
#   simulazione.
#
#   Esempio:
#        ./nbody 1000000
#
#   significa:
#        esegui 1.000.000 di iterazioni della simulazione n-body.
#
#   Non significa:
#        simula 1.000.000 di corpi.
#
# ==============================================================================


# ------------------------------------------------------------------------------
# Nome della macchina.
#
# Modificare questo valore prima di eseguire lo script sull'altra macchina.
#
# Esempio:
#   sulla prima macchina:   PC_NAME="PC1"
#   sulla seconda macchina: PC_NAME="PC2"
# ------------------------------------------------------------------------------

PC_NAME="PC1"


# ------------------------------------------------------------------------------
# Nome del file CSV di output.
# ------------------------------------------------------------------------------

OUTPUT="misure_${PC_NAME}.csv"


# ------------------------------------------------------------------------------
# Numero di osservazioni da raccogliere per ogni configurazione.
#
# In questo caso usiamo 40 osservazioni, in linea con l'impostazione che vogliamo
# adottare nell'elaborato.
#
# Ogni osservazione corrisponde a una singola esecuzione di ./nbody.
# ------------------------------------------------------------------------------

OBSERVATIONS=40


# ------------------------------------------------------------------------------
# Configurazioni del benchmark.
#
# Ogni valore rappresenta il numero di iterazioni temporali della simulazione.
#
# Questi valori possono essere modificati dopo una calibrazione iniziale.
# Se 10000 è troppo veloce e produce tempi molto piccoli, conviene aumentare
# i valori, ad esempio 100000, 1000000, 10000000.
# ------------------------------------------------------------------------------

CONFIGS=(
  10000
  100000
  1000000
)


# ------------------------------------------------------------------------------
# Controlli preliminari.
# ------------------------------------------------------------------------------

if [ ! -f "./nbody" ]; then
  echo "Errore: eseguibile ./nbody non trovato."
  echo "Compila prima il benchmark con:"
  echo "  gcc -O3 nbody.c -o nbody -lm"
  exit 1
fi

if [ ! -x "./nbody" ]; then
  echo "Errore: ./nbody esiste ma non è eseguibile."
  echo "Rendi il file eseguibile con:"
  echo "  chmod +x nbody"
  exit 1
fi

if ! command -v taskset > /dev/null 2>&1; then
  echo "Errore: comando taskset non trovato."
  echo "Installa util-linux con:"
  echo "  sudo apt install util-linux"
  exit 1
fi


# ------------------------------------------------------------------------------
# Creazione del file CSV.
# ------------------------------------------------------------------------------

echo "pc,configurazione,osservazione,tempo_s,energia_iniziale,energia_finale" > "$OUTPUT"


# ------------------------------------------------------------------------------
# Esecuzione del benchmark.
#
# Per ogni configurazione:
#   - eseguiamo ./nbody CONFIG per OBSERVATIONS volte;
#   - salviamo una riga nel CSV per ogni esecuzione;
#   - ogni riga rappresenta una osservazione statistica.
# ------------------------------------------------------------------------------

for CONFIG in "${CONFIGS[@]}"; do
  echo "============================================================"
  echo "Configurazione: ${CONFIG} iterazioni"
  echo "Osservazioni da raccogliere: ${OBSERVATIONS}"
  echo "============================================================"

  for OBS in $(seq 1 "$OBSERVATIONS"); do

    # Esecuzione vincolata al core logico 0.
    #
    # Il programma nbody stampa una riga nel formato:
    #   iterations,time_seconds,initial_energy,final_energy
    #
    # Esempio:
    #   1000000,0.842391204,-0.169075164,-0.169087605

    RESULT=$(taskset -c 0 ./nbody "$CONFIG")

    ITERATIONS=$(echo "$RESULT" | cut -d',' -f1)
    TEMPO=$(echo "$RESULT" | cut -d',' -f2)
    ENERGIA_INIZIALE=$(echo "$RESULT" | cut -d',' -f3)
    ENERGIA_FINALE=$(echo "$RESULT" | cut -d',' -f4)

    # Controllo minimo sul formato dell'output.
    if [ -z "$TEMPO" ] || [ -z "$ENERGIA_INIZIALE" ] || [ -z "$ENERGIA_FINALE" ]; then
      echo "Errore: output inatteso da ./nbody:"
      echo "$RESULT"
      exit 1
    fi

    echo "$PC_NAME,$ITERATIONS,$OBS,$TEMPO,$ENERGIA_INIZIALE,$ENERGIA_FINALE" >> "$OUTPUT"

    echo "PC=${PC_NAME} | config=${ITERATIONS} | osservazione=${OBS}/${OBSERVATIONS} | tempo=${TEMPO}s"
  done

  echo "Completata configurazione: ${CONFIG} iterazioni"
  echo
done


# ------------------------------------------------------------------------------
# Fine.
# ------------------------------------------------------------------------------

echo "Benchmark completato."
echo "File CSV generato: $OUTPUT"
echo
echo "Prossimo passo:"
echo "  Copia i file misure_PC1.csv e misure_PC2.csv nella stessa cartella"
echo "  e lancia lo script Python di analisi per calcolare media, deviazione standard"
echo "  e numerosità campionaria richiesta."