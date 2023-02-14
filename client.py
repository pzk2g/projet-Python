import hashlib, re, socket

CODAGE = 'utf8'
#nombre maximale caractères recue du serveur
SIZE = 4096
#nombre de zéro pour la difficulté de trouver la valeur aléatoire
ZERO = 1
#nombre ce caractères des noms des participants
FORMAT = 32
#limite où la recherche de la valeur aléatoire s'arrète si elle n'est pas trouvée
LIMITE = 1_000_000_000
#radical du nom des fichiers .txt des blocs de transactions
BLOCNAME = "BLOC"
OPTION = "\n-> Oui : Tapez 1\n-> Non : Tapez 0\n--> "

#numero de port pour la communication avec le serveur
numero_port_serveur = 7777

#Liste qui contiendra la liste des blocs de transactions d'une blockchain
#envoyé au serveur
liste_bloc = []

"""
fonction nouvellle_transaction
    retourne 1 si la nouvellle transaction est bien notée dans fichier, -1 sinon
@param reponse un entier (0 ou 1)
    1 si on accepte d'entrer une nouvelle transaction 0 sinon
@param fichier nom de fichier(bloc) .txt ou sera notée la nouvelle transaction
"""
def nouvellle_transaction(reponse, fichier):
    if reponse == "0":
        return -1
    while(reponse == "1"):
        print("+"*29, " NOUVELLE TRANSACTION ", "+"*29)
        emetteur = input("Nom de l'emetteur : ")
        recepteur = input("Nom du recepteur : ")
        montant = input("Montant de la transaction (en euros): ")

        #le nom des participants est enregistrée sur FORMAT = 32 caractères,
        #s'il y en moins, on complète leur noms de petits points
        #On ne vérife pas la validité des noms, même un nom vide accepté
        #si les participants souhaitent être parfaitements anonymes.
        #Oui c'est possible :)

        format_emetteur = FORMAT - len(emetteur)
        format_recepteur = FORMAT - len(recepteur)

        #Mais le format réel d'une somme d'argent (en euros) est vérifié
        re_montant = re.compile(r'^(\d*(\d\.?|\.\d{1,2}))$')

        while not re_montant.search(montant):
            print(">> Montant mal écrit, vérifiez...")
            montant = input("Montant de la transaction : ")

        fichier.write(emetteur + "."*format_emetteur
                      + " donne " + montant + "€"
                      + " à " + recepteur + "."*format_recepteur + "\n")
        reponse = input("\nNouvelle Transaction ?" + OPTION)
        while reponse != "1" and reponse != "0":
            reponse = input("\nNouvelle Transaction ?" + OPTION)

    print("-"*30, "FIN DE TRANSACTION ", "-"*30)
    return 1

"""
fonction bloc_initial
    retourn 1 si le bloc initial (le bloc 0) est bien enregistré -1 sinon
"""
def bloc_initial():
    succes = -1
    outfile = BLOCNAME + "0.txt"
    try:
    	fichier = open(outfile, "w")
    except Exception as e:
    	print(e.args)

    liste_bloc.append(outfile)

    fichier.write(BLOCNAME + "-0\n")

    reponse = input("Nouvelle Transaction ?" + OPTION)
    while reponse != "1" and reponse != "0":
        reponse = input("Nouvelle Transaction ?" + OPTION)

    if(reponse == "1"):
        succes = nouvellle_transaction(reponse, fichier)
        fichier.write("0"*64 + '\n')

    fichier.close()

    return succes

"""
fonction puzzle
    retoune
        - la valeur aléatoire calculée à partir des informations dans filename
        - le hash du bloc enregistré dans filename avec le nombre de ZERO voulu
        - -1 pour chacune de ces résultat si il ne sont pas trouvés
    On aurait pu ne retourner que la valeur aléatoire mais on souhaitait garder
    une trace du hash.
    cete fonction nous ait surtout utile pour écrire la valeur aléatoire trouvée
    à la fin du bloc enregisté dans filename
@param filename fichier .txt où est notée les informations d'un bloc
"""
def puzzle(filename):
    init_puzzle = ""
    try:
    	fichier = open(filename, "r")
    except Exception as e:
    	print(e.args)

    lignes = fichier.readlines()
    lignes = [ligne.rstrip('\n') for ligne in lignes]
    #On réupère toute les informations dans filename
    #ces informations sont pour l'instant:
    #le numéro du bloc actuel de transactios
    #la liste des transactios
    #le hash du bloc précédent. le hash du bloc initial est 0 par convention
    init_puzzle = "".join(lignes)
    puzzle = init_puzzle

    for valeur in range(LIMITE):
        puzzle = init_puzzle + str(valeur)
        hash = hashlib.sha256(puzzle.encode()).hexdigest()
        if hash.startswith("0"*ZERO):
            fichier = open(filename, 'a')

            #une fois trouvée la valeur aléatoire du bloc actuel trouvée,
            #on l'ajoute à la fin du bloc actuel enregisté dans filename
            fichier.write(str(valeur) + '\n')

            return valeur, hash
    fichier.close()

    return -1, -1

