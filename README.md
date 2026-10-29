# Kieker Analysis
Jupyter notebook project analysing PROV data captured using git2prov.

# Requirements
Poetry is used to manage dependencies. 
follow these [instructions](https://python-poetry.org/docs/#installation) to install Poetry.  
You will also need Docker

# Instructions
- you will need a provenance data archive file in ttl format 
## first time setup or rebuild
- clone the repo
- unpack the archive at './data/kieker_dump.ttl
- open a terminal in the repo root  
- run ```./bin/run.sh --build```  
## normal usage
- open a terminal in the repo root  
- run ```./bin/run.sh```  
## notes
- The jupyterlab server is available at localhost:8888
- The GraphDB instance will be available at localhost:3030
- A url with token will be printed in the logs if you want to integrate with your IDE  
- **!!important!!**  
If you make changes to the data, these will be lost on rebuild. If you want to persist or commit them you must replace the 
file at ```./data/kieker_dump.ttl```
To export changes, you can run ```./export.sh```