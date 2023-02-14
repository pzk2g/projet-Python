#!/usr/bin/python3
import hashlib
import sys, os, glob, shutil
import socket

#nombre maximale caractères recue du serveur
SIZE = 4096
CODAGE = 'utf8'
#radical du nom des fichiers .txt des blockchain construites
BLOCKCHAIN = "Ma_Blockchain"

#numero de port pour la communication avec le client
numero_port_serveur = 7777

#liste qui contiendra la liste des informations d'un bloc
liste_bloc = []

#Liste qui contiendra la liste des blocs de transactions d'une blockchain
#récue du client
liste_fichier = []

"""
fonction vérification
    retourne vrai si la valeur alétoire du bloc courant est bien liée
    au hash du bloc précédent faux sinon
@param numero_bloc_prec numéro du bloc précédent
@param transaction_prec liste des transactions du bloc précédent
@param hash_bloc hash du bloc courant
@param hash_bloc_prec hash du bloc précédent
@param valeur_aleatoire_prec la valeur alétoire du bloc précédent
"""
def verification(numero_bloc_prec, transaction_prec, hash_bloc, hash_bloc_prec, valeur_aleatoire_prec):
    puzzle = numero_bloc_prec + transaction_prec + hash_bloc_prec + valeur_aleatoire_prec
    return (hashlib.sha256(puzzle.encode()).hexdigest() == hash_bloc)

"""
fonction blockchain
    retourne 1 si une blockchain a bien été construite -1 sinon
@param numero_blockchain numéro de la blockchain construite et enregistrée
    dans le fichier Ma_Blockchain(numero_blockchain).txt
    On numérote les blockchain pour avoir un historique, pour
    pas que le construction la contruction d'une nouvelle écrase la précédente
"""
def blockchain(numero_blockchain):
    """
    on connait la structure d'un bloc de transaction:
        -   numero_bloc
        -   transaction 1
            transaction 2
            ...
            transaction n
        -   hash du bloc précédent
        -   valeur aléatoire trouvée
    """
    ma_blockchain = BLOCKCHAIN + str(numero_blockchain) + ".txt"
    try:
    	fichier_blockchain = open(ma_blockchain, "w")
    except Exception as e:
    	print(e.args)
    #Il y a toujours au moins un fichier (bloc de transaction) envoyé au serveur
    if len(liste_fichier) == 1:
        longueur = len(liste_bloc[0])
        numero_bloc = liste_bloc[0][0]
        transaction = "\n".join(transactions for transactions in liste_bloc[0][1:longueur-2])
        valeur_aleatoire = liste_bloc[0][longueur-1]
        hash_bloc = liste_bloc[0][longueur-2]

        fichier_blockchain.write(numero_bloc + "\n" + transaction + "\n" + valeur_aleatoire + "\n" + hash_bloc)
        fichier_blockchain.close()

        return ma_blockchain

    for i in range(len(liste_fichier) - 1):
        longueur = len(liste_bloc[i])
        longueur_prec = len(liste_bloc[i + 1])

        numero_bloc = liste_bloc[i][0]
        numero_bloc_prec = liste_bloc[i + 1][0]

        transaction = "".join([transactions for transactions in liste_bloc[i][1:longueur-2]])
        transaction_prec = "".join([transactions for transactions in liste_bloc[i + 1][1:longueur_prec-2]])

        transaction_blockchain = "\n".join([transactions for transactions in liste_bloc[i][1:longueur-2]])
        transaction_prec_blockchain = "\n".join([transactions for transactions in liste_bloc[i + 1][1:longueur_prec-2]])

        valeur_aleatoire = liste_bloc[i][longueur-1]
        valeur_aleatoire_prec = liste_bloc[i + 1][longueur_prec-1]

        hash_bloc = liste_bloc[i][longueur-2]
        hash_bloc_prec = liste_bloc[i + 1][longueur_prec-2]

        if(verification(numero_bloc_prec, transaction_prec, hash_bloc, hash_bloc_prec, valeur_aleatoire_prec)):
            fichier_blockchain.write(numero_bloc + "\n"
                                    + transaction_blockchain + "\n"
                                    + valeur_aleatoire + "\n" + hash_bloc
                                    + "\n\n" + "^"*70 + "\n")
            if(i == len(liste_fichier) - 2):
                fichier_blockchain.write(numero_bloc_prec + "\n"
                                        + transaction_prec_blockchain + "\n"
                                        + valeur_aleatoire_prec + "\n"
                                        + hash_bloc_prec
                                        + "\n" + "^"*80 + "\n")
        else:
            return -1

    fichier_blockchain.close()
    return ma_blockchain