"""
fonction new_bloc
    retoune 1 si un nouveau bloc de transactions est bien enregistré, -1 sinon
"""
def new_bloc():
    #nous permet de controler si le bloc initial est bien crée
    #avant de créer les blocs suivant, sinon on arrète tout
    initial = -1
    #nous permet de numéroter les blocs
    numero = 0

    valeur_precedente = 0
    hash_bloc_precedent = 0

    reponse_bloc = input("\nNOUVEAU BLOC DE TRANSACTIONS ?" + OPTION)
    while reponse_bloc != "1" and reponse_bloc != "0":
        reponse_bloc = input("\nNOUVEAU BLOC DE TRANSACTIONS ?" + OPTION)

    if(reponse_bloc == "1") :
        print("+"*80, "\n" + "+", " "*29, "CREATION DU BLOC-0", " "*29, "+\n", "+"*80)
        initial = bloc_initial()

        #Par appel de la fonction puzzle,
        #on récupère le hash du bloc 0 (pour le bloc suivant)
        #et on écrit sa valeur alétoire trouvée à la fin du bloc
        valeur_precedente, hash_bloc_precedent  = puzzle(BLOCNAME + "0.txt")
    else :
        print("\nPas De Nouveau Bloc de Transactions")
        return -1
    if(initial == 1):
        reponse_bloc = input("\nNOUVEAU BLOC DE TRANSACTIONS ?" + OPTION)
        while reponse_bloc != "1" and reponse_bloc != "0":
            reponse_bloc = input("\nNOUVEAU BLOC DE TRANSACTIONS ?" + OPTION)

        while(reponse_bloc == "1"):

            numero += 1
            print("+"*80, "\n", "+", " "*29, "CREATION DU BLOC-", numero, " "*29, "+\n", "+"*80)

            filename_precedant = BLOCNAME + str(numero - 1) + ".txt"

            reponse_transaction = input("\nNouvelle Transaction ?" + OPTION)
            while reponse_transaction != "1" and reponse_transaction != "0":
                reponse_transaction = input("\nNouvelle transaction ?" + OPTION)

            if(reponse_transaction != "1") :
                print("Pas de Nouveau Bloc de Transactions, car vous n'avez pas enregistrée de nouvelle transaction")
                return initial

            new_f = BLOCNAME + str(numero) + ".txt"
            try:
            	fichier = open(new_f, "w")
            except Exception as e:
            	print(e.args)
            liste_bloc.append(new_f)
            #fichier.write("Bloc " + numero_bloc)
            fichier.write(BLOCNAME + "-" + str(numero) + '\n')
            nouvellle_transaction(reponse_transaction, fichier)
            fichier.write(str(hash_bloc_precedent) + '\n')
            fichier.close()

            #Par appel de la fonction puzzle,
            #on récupère le hash du bloc actuel (pour le bloc suivant)
            #et on écrit sa valeur alétoire trouvée à la fin du bloc
            valeur_precedente, hash_bloc_precedent = puzzle(new_f)
            reponse_bloc = input("\nNOUVEAU BLOC DE TRANSACTIONS ?" + OPTION)
            while reponse_bloc != "1" and reponse_bloc != "0":
                reponse_bloc = input("\nNOUVEAU BLOC DE TRANSACTIONS ?" + OPTION)


        print("\n----------BLOC DE TRANSACTIONS TERMINE---------------")
    else:
        return -1

    return initial


"""
Communication avec le serveur pour la vérification et la validation de la blockchain
créée par ici le client avant le partage de la blockchain par le serveur dans le "réseau"
"""
adresse_serveur = 'localhost'
connexion = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
connexion.connect((socket.gethostbyname(adresse_serveur), numero_port_serveur))

while 1:
    reponse = input("\nCréer une nouvelle BLOCKCHAIN ?" + OPTION)
    while reponse != "1" and reponse != "0" :
        reponse = input("\nCréer une nouvelle BLOCKCHAIN ?" + OPTION)
    while reponse == "1" :

        retour = new_bloc()
        if retour != 1:
            print("AUCUN BLOC DE TRANSACTION CREE, PAS DE BLOCKCHAIN ! \n CREEZ-EN 1 POUR COMMENCER !")
            break

        reponse = input("Voulez-vous partagez votre BLOCKCHAIN ?" + OPTION)
        while reponse != "1" and reponse != "0" :
            reponse = input("Voulez-vous partagez votre BLOCKCHAIN ?" + OPTION)

        if reponse == "0" :
            print("Très bien, Merci A Bientôt !")
            break

        ligne = bytes(reponse, CODAGE)

        connexion.sendall(ligne)
        print(connexion.recv(SIZE), CODAGE)
        print("\nEnvoie de vos blocs enregistrés en cours...")
        for bloc in liste_bloc:
            ligne = bytes(bloc, CODAGE)
            connexion.sendall(ligne)
            print("> " + bloc + " envoyé")
            message = connexion.recv(SIZE)
            print(str(message, CODAGE))

        reponse = input("Confirmer le partage de votre BLOCKCHAIN ?\n-> Oui : Tapez 'Y'\n-> Non : Tapez 'N'\n-->")
        while reponse != "Y".casefold() and reponse != "N".casefold() :
            reponse = input("Confirmer le partage de votre BLOCKCHAIN ?\n-> Oui : Tapez 'Y'\n-> Non : Tapez 'N'\n-->")
        if reponse == "0":
            print("Partage de BLOCKCHAIN ANNULE !\n Merci, A Bientôt !")
            break
        ligne = bytes(reponse,CODAGE)
        connexion.sendall(ligne)
        message = connexion.recv(SIZE)
        print(str(message, CODAGE))

        #Il faut vider la liste contenant les blocs de transactions une fois
        #la blockchain construite pour permettre de miner une nouvelle
        #chaine de bloc quand on est toujours connecté avec le serveur,c'est à
        #dire sans avoir à relancer la connection à chaque fois qu'on veuut
        #construire une nouvelle blockchain
        liste_bloc.clear()

        reponse = input("Créer une nouvelle BLOCKCHAIN ?" + OPTION)
        while reponse != "1" and reponse != "0" :
            reponse = input("Créer une nouvelle BLOCKCHAIN ?" + OPTION)

    if reponse == "0":
        print("PAS DE NOUVELLE BLOCKCHAIN ! \nMerci, A Bientôt !")
        break

connexion.close()
