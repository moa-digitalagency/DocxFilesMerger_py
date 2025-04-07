#!/usr/bin/env python3
"""
DocxFilesMerger - Application de traitement et fusion de documents.
Version: CLI améliorée
Développé par MOA Digital Agency LLC (https://myoneart.com)
Email: moa@myoneart.com
Copyright © 2025 MOA Digital Agency LLC. Tous droits réservés.
"""

import os
import sys
import time
import argparse
import glob
from pathlib import Path
from docx_files_merger import process_zip_file


def traiter_fichier(chemin_zip, dossier_sortie, silencieux=False):
    """
    Traite un fichier ZIP pour extraire, fusionner et convertir son contenu.
    
    Args:
        chemin_zip: Chemin vers le fichier ZIP à traiter
        dossier_sortie: Dossier où stocker les résultats
        silencieux: Mode silencieux (sans affichage de progression)
        
    Returns:
        Un dictionnaire avec le résultat du traitement
    """
    # Vérifier que le fichier existe
    if not os.path.isfile(chemin_zip):
        return {
            "statut": "erreur",
            "message": f"Le fichier {chemin_zip} n'existe pas.",
            "docx": None,
            "pdf": None
        }
    
    # Nom du fichier sans extension
    nom_fichier = os.path.basename(chemin_zip)
    nom_base = os.path.splitext(nom_fichier)[0]
    
    # Créer un sous-dossier pour les résultats si nécessaire
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie, exist_ok=True)
    
    # Mesurer le temps de traitement
    debut = time.time()
    
    try:
        # Traiter le fichier
        docx_path, pdf_path = process_zip_file(
            chemin_zip, 
            dossier_sortie,
            show_progress=(not silencieux)
        )
        
        temps_total = time.time() - debut
        
        if docx_path and pdf_path:
            return {
                "statut": "succès",
                "temps": temps_total,
                "docx": docx_path,
                "pdf": pdf_path,
                "message": f"Traitement réussi en {temps_total:.2f} secondes."
            }
        else:
            return {
                "statut": "partiel",
                "temps": temps_total,
                "docx": docx_path,
                "pdf": pdf_path,
                "message": "Traitement partiel (certains fichiers n'ont pas pu être générés)."
            }
    
    except Exception as e:
        temps_total = time.time() - debut
        return {
            "statut": "erreur",
            "temps": temps_total,
            "docx": None,
            "pdf": None,
            "message": f"Erreur lors du traitement: {str(e)}"
        }


def traiter_dossier(dossier_zip, dossier_sortie, silencieux=False):
    """
    Traite tous les fichiers ZIP d'un dossier.
    
    Args:
        dossier_zip: Chemin vers le dossier contenant les fichiers ZIP
        dossier_sortie: Dossier où stocker les résultats
        silencieux: Mode silencieux (sans affichage de progression)
        
    Returns:
        Une liste de dictionnaires contenant les résultats du traitement
    """
    # Vérifier que le dossier existe
    if not os.path.isdir(dossier_zip):
        print(f"Erreur: Le dossier {dossier_zip} n'existe pas.")
        return []
    
    # Trouver tous les fichiers ZIP
    fichiers_zip = glob.glob(os.path.join(dossier_zip, "*.zip"))
    
    if not fichiers_zip:
        print(f"Aucun fichier ZIP trouvé dans {dossier_zip}.")
        return []
    
    if not silencieux:
        print(f"Traitement de {len(fichiers_zip)} fichiers ZIP...")
    
    resultats = []
    
    # Traiter chaque fichier
    for i, zip_path in enumerate(fichiers_zip):
        if not silencieux:
            print(f"\n[{i+1}/{len(fichiers_zip)}] Traitement de {os.path.basename(zip_path)}...")
        
        # Créer un sous-dossier spécifique pour ce fichier
        nom_base = os.path.splitext(os.path.basename(zip_path))[0]
        dossier_resultat = os.path.join(dossier_sortie, nom_base)
        
        # Traiter le fichier
        resultat = traiter_fichier(zip_path, dossier_resultat, silencieux)
        resultat["fichier"] = zip_path
        resultats.append(resultat)
        
        # Afficher le résultat
        if not silencieux:
            if resultat["statut"] == "succès":
                print(f"  ✅ {resultat['message']}")
            elif resultat["statut"] == "partiel":
                print(f"  ⚠️ {resultat['message']}")
            else:
                print(f"  ❌ {resultat['message']}")
    
    # Afficher le résumé
    if not silencieux:
        reussis = sum(1 for r in resultats if r["statut"] == "succès")
        partiels = sum(1 for r in resultats if r["statut"] == "partiel")
        print(f"\nRésumé: {reussis} succès, {partiels} partiels, {len(fichiers_zip) - reussis - partiels} échecs sur {len(fichiers_zip)} fichiers.")
    
    return resultats


