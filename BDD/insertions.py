# -*- coding: utf-8 -*-
"""

Ce programme a pour but de faciliter l'insertion de données massives dans une base de données.

"""

##### Définitions #####
def insertion_colonne (table, nom_colonne, fichier_entree, fichier_sortie, id_start = 1, header = False) :
    ''' Permet de systématiser l'insertion d'une colonne de données dans une table SQL existante '''
    data_input = open(fichier_entree, 'r')
    data_output = open (fichier_sortie, 'w')
    
    if header :
        data_input.readline()
    
    for ligne in data_input :
        data_output.write('UPDATE ' + table + ' SET ' + nom_colonne + ' = \'' + ligne[:-2] + '\' WHERE id = ' + str(id_start) + ';\n')
        id_start += 1
    
    data_input.close()
    data_output.close()
    
    # Fin du fichier, améliorable... #
    data_output = open (fichier_sortie, 'r')
    contenu = data_output.readlines()
    contenu[-1] = contenu[-1][:-2] + ';'
    
    
    data_output = open(fichier_sortie, 'w')
    data_output.write(''.join(contenu))
    
    data_output.close()
    
def insertion_lignes (table, nom_colonnes, fichier_entree, fichier_sortie = 'instructions.sql', header = False) :
    ''' Permet d'insérer un nombre arbitraire de lignes
    insertion_lignes (table, nom_colonnes, fichier_entree, fichier_sortie = 'instructions.sql', header = False)
    
    ATTENTION : le fichier doit être consolidé, avec un nombre de colonnes correspondant au nom des colonnes
    '''
    
    data_input = open(fichier_entree, 'r')
    data_output = open(fichier_sortie, 'w')
    
    
    
    data_output.write("INSERT INTO " + table + " (" + nom_colonnes + ") VALUES\n")
    
    content = ''
    
    for ligne in data_input : 
        # Supprime les " présents de base dans le fichier #
        ligne = ligne.replace('"', '')
        
        content += "("
        for x in ligne.split(',') :
            content += "\"" + x + "\", "
        content = content[:-2] + "),\n"
    
    content = content[:-2] + ";"
    
    data_output.write(content)
    
    data_input.close()
    data_output.close()

##### Exploitation #####

#insertion_colonne(table = 'etablissement', nom_colonne = 'structure_juridique', fichier_entree = 'structure_juridique.csv', fichier_sortie = 'instructions.sql')
insertion_lignes ('ma_table', 'id, nom', 'donnees_entree.csv')
