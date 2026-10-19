# BD-ORTHO-donwload
API to donwload BD ORTHO data by region of insterest

- `python download_dept.py <dept_code>` to download the BD-ORTHO tiles of a specified department. Replace `<dept_code>` with your department code (e.g. `D065`) found at https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_BD-ORTHO?redirected_from=geoservices.ign.fr
- `python mark_tiles_in_poly.py <dir_tiles> <file_poly>` to mark all tiles that intersects a given polygon file. The polygon file may contain multiple polygons.