#Important pour déplacer des fichiers (indésirables) qui ne nous servent plus
#et pouvant faire "bugger" le serveur
#A Changer Selon Vos Repertoires
source = '/home/prinz/Documents/blockchain'
destination = '/home/prinz/Documents/blockchain/RESEAU'

"""
Communication  avec le client (qui a construit la blockchain)
"""
connexion = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
connexion.bind(('', numero_port_serveur))
connexion.listen(socket.SOMAXCONN)

(communication_client, tsap_client) = connexion.accept()
print('Connexion du client depuis :', tsap_client)

while 1:
    numero_blockchain = 0
    ligne = communication_client.recv(SIZE)
    if not ligne:
        break
    if ligne == bytes("1", CODAGE):
        communication_client.sendall(bytes("\nServeur en attente des blocs...", CODAGE))
    elif str(ligne, CODAGE).endswith(".txt"):
        liste_fichier.append(str(ligne, CODAGE))
        communication_client.sendall(bytes("> " + str(ligne) + " Bien Recue <\n", CODAGE))

    elif ligne == bytes("y".casefold(), CODAGE):
        message = "xxxxxxxxxxxxx ECHEC DE CREATION DE VOTRE BLOCKCHAIN, ELLE EST COMPROMISE ! PARTAGE ANNULE ! xxxxxxxxxxxxxx"
        #on veut vérifier la validité de la blockchain en vérifiant le bloc
        #actuel est bien lié au bloc précédent
        liste_fichier.reverse()
        for bloc in liste_fichier :
            try:
            	fichier = open(bloc, "r")
            except Exception as e:
            	print(e.args)

            liste_lignes = fichier.readlines()
            lignes = [ligne.rstrip('\n') for ligne in liste_lignes]
            liste_bloc.append(lignes)
            fichier.close()

        ma_blockchain = blockchain(numero_blockchain)
        if ma_blockchain != -1:
            try:
            	fichier = open(ma_blockchain, "r")
            except Exception as e:
            	print(e.args)

            lignes = fichier.readlines()
            resume = "".join(lignes)
            message = ">>>>>>>>>>>>> VOTRE BLOCKCHAIN A ETE CONSTRUITE ET PARTAGE AVEC SUCCES ! <<<<<<<<<<<<<"
            voici = "\n\n >>>>>>>>>>>>>>>>>>>>>>>>>>>>> RESUME : <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n"
            decor = "\n" + "$"*100 + "\n"
            message =  message + voici + decor + resume + decor
            """
            il faut vider la liste_fichier qui contient la liste de blocs
            de transactios recue du client
            Il faut également vider la liste contenant les blocs de transactions une fois
            la blockchain construite pour permettre de miner une nouvelle
            chaine de bloc quand on est toujours connecté au client,c'est à
            dire sans avoir à relancer la connection à chaque fois qu'on veuut
            construire une nouvelle blockchain
            """
            liste_fichier.clear()
            liste_bloc.clear()
            fichier.close()

        #le numero_blockchain augmente chaque fois qu'on veut créer une nouvelle blockchain
        numero_blockchain += 1
        communication_client.sendall(bytes(message, CODAGE))
        allfiles = glob.glob(os.path.join(source, '*.txt*'), recursive=True)
        print("Fichier à déplacer", allfiles)

        #On déplace (partage) les blocs et la blockchain de ces blocs dans (avec le réseau)
        #un autre repertoire. Car si on les laisse il yaura une modification
        #c'est à dire une réecriture dans des fichier (qui sont par exemple ouvert en mode ajout )
        #ce qui entrenerait la compomission immédiat de la blockchain
        for file_path in allfiles:
        	dst_path = os.path.join(destination, os.path.basename(file_path))
        	shutil.move(file_path, dst_path)
        	print(f"Moved {file_path} -> {dst_path}")

    else:
        communication_client.sendall(bytes("BLOCKCHAIN ANNULE \nMerci, A Bientôt !", CODAGE))
        break

communication_client.close()
connexion.close()