def main():
    """Fonction principale du script"""
    # Créer le parser d'arguments
    parser = argparse.ArgumentParser(
        description="DocxFilesMerger CLI - Outil de traitement de documents",
        epilog="Développé par MOA Digital Agency LLC (https://myoneart.com)"
    )
    
    # Groupe d'arguments mutuellement exclusifs pour l'entrée
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-f", "--fichier", help="Chemin vers un fichier ZIP à traiter")
    input_group.add_argument("-d", "--dossier", help="Chemin vers un dossier contenant des fichiers ZIP à traiter")
    
    # Arguments pour la sortie et les options
    parser.add_argument("-o", "--output", default="./output",
                        help="Dossier de sortie pour les fichiers générés (par défaut: ./output)")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Mode silencieux (sans affichage de progression)")
    parser.add_argument("-r", "--rapport", help="Générer un rapport CSV des résultats")
    
    # Parser les arguments
    args = parser.parse_args()
    
    # Traiter selon le mode d'entrée
    if args.fichier:
        # Traitement d'un seul fichier
        resultat = traiter_fichier(args.fichier, args.output, args.quiet)
        
        if not args.quiet:
            if resultat["statut"] == "succès":
                print(f"\n✅ {resultat['message']}")
                print(f"Document DOCX: {resultat['docx']}")
                print(f"Document PDF: {resultat['pdf']}")
            elif resultat["statut"] == "partiel":
                print(f"\n⚠️ {resultat['message']}")
                if resultat['docx']:
                    print(f"Document DOCX: {resultat['docx']}")
                if resultat['pdf']:
                    print(f"Document PDF: {resultat['pdf']}")
            else:
                print(f"\n❌ {resultat['message']}")
        
        # Générer un rapport si demandé
        if args.rapport:
            generer_rapport([resultat], args.rapport)
        
        # Code de retour basé sur le résultat
        return 0 if resultat["statut"] in ["succès", "partiel"] else 1
    
    else:
        # Traitement d'un dossier
        resultats = traiter_dossier(args.dossier, args.output, args.quiet)
        
        # Générer un rapport si demandé
        if args.rapport:
            generer_rapport(resultats, args.rapport)
        
        # Code de retour basé sur les résultats
        if not resultats:
            return 1
        
        echecs = sum(1 for r in resultats if r["statut"] == "erreur")
        return 0 if echecs < len(resultats) else 1


def generer_rapport(resultats, chemin_rapport):
    """
    Génère un rapport CSV des résultats du traitement.
    
    Args:
        resultats: Liste de dictionnaires contenant les résultats
        chemin_rapport: Chemin où sauvegarder le rapport CSV
    """
    import csv
    from datetime import datetime
    
    # En-têtes du CSV
    en_tetes = ["Date", "Fichier", "Statut", "Temps (s)", "DOCX", "PDF", "Message"]
    
    try:
        with open(chemin_rapport, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(en_tetes)
            
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for r in resultats:
                fichier = r.get("fichier", "?")
                if isinstance(fichier, str):
                    fichier = os.path.basename(fichier)
                
                writer.writerow([
                    date_str,
                    fichier,
                    r["statut"],
                    f"{r.get('temps', 0):.2f}",
                    os.path.basename(r["docx"]) if r["docx"] else "-",
                    os.path.basename(r["pdf"]) if r["pdf"] else "-",
                    r["message"]
                ])
        
        print(f"Rapport généré: {chemin_rapport}")
    
    except Exception as e:
        print(f"Erreur lors de la génération du rapport: {str(e)}")


if __name__ == "__main__":
    sys.exit(main())