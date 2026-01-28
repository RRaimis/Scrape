# TO DO:



# Conda tips

1. to create new clean environment --> conda create -n pydata

2. to run the environment (in anaconda prompt) --> conda activate pydata 

3. install necessary packages --> conda install numpy pandas ...

4. if these is something you dont have in conda, just use --> pip install nibabel nilearn

5. for first time packages, we can export env to environment.yml file after conda activate pydata, you need to create directory:

- cd C:\Users\Ocpc\Desktop\Git\1_datascience_project_template

- conda env export --from-history > env/environment.yml <-- # when u set template folder, export it environment.yml file
>
ON NEW MACHINE:

- cd C:\Users\Ocpc\Desktop\Git\1_datascience_project_template <-- where you want to export 

- conda env create -f env/environment.yml <-- creates env, contains "pydata" or other env inside environment.yml

- conda activate pydata

---

# Syncing python environments between 2 machines:

after installing packages simply by conda install packagename, you need to update environment.yml file on machine A:

- cd C:\Users\Ocpc\Desktop\Git\1_datascience_project_template

- conda activate pydata

- conda env export --from-history > env/environment.yml

↓ 

commit and push (this will help to update the env file so it goes into git)

on machine B:

- cd path/to/template-ds

- conda activate pydata

- conda env update -f env/environment.yml --prune
