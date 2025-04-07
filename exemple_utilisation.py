#!/usr/bin/env python3
"""
Exemple d'utilisation du module docx_files_merger comme bibliothèque
Pour traiter plusieurs fichiers ZIP en une fois.

Développé par MOA Digital Agency LLC (https://myoneart.com)
Email: moa@myoneart.com
Copyright © 2025 MOA Digital Agency LLC. Tous droits réservés.
"""

import os
import sys
import glob
import time
from docx_files_merger import process_zip_file


def traiter_dossier_archives(dossier_archives, dossier_resultats):
    """
    Traite tous les fichiers ZIP dans un dossier.
    
    Args:
        dossier_archives: Chemin vers le dossier contenant les archives ZIP
        dossier_resultats: Chemin vers le dossier où stocker les résultats
        
    Returns:
        Une liste de dictionnaires contenant les résultats du traitement
    """
    # Vérifier que le dossier d'archives existe
    if not os.path.isdir(dossier_archives):
        print(f"Erreur: Le dossier {dossier_archives} n'existe pas.")
        return []
    
    # Créer le dossier de résultats s'il n'existe pas
    os.makedirs(dossier_resultats, exist_ok=True)
    
    # Récupérer tous les fichiers ZIP du dossier
    fichiers_zip = glob.glob(os.path.join(dossier_archives, "*.zip"))
    
    if not fichiers_zip:
        print(f"Aucun fichier ZIP trouvé dans {dossier_archives}.")
        return []
    
    print(f"Traitement de {len(fichiers_zip)} fichiers ZIP...")
    
    resultats = []
    
    # Traiter chaque fichier
    for i, zip_path in enumerate(fichiers_zip):
        # Récupérer le nom du fichier sans extension
        nom_fichier = os.path.basename(zip_path)
        nom_base = os.path.splitext(nom_fichier)[0]
        
        # Créer un sous-dossier pour les résultats de ce fichier
        dossier_sortie = os.path.join(dossier_resultats, nom_base)
        
        print(f"\n[{i+1}/{len(fichiers_zip)}] Traitement de {nom_fichier}...")
        
        # Mesurer le temps de traitement
        debut = time.time()
        
        try:
            # Traiter le fichier ZIP (en mode silencieux)
            docx_path, pdf_path = process_zip_file(zip_path, dossier_sortie, show_progress=False)
            
            temps_total = time.time() - debut
            
            if docx_path and pdf_path:
                statut = "Succès"
                resultat = {
                    "fichier": nom_fichier,
                    "statut": statut,
                    "temps": temps_total,
                    "docx": docx_path,
                    "pdf": pdf_path
                }
                resultats.append(resultat)
                print(f"  ✅ Traitement réussi en {temps_total:.1f} secondes.")
            else:
                statut = "Échec"
                resultat = {
                    "fichier": nom_fichier,
                    "statut": statut,
                    "temps": temps_total,
                    "erreur": "Aucun fichier généré"
                }
                resultats.append(resultat)
                print(f"  ❌ Échec du traitement.")
                
        except Exception as e:
            temps_total = time.time() - debut
            resultat = {
                "fichier": nom_fichier,
                "statut": "Erreur",
                "temps": temps_total,
                "erreur": str(e)
            }
            resultats.append(resultat)
            print(f"  ❌ Erreur: {str(e)}")
    
    # Afficher un résumé
    reussis = sum(1 for r in resultats if r["statut"] == "Succès")
    print(f"\nRésumé: {reussis}/{len(fichiers_zip)} fichiers traités avec succès.")
    
    return resultats


def main():
    """Fonction principale"""
    # Vérifier les arguments
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <dossier_archives> <dossier_resultats>")
        sys.exit(1)
    
    dossier_archives = sys.argv[1]
    dossier_resultats = sys.argv[2]
    
    # Traiter les fichiers
    resultats = traiter_dossier_archives(dossier_archives, dossier_resultats)
    
    # Afficher les résultats détaillés
    if resultats:
        print("\nDétails des traitements:")
        for i, res in enumerate(resultats):
            print(f"{i+1}. {res['fichier']}: {res['statut']} ({res['temps']:.1f}s)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())